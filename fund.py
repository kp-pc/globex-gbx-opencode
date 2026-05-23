import time
import sqlite3
from typing import Optional

import config


SIGNERS = [
    "GDevFundSigner1",
    "GDevFundSigner2",
    "GDevFundSigner3",
]


class DevFund:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn
        self._init_tables()

    def _init_tables(self):
        c = self.conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS fund_transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                block_index INTEGER NOT NULL,
                amount INTEGER NOT NULL,
                source TEXT NOT NULL DEFAULT 'block_reward',
                timestamp INTEGER NOT NULL,
                description TEXT DEFAULT ''
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS fund_releases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                amount INTEGER NOT NULL,
                recipient TEXT NOT NULL,
                approvals INTEGER NOT NULL DEFAULT 0,
                required_approvals INTEGER NOT NULL DEFAULT 2,
                released INTEGER NOT NULL DEFAULT 0,
                created_at INTEGER NOT NULL,
                released_at INTEGER DEFAULT NULL
            )
        """)
        self.conn.commit()

    def contribute(self, block_index: int, amount: int, description: str = ""):
        c = self.conn.cursor()
        c.execute("""INSERT INTO fund_transactions
                     (block_index, amount, source, timestamp, description)
                     VALUES (?, ?, 'block_reward', ?, ?)""",
                  (block_index, amount, int(time.time()), description))
        self.conn.commit()

    def get_total_accumulated(self) -> int:
        c = self.conn.cursor()
        c.execute("SELECT COALESCE(SUM(amount), 0) FROM fund_transactions")
        return c.fetchone()[0]

    def get_vested_amount(self, current_block: int) -> int:
        total = self.get_total_accumulated()
        if current_block >= config.FUND_VESTING_BLOCKS:
            return total
        return total * current_block // config.FUND_VESTING_BLOCKS

    def get_locked_amount(self, current_block: int) -> int:
        return self.get_total_accumulated() - self.get_vested_amount(current_block)

    def get_released_amount(self) -> int:
        c = self.conn.cursor()
        c.execute("""SELECT COALESCE(SUM(amount), 0)
                     FROM fund_releases WHERE released = 1""")
        return c.fetchone()[0]

    def get_available_balance(self, current_block: int) -> int:
        return self.get_vested_amount(current_block) - self.get_released_amount()

    def propose_release(self, amount: int, recipient: str) -> int:
        c = self.conn.cursor()
        c.execute("""INSERT INTO fund_releases
                     (amount, recipient, approvals, required_approvals,
                      created_at, released)
                     VALUES (?, ?, 0, ?, ?, 0)""",
                  (amount, recipient, config.FUND_MULTISIG_REQUIRED, int(time.time())))
        self.conn.commit()
        return c.lastrowid

    def approve_release(self, release_id: int, signer: str) -> Optional[int]:
        if signer not in SIGNERS:
            return None
        c = self.conn.cursor()
        c.execute("""SELECT amount, approvals, required_approvals, released
                     FROM fund_releases WHERE id = ?""", (release_id,))
        row = c.fetchone()
        if not row or row["released"]:
            return None
        new_approvals = row["approvals"] + 1
        if new_approvals >= row["required_approvals"]:
            c.execute("""UPDATE fund_releases
                         SET approvals = ?, released = 1, released_at = ?
                         WHERE id = ?""",
                      (new_approvals, int(time.time()), release_id))
            self.conn.commit()
            return row["amount"]
        c.execute("UPDATE fund_releases SET approvals = ? WHERE id = ?",
                  (new_approvals, release_id))
        self.conn.commit()
        return None

    def get_report(self, current_block: int) -> dict:
        return {
            "address": config.FUND_ADDRESS,
            "total_accumulated": self.get_total_accumulated(),
            "vested": self.get_vested_amount(current_block),
            "locked": self.get_locked_amount(current_block),
            "released": self.get_released_amount(),
            "available": self.get_available_balance(current_block),
            "signers": SIGNERS,
            "required_signatures": config.FUND_MULTISIG_REQUIRED,
            "vesting_blocks": config.FUND_VESTING_BLOCKS,
            "current_block": current_block,
            "vesting_progress_pct": round(
                current_block / config.FUND_VESTING_BLOCKS * 100, 2
            ) if current_block <= config.FUND_VESTING_BLOCKS else 100,
            "pending_releases": self._get_pending_releases(),
        }

    def get_transactions(self, limit: int = 50) -> list:
        c = self.conn.cursor()
        c.execute("""SELECT * FROM fund_transactions
                     ORDER BY timestamp DESC LIMIT ?""", (limit,))
        return [{
            "id": row["id"],
            "block_index": row["block_index"],
            "amount": row["amount"],
            "source": row["source"],
            "timestamp": row["timestamp"],
            "description": row["description"],
        } for row in c.fetchall()]

    def _get_pending_releases(self) -> list:
        c = self.conn.cursor()
        c.execute("""SELECT * FROM fund_releases
                     WHERE released = 0 ORDER BY created_at DESC""")
        return [{
            "id": row["id"],
            "amount": row["amount"],
            "recipient": row["recipient"],
            "approvals": row["approvals"],
            "required_approvals": row["required_approvals"],
        } for row in c.fetchall()]
