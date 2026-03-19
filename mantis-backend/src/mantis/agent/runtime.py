"""
M.A.N.T.I.S. — Core Agent Runtime
The main decision loop that runs continuously at SENTRY_INTERVAL_SECONDS.

Each tick:
  1. SENSE    → Collect data from all active Skills (context_builder)
  2. THINK    → LLM evaluates context against thresholds (reasoner)
  3. DECIDE   → Guard layer validates the action (guards)
  4. EXECUTE  → Hedera / BonzoLend Skill submits signed transaction (executor)
  5. LOG      → Action & metrics written to dashboard log
  6. REMEMBER → Memory Skill updates persistent state
"""

from __future__ import annotations

import asyncio
import time

from mantis.agent.context_builder import build_context
from mantis.agent.executor import run as execute_plan
from mantis.agent.guards import validate
from mantis.agent.reasoner import think
from mantis.config import get_settings
from mantis.logging import get_agent_logger, log_to_dashboard
from mantis.skills.bonzo_lend import BonzoLendSkill
from mantis.skills.hedera import HederaSkill
from mantis.skills.memory import MemorySkill
from mantis.skills.oracle import OracleSkill
from mantis.skills.sentry import SentrySkill
from mantis.types import AgentAction

logger = get_agent_logger()


class AgentRuntime:
    """
    Continuous agent loop.
    Instantiate once and call start() to begin the decision loop.
    """

    def __init__(self) -> None:
        self.settings = get_settings()

        # Skills
        self.sentry = SentrySkill()
        self.oracle = OracleSkill()
        self.hedera = HederaSkill()
        self.memory = MemorySkill()
        self.bonzo_lend = BonzoLendSkill()

        # Runtime state
        self._running = False
        self._task: asyncio.Task | None = None
        self._start_time = time.time()
        self._tick_count = 0

    # ── Lifecycle ────────────────────────────────────────────────────────

    def start(self) -> asyncio.Task:
        """Start the agent decision loop in the background."""
        if self._running:
            logger.warning("Runtime: Agent is already running")
            return self._task  # type: ignore

        self._running = True
        self._start_time = time.time()
        self._task = asyncio.create_task(self._loop())
        logger.info(
            f"Runtime: M.A.N.T.I.S. agent started — "
            f"interval={self.settings.sentry_interval_seconds}s, "
            f"risk_profile={self.settings.risk_profile}, "
            f"bonzo_lend={'enabled' if self.settings.bonzo_lending_enabled else 'disabled'}"
        )
        return self._task

    def stop(self) -> None:
        """Stop the agent decision loop."""
        self._running = False
        if self._task and not self._task.done():
            self._task.cancel()
        logger.info("Runtime: Agent stopped")

    @property
    def is_running(self) -> bool:
        return self._running

    @property
    def uptime(self) -> float:
        return time.time() - self._start_time

    # ── Main Loop ────────────────────────────────────────────────────────

    async def _loop(self) -> None:
        """The core repeating decision loop."""
        while self._running:
            try:
                await self._tick()
            except asyncio.CancelledError:
                logger.info("Runtime: Loop cancelled")
                break
            except Exception as exc:
                logger.error(f"Runtime: Tick failed — {exc}", exc_info=True)
                await log_to_dashboard(
                    action="ERROR",
                    message=f"Agent tick failed: {exc}",
                    urgency="HIGH",
                )

            # Sleep until next interval
            await asyncio.sleep(self.settings.sentry_interval_seconds)

    async def _tick(self) -> None:
        """Execute a single decision cycle."""
        self._tick_count += 1
        tick_start = time.time()

        logger.info(f"Runtime: ── TICK #{self._tick_count} START ──")

        # ── 1. SENSE ─────────────────────────────────────────────────
        logger.info("Runtime: [1/6] SENSE — collecting data from skills")
        context = await build_context(
            self.sentry, self.oracle, self.hedera, self.bonzo_lend
        )

        logger.info(
            f"Runtime: Context — price=${context.market.hbar_price_usd}, "
            f"vol={context.market.realized_vol_24h} ({context.market.vol_label.value}), "
            f"sentiment={context.sentiment.score} ({context.sentiment.label.value})"
        )
        if context.lending:
            logger.info(
                f"Runtime: Lending — "
                f"collateral=${context.lending.total_collateral_usd:.2f}, "
                f"debt=${context.lending.total_debt_usd:.2f}, "
                f"HF={context.lending.health_factor:.2f}"
            )

        # ── 2. THINK ─────────────────────────────────────────────────
        logger.info("Runtime: [2/6] THINK — reasoning about action")
        plan = await think(context)

        # ── 3. DECIDE (guards) ───────────────────────────────────────
        logger.info("Runtime: [3/6] DECIDE — validating against guards")
        meta = await self.memory.get_agent_meta()
        plan = validate(plan, meta)

        logger.info(
            f"Runtime: Decision = {plan.action.value} "
            f"(confidence={plan.confidence:.2f}, urgency={plan.urgency.value})"
        )

        # ── 4. EXECUTE ───────────────────────────────────────────────
        logger.info("Runtime: [4/6] EXECUTE — dispatching action")
        result = await execute_plan(
            plan, self.hedera, self.memory, self.bonzo_lend
        )

        # ── 5. LOG (handled by executor) ─────────────────────────────
        logger.info("Runtime: [5/6] LOG — done (handled in executor)")

        # ── 6. REMEMBER ──────────────────────────────────────────────
        logger.info("Runtime: [6/6] REMEMBER — updating persistent state")

        # Update agent meta
        is_same_action = plan.action == meta.last_action
        new_meta = meta.model_copy(
            update={
                "last_action": plan.action,
                "last_action_ts": time.time(),
                "last_harvest_ts": (
                    time.time()
                    if plan.action in (AgentAction.HARVEST, AgentAction.HARVEST_AND_SWAP)
                    else meta.last_harvest_ts
                ),
                "consecutive_no_ops": (
                    meta.consecutive_no_ops + 1
                    if plan.action == AgentAction.NO_OP
                    else 0
                ),
                "consecutive_same_action": (
                    meta.consecutive_same_action + 1
                    if is_same_action and plan.action not in (AgentAction.NO_OP, AgentAction.LOG_ONLY)
                    else (1 if plan.action not in (AgentAction.NO_OP, AgentAction.LOG_ONLY) else 0)
                ),
            }
        )
        await self.memory.update_agent_meta(new_meta)

        # Log APY snapshot
        if context.vault.current_apy > 0:
            await self.memory.log_apy(context.vault.vault_id, context.vault.current_apy)

        # Cache vault state
        await self.memory.cache_vault_state(
            context.vault.vault_id,
            context.vault.model_dump(),
        )

        # Cache lending position
        if context.lending:
            await self.memory.cache_vault_state(
                "bonzo_lend",
                context.lending.model_dump(),
            )

        elapsed = time.time() - tick_start
        logger.info(f"Runtime: ── TICK #{self._tick_count} END ({elapsed:.2f}s) ──")


# ── Module-level singleton ───────────────────────────────────────────────────
_runtime: AgentRuntime | None = None


def get_runtime() -> AgentRuntime:
    global _runtime
    if _runtime is None:
        _runtime = AgentRuntime()
    return _runtime
