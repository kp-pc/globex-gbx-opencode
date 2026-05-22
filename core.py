import json
import struct
import time
import sqlite3
import os
from typing import Optional

import config
import utils


def tx_hash(tx: dict) -> str:
    raw = json.dumps(tx, sort_keys=True).encode()
    return utils.sha256d(raw).hex()


class Block:
    def __init__(self, index, timestamp, transactions, prev_hash, target,
                 nonce=0, hash_val=None, merkle_root_val=None):
        self.index = index
        self.timestamp = timestamp
        self.transactions = transactions
        self.prev_hash = prev_hash
        self.target = target
        self.nonce = nonce
        if merkle_root_val:
            self.merkle_root = merkle_root_val
        else:
            tx_hashes = [bytes.fromhex(tx_hash(t)) for t in transactions]
            self.merkle_root = utils.merkle_root(tx_hashes)
        if hash_val:
            self.hash = hash_val
        else:
            self.hash = self.calculate_hash()

    def header_bytes(self) -> bytes:
        return (struct.pack("<Q", self.index) +
                struct.pack("<I", self.timestamp) +
                bytes.fromhex(self.prev_hash) +
                self.merkle_root +
                self.target.to_bytes(32, 'big') +
                struct.pack("<Q", self.nonce))

    def calculate_hash(self) -> str:
        return utils.sha256d(self.header_bytes()).hex()

    def mine(self) -> int:
        target_int = self.target
        while True:
            hash_int = int(self.hash, 16)
            if hash_int < target_int:
                return self.nonce
            self.nonce += 1
            self.hash = self.calculate_hash()

    def to_dict(self) -> dict:
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "transactions": self.transactions,
            "prev_hash": self.prev_hash,
            "target": self.target,
            "nonce": self.nonce,
            "merkle_root": self.merkle_root.hex(),
            "hash": self.hash
        }

    @classmethod
    def from_dict(cls, d: dict):
        return cls(
            index=d["index"],
            timestamp=d["timestamp"],
            transactions=d["transactions"],
            prev_hash=d["prev_hash"],
            target=d["target"],
            nonce=d["nonce"],
            hash_val=d["hash"],
            merkle_root_val=bytes.fromhex(d["merkle_root"])
        )


class Blockchain:
    def __init__(self, db_path="blockchain.db"):
        self.db_path = db_path
        self.mempool = []
        self.balances = {}
        self._last_block = None
        self._init_db()
        if not self._load_chain():
            self._create_genesis_block()

    def _init_db(self):
        os.makedirs(os.path.dirname(os.path.abspath(self.db_path)) or ".", exist_ok=True)
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        c = self.conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS blocks (
                idx INTEGER PRIMARY KEY,
                hash TEXT UNIQUE,
                prev_hash TEXT,
                timestamp INTEGER,
                target TEXT,
                nonce INTEGER,
                merkle_root TEXT,
                transactions TEXT
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS mempool (
                tx_hash TEXT PRIMARY KEY,
                sender TEXT,
                recipient TEXT,
                amount INTEGER,
                fee INTEGER,
                timestamp INTEGER,
                nonce INTEGER,
                signature TEXT
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS peers (
                address TEXT,
                port INTEGER,
                last_seen INTEGER,
                PRIMARY KEY (address, port)
            )
        """)
        self.conn.commit()

    def _load_chain(self) -> bool:
        c = self.conn.cursor()
        c.execute("SELECT COUNT(*) FROM blocks")
        if c.fetchone()[0] == 0:
            return False
        self._rebuild_balances()
        self._load_mempool()
        return True

    def _rebuild_balances(self):
        self.balances = {}
        c = self.conn.cursor()
        c.execute("SELECT idx FROM blocks ORDER BY idx ASC")
        for (idx,) in c.fetchall():
            block = self.get_block_by_index(idx)
            if block:
                self._apply_block(block)

    def _apply_block(self, block: Block):
        for tx in block.transactions:
            sender = tx.get("sender", "0")
            recipient = tx.get("recipient", "")
            amount = tx.get("amount", 0)
            fee = tx.get("fee", 0)
            if sender != "0":
                self.balances[sender] = self.balances.get(sender, 0) - amount - fee
            self.balances[recipient] = self.balances.get(recipient, 0) + amount

    def _load_mempool(self):
        self.mempool = []
        c = self.conn.cursor()
        c.execute("SELECT * FROM mempool ORDER BY timestamp ASC")
        for row in c.fetchall():
            self.mempool.append({
                "tx_hash": row["tx_hash"],
                "sender": row["sender"],
                "recipient": row["recipient"],
                "amount": row["amount"],
                "fee": row["fee"],
                "timestamp": row["timestamp"],
                "nonce": row["nonce"],
                "signature": row["signature"]
            })

    def _create_genesis_block(self):
        genesis = Block(
            index=0,
            timestamp=config.GENESIS_TIMESTAMP,
            transactions=[],
            prev_hash="0" * 64,
            target=config.GENESIS_TARGET,
            nonce=0
        )
        if int(genesis.hash, 16) >= genesis.target:
            genesis.mine()
        self._store_block(genesis)

    def _store_block(self, block: Block):
        c = self.conn.cursor()
        c.execute("""
            INSERT OR IGNORE INTO blocks (idx, hash, prev_hash, timestamp, target, nonce, merkle_root, transactions)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            block.index, block.hash, block.prev_hash, block.timestamp,
            str(block.target), block.nonce, block.merkle_root.hex(),
            json.dumps(block.transactions)
        ))
        self.conn.commit()
        self._last_block = block

    def _block_from_row(self, row) -> Optional[Block]:
        if not row:
            return None
        return Block(
            index=row["idx"],
            timestamp=row["timestamp"],
            transactions=json.loads(row["transactions"]),
            prev_hash=row["prev_hash"],
            target=int(row["target"]),
            nonce=row["nonce"],
            hash_val=row["hash"],
            merkle_root_val=bytes.fromhex(row["merkle_root"])
        )

    def get_block_by_index(self, index: int) -> Optional[Block]:
        c = self.conn.cursor()
        c.execute("SELECT * FROM blocks WHERE idx = ?", (index,))
        return self._block_from_row(c.fetchone())

    def get_block_by_hash(self, hash_val: str) -> Optional[Block]:
        c = self.conn.cursor()
        c.execute("SELECT * FROM blocks WHERE hash = ?", (hash_val,))
        return self._block_from_row(c.fetchone())

    def get_last_block(self) -> Optional[Block]:
        if self._last_block:
            return self._last_block
        c = self.conn.cursor()
        c.execute("SELECT * FROM blocks ORDER BY idx DESC LIMIT 1")
        block = self._block_from_row(c.fetchone())
        self._last_block = block
        return block

    def get_chain_length(self) -> int:
        c = self.conn.cursor()
        c.execute("SELECT MAX(idx) FROM blocks")
        row = c.fetchone()
        return (row[0] or 0) + 1

    def get_block_reward(self, height: int) -> int:
        halvings = height // config.HALVING_INTERVAL
        reward = config.INITIAL_BLOCK_REWARD >> halvings
        if reward < config.DUST_LIMIT:
            return 0
        return reward

    def _adjust_target(self) -> int:
        last_block = self.get_last_block()
        if not last_block:
            return config.GENESIS_TARGET
        if last_block.index < 1:
            return last_block.target
        if (last_block.index + 1) % config.DIFFICULTY_ADJUSTMENT_INTERVAL != 0:
            return last_block.target
        start_index = last_block.index + 1 - config.DIFFICULTY_ADJUSTMENT_INTERVAL
        c = self.conn.cursor()
        c.execute("SELECT timestamp FROM blocks WHERE idx = ?", (start_index,))
        row = c.fetchone()
        if not row:
            return last_block.target
        actual_time = last_block.timestamp - row[0]
        expected_time = config.TARGET_BLOCK_TIME * config.DIFFICULTY_ADJUSTMENT_INTERVAL
        if actual_time <= 0:
            actual_time = 1
        new_target = int(last_block.target * actual_time / expected_time)
        if new_target > config.MAX_TARGET:
            return config.MAX_TARGET
        if new_target < config.MIN_TARGET:
            return config.MIN_TARGET
        return new_target

    def create_coinbase_transaction(self, miner_address: str, height: int, total_fees: int = 0) -> dict:
        reward = self.get_block_reward(height) + total_fees
        return {
            "sender": "0",
            "recipient": miner_address,
            "amount": reward,
            "fee": 0,
            "timestamp": int(time.time()),
            "nonce": 0,
            "signature": "",
            "tx_hash": ""
        }

    def add_transaction(self, tx: dict) -> Optional[str]:
        required = ["sender", "recipient", "amount", "timestamp", "nonce", "signature"]
        for key in required:
            if key not in tx:
                return None
        if tx["sender"] == "0":
            return None
        if tx["amount"] < config.DUST_LIMIT and tx["amount"] > 0:
            return None
        h = tx_hash(tx)
        tx["tx_hash"] = h
        if h not in [t["tx_hash"] for t in self.mempool]:
            c = self.conn.cursor()
            c.execute("""
                INSERT OR IGNORE INTO mempool (tx_hash, sender, recipient, amount, fee, timestamp, nonce, signature)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                h, tx["sender"], tx["recipient"], tx["amount"],
                tx.get("fee", 0), tx["timestamp"], tx["nonce"], tx["signature"]
            ))
            self.conn.commit()
            self.mempool.append(tx)
        return h

    def mine_block(self, miner_address: str) -> Optional[Block]:
        last_block = self.get_last_block()
        if not last_block:
            return None
        height = last_block.index + 1
        target = self._adjust_target()
        c = self.conn.cursor()
        c.execute("SELECT SUM(fee) FROM mempool")
        total_fees = c.fetchone()[0] or 0
        coinbase = self.create_coinbase_transaction(miner_address, height, total_fees)
        coinbase["tx_hash"] = tx_hash(coinbase)
        txs = [coinbase]
        c.execute("SELECT * FROM mempool ORDER BY fee DESC, timestamp ASC LIMIT ?",
                  (config.MAX_TRANSACTIONS_PER_BLOCK - 1,))
        for row in c.fetchall():
            fee = row["fee"]
            txs.append({
                "tx_hash": row["tx_hash"],
                "sender": row["sender"],
                "recipient": row["recipient"],
                "amount": row["amount"],
                "fee": fee,
                "timestamp": row["timestamp"],
                "nonce": row["nonce"],
                "signature": row["signature"]
            })
        block = Block(
            index=height,
            timestamp=int(time.time()),
            transactions=txs,
            prev_hash=last_block.hash,
            target=target,
            nonce=0
        )
        block.mine()
        self._store_block(block)
        self._apply_block(block)
        mined_hashes = [tx["tx_hash"] for tx in txs if tx["tx_hash"]]
        c.execute("DELETE FROM mempool WHERE tx_hash IN ({})".format(
            ",".join("?" for _ in mined_hashes)), mined_hashes)
        self.conn.commit()
        self._load_mempool()
        return block

    def get_balance(self, address: str) -> int:
        return self.balances.get(address, 0)

    def validate_chain(self) -> bool:
        c = self.conn.cursor()
        c.execute("SELECT * FROM blocks ORDER BY idx ASC")
        rows = c.fetchall()
        for row in rows:
            if row["idx"] == 0:
                continue
            block = self._block_from_row(row)
            if not block:
                return False
            if block.calculate_hash() != block.hash:
                return False
            if int(block.hash, 16) >= block.target:
                return False
            prev = self.get_block_by_index(block.index - 1)
            if not prev or block.prev_hash != prev.hash:
                return False
        return True

    def add_peer(self, address: str, port: int):
        c = self.conn.cursor()
        c.execute("""
            INSERT OR REPLACE INTO peers (address, port, last_seen)
            VALUES (?, ?, ?)
        """, (address, port, int(time.time())))
        self.conn.commit()

    def get_peers(self) -> list:
        c = self.conn.cursor()
        c.execute("SELECT * FROM peers ORDER BY last_seen DESC")
        return [{"address": row["address"], "port": row["port"]} for row in c.fetchall()]

    def resolve_conflicts(self, other_chain: list) -> bool:
        if len(other_chain) <= self.get_chain_length():
            return False
        for block_data in other_chain:
            block = Block.from_dict(block_data)
            if block.index == 0:
                continue
            existing = self.get_block_by_index(block.index)
            if not existing:
                if block.index != self.get_chain_length():
                    return False
                last = self.get_last_block()
                if block.prev_hash != last.hash:
                    return False
                if int(block.hash, 16) >= block.target:
                    return False
                self._store_block(block)
                self._apply_block(block)
        return True
