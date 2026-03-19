"""
M.A.N.T.I.S. — Oracle Skill (Refactored)
Market data & price feeds using DataProvider chains.

Price Sources (priority order):
  1. SupraOracles  — on-chain oracle (tier 1)
  2. CoinGecko     — free REST API (tier 2)
  3. Binance       — public ticker (tier 2)

Supplementary Data:
  - DeFi Llama    — pool-level APY for vault monitoring
  - Fear & Greed  — alternative.me crypto sentiment index

All sources use the DataProvider pattern (timeout, cache, fallback).
Inspired by worldmonitor's market data pipeline.
"""

from __future__ import annotations

import asyncio
import math
import time
from datetime import datetime, timezone

from mantis.config import get_settings
from mantis.data.cache import CacheTier, get_cache
from mantis.data.providers import DataProvider, fetch_json, fetch_with_fallback
from mantis.logging import get_agent_logger
from mantis.skills import Skill
from mantis.types import OracleData, VolatilityLabel

logger = get_agent_logger()

# ── In-memory price history for volatility computation ───────────────────────
_price_history: list[float] = []
_MAX_HISTORY = 1440  # 24h of 1-minute candles


# ── Volatility Computation ───────────────────────────────────────────────────

def _compute_realized_vol(prices: list[float]) -> float:
    """Compute annualized realized volatility from price series."""
    if len(prices) < 2:
        return 0.0

    returns = []
    for i in range(1, len(prices)):
        if prices[i - 1] > 0:
            returns.append(math.log(prices[i] / prices[i - 1]))

    if not returns:
        return 0.0

    n = len(returns)
    mean = sum(returns) / n
    variance = sum((r - mean) ** 2 for r in returns) / n
    std_dev = math.sqrt(variance)
    # Annualize (assuming 1-minute samples → 525600 per year)
    return std_dev * math.sqrt(525600)


def _classify_vol(vol: float) -> VolatilityLabel:
    if vol >= 0.90:
        return VolatilityLabel.EXTREME
    if vol >= 0.60:
        return VolatilityLabel.HIGH
    if vol >= 0.35:
        return VolatilityLabel.MEDIUM
    return VolatilityLabel.LOW


# ── Price Providers ──────────────────────────────────────────────────────────

class SupraOraclesPriceProvider(DataProvider):
    """SupraOracles — on-chain price oracle (tier 1)."""
    provider_name = "oracle:supra"
    cache_tier = CacheTier.HOT
    timeout_ms = 5_000

    async def _fetch(self) -> dict | None:
        settings = get_settings()
        if not settings.supra_oracle_api_key:
            return None

        url = (
            f"{settings.supra_oracle_endpoint}"
            f"?pair={settings.oracles_hbar_pair}"
        )
        headers = {}
        if settings.supra_oracle_api_key:
            headers["x-api-key"] = settings.supra_oracle_api_key

        data = await fetch_json(url, timeout_ms=self.timeout_ms, headers=headers)
        if data and "price" in data:
            return {
                "price": float(data["price"]),
                "source": "SupraOracles",
                "timestamp": time.time(),
            }
        return None


class CoinGeckoPriceProvider(DataProvider):
    """CoinGecko — free REST API (tier 2). Primary fallback."""
    provider_name = "oracle:coingecko"
    cache_tier = CacheTier.HOT
    timeout_ms = 8_000

    async def _fetch(self) -> dict | None:
        url = (
            "https://api.coingecko.com/api/v3/simple/price"
            "?ids=hedera-hashgraph&vs_currencies=usd"
            "&include_24hr_change=true&include_market_cap=true"
        )
        data = await fetch_json(url, timeout_ms=self.timeout_ms)
        if data and "hedera-hashgraph" in data:
            hbar = data["hedera-hashgraph"]
            return {
                "price": float(hbar.get("usd", 0)),
                "change_24h_pct": float(hbar.get("usd_24h_change", 0)),
                "market_cap": float(hbar.get("usd_market_cap", 0)),
                "source": "CoinGecko",
                "timestamp": time.time(),
            }
        return None


class BinancePriceProvider(DataProvider):
    """Binance — public ticker API (tier 2). Secondary fallback."""
    provider_name = "oracle:binance"
    cache_tier = CacheTier.HOT
    timeout_ms = 5_000

    async def _fetch(self) -> dict | None:
        url = "https://api.binance.com/api/v3/ticker/24hr?symbol=HBARUSDT"
        data = await fetch_json(url, timeout_ms=self.timeout_ms)
        if data and "lastPrice" in data:
            return {
                "price": float(data["lastPrice"]),
                "change_24h_pct": float(data.get("priceChangePercent", 0)),
                "volume_24h": float(data.get("quoteVolume", 0)),
                "source": "Binance",
                "timestamp": time.time(),
            }
        return None


# ── Supplementary Data Providers ─────────────────────────────────────────────

class FearGreedProvider(DataProvider):
    """Alternative.me Fear & Greed Index — market sentiment indicator."""
    provider_name = "oracle:fear_greed"
    cache_tier = CacheTier.WARM
    timeout_ms = 8_000

    async def _fetch(self) -> dict | None:
        url = "https://api.alternative.me/fng/?limit=1"
        data = await fetch_json(url, timeout_ms=self.timeout_ms)
        if data and "data" in data and data["data"]:
            entry = data["data"][0]
            return {
                "value": int(entry.get("value", 50)),
                "label": entry.get("value_classification", "Neutral"),
                "timestamp": entry.get("timestamp", ""),
            }
        return None


class DefiLlamaPoolProvider(DataProvider):
    """DeFi Llama — Hedera pool APY data for vault benchmarking."""
    provider_name = "oracle:defillama_pools"
    cache_tier = CacheTier.WARM
    timeout_ms = 10_000

    async def _fetch(self) -> list[dict] | None:
        url = "https://yields.llama.fi/pools"
        data = await fetch_json(url, timeout_ms=self.timeout_ms)
        if not data or "data" not in data:
            return None

        # Filter for Hedera chain pools
        hedera_pools = [
            {
                "pool": p.get("pool", ""),
                "project": p.get("project", ""),
                "symbol": p.get("symbol", ""),
                "tvl_usd": p.get("tvlUsd", 0),
                "apy": p.get("apy", 0),
                "apy_base": p.get("apyBase", 0),
                "apy_reward": p.get("apyReward", 0),
            }
            for p in data["data"]
            if p.get("chain", "").lower() == "hedera" and p.get("tvlUsd", 0) > 10_000
        ]

        # Sort by TVL descending
        hedera_pools.sort(key=lambda p: p["tvl_usd"], reverse=True)
        return hedera_pools[:20]


# ── Main Oracle Skill ────────────────────────────────────────────────────────

class OracleSkill(Skill):
    """
    Multi-source market data with provider chain fallback.
    Inspired by worldmonitor's market data pipeline pattern.
    """
    name = "oracle"
    version = "2.0.0"

    def __init__(self) -> None:
        cache = get_cache()
        self._price_providers = [
            SupraOraclesPriceProvider(cache),
            CoinGeckoPriceProvider(cache),
            BinancePriceProvider(cache),
        ]
        self._fear_greed = FearGreedProvider(cache)
        self._pool_provider = DefiLlamaPoolProvider(cache)

    async def collect(self) -> OracleData:
        """Fetch price data from provider chain and compute market metrics."""
        global _price_history

        # ── Parallel fetches ─────────────────────────────────────────
        price_result, fear_greed, pools = await asyncio.gather(
            fetch_with_fallback(*self._price_providers),
            self._safe_fetch(self._fear_greed),
            self._safe_fetch(self._pool_provider),
        )

        # ── Price data ───────────────────────────────────────────────
        if price_result and isinstance(price_result, dict):
            price = price_result.get("price", 0.0)
            change_24h = price_result.get("change_24h_pct", 0.0)
            source = price_result.get("source", "unknown")
        else:
            price = 0.08
            change_24h = 0.0
            source = "fallback_default"

        # Update price history for volatility
        if price > 0:
            _price_history.append(price)
            if len(_price_history) > _MAX_HISTORY:
                _price_history = _price_history[-_MAX_HISTORY:]

        # ── Volatility ───────────────────────────────────────────────
        vol = _compute_realized_vol(_price_history)
        vol_label = _classify_vol(vol)

        # ── Price changes ────────────────────────────────────────────
        change_1h = 0.0
        if len(_price_history) >= 60:
            old = _price_history[-60]
            if old > 0:
                change_1h = ((price - old) / old) * 100

        # ── Fear & Greed enrichment ──────────────────────────────────
        fear_greed_value = None
        fear_greed_label = None
        if fear_greed and isinstance(fear_greed, dict):
            fear_greed_value = fear_greed.get("value")
            fear_greed_label = fear_greed.get("label")

        # ── Pool data enrichment ─────────────────────────────────────
        hedera_pools = pools if isinstance(pools, list) else []

        logger.info(
            f"Oracle: price=${price:.6f} ({source}) | "
            f"vol={vol:.4f} ({vol_label.value}) | "
            f"Δ1h={change_1h:+.2f}% Δ24h={change_24h:+.2f}% | "
            f"F&G={fear_greed_value or 'N/A'} | "
            f"pools={len(hedera_pools)}"
        )

        return OracleData(
            hbar_price_usd=round(price, 6),
            change_1h_pct=round(change_1h, 4),
            change_24h_pct=round(change_24h, 4),
            realized_vol_24h=round(vol, 4),
            vol_label=vol_label,
            data_source=source,
            fear_greed_index=fear_greed_value,
            fear_greed_label=fear_greed_label,
            hedera_top_pools=hedera_pools[:5] if hedera_pools else [],
        )

    async def _safe_fetch(self, provider: DataProvider):
        try:
            return await provider.get()
        except Exception as exc:
            logger.warning(f"Oracle: {provider.provider_name} failed — {exc}")
            return None
