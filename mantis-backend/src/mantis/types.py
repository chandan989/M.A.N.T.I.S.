"""
M.A.N.T.I.S. — Shared Types
All data models used across skills, agent runtime, and API.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


# ── Enums ────────────────────────────────────────────────────────────────────

class SentimentLabel(str, Enum):
    VERY_BEARISH = "VERY_BEARISH"
    BEARISH = "BEARISH"
    NEUTRAL = "NEUTRAL"
    BULLISH = "BULLISH"
    VERY_BULLISH = "VERY_BULLISH"


class VolatilityLabel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    EXTREME = "EXTREME"


class AgentAction(str, Enum):
    NO_OP = "NO_OP"
    HARVEST = "HARVEST"
    HARVEST_AND_SWAP = "HARVEST_AND_SWAP"
    TIGHTEN_RANGE = "TIGHTEN_RANGE"
    WIDEN_RANGE = "WIDEN_RANGE"
    WITHDRAW_ALL = "WITHDRAW_ALL"
    LOG_ONLY = "LOG_ONLY"
    # Bonzo Lend actions
    SUPPLY = "SUPPLY"
    WITHDRAW_SUPPLY = "WITHDRAW_SUPPLY"
    BORROW = "BORROW"
    REPAY = "REPAY"


class RiskProfile(str, Enum):
    CONSERVATIVE = "conservative"
    MODERATE = "moderate"
    AGGRESSIVE = "aggressive"


class Urgency(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


# ── Skill Data Models ────────────────────────────────────────────────────────

class SentryData(BaseModel):
    """Output from the Sentry Skill — sentiment analysis."""
    score: float = Field(ge=-1.0, le=1.0, description="Sentiment score: -1 (very bearish) to +1 (very bullish)")
    label: SentimentLabel
    top_signals: list[str] = Field(default_factory=list)
    source_count: int = 0
    trending_topics: list[str] = Field(default_factory=list)


class OracleData(BaseModel):
    """Output from the Oracle Skill — price & volatility."""
    hbar_price_usd: float
    change_1h_pct: float = 0.0
    change_24h_pct: float = 0.0
    realized_vol_24h: float = 0.0
    vol_label: VolatilityLabel = VolatilityLabel.LOW
    data_source: str = "unknown"
    fear_greed_index: Optional[int] = None
    fear_greed_label: Optional[str] = None
    hedera_top_pools: list[dict] = Field(default_factory=list)


class VaultState(BaseModel):
    """Current state of a Bonzo Vault position."""
    vault_id: str
    strategy: str = "HBAR/USDC"
    in_range: bool = True
    range_lower: float = 0.0
    range_upper: float = 0.0
    pending_rewards_usd: float = 0.0
    last_harvest_hours_ago: float = 0.0
    current_apy: float = 0.0


class UserProfile(BaseModel):
    """User configuration."""
    risk_profile: RiskProfile = RiskProfile.MODERATE
    wallets: list[str] = Field(default_factory=list)


# ── Bonzo Lend Models ────────────────────────────────────────────────────────

class LendingPosition(BaseModel):
    """User's lending account data from Bonzo Lend (Aave v2)."""
    total_collateral_usd: float = 0.0
    total_debt_usd: float = 0.0
    available_borrows_usd: float = 0.0
    liquidation_threshold: float = 0.0  # percentage (e.g. 80.0 = 80%)
    ltv: float = 0.0                     # loan-to-value percentage
    health_factor: float = Field(default=999.0, description="Position health: <1.0 = liquidatable")
    net_apy: float = 0.0                 # combined supply APY - borrow APY


class LendingReserve(BaseModel):
    """Info about a single lending market on Bonzo Lend."""
    asset: str = ""                       # e.g. "WHBAR", "USDC"
    asset_address: str = ""               # EVM address
    supply_apy: float = 0.0
    variable_borrow_apy: float = 0.0
    stable_borrow_apy: float = 0.0
    total_supplied_usd: float = 0.0
    total_borrowed_usd: float = 0.0


# ── Agent Context ────────────────────────────────────────────────────────────

class AgentContext(BaseModel):
    """Full context assembled for LLM reasoning each tick."""
    timestamp: float
    sentiment: SentryData
    market: OracleData
    vault: VaultState
    user: UserProfile
    lending: Optional[LendingPosition] = None


# ── Action Plan (LLM Output) ────────────────────────────────────────────────

class ActionPlan(BaseModel):
    """Structured output from the LLM reasoning engine."""
    action: AgentAction = AgentAction.NO_OP
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    rationale: str = ""
    urgency: Urgency = Urgency.LOW
    parameters: dict = Field(default_factory=dict)
    log_message: str = ""


# ── Execution Result ─────────────────────────────────────────────────────────

class ExecutionResult(BaseModel):
    """Result from an on-chain execution."""
    success: bool
    tx_id: Optional[str] = None
    message: str = ""
    error: Optional[str] = None


# ── Agent Meta (persisted) ───────────────────────────────────────────────────

class AgentMeta(BaseModel):
    """Persisted agent state metadata."""
    last_action: AgentAction = AgentAction.NO_OP
    last_action_ts: float = 0.0
    last_harvest_ts: float = 0.0
    consecutive_no_ops: int = 0
    consecutive_same_action: int = 0
    execution_paused: bool = False


# ── Log Entry ────────────────────────────────────────────────────────────────

class AgentLogEntry(BaseModel):
    """A single log entry for the dashboard."""
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    action: AgentAction
    message: str
    tx_id: Optional[str] = None
    confidence: float = 0.0
    urgency: Urgency = Urgency.LOW


# ── API Response Models ──────────────────────────────────────────────────────

class StatusResponse(BaseModel):
    """Agent status summary for the dashboard."""
    agent_running: bool = True
    execution_paused: bool = False
    last_action: AgentAction = AgentAction.NO_OP
    last_action_ts: float = 0.0
    risk_profile: RiskProfile = RiskProfile.MODERATE
    vault_summary: Optional[VaultState] = None
    lending_summary: Optional[LendingPosition] = None
    uptime_seconds: float = 0.0


class APYSnapshot(BaseModel):
    """A single APY data point."""
    timestamp: str
    apy: float
    vault_id: str
