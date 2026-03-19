"""
M.A.N.T.I.S. — Memory Skill
Persistent agent state using SQLite (via aiosqlite for async).

Tables:
  - agent_state: last action, timestamps, counters
  - vault_state: cached vault positions
  - apy_log:     APY snapshots over time
  - action_log:  full audit trail of agent actions
"""

from __future__ import annotations

import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import aiosqlite

from mantis.config import get_settings
from mantis.logging import get_agent_logger
from mantis.skills import Skill
from mantis.types import AgentAction, AgentMeta, APYSnapshot

logger = get_agent_logger()

# ── SQL Schema ───────────────────────────────────────────────────────────────
_SCHEMA = """
CREATE TABLE IF NOT EXISTS agent_state (
    key   TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS vault_state (
    vault_id   TEXT PRIMARY KEY,
    state_json TEXT NOT NULL,
    updated_at REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS apy_log (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    vault_id  TEXT NOT NULL,
    apy       REAL NOT NULL,
    timestamp TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS action_log (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    action     TEXT NOT NULL,
    message    TEXT NOT NULL,
    tx_id      TEXT,
    confidence REAL DEFAULT 0,
    urgency    TEXT DEFAULT 'LOW',
    timestamp  TEXT NOT NULL
);
"""


class MemorySkill(Skill):
    name = "memory"
    version = "1.0.0"

    def __init__(self) -> None:
        settings = get_settings()
        self._db_path = Path(settings.memory_db_path)
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialized = False

    async def _get_db(self) -> aiosqlite.Connection:
        db = await aiosqlite.connect(str(self._db_path))
        if not self._initialized:
            await db.executescript(_SCHEMA)
            await db.commit()
            self._initialized = True
        return db

    # ── Skill interface ──────────────────────────────────────────────────

    async def collect(self) -> AgentMeta:
        """Return current agent metadata from persistent storage."""
        return await self.get_agent_meta()

    # ── Agent Meta ───────────────────────────────────────────────────────

    async def get_agent_meta(self) -> AgentMeta:
        db = await self._get_db()
        try:
            cursor = await db.execute(
                "SELECT value FROM agent_state WHERE key = 'meta'"
            )
            row = await cursor.fetchone()
            if row:
                return AgentMeta.model_validate_json(row[0])
            return AgentMeta()
        finally:
            await db.close()

    async def update_agent_meta(self, meta: AgentMeta) -> None:
        db = await self._get_db()
        try:
            await db.execute(
                "INSERT OR REPLACE INTO agent_state (key, value) VALUES ('meta', ?)",
                (meta.model_dump_json(),),
            )
            await db.commit()
        finally:
            await db.close()

    # ── Action Logging ───────────────────────────────────────────────────

    async def log_action(
        self,
        action: str,
        message: str,
        tx_id: str | None = None,
        confidence: float = 0.0,
        urgency: str = "LOW",
    ) -> None:
        db = await self._get_db()
        try:
            await db.execute(
                """INSERT INTO action_log (action, message, tx_id, confidence, urgency, timestamp)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (
                    action,
                    message,
                    tx_id,
                    confidence,
                    urgency,
                    datetime.now(timezone.utc).isoformat(),
                ),
            )
            await db.commit()
        finally:
            await db.close()

    async def get_recent_logs(self, limit: int = 50) -> list[dict]:
        db = await self._get_db()
        try:
            cursor = await db.execute(
                "SELECT action, message, tx_id, confidence, urgency, timestamp "
                "FROM action_log ORDER BY id DESC LIMIT ?",
                (limit,),
            )
            rows = await cursor.fetchall()
            return [
                {
                    "action": r[0],
                    "message": r[1],
                    "tx_id": r[2],
                    "confidence": r[3],
                    "urgency": r[4],
                    "timestamp": r[5],
                }
                for r in rows
            ]
        finally:
            await db.close()

    # ── APY Logging ──────────────────────────────────────────────────────

    async def log_apy(self, vault_id: str, apy: float) -> None:
        db = await self._get_db()
        try:
            await db.execute(
                "INSERT INTO apy_log (vault_id, apy, timestamp) VALUES (?, ?, ?)",
                (vault_id, apy, datetime.now(timezone.utc).isoformat()),
            )
            await db.commit()
        finally:
            await db.close()

    async def get_apy_history(self, vault_id: str, limit: int = 100) -> list[APYSnapshot]:
        db = await self._get_db()
        try:
            cursor = await db.execute(
                "SELECT vault_id, apy, timestamp FROM apy_log "
                "WHERE vault_id = ? ORDER BY id DESC LIMIT ?",
                (vault_id, limit),
            )
            rows = await cursor.fetchall()
            return [
                APYSnapshot(vault_id=r[0], apy=r[1], timestamp=r[2])
                for r in rows
            ]
        finally:
            await db.close()

    # ── Vault State Cache ────────────────────────────────────────────────

    async def cache_vault_state(self, vault_id: str, state: dict) -> None:
        db = await self._get_db()
        try:
            await db.execute(
                "INSERT OR REPLACE INTO vault_state (vault_id, state_json, updated_at) "
                "VALUES (?, ?, ?)",
                (vault_id, json.dumps(state), time.time()),
            )
            await db.commit()
        finally:
            await db.close()

    async def get_cached_vault_state(self, vault_id: str) -> dict | None:
        db = await self._get_db()
        try:
            cursor = await db.execute(
                "SELECT state_json FROM vault_state WHERE vault_id = ?",
                (vault_id,),
            )
            row = await cursor.fetchone()
            return json.loads(row[0]) if row else None
        finally:
            await db.close()
