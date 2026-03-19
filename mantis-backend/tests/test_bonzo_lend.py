"""
Tests for Bonzo Lend integration.
"""

import time

import pytest

from mantis.agent.guards import validate
from mantis.types import (
    ActionPlan,
    AgentAction,
    AgentMeta,
    LendingPosition,
    LendingReserve,
    Urgency,
)


class TestLendingTypes:
    """Test that new lending types work correctly."""

    def test_lending_position_defaults(self):
        pos = LendingPosition()
        assert pos.total_collateral_usd == 0.0
        assert pos.total_debt_usd == 0.0
        assert pos.health_factor == 999.0

    def test_lending_position_with_values(self):
        pos = LendingPosition(
            total_collateral_usd=1000.0,
            total_debt_usd=500.0,
            available_borrows_usd=250.0,
            liquidation_threshold=80.0,
            ltv=75.0,
            health_factor=1.6,
            net_apy=3.5,
        )
        assert pos.total_collateral_usd == 1000.0
        assert pos.health_factor == 1.6

    def test_lending_reserve(self):
        reserve = LendingReserve(
            asset="WHBAR",
            supply_apy=4.2,
            variable_borrow_apy=6.8,
            total_supplied_usd=5_000_000,
        )
        assert reserve.asset == "WHBAR"
        assert reserve.supply_apy == 4.2


class TestLendingActions:
    """Test that new agent actions exist."""

    def test_supply_action_exists(self):
        assert AgentAction.SUPPLY == "SUPPLY"

    def test_withdraw_supply_action_exists(self):
        assert AgentAction.WITHDRAW_SUPPLY == "WITHDRAW_SUPPLY"

    def test_borrow_action_exists(self):
        assert AgentAction.BORROW == "BORROW"

    def test_repay_action_exists(self):
        assert AgentAction.REPAY == "REPAY"


class TestLendingGuards:
    """Test lending-specific guard checks."""

    def test_borrow_blocked_when_no_capacity(self):
        """BORROW should be blocked if available_borrows_usd is 0."""
        plan = ActionPlan(
            action=AgentAction.BORROW,
            parameters={
                "asset": "USDC",
                "amount": 100,
                "available_borrows_usd": 0,
            },
        )
        meta = AgentMeta()
        result = validate(plan, meta)
        assert result.action == AgentAction.LOG_ONLY
        assert "borrowing capacity" in result.rationale.lower() or "Guard" in result.rationale

    def test_borrow_blocked_when_health_factor_low(self):
        """BORROW should be blocked if health factor is below minimum."""
        plan = ActionPlan(
            action=AgentAction.BORROW,
            parameters={
                "asset": "USDC",
                "amount": 100,
                "current_health_factor": 1.2,
            },
        )
        meta = AgentMeta()
        result = validate(plan, meta)
        assert result.action == AgentAction.LOG_ONLY
        assert "health factor" in result.rationale.lower() or "Guard" in result.rationale

    def test_borrow_allowed_when_healthy(self):
        """BORROW should be allowed when health factor is good."""
        plan = ActionPlan(
            action=AgentAction.BORROW,
            parameters={
                "asset": "USDC",
                "amount": 100,
                "current_health_factor": 5.0,
                "available_borrows_usd": 1000,
            },
        )
        meta = AgentMeta()
        result = validate(plan, meta)
        assert result.action == AgentAction.BORROW

    def test_supply_passes_guards(self):
        """SUPPLY should pass through guards like a normal action."""
        plan = ActionPlan(
            action=AgentAction.SUPPLY,
            parameters={"asset": "WHBAR", "amount": 100},
        )
        meta = AgentMeta()
        result = validate(plan, meta)
        assert result.action == AgentAction.SUPPLY

    def test_repay_passes_guards(self):
        """REPAY should pass through guards."""
        plan = ActionPlan(
            action=AgentAction.REPAY,
            parameters={"asset": "USDC", "amount": 50},
        )
        meta = AgentMeta()
        result = validate(plan, meta)
        assert result.action == AgentAction.REPAY

    def test_lending_action_paused_is_blocked(self):
        """Lending actions should be blocked when execution is paused."""
        plan = ActionPlan(
            action=AgentAction.SUPPLY,
            parameters={"asset": "WHBAR", "amount": 100},
        )
        meta = AgentMeta(execution_paused=True)
        result = validate(plan, meta)
        assert result.action == AgentAction.LOG_ONLY
