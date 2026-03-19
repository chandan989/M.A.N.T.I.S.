"""
Tests for the Guard Layer.
"""

import time

import pytest

from mantis.agent.guards import validate
from mantis.types import ActionPlan, AgentAction, AgentMeta, Urgency


class TestGuards:
    """Guard layer validation tests."""

    def test_no_op_passes(self):
        plan = ActionPlan(action=AgentAction.NO_OP)
        meta = AgentMeta()
        result = validate(plan, meta)
        assert result.action == AgentAction.NO_OP

    def test_harvest_blocked_by_interval(self):
        """Harvest should be blocked if last harvest was too recent."""
        plan = ActionPlan(action=AgentAction.HARVEST, parameters={"vault_id": "0.0.123"})
        meta = AgentMeta(last_harvest_ts=time.time() - 1800)  # 30 min ago
        result = validate(plan, meta)
        assert result.action == AgentAction.NO_OP
        assert "Guard" in result.rationale or "cooldown" in result.rationale.lower()

    def test_harvest_allowed_after_interval(self):
        """Harvest should be allowed if enough time has passed."""
        plan = ActionPlan(action=AgentAction.HARVEST, parameters={"vault_id": "0.0.123"})
        meta = AgentMeta(last_harvest_ts=time.time() - 10800)  # 3 hours ago
        result = validate(plan, meta)
        assert result.action == AgentAction.HARVEST

    def test_cooldown_blocks_3rd_consecutive(self):
        """Same action 3 times in a row should be downgraded to LOG_ONLY."""
        plan = ActionPlan(action=AgentAction.WIDEN_RANGE, parameters={
            "vault_id": "0.0.123",
            "new_range_lower": 0.06,
            "new_range_upper": 0.12,
        })
        meta = AgentMeta(
            last_action=AgentAction.WIDEN_RANGE,
            consecutive_same_action=2,
        )
        result = validate(plan, meta)
        assert result.action == AgentAction.LOG_ONLY

    def test_sanity_check_invalid_range(self):
        """Range where lower >= upper should be rejected."""
        plan = ActionPlan(action=AgentAction.TIGHTEN_RANGE, parameters={
            "vault_id": "0.0.123",
            "new_range_lower": 0.12,
            "new_range_upper": 0.06,
        })
        meta = AgentMeta()
        result = validate(plan, meta)
        assert result.action == AgentAction.NO_OP

    def test_sanity_check_valid_range(self):
        """Valid range should pass."""
        plan = ActionPlan(action=AgentAction.TIGHTEN_RANGE, parameters={
            "vault_id": "0.0.123",
            "new_range_lower": 0.08,
            "new_range_upper": 0.10,
        })
        meta = AgentMeta()
        result = validate(plan, meta)
        assert result.action == AgentAction.TIGHTEN_RANGE

    def test_paused_execution_blocks_actions(self):
        """When paused, all actions except NO_OP/LOG_ONLY should be blocked."""
        plan = ActionPlan(action=AgentAction.HARVEST, parameters={"vault_id": "0.0.123"})
        meta = AgentMeta(execution_paused=True)
        result = validate(plan, meta)
        assert result.action == AgentAction.LOG_ONLY

    def test_withdraw_low_urgency_blocked(self):
        """WITHDRAW_ALL with LOW urgency should be suspicious."""
        plan = ActionPlan(
            action=AgentAction.WITHDRAW_ALL,
            urgency=Urgency.LOW,
            parameters={"vault_id": "0.0.123"},
        )
        meta = AgentMeta()
        result = validate(plan, meta)
        assert result.action == AgentAction.LOG_ONLY
