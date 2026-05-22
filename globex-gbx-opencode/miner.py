import time
import threading
import requests
import struct

import config
from core import Block, tx_hash
from wallet import Wallet


class Miner:
    def __init__(self, node_url: str, address: str, threads: int = 1):
        self.node_url = node_url.rstrip("/")
        self.address = address
        self.threads = threads
        self.hash_count = 0
        self.running = False
        self.solved = threading.Event()
        self._lock = threading.Lock()

    def _api_get(self, path: str):
        resp = requests.get(f"{self.node_url}{path}", timeout=10)
        resp.raise_for_status()
        return resp.json()

    def _api_post(self, path: str, data: dict):
        resp = requests.post(f"{self.node_url}{path}", json=data, timeout=10)
        resp.raise_for_status()
        return resp.json()

    def _mine_thread(self, block: Block, start_nonce: int, step: int):
        target_int = block.target
        block.nonce = start_nonce
        local_count = 0
        while not self.solved.is_set():
            block.hash = block.calculate_hash()
            local_count += 1
            if int(block.hash, 16) < target_int:
                with self._lock:
                    self.hash_count += local_count
                self.solved.set()
                return block.nonce
            block.nonce += step
        with self._lock:
            self.hash_count += local_count
        return None

    def _build_candidate(self) -> Block:
        last = self._api_get("/blocks/latest")
        mempool = self._api_get("/mempool")
        height = last["index"] + 1
        target = self._calculate_target(last)
        coinbase = {
            "sender": "0",
            "recipient": self.address,
            "amount": self._get_block_reward(height),
            "fee": 0,
            "timestamp": int(time.time()),
            "nonce": 0,
            "signature": "",
            "tx_hash": ""
        }
        coinbase["tx_hash"] = tx_hash(coinbase)
        txs = [coinbase]
        for tx in mempool.get("mempool", []):
            txs.append(tx)
            if len(txs) >= config.MAX_TRANSACTIONS_PER_BLOCK:
                break
        return Block(
            index=height,
            timestamp=int(time.time()),
            transactions=txs,
            prev_hash=last["hash"],
            target=target,
            nonce=0
        )

    def _calculate_target(self, last_block: dict) -> int:
        height = last_block["index"] + 1
        if height % config.DIFFICULTY_ADJUSTMENT_INTERVAL == 0 and height > 0:
            try:
                start_block_resp = requests.get(
                    f"{self.node_url}/chain", timeout=5
                ).json()
                start_idx = height - config.DIFFICULTY_ADJUSTMENT_INTERVAL
                for b in start_block_resp.get("chain", []):
                    if b["index"] == start_idx:
                        actual_time = last_block["timestamp"] - b["timestamp"]
                        expected = config.TARGET_BLOCK_TIME * config.DIFFICULTY_ADJUSTMENT_INTERVAL
                        if actual_time <= 0:
                            actual_time = 1
                        new_target = int(last_block["target"] * actual_time / expected)
                        if new_target > config.MAX_TARGET:
                            return config.MAX_TARGET
                        if new_target < config.MIN_TARGET:
                            return config.MIN_TARGET
                        return new_target
            except Exception:
                pass
        return last_block["target"]

    def _get_block_reward(self, height: int) -> int:
        halvings = height // config.HALVING_INTERVAL
        reward = config.INITIAL_BLOCK_REWARD >> halvings
        return reward if reward >= config.DUST_LIMIT else 0

    def start(self):
        self.running = True
        print(f"Miner started: {self.threads} threads, address: {self.address}")
        hashrate_interval = 10
        last_time = time.time()
        while self.running:
            self.solved.clear()
            try:
                block = self._build_candidate()
            except Exception as e:
                print(f"Failed to build candidate: {e}")
                time.sleep(5)
                continue
            self.hash_count = 0
            threads = []
            for i in range(self.threads):
                t = threading.Thread(
                    target=self._mine_thread,
                    args=(block, i, self.threads),
                    daemon=True
                )
                t.start()
                threads.append(t)
            last_count = 0
            while not self.solved.is_set():
                time.sleep(1)
                now = time.time()
                elapsed = now - last_time
                if elapsed >= hashrate_interval:
                    with self._lock:
                        hashes = self.hash_count - last_count
                        last_count = self.hash_count
                    hash_rate = hashes / elapsed
                    unit = "H/s"
                    rate_display = hash_rate
                    if rate_display >= 1000000:
                        rate_display /= 1000000
                        unit = "MH/s"
                    elif rate_display >= 1000:
                        rate_display /= 1000
                        unit = "KH/s"
                    print(f"Hash rate: {rate_display:.2f} {unit}  "
                          f"Nonce: {block.nonce}  "
                          f"Target: {hex(block.target)[:12]}")
                    last_time = now
            for t in threads:
                t.join(timeout=1)
            try:
                result = self._submit_block(block)
                print(f"Block mined! Hash: {block.hash[:16]}... "
                      f"Height: {block.index}")
            except Exception as e:
                print(f"Block submission failed: {e}")
                time.sleep(2)

    def _submit_block(self, block: Block) -> dict:
        block_data = {
            "index": block.index,
            "timestamp": block.timestamp,
            "transactions": block.transactions,
            "prev_hash": block.prev_hash,
            "target": block.target,
            "nonce": block.nonce,
            "merkle_root": block.merkle_root.hex(),
            "hash": block.hash
        }
        return self._api_post("/blocks/submit", block_data)

    def stop(self):
        self.running = False
        self.solved.set()


def start_miner(node_url: str, address: str, threads: int = 1):
    miner = Miner(node_url, address, threads)
    try:
        miner.start()
    except KeyboardInterrupt:
        miner.stop()
        print("\nMiner stopped.")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Globex CPU Miner")
    parser.add_argument("--node", default="http://127.0.0.1:8545")
    parser.add_argument("--address", required=True)
    parser.add_argument("--threads", type=int, default=1)
    args = parser.parse_args()
    start_miner(args.node, args.address, args.threads)
