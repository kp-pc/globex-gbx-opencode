import json
import time
import threading
import requests
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

import config
from core import Blockchain
from wallet import Wallet, create_transaction

app = FastAPI(title="Globex GBX Node", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

blockchain = Blockchain(db_path="globex_data/blockchain.db")
mining_lock = threading.Lock()


class TransactionRequest(BaseModel):
    sender: str
    recipient: str
    amount: int
    fee: int = 0
    nonce: int = 0
    public_key: str = ""
    signature: str = ""


class PeerRequest(BaseModel):
    address: str
    port: int


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


gui_dir = Path(__file__).parent / "gui"
if gui_dir.exists():
    app.mount("/", StaticFiles(directory=str(gui_dir), html=True), name="gui")


def start_node(host: str = "0.0.0.0", port: int = 8545):
    import uvicorn
    uvicorn.run(app, host=host, port=port, log_level="info")


if __name__ == "__main__":
    start_node()
