import time
import sqlite3
from typing import Optional

import config


class Staker:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn
        self._init_tables()

    def _init_tables(self):
        c = self.conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS validators (
                address TEXT PRIMARY KEY,
                stake INTEGER NOT NULL DEFAULT 0,
                locked_until INTEGER NOT NULL DEFAULT 0,
                missed_blocks INTEGER NOT NULL DEFAULT 0,
                blocks_validated INTEGER NOT NULL DEFAULT 0,
                is_slashed INTEGER NOT NULL DEFAULT 0,
                registered_at INTEGER NOT NULL
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS stakes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                validator TEXT NOT NULL,
                amount INTEGER NOT NULL,
                lock_start INTEGER NOT NULL,
                lock_end INTEGER NOT NULL,
                withdrawn INTEGER NOT NULL DEFAULT 0,
                FOREIGN KEY (validator) REFERENCES validators(address)
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS checkpoints (
                block_index INTEGER PRIMARY KEY,
                block_hash TEXT NOT NULL,
                finalized_at INTEGER NOT NULL,
                validator_count INTEGER NOT NULL DEFAULT 0
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS slashing_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                validator TEXT NOT NULL,
                block_index INTEGER NOT NULL DEFAULT 0,
                reason TEXT NOT NULL,
                penalty INTEGER NOT NULL,
                occurred_at INTEGER NOT NULL
            )
        """)
        c.execute("PRAGMA table_info(validators)")
        cols = [row[1] for row in c.fetchall()]
        if "blocks_validated" not in cols:
            c.execute("ALTER TABLE validators ADD COLUMN blocks_validated INTEGER NOT NULL DEFAULT 0")
        if "registered_at" not in cols:
            c.execute("ALTER TABLE validators ADD COLUMN registered_at INTEGER NOT NULL DEFAULT 0")
        self.conn.commit()

    def register_validator(self, address: str, amount: int) -> bool:
        if amount < config.STAKE_MINIMUM:
            return False
        now = int(time.time())
        c = self.conn.cursor()
        c.execute("""
            INSERT OR REPLACE INTO validators
            (address, stake, locked_until, missed_blocks, is_slashed, registered_at)
            VALUES (?, ?, ?, 0, 0, ?)
        """, (address, amount, now + config.STAKE_LOCK_BLOCKS * config.TARGET_BLOCK_TIME, now))
        c.execute("""
            INSERT INTO stakes (validator, amount, lock_start, lock_end, withdrawn)
            VALUES (?, ?, ?, ?, 0)
        """, (address, amount, now,
              now + config.STAKE_LOCK_BLOCKS * config.TARGET_BLOCK_TIME))
        self.conn.commit()
        return True

    def _distribute_stake_reward(self, address: str, height: int):
        c = self.conn.cursor()
        c.execute("SELECT stake FROM validators WHERE address = ?", (address,))
        row = c.fetchone()
        if not row or row[0] == 0:
            return
        reward = max(1, row[0] * config.STAKE_REWARD_RATE // (config.HALVING_INTERVAL * 100))
        c.execute("UPDATE validators SET stake = stake + ? WHERE address = ?",
                  (reward, address))
        self.conn.commit()

    def report_missed_block(self, address: str):
        c = self.conn.cursor()
        c.execute("""UPDATE validators
                     SET missed_blocks = missed_blocks + 1
                     WHERE address = ?""", (address,))
        self.conn.commit()
        c.execute("SELECT missed_blocks FROM validators WHERE address = ?", (address,))
        row = c.fetchone()
        if row and row[0] >= config.SLASHING_THRESHOLD_MISSED:
            self.slash(address, "Missed too many blocks")

    def record_block_validated(self, address: str):
        c = self.conn.cursor()
        c.execute("""UPDATE validators
                     SET blocks_validated = blocks_validated + 1
                     WHERE address = ?""", (address,))
        self.conn.commit()

    def slash(self, address: str, reason: str):
        c = self.conn.cursor()
        c.execute("SELECT stake FROM validators WHERE address = ? AND is_slashed = 0",
                  (address,))
        row = c.fetchone()
        if not row:
            return
        penalty = row[0] * config.SLASHING_PENALTY_PERCENT // 100
        remaining = row[0] - penalty
        c.execute("""UPDATE validators
                     SET stake = ?, is_slashed = 1
                     WHERE address = ?""", (remaining, address))
        c.execute("""UPDATE stakes
                     SET withdrawn = 1
                     WHERE validator = ? AND withdrawn = 0""", (address,))
        c.execute("""INSERT INTO slashing_events
                     (validator, block_index, reason, penalty, occurred_at)
                     VALUES (?, ?, ?, ?, ?)""",
                  (address, 0, reason, penalty, int(time.time())))
        self.conn.commit()

    def can_withdraw(self, address: str) -> bool:
        now = int(time.time())
        c = self.conn.cursor()
        c.execute("""SELECT locked_until, is_slashed
                     FROM validators WHERE address = ?""", (address,))
        row = c.fetchone()
        if not row:
            return False
        return row[1] == 0 and now >= row[0]

    def withdraw_stake(self, address: str) -> Optional[int]:
        if not self.can_withdraw(address):
            return None
        c = self.conn.cursor()
        c.execute("SELECT stake FROM validators WHERE address = ?", (address,))
        row = c.fetchone()
        if not row:
            return None
        amount = row[0]
        c.execute("DELETE FROM validators WHERE address = ?", (address,))
        c.execute("UPDATE stakes SET withdrawn = 1 WHERE validator = ?", (address,))
        self.conn.commit()
        return amount

    def finalize_checkpoint(self, block_index: int, block_hash: str):
        if block_index % config.FINALITY_CHECKPOINT_INTERVAL != 0:
            return
        c = self.conn.cursor()
        c.execute("SELECT COUNT(*) FROM validators WHERE is_slashed = 0")
        validator_count = c.fetchone()[0]
        c.execute("""
            INSERT OR REPLACE INTO checkpoints
            (block_index, block_hash, finalized_at, validator_count)
            VALUES (?, ?, ?, ?)
        """, (block_index, block_hash, int(time.time()), validator_count))
        self.conn.commit()

    def is_finalized(self, block_index: int) -> bool:
        c = self.conn.cursor()
        c.execute("SELECT 1 FROM checkpoints WHERE block_index = ?", (block_index,))
        return c.fetchone() is not None

    def add_slashing_event(self, address: str, block_index: int, reason: str, penalty: int):
        c = self.conn.cursor()
        c.execute("""INSERT INTO slashing_events
                     (validator, block_index, reason, penalty, occurred_at)
                     VALUES (?, ?, ?, ?, ?)""",
                  (address, block_index, reason, penalty, int(time.time())))
        self.conn.commit()

    def get_slashing_events(self, limit: int = 50) -> list:
        c = self.conn.cursor()
        c.execute("""SELECT * FROM slashing_events
                     ORDER BY occurred_at DESC LIMIT ?""", (limit,))
        return [{
            "id": row["id"],
            "validator": row["validator"],
            "block_index": row["block_index"],
            "reason": row["reason"],
            "penalty": row["penalty"],
            "occurred_at": row["occurred_at"],
        } for row in c.fetchall()]

    def get_staking_dashboard(self, address: str) -> Optional[dict]:
        v = self.get_validator(address)
        if not v:
            return None
        now = int(time.time())
        lock_remaining = max(0, v["locked_until"] - now)
        total_stake = sum(
            s["stake"] for s in self.get_validators()
        ) or 1
        stake_share = v["stake"] / total_stake
        blocks_per_year = 365 * 24 * 3600 // config.TARGET_BLOCK_TIME
        annual_rewards = int(v["stake"] * config.STAKE_REWARD_RATE // 100)
        daily_reward = annual_rewards // 365
        return {
            "address": address,
            "stake": v["stake"],
            "stake_formatted": v["stake"] / config.GBX,
            "locked_until": v["locked_until"],
            "lock_remaining": lock_remaining,
            "lock_remaining_days": lock_remaining // 86400,
            "total_stake_pool": total_stake,
            "stake_share_pct": round(stake_share * 100, 2),
            "estimated_annual_rewards": annual_rewards,
            "estimated_annual_formatted": annual_rewards / config.GBX,
            "estimated_daily_rewards": daily_reward,
            "estimated_daily_formatted": daily_reward / config.GBX,
            "apy_pct": config.STAKE_REWARD_RATE,
        }

    def get_validator_stats(self, address: str) -> Optional[dict]:
        v = self.get_validator(address)
        if not v:
            return None
        now = int(time.time())
        registered_seconds = now - v.get("registered_at", now)
        expected_blocks = max(1, registered_seconds // config.TARGET_BLOCK_TIME)
        total_blocks = v["blocks_validated"] + v["missed_blocks"]
        uptime_pct = round(
            v["blocks_validated"] / max(1, total_blocks) * 100, 2
        ) if total_blocks > 0 else 0.0
        return {
            "address": address,
            "stake": v["stake"],
            "stake_formatted": v["stake"] / config.GBX,
            "blocks_validated": v["blocks_validated"],
            "missed_blocks": v["missed_blocks"],
            "total_blocks": total_blocks,
            "uptime_pct": uptime_pct,
            "is_slashed": v["is_slashed"],
            "registered_at": v.get("registered_at", 0),
            "locked_until": v["locked_until"],
        }

    def get_validator(self, address: str) -> Optional[dict]:
        c = self.conn.cursor()
        c.execute("SELECT * FROM validators WHERE address = ?", (address,))
        row = c.fetchone()
        if not row:
            return None
        return {
            "address": row["address"],
            "stake": row["stake"],
            "locked_until": row["locked_until"],
            "missed_blocks": row["missed_blocks"],
            "blocks_validated": row["blocks_validated"],
            "is_slashed": bool(row["is_slashed"]),
            "registered_at": row["registered_at"],
        }

    def get_validators(self) -> list:
        c = self.conn.cursor()
        c.execute("SELECT * FROM validators WHERE is_slashed = 0 ORDER BY stake DESC")
        return [{
            "address": row["address"],
            "stake": row["stake"],
            "locked_until": row["locked_until"],
            "missed_blocks": row["missed_blocks"],
            "blocks_validated": row["blocks_validated"],
        } for row in c.fetchall()]

    def get_checkpoints(self, limit: int = 10) -> list:
        c = self.conn.cursor()
        c.execute("""SELECT * FROM checkpoints
                     ORDER BY block_index DESC LIMIT ?""", (limit,))
        return [{
            "block_index": row["block_index"],
            "block_hash": row["block_hash"],
            "finalized_at": row["finalized_at"],
            "validator_count": row["validator_count"],
        } for row in c.fetchall()]

    def on_block_mined(self, address: str, height: int, block_hash: str):
        self._distribute_stake_reward(address, height)
        self.record_block_validated(address)
        self.finalize_checkpoint(height, block_hash)
