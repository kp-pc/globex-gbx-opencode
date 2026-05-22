import json
import time
import threading
import io
import base64
import requests
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import Response
from pydantic import BaseModel
import qrcode

import config
from core import Blockchain
from wallet import Wallet, WalletError, create_transaction
from staking import Staker

app = FastAPI(title="Globex GBX Node", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

blockchain = Blockchain(db_path="globex_data/blockchain.db")
staker = Staker(blockchain.conn)
mining_lock = threading.Lock()

WALLETS_DIR = Path(__file__).parent / "globex_data" / "wallets"
WALLETS_DIR.mkdir(parents=True, exist_ok=True)


class TransactionRequest(BaseModel):
    sender: str
    recipient: str
    amount: int
    fee: int = 0
    nonce: int = 0
    memo: str = ""
    public_key: str = ""
    signature: str = ""


class WalletCreateRequest(BaseModel):
    password: str = ""


class WalletImportRequest(BaseModel):
    wif: str = ""
    seed_phrase: str = ""
    passphrase: str = ""
    password: str = ""


class SendRequest(BaseModel):
    sender: str
    recipient: str
    amount: int
    fee: int = 0
    memo: str = ""
    private_key: str = ""


class PeerRequest(BaseModel):
    address: str
    port: int


class StakeRequest(BaseModel):
    address: str
    amount: int


@app.get("/")
def root():
    last = blockchain.get_last_block()
    return {
        "node": "Globex GBX",
        "chain_length": blockchain.get_chain_length(),
        "last_block": last.hash if last else None,
        "last_block_index": last.index if last else None,
        "mempool_size": len(blockchain.mempool),
        "peers_count": len(blockchain.get_peers()),
        "version": config.NODE_VERSION
    }


@app.get("/chain")
def get_chain():
    c = blockchain.conn.cursor()
    c.execute("SELECT * FROM blocks ORDER BY idx ASC")
    chain = []
    for row in c.fetchall():
        chain.append({
            "index": row["idx"],
            "hash": row["hash"],
            "prev_hash": row["prev_hash"],
            "timestamp": row["timestamp"],
            "target": int(row["target"]),
            "nonce": row["nonce"],
            "merkle_root": row["merkle_root"],
            "transactions": json.loads(row["transactions"]),
        })
    return {"chain": chain, "length": len(chain)}


@app.get("/balance/{address}")
def get_balance(address: str):
    balance = blockchain.get_balance(address)
    return {"address": address, "balance": balance, "formatted": balance / config.GBX}


@app.post("/transactions/new")
def new_transaction(tx: TransactionRequest):
    tx_dict = {
        "sender": tx.sender,
        "recipient": tx.recipient,
        "amount": tx.amount,
        "fee": tx.fee,
        "timestamp": int(time.time()),
        "nonce": tx.nonce,
        "memo": tx.memo,
        "public_key": tx.public_key,
        "signature": tx.signature
    }
    if tx.sender != "0":
        if not Wallet.verify_transaction(tx_dict):
            raise HTTPException(status_code=400, detail="Invalid signature")
        sender_balance = blockchain.get_balance(tx.sender)
        if sender_balance < tx.amount + tx.fee:
            raise HTTPException(status_code=400, detail="Insufficient balance")
    tx_hash = blockchain.add_transaction(tx_dict)
    if not tx_hash:
        raise HTTPException(status_code=400, detail="Transaction rejected")
    return {"message": "Transaction added", "tx_hash": tx_hash}


@app.get("/mine")
def mine(address: str):
    if not mining_lock.acquire(blocking=False):
        return {"message": "Mining already in progress"}
    try:
        block = blockchain.mine_block(address)
        if not block:
            raise HTTPException(status_code=500, detail="Mining failed")
        return {
            "message": "Block mined",
            "index": block.index,
            "hash": block.hash,
            "transactions": len(block.transactions)
        }
    finally:
        mining_lock.release()


@app.get("/blocks/latest")
def get_latest_block():
    block = blockchain.get_last_block()
    if not block:
        raise HTTPException(status_code=404, detail="No blocks")
    return block.to_dict()


class BlockSubmitRequest(BaseModel):
    index: int
    timestamp: int
    transactions: list
    prev_hash: str
    target: int
    nonce: int
    merkle_root: str
    hash: str


@app.post("/blocks/submit")
def submit_block(block_data: BlockSubmitRequest):
    from core import Block
    block = Block(
        index=block_data.index,
        timestamp=block_data.timestamp,
        transactions=block_data.transactions,
        prev_hash=block_data.prev_hash,
        target=block_data.target,
        nonce=block_data.nonce,
        hash_val=block_data.hash,
        merkle_root_val=bytes.fromhex(block_data.merkle_root)
    )
    last = blockchain.get_last_block()
    if block.index != (last.index + 1) if last else 0:
        raise HTTPException(status_code=400, detail="Invalid block index")
    if block.prev_hash != last.hash:
        raise HTTPException(status_code=400, detail="Previous hash mismatch")
    if block.calculate_hash() != block.hash:
        raise HTTPException(status_code=400, detail="Invalid block hash")
    if int(block.hash, 16) >= block.target:
        raise HTTPException(status_code=400, detail="Block hash does not meet target")
    for tx in block.transactions:
        if tx.get("sender", "0") != "0":
            if not Wallet.verify_transaction(tx):
                raise HTTPException(status_code=400, detail="Invalid transaction signature")
    blockchain._store_block(block)
    blockchain._apply_block(block)
    mined_hashes = [tx["tx_hash"] for tx in block.transactions if tx.get("tx_hash")]
    if mined_hashes:
        c = blockchain.conn.cursor()
        c.execute("DELETE FROM mempool WHERE tx_hash IN ({})".format(
            ",".join("?" for _ in mined_hashes)), mined_hashes)
        blockchain.conn.commit()
        blockchain._load_mempool()
    return {"message": "Block accepted", "hash": block.hash}


@app.post("/nodes/register")
def register_peer(peer: PeerRequest):
    blockchain.add_peer(peer.address, peer.port)
    return {"message": "Peer registered", "peer": f"{peer.address}:{peer.port}"}


@app.get("/nodes/resolve")
def resolve_conflicts():
    peers = blockchain.get_peers()
    replaced = False
    for peer in peers:
        try:
            resp = requests.get(
                f"http://{peer['address']}:{peer['port']}/chain",
                timeout=5
            )
            if resp.status_code == 200:
                other_chain = resp.json().get("chain", [])
                if blockchain.resolve_conflicts(other_chain):
                    replaced = True
        except Exception:
            continue
    return {
        "message": "Chain resolved",
        "chain_replaced": replaced,
        "chain_length": blockchain.get_chain_length()
    }


@app.get("/mempool")
def get_mempool():
    return {"mempool": blockchain.mempool, "size": len(blockchain.mempool)}


@app.get("/peers")
def get_peers():
    return {"peers": blockchain.get_peers()}


@app.get("/stats")
def get_stats():
    last = blockchain.get_last_block()
    return {
        "chain_length": blockchain.get_chain_length(),
        "last_block_hash": last.hash if last else None,
        "last_block_time": last.timestamp if last else None,
        "mempool_size": len(blockchain.mempool),
        "peers_count": len(blockchain.get_peers()),
        "total_supply": sum(blockchain.balances.values()),
        "latest_target": last.target if last else None,
    }


@app.post("/wallet/create")
def wallet_create(req: WalletCreateRequest):
    wallet = Wallet()
    path = WALLETS_DIR / f"{wallet.address}.json"
    wallet.save(str(path), password=req.password or None)
    return {
        "address": wallet.address,
        "public_key": wallet.public_key.hex(),
        "wif": wallet.to_wif() if not req.password else None,
        "encrypted": bool(req.password),
        "file": str(path)
    }


@app.post("/wallet/import")
def wallet_import(req: WalletImportRequest):
    try:
        if req.wif:
            wallet = Wallet.from_wif(req.wif)
        elif req.seed_phrase:
            wallet = Wallet.from_seed_phrase(req.seed_phrase, req.passphrase)
        else:
            raise HTTPException(400, "Provide wif or seed_phrase")
    except WalletError as e:
        raise HTTPException(400, str(e))
    path = WALLETS_DIR / f"{wallet.address}.json"
    wallet.save(str(path), password=req.password or None)
    return {
        "address": wallet.address,
        "public_key": wallet.public_key.hex(),
        "file": str(path)
    }


@app.get("/wallet/{address}/qrcode")
def wallet_qrcode(address: str):
    qr = qrcode.make(address)
    buf = io.BytesIO()
    qr.save(buf, format="PNG")
    buf.seek(0)
    return Response(content=buf.getvalue(), media_type="image/png")


@app.post("/transactions/create-and-send")
def create_and_send(req: SendRequest):
    try:
        wallet = Wallet(private_key=bytes.fromhex(req.private_key))
    except Exception:
        raise HTTPException(400, "Invalid private key")
    if wallet.address != req.sender:
        raise HTTPException(400, "Private key does not match sender address")
    balance = blockchain.get_balance(req.sender)
    total = req.amount + req.fee
    if balance < total:
        raise HTTPException(400, f"Insufficient balance: {balance/config.GBX:.2f} GBX, need {total/config.GBX:.2f} GBX")
    tx = create_transaction(req.sender, req.recipient, req.amount, req.fee)
    tx["memo"] = req.memo
    signed = wallet.sign_transaction(tx)
    tx_hash = blockchain.add_transaction(signed)
    if not tx_hash:
        raise HTTPException(400, "Transaction rejected")
    return {"message": "Transaction sent", "tx_hash": tx_hash}


@app.get("/mining/stats")
def mining_stats():
    s = blockchain.mining_stats
    return {
        "is_mining": s.is_mining,
        "hash_rate": s.hash_rate,
        "current_nonce": s.current_nonce,
        "last_block_height": s.last_block_height,
        "last_block_hash": s.last_block_hash,
        "total_hashes": s.total_hashes,
    }


@app.get("/mining/info")
def mining_info():
    last = blockchain.get_last_block()
    if not last:
        return {"difficulty": 1, "target": config.GENESIS_TARGET}
    target_max = config.MAX_TARGET
    difficulty = target_max / last.target if last.target > 0 else 1
    return {
        "difficulty": difficulty,
        "target": last.target,
        "target_hex": hex(last.target),
        "block_height": last.index,
        "block_time": config.TARGET_BLOCK_TIME,
    }


@app.get("/sync/status")
def sync_status():
    peers = blockchain.get_peers()
    local_height = blockchain.get_chain_length()
    syncing = False
    highest_peer_height = 0
    for peer in peers:
        try:
            resp = requests.get(
                f"http://{peer['address']}:{peer['port']}/",
                timeout=3
            )
            if resp.status_code == 200:
                peer_height = resp.json().get("chain_length", 0)
                if peer_height > highest_peer_height:
                    highest_peer_height = peer_height
        except Exception:
            continue
    if highest_peer_height > local_height + 1:
        syncing = True
    return {
        "syncing": syncing,
        "local_height": local_height,
        "highest_peer_height": highest_peer_height,
        "peers_connected": len(peers),
        "progress": (local_height / highest_peer_height * 100) if highest_peer_height > 0 else 100,
    }


@app.get("/staking/validators")
def staking_validators():
    return {"validators": staker.get_validators(), "count": len(staker.get_validators())}


@app.get("/staking/validator/{address}")
def staking_validator(address: str):
    v = staker.get_validator(address)
    if not v:
        raise HTTPException(404, "Validator not found")
    return v


@app.post("/staking/register")
def staking_register(req: StakeRequest):
    if req.amount < config.STAKE_MINIMUM:
        raise HTTPException(400, f"Minimum stake is {config.STAKE_MINIMUM // config.GBX} GBX")
    balance = blockchain.get_balance(req.address)
    if balance < req.amount:
        raise HTTPException(400, "Insufficient balance")
    if staker.register_validator(req.address, req.amount):
        return {"message": "Validator registered", "address": req.address, "stake": req.amount}
    raise HTTPException(500, "Registration failed")


@app.get("/staking/checkpoints")
def staking_checkpoints():
    return {"checkpoints": staker.get_checkpoints(limit=20)}


gui_dir = Path(__file__).parent / "gui"
if gui_dir.exists():
    app.mount("/", StaticFiles(directory=str(gui_dir), html=True), name="gui")


def start_node(host: str = "0.0.0.0", port: int = 8545):
    import uvicorn
    uvicorn.run(app, host=host, port=port, log_level="info")


if __name__ == "__main__":
    start_node()
