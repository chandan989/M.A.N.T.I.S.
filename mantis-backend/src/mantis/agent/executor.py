"""
M.A.N.T.I.S. — Executor
Dispatches approved ActionPlans to the appropriate Skill for on-chain execution.
Supports both Bonzo Vault (Hedera Skill) and Bonzo Lend actions.
"""

from __future__ import annotations

from mantis.logging import get_agent_logger, log_to_dashboard
from mantis.skills.bonzo_lend import BonzoLendSkill
from mantis.skills.hedera import HederaSkill
from mantis.skills.memory import MemorySkill
from mantis.types import ActionPlan, AgentAction, ExecutionResult

logger = get_agent_logger()

# Actions routed to BonzoLendSkill instead of HederaSkill
_LENDING_ACTIONS = {
    AgentAction.SUPPLY,
    AgentAction.WITHDRAW_SUPPLY,
    AgentAction.BORROW,
    AgentAction.REPAY,
}


async def run(
    plan: ActionPlan,
    hedera: HederaSkill,
    memory: MemorySkill,
    bonzo_lend: BonzoLendSkill | None = None,
) -> ExecutionResult | None:
    """
    Execute the approved action plan.
    - NO_OP and LOG_ONLY skip on-chain execution.
    - Lending actions (SUPPLY, WITHDRAW_SUPPLY, BORROW, REPAY) go to BonzoLendSkill.
    - All other actions are forwarded to the Hedera Skill.
    - Results are logged to dashboard and persisted in memory.
    """
    action = plan.action

    # ── LOG_ONLY / NO_OP ─────────────────────────────────────────────────
    if action in (AgentAction.NO_OP, AgentAction.LOG_ONLY):
        message = plan.log_message or f"{action.value}: {plan.rationale}"
        logger.info(f"Executor: {action.value} — {message}")

        await log_to_dashboard(
            action=action.value,
            message=message,
            confidence=plan.confidence,
            urgency=plan.urgency.value,
        )
        await memory.log_action(
            action=action.value,
            message=message,
            confidence=plan.confidence,
            urgency=plan.urgency.value,
        )
        return None

    # ── Lending action → BonzoLendSkill ──────────────────────────────────
    if action in _LENDING_ACTIONS:
        if not bonzo_lend:
            logger.error(f"Executor: Lending action {action.value} but BonzoLendSkill not available")
            result = ExecutionResult(
                success=False,
                error="BonzoLendSkill not configured",
            )
        else:
            logger.info(f"Executor: Dispatching {action.value} to BonzoLend Skill")
            params = {"action": action.value, **plan.parameters}
            result = await bonzo_lend.execute(params)
    else:
        # ── Vault action → HederaSkill ───────────────────────────────────
        logger.info(f"Executor: Dispatching {action.value} to Hedera Skill")
        params = {"action": action.value, **plan.parameters}
        result = await hedera.execute(params)

    # Log result
    log_msg = plan.log_message or f"{action.value}: {result.message}"
    if result.success:
        logger.info(f"Executor: {action.value} succeeded — tx:{result.tx_id}")
    else:
        logger.error(f"Executor: {action.value} failed — {result.error}")
        log_msg = f"❌ {action.value} FAILED: {result.error}"

    await log_to_dashboard(
        action=action.value,
        message=log_msg,
        tx_id=result.tx_id,
        confidence=plan.confidence,
        urgency=plan.urgency.value,
    )
    await memory.log_action(
        action=action.value,
        message=log_msg,
        tx_id=result.tx_id,
        confidence=plan.confidence,
        urgency=plan.urgency.value,
    )

    return result
