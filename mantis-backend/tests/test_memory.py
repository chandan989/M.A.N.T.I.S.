"""
Tests for the Memory Skill (SQLite persistence).
"""

import os
import tempfile
import uuid

import pytest

from mantis.skills.memory import MemorySkill
from mantis.types import AgentAction, AgentMeta


@pytest.fixture
def memory():
    """Return a fresh MemorySkill with a completely unique DB for each test."""
    unique_db = os.path.join(tempfile.mkdtemp(), f"test_{uuid.uuid4().hex[:8]}.db")
    os.environ["MEMORY_DB_PATH"] = unique_db
    skill = MemorySkill()
    skill._db_path = unique_db
    skill._initialized = False  # Force re-init of tables
    return skill


@pytest.mark.asyncio
async def test_agent_meta_roundtrip(memory: MemorySkill):
    """Store and retrieve agent meta."""
    meta = AgentMeta(
        last_action=AgentAction.HARVEST,
        last_action_ts=1000.0,
        last_harvest_ts=1000.0,
        consecutive_no_ops=0,
        consecutive_same_action=1,
    )
    await memory.update_agent_meta(meta)
    retrieved = await memory.get_agent_meta()

    assert retrieved.last_action == AgentAction.HARVEST
    assert retrieved.last_harvest_ts == 1000.0
    assert retrieved.consecutive_same_action == 1


@pytest.mark.asyncio
async def test_action_log(memory: MemorySkill):
    """Log actions and retrieve them."""
    await memory.log_action(
        action="HARVEST",
        message="Test harvest",
        tx_id="0.0.test@123",
        confidence=0.85,
        urgency="HIGH",
    )
    await memory.log_action(
        action="NO_OP",
        message="Nothing to do",
    )

    logs = await memory.get_recent_logs(limit=10)
    assert len(logs) == 2
    assert logs[0]["action"] == "NO_OP"  # Most recent first
    assert logs[1]["action"] == "HARVEST"
    assert logs[1]["tx_id"] == "0.0.test@123"


@pytest.mark.asyncio
async def test_apy_logging(memory: MemorySkill):
    """Log and retrieve APY snapshots."""
    await memory.log_apy("0.0.123", 14.2)
    await memory.log_apy("0.0.123", 15.1)
    await memory.log_apy("0.0.456", 8.5)

    history = await memory.get_apy_history("0.0.123", limit=10)
    assert len(history) == 2
    assert history[0].apy == 15.1  # Most recent first


@pytest.mark.asyncio
async def test_vault_state_cache(memory: MemorySkill):
    """Cache and retrieve vault state."""
    state = {"vault_id": "0.0.123", "strategy": "HBAR/USDC", "current_apy": 14.2}
    await memory.cache_vault_state("0.0.123", state)

    cached = await memory.get_cached_vault_state("0.0.123")
    assert cached is not None
    assert cached["vault_id"] == "0.0.123"
    assert cached["current_apy"] == 14.2

    # Non-existent vault
    missing = await memory.get_cached_vault_state("0.0.999")
    assert missing is None
