"""
M.A.N.T.I.S. — LLM Reasoning Engine
Sends structured context to an LLM and parses the ActionPlan response.

Supports: OpenAI (GPT-4o) and Anthropic (Claude) via their official SDKs.
"""

from __future__ import annotations

import json

from mantis.config import get_settings
from mantis.logging import get_agent_logger
from mantis.types import ActionPlan, AgentAction, AgentContext, Urgency

logger = get_agent_logger()


# ── System Prompt ────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are M.A.N.T.I.S. (Market Analysis & Network Tactical Integration System), an intelligent DeFi keeper agent managing a user's Bonzo Finance positions on the Hedera network. You manage both Bonzo Vault (CLMM) positions and Bonzo Lend (lending/borrowing) positions. Your job is to protect user capital and maximize risk-adjusted yield.

AVAILABLE ACTIONS — VAULT MANAGEMENT:
- NO_OP: Do nothing this tick.
- HARVEST: Trigger an early harvest of pending vault rewards.
- HARVEST_AND_SWAP: Harvest rewards and swap to USDC immediately.
- TIGHTEN_RANGE: Narrow the liquidity range (more fees, more IL risk).
- WIDEN_RANGE: Expand the liquidity range (less fees, less IL risk).
- WITHDRAW_ALL: Full emergency withdrawal to single-sided stablecoin.
- LOG_ONLY: No on-chain action, but record developing situation to the log.

AVAILABLE ACTIONS — LENDING (BONZO LEND):
- SUPPLY: Deposit idle assets into Bonzo Lend to earn supply APY.
- WITHDRAW_SUPPLY: Remove supplied collateral from Bonzo Lend.
- BORROW: Take a loan against supplied collateral. Requires parameters: asset, amount, rate_mode (1=stable, 2=variable).
- REPAY: Repay outstanding debt. Requires parameters: asset, amount, rate_mode.

RISK PROFILE CONSTRAINTS for '{risk_profile}':
{risk_constraints}

DECISION GUIDELINES — VAULTS:
- LOW volatility (<0.35) + rewards age >4h → HARVEST
- LOW volatility (<0.35) → consider TIGHTEN_RANGE
- MEDIUM volatility (0.35–0.60) + neutral sentiment + rewards >2h → HARVEST
- MEDIUM volatility + bearish sentiment + rewards >2h → HARVEST_AND_SWAP
- HIGH volatility (>0.60) → WIDEN_RANGE
- HIGH volatility + very bearish sentiment + rewards >2h → HARVEST_AND_SWAP + WIDEN_RANGE
- EXTREME volatility (>0.90) + bearish → WITHDRAW_ALL (moderate/conservative profiles)

DECISION GUIDELINES — LENDING:
- Health factor < 1.5 → REPAY to improve position safety
- Health factor < 1.2 → REPAY urgently (HIGH priority)
- Health factor < 1.05 → REPAY or WITHDRAW_SUPPLY (CRITICAL priority)
- Idle capital with low volatility → consider SUPPLY to earn yield
- Supply APY significantly > borrow APY → consider leveraged yield strategies (aggressive profile only)
- If lending position exists, always report health factor in the log_message

Always respond with ONLY a valid JSON object. No markdown, no explanation text.

Response format:
{{
  "action": "ACTION_NAME",
  "confidence": 0.0 to 1.0,
  "rationale": "Brief explanation of your reasoning",
  "urgency": "LOW" | "MEDIUM" | "HIGH" | "CRITICAL",
  "parameters": {{}},
  "log_message": "Human-readable log entry for the dashboard"
}}
"""

RISK_CONSTRAINTS = {
    "conservative": """- Max single-tx value: $5,000
- Min hours between harvests: 4
- Max volatility for tightening range: 0.25
- Require vol > 0.50 to widen range
- Require vol > 0.75 or sentiment < -0.60 to consider WITHDRAW_ALL
- Prefer NO_OP over aggressive actions""",
    "moderate": """- Max single-tx value: $10,000
- Min hours between harvests: 2
- Max volatility for tightening range: 0.35
- Require vol > 0.60 to widen range
- Require vol > 0.90 or sentiment < -0.80 to consider WITHDRAW_ALL""",
    "aggressive": """- Max single-tx value: $50,000
- Min hours between harvests: 1
- Max volatility for tightening range: 0.50
- Require vol > 0.75 to widen range
- Only consider WITHDRAW_ALL at vol > 1.20 or sentiment < -0.90
- Prefer active management to capture maximum fees""",
}


def _build_system_prompt(risk_profile: str) -> str:
    constraints = RISK_CONSTRAINTS.get(risk_profile, RISK_CONSTRAINTS["moderate"])
    return SYSTEM_PROMPT.format(risk_profile=risk_profile, risk_constraints=constraints)


def _build_user_message(context: AgentContext) -> str:
    return (
        "Current market context:\n"
        f"```json\n{context.model_dump_json(indent=2)}\n```\n\n"
        "Based on this context, what action should I take? "
        "Respond with ONLY a JSON object."
    )


# ── LLM Callers ──────────────────────────────────────────────────────────────

async def _call_openai(system: str, user_msg: str, model: str) -> str:
    from openai import AsyncOpenAI

    settings = get_settings()
    client = AsyncOpenAI(api_key=settings.openai_api_key)

    response = await client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user_msg},
        ],
        temperature=0.3,
        max_tokens=1024,
        response_format={"type": "json_object"},
    )
    return response.choices[0].message.content or "{}"


async def _call_anthropic(system: str, user_msg: str, model: str) -> str:
    from anthropic import AsyncAnthropic

    settings = get_settings()
    client = AsyncAnthropic(api_key=settings.anthropic_api_key)

    response = await client.messages.create(
        model=model,
        max_tokens=1024,
        system=system,
        messages=[{"role": "user", "content": user_msg}],
    )
    return response.content[0].text if response.content else "{}"


def _parse_action_plan(raw: str) -> ActionPlan:
    """Parse LLM JSON response into an ActionPlan, with fallback."""
    try:
        # Handle markdown code blocks
        cleaned = raw.strip()
        if cleaned.startswith("```"):
            lines = cleaned.split("\n")
            lines = [l for l in lines if not l.strip().startswith("```")]
            cleaned = "\n".join(lines)

        data = json.loads(cleaned)

        return ActionPlan(
            action=AgentAction(data.get("action", "NO_OP")),
            confidence=float(data.get("confidence", 0.5)),
            rationale=data.get("rationale", ""),
            urgency=Urgency(data.get("urgency", "LOW")),
            parameters=data.get("parameters", {}),
            log_message=data.get("log_message", ""),
        )
    except Exception as exc:
        logger.error(f"Reasoner: Failed to parse LLM response — {exc}\nRaw: {raw[:500]}")
        return ActionPlan(
            action=AgentAction.LOG_ONLY,
            rationale=f"LLM parse error: {exc}",
            log_message="⚠️ Reasoning engine returned unparseable output — defaulting to LOG_ONLY",
        )


# ── Public API ───────────────────────────────────────────────────────────────

async def think(context: AgentContext) -> ActionPlan:
    """
    Send context to the LLM and get back an ActionPlan.
    Falls back to a rule-based decision if LLM is unavailable.
    """
    settings = get_settings()
    model = settings.llm_model
    risk_profile = settings.risk_profile

    system = _build_system_prompt(risk_profile)
    user_msg = _build_user_message(context)

    logger.info(f"Reasoner: Requesting decision from {model}")

    try:
        if "claude" in model.lower() or "anthropic" in model.lower():
            if not settings.anthropic_api_key:
                logger.warning("Reasoner: Anthropic API key not set — using rule-based fallback")
                return _rule_based_fallback(context, settings)
            raw = await _call_anthropic(system, user_msg, model)
        else:
            if not settings.openai_api_key:
                logger.warning("Reasoner: OpenAI API key not set — using rule-based fallback")
                return _rule_based_fallback(context, settings)
            raw = await _call_openai(system, user_msg, model)

        plan = _parse_action_plan(raw)
        logger.info(
            f"Reasoner: Decision = {plan.action.value} "
            f"(confidence={plan.confidence}, urgency={plan.urgency.value})"
        )
        return plan

    except Exception as exc:
        logger.error(f"Reasoner: LLM call failed — {exc}")
        return _rule_based_fallback(context, settings)


# ── Rule-Based Fallback ─────────────────────────────────────────────────────

def _rule_based_fallback(context: AgentContext, settings) -> ActionPlan:
    """
    Deterministic fallback when the LLM is unavailable.
    Follows the decision matrix from DECISION_LOOP.md.
    """
    vol = context.market.realized_vol_24h
    sentiment = context.sentiment.score
    rewards_age = context.vault.last_harvest_hours_ago

    logger.info(
        f"Reasoner: Rule-based fallback — vol={vol}, sentiment={sentiment}, rewards_age={rewards_age}h"
    )

    # ── Lending health check (takes priority if position at risk) ────
    lending_plan = _lending_health_check(context, settings)
    if lending_plan:
        return lending_plan

    # EXTREME volatility + bearish → WITHDRAW_ALL
    if vol > settings.volatility_threshold_emergency and sentiment < settings.sentiment_threshold_swap:
        return ActionPlan(
            action=AgentAction.WITHDRAW_ALL,
            confidence=0.85,
            rationale=f"Emergency: vol={vol} > {settings.volatility_threshold_emergency}, sentiment={sentiment}",
            urgency=Urgency.CRITICAL,
            parameters={"vault_id": context.vault.vault_id},
            log_message=f"🚨 EMERGENCY WITHDRAWAL: Vol {vol:.0%} + Sentiment {sentiment:.2f}",
        )

    # HIGH volatility + very bearish → HARVEST_AND_SWAP + WIDEN
    if vol > settings.volatility_threshold_widen and sentiment < settings.sentiment_threshold_swap:
        if rewards_age >= settings.min_harvest_interval_hours:
            return ActionPlan(
                action=AgentAction.HARVEST_AND_SWAP,
                confidence=0.80,
                rationale=f"High vol ({vol}) + very bearish ({sentiment}). Harvest and protect.",
                urgency=Urgency.HIGH,
                parameters={"vault_id": context.vault.vault_id},
                log_message=f"⚠️ HARVEST+SWAP: Vol {vol:.0%} | Sentiment {sentiment:.2f}",
            )

    # HIGH volatility → WIDEN_RANGE
    if vol > settings.volatility_threshold_widen:
        return ActionPlan(
            action=AgentAction.WIDEN_RANGE,
            confidence=0.75,
            rationale=f"High volatility ({vol}) — widening range to reduce IL risk",
            urgency=Urgency.HIGH,
            parameters={
                "vault_id": context.vault.vault_id,
                "new_range_lower": round(context.vault.range_lower * 0.85, 4),
                "new_range_upper": round(context.vault.range_upper * 1.15, 4),
            },
            log_message=f"📊 WIDEN RANGE: Vol {vol:.0%} exceeds threshold",
        )

    # MEDIUM volatility + bearish + rewards ready → HARVEST_AND_SWAP
    if vol >= settings.volatility_threshold_tighten and sentiment < settings.sentiment_threshold_harvest:
        if rewards_age >= settings.min_harvest_interval_hours:
            return ActionPlan(
                action=AgentAction.HARVEST_AND_SWAP,
                confidence=0.70,
                rationale=f"Medium vol + bearish sentiment. Harvesting and swapping to protect.",
                urgency=Urgency.MEDIUM,
                parameters={"vault_id": context.vault.vault_id},
                log_message=f"🔄 HARVEST+SWAP: Sentiment {sentiment:.2f} | Rewards {rewards_age:.1f}h old",
            )

    # LOW volatility + old rewards → HARVEST
    if vol < settings.volatility_threshold_tighten and rewards_age > 4:
        return ActionPlan(
            action=AgentAction.HARVEST,
            confidence=0.65,
            rationale=f"Low volatility, rewards are {rewards_age:.1f}h old — harvesting",
            urgency=Urgency.LOW,
            parameters={"vault_id": context.vault.vault_id},
            log_message=f"🌾 HARVEST: Rewards {rewards_age:.1f}h old | Vol is low ({vol:.0%})",
        )

    # LOW volatility → TIGHTEN_RANGE
    if vol < settings.volatility_threshold_tighten:
        return ActionPlan(
            action=AgentAction.TIGHTEN_RANGE,
            confidence=0.55,
            rationale=f"Low volatility ({vol}) — tightening range for better fee capture",
            urgency=Urgency.LOW,
            parameters={
                "vault_id": context.vault.vault_id,
                "new_range_lower": round(context.vault.range_lower * 1.05, 4),
                "new_range_upper": round(context.vault.range_upper * 0.95, 4),
            },
            log_message=f"🎯 TIGHTEN RANGE: Vol low ({vol:.0%}) — concentrating liquidity",
        )

    # Default: NO_OP
    return ActionPlan(
        action=AgentAction.NO_OP,
        confidence=0.90,
        rationale="No actionable conditions detected",
        urgency=Urgency.LOW,
        log_message="✅ NO-OP: Market conditions within normal parameters",
    )


def _lending_health_check(context: AgentContext, settings) -> ActionPlan | None:
    """
    Check lending position health factor and return a protective action
    if needed. Returns None if lending position is healthy.
    """
    if not context.lending:
        return None

    hf = context.lending.health_factor
    debt = context.lending.total_debt_usd

    # No debt means no liquidation risk
    if debt <= 0:
        return None

    # CRITICAL: Health factor very close to liquidation
    if hf < 1.05:
        return ActionPlan(
            action=AgentAction.REPAY,
            confidence=0.95,
            rationale=f"CRITICAL: Health factor {hf:.2f} near liquidation. Immediate repay required.",
            urgency=Urgency.CRITICAL,
            parameters={"asset": "USDC", "amount": debt * 0.5},
            log_message=f"🚨 EMERGENCY REPAY: Health factor {hf:.2f} — liquidation imminent",
        )

    # HIGH: Health factor below danger threshold
    if hf < 1.2:
        return ActionPlan(
            action=AgentAction.REPAY,
            confidence=0.85,
            rationale=f"Health factor {hf:.2f} below 1.2. Repaying to improve safety margin.",
            urgency=Urgency.HIGH,
            parameters={"asset": "USDC", "amount": debt * 0.3},
            log_message=f"⚠️ REPAY: Health factor {hf:.2f} — reducing debt for safety",
        )

    # MEDIUM: Health factor below configured minimum
    min_hf = settings.bonzo_lending_health_factor_min
    if hf < min_hf:
        return ActionPlan(
            action=AgentAction.REPAY,
            confidence=0.70,
            rationale=f"Health factor {hf:.2f} below minimum threshold {min_hf}. Partial repay.",
            urgency=Urgency.MEDIUM,
            parameters={"asset": "USDC", "amount": debt * 0.15},
            log_message=f"🔄 REPAY: Health factor {hf:.2f} < {min_hf} threshold",
        )

    return None
