"""
M.A.N.T.I.S. — Configuration
Loads all environment variables with typed defaults and validation.
"""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings

# ── Load .env from project root ──────────────────────────────────────────────
_env_path = Path(__file__).resolve().parents[2] / ".env"
if not _env_path.exists():
    # Fallback: look at the monorepo root
    _env_path = Path(__file__).resolve().parents[3] / ".env"
load_dotenv(_env_path, override=False)


# ── Settings ─────────────────────────────────────────────────────────────────
class Settings(BaseSettings):
    """Typed environment configuration for M.A.N.T.I.S."""

    # ── Hedera Network ───────────────────────────────────────────────────
    hedera_account_id: str = Field(default="", description="Hedera operator account ID (e.g. 0.0.12345)")
    hedera_private_key: str = Field(default="", description="ECDSA hex private key (0x...) or DER-encoded ED25519")
    hedera_network: str = Field(default="testnet", description="testnet | mainnet")
    hedera_rpc_url: str = Field(default="", description="Override JSON-RPC relay URL (auto-set from network)")
    hedera_mirror_url: str = Field(default="", description="Override mirror node URL (auto-set from network)")

    # ── Bonzo Finance ────────────────────────────────────────────────────
    bonzo_vault_ids: str = Field(default="", description="Comma-separated Bonzo Vault contract IDs")

    # ── Bonzo Lend (Aave v2 fork) ────────────────────────────────────────
    bonzo_lending_pool_id: str = Field(default="", description="Bonzo LendingPool contract ID (Hedera)")
    bonzo_lending_enabled: bool = Field(default=True, description="Enable Bonzo Lend integration")
    bonzo_lending_health_factor_min: float = Field(default=1.5, description="Min health factor before protective action")
    bonzo_data_api_url: str = Field(default="https://data.bonzo.finance", description="Bonzo Data API base URL")

    # ── LLM Reasoning Engine ─────────────────────────────────────────────
    openai_api_key: str = Field(default="", description="OpenAI API key")
    anthropic_api_key: str = Field(default="", description="Anthropic API key")
    llm_model: str = Field(default="gpt-4o", description="gpt-4o | claude-3-5-sonnet | deepseek-chat")

    # ── Oracle Skill ─────────────────────────────────────────────────────
    supra_oracle_endpoint: str = Field(default="https://api.supraoracles.com/rpc/")
    supra_oracle_api_key: str = Field(default="")
    oracles_hbar_pair: str = Field(default="HBAR_USDC")

    # ── Sentry Skill ─────────────────────────────────────────────────────
    twitter_bearer_token: str = Field(default="")
    cryptopanic_api_key: str = Field(default="")
    sentry_keywords: str = Field(default="HBAR,Hedera,Bonzo,SaucerSwap")
    sentry_lookback_minutes: int = Field(default=30)

    # ── Comms ────────────────────────────────────────────────────────────
    comms_channel: str = Field(default="telegram")
    telegram_bot_token: str = Field(default="")
    telegram_chat_id: str = Field(default="")

    # ── Agent Behaviour ──────────────────────────────────────────────────
    risk_profile: str = Field(default="moderate", description="conservative | moderate | aggressive")
    volatility_threshold_widen: float = Field(default=0.60)
    volatility_threshold_tighten: float = Field(default=0.35)
    volatility_threshold_emergency: float = Field(default=0.90)
    sentiment_threshold_harvest: float = Field(default=-0.40)
    sentiment_threshold_swap: float = Field(default=-0.70)
    min_harvest_interval_hours: float = Field(default=2.0)
    sentry_interval_seconds: int = Field(default=60)

    # ── Memory / State ───────────────────────────────────────────────────
    memory_backend: str = Field(default="sqlite")
    memory_db_path: str = Field(default="./data/mantis.db")

    # ── Logging ──────────────────────────────────────────────────────────
    log_level: str = Field(default="info")
    log_dir: str = Field(default="./logs")

    # ── Server ───────────────────────────────────────────────────────────
    server_host: str = Field(default="0.0.0.0")
    server_port: int = Field(default=3001)
    cors_origins: str = Field(default="http://localhost:5173,http://localhost:3000")

    # ── Helpers ──────────────────────────────────────────────────────────
    @property
    def vault_id_list(self) -> list[str]:
        return [v.strip() for v in self.bonzo_vault_ids.split(",") if v.strip()]

    @property
    def keyword_list(self) -> list[str]:
        return [k.strip() for k in self.sentry_keywords.split(",") if k.strip()]

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def resolved_rpc_url(self) -> str:
        if self.hedera_rpc_url:
            return self.hedera_rpc_url
        return (
            "https://mainnet.hashio.io/api"
            if self.hedera_network == "mainnet"
            else "https://testnet.hashio.io/api"
        )

    @property
    def resolved_mirror_url(self) -> str:
        if self.hedera_mirror_url:
            return self.hedera_mirror_url
        return (
            "https://mainnet.mirrornode.hedera.com"
            if self.hedera_network == "mainnet"
            else "https://testnet.mirrornode.hedera.com"
        )

    model_config = {"env_prefix": "", "case_sensitive": False}


# ── Singleton ────────────────────────────────────────────────────────────────
_settings: Settings | None = None


def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
