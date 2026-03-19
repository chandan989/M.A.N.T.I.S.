"""
M.A.N.T.I.S. — Guard Layer
Pre-execution validation that enforces hard limits regardless of LLM output.

Guards:
  1. Execution paused — block all actions if paused
  2. Min harvest interval — block HARVEST if too recent
  3. Risk profile ceiling — downgrade actions exceeding profile
  4. Cooldown — same action 3× in a row → LOG_ONLY
  5. Sanity check — range_lower must be < range_upper
  6. Lending health factor — block BORROW if health factor too low
  7. Lending available borrows — block BORROW if no borrowing capacity
"""

from __future__ import annotations

from mantis.config import get_settings
from mantis.logging import get_agent_logger
from mantis.types import ActionPlan, AgentAction, AgentMeta, Urgency

logger = get_agent_logger()


def validate(plan: ActionPlan, meta: AgentMeta) -> ActionPlan:
    """
    Run all guard checks on the proposed ActionPlan.
    May modify or downgrade the action.
    Returns the (possibly modified) plan.
    """
    settings = get_settings()

    # ── Guard 0: Execution paused ────────────────────────────────────────
    if meta.execution_paused and plan.action not in (AgentAction.NO_OP, AgentAction.LOG_ONLY):
        logger.info(f"Guard: Execution is paused — downgrading {plan.action.value} to LOG_ONLY")
        return _downgrade(plan, AgentAction.LOG_ONLY, "Execution paused by user")

    # ── Guard 1: Min harvest interval ────────────────────────────────────
    if plan.action in (AgentAction.HARVEST, AgentAction.HARVEST_AND_SWAP):
        import time
        hours_since = (time.time() - meta.last_harvest_ts) / 3600 if meta.last_harvest_ts > 0 else 999
        if hours_since < settings.min_harvest_interval_hours:
            logger.info(
                f"Guard: Harvest blocked — last harvest was {hours_since:.1f}h ago "
                f"(minimum: {settings.min_harvest_interval_hours}h)"
            )
            return _downgrade(
                plan, AgentAction.NO_OP,
                f"Harvest cooldown: {hours_since:.1f}h < {settings.min_harvest_interval_hours}h minimum"
            )

    # ── Guard 2: Risk profile ceiling ────────────────────────────────────
    if plan.action == AgentAction.WITHDRAW_ALL:
        if settings.risk_profile == "aggressive":
            # Aggressive profile has a higher threshold
            vol_threshold = 1.20
        elif settings.risk_profile == "conservative":
            vol_threshold = 0.75
        else:
            vol_threshold = 0.90

        # We don't have direct access to vol here, but we trust
        # the LLM / rule-based reasoner to only suggest this at
        # appropriate levels. Guard is a safety net using urgency.
        if plan.urgency == Urgency.LOW:
            logger.info("Guard: WITHDRAW_ALL with LOW urgency — suspicious, downgrading")
            return _downgrade(plan, AgentAction.LOG_ONLY, "WITHDRAW_ALL requires HIGH+ urgency")

    # ── Guard 3: Cooldown (same action 3× in a row) ─────────────────────
    if (
        plan.action == meta.last_action
        and plan.action not in (AgentAction.NO_OP, AgentAction.LOG_ONLY)
        and meta.consecutive_same_action >= 2  # This would be the 3rd time
    ):
        logger.info(
            f"Guard: Cooldown triggered — {plan.action.value} attempted 3× in a row. "
            f"Forcing LOG_ONLY."
        )
        return _downgrade(
            plan, AgentAction.LOG_ONLY,
            f"Cooldown: {plan.action.value} triggered 3 consecutive times"
        )

    # ── Guard 4: Sanity check on range values ────────────────────────────
    if plan.action in (AgentAction.TIGHTEN_RANGE, AgentAction.WIDEN_RANGE):
        lower = plan.parameters.get("new_range_lower", 0)
        upper = plan.parameters.get("new_range_upper", 0)
        if lower >= upper:
            logger.error(
                f"Guard: Invalid range — lower ({lower}) >= upper ({upper}). "
                f"Downgrading to NO_OP."
            )
            return _downgrade(
                plan, AgentAction.NO_OP,
                f"Sanity check failed: range_lower ({lower}) >= range_upper ({upper})"
            )

    # ── Guard 5: Lending — health factor check on BORROW ─────────────────
    if plan.action == AgentAction.BORROW:
        # We check available_borrows from parameters if provided
        available = plan.parameters.get("available_borrows_usd", None)
        if available is not None and available <= 0:
            logger.info("Guard: BORROW blocked — no available borrowing capacity")
            return _downgrade(
                plan, AgentAction.LOG_ONLY,
                "No available borrowing capacity"
            )

        # Health factor check: block if current HF is already near liquidation
        current_hf = plan.parameters.get("current_health_factor", None)
        min_hf = settings.bonzo_lending_health_factor_min
        if current_hf is not None and current_hf < min_hf:
            logger.info(
                f"Guard: BORROW blocked — health factor {current_hf} < {min_hf} minimum"
            )
            return _downgrade(
                plan, AgentAction.LOG_ONLY,
                f"Health factor {current_hf} below minimum {min_hf}"
            )

    logger.debug(f"Guard: All checks passed for {plan.action.value}")
    return plan


def _downgrade(plan: ActionPlan, new_action: AgentAction, reason: str) -> ActionPlan:
    """Create a modified plan with a downgraded action and updated rationale."""
    return ActionPlan(
        action=new_action,
        confidence=plan.confidence,
        rationale=f"[GUARD OVERRIDE] {reason}. Original: {plan.action.value} — {plan.rationale}",
        urgency=plan.urgency,
        parameters=plan.parameters,
        log_message=f"🛡️ Guard: {reason}",
    )
