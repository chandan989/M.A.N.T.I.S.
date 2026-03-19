"""
M.A.N.T.I.S. — Context Builder
Aggregates data from all active skills into a unified AgentContext.
"""

from __future__ import annotations

import asyncio
import time

from mantis.config import get_settings
from mantis.logging import get_agent_logger
from mantis.skills.bonzo_lend import BonzoLendSkill
from mantis.skills.hedera import HederaSkill
from mantis.skills.oracle import OracleSkill
from mantis.skills.sentry import SentrySkill
from mantis.types import (
    AgentContext,
    LendingPosition,
    OracleData,
    RiskProfile,
    SentimentLabel,
    SentryData,
    UserProfile,
    VaultState,
    VolatilityLabel,
)

logger = get_agent_logger()


async def build_context(
    sentry: SentrySkill,
    oracle: OracleSkill,
    hedera: HederaSkill,
    bonzo_lend: BonzoLendSkill | None = None,
) -> AgentContext:
    """
    Call collect() on all skills in parallel and assemble a unified context
    for the LLM reasoner.
    """
    settings = get_settings()

    # Build list of coroutines
    coros = [
        _safe_collect_sentry(sentry),
        _safe_collect_oracle(oracle),
        _safe_collect_hedera(hedera),
    ]
    if bonzo_lend and settings.bonzo_lending_enabled:
        coros.append(_safe_collect_bonzo_lend(bonzo_lend))

    # Parallel data collection
    results = await asyncio.gather(*coros, return_exceptions=False)

    sentry_data = results[0]
    oracle_data = results[1]
    vault_data = results[2]
    lending_data = results[3] if len(results) > 3 else None

    return AgentContext(
        timestamp=time.time(),
        sentiment=sentry_data,
        market=oracle_data,
        vault=vault_data,
        user=UserProfile(
            risk_profile=RiskProfile(settings.risk_profile),
            wallets=[settings.hedera_account_id] if settings.hedera_account_id else [],
        ),
        lending=lending_data,
    )


async def _safe_collect_sentry(skill: SentrySkill) -> SentryData:
    try:
        return await skill.collect()
    except Exception as exc:
        logger.error(f"Context: Sentry skill failed — {exc}")
        return SentryData(score=0.0, label=SentimentLabel.NEUTRAL)


async def _safe_collect_oracle(skill: OracleSkill) -> OracleData:
    try:
        return await skill.collect()
    except Exception as exc:
        logger.error(f"Context: Oracle skill failed — {exc}")
        return OracleData(hbar_price_usd=0.08, data_source="error_fallback")


async def _safe_collect_hedera(skill: HederaSkill) -> VaultState:
    try:
        return await skill.collect()
    except Exception as exc:
        logger.error(f"Context: Hedera skill failed — {exc}")
        return VaultState(vault_id="unknown")


async def _safe_collect_bonzo_lend(skill: BonzoLendSkill) -> LendingPosition:
    try:
        return await skill.collect()
    except Exception as exc:
        logger.error(f"Context: BonzoLend skill failed — {exc}")
        return LendingPosition()
