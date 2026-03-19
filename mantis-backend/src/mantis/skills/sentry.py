"""
M.A.N.T.I.S. — Sentry Skill (Refactored)
Multi-source sentiment analysis using DataProvider patterns.

Sources:
  1. CryptoPanic  — news sentiment with signal classification (tier 1)
  2. CoinGecko    — Fear & Greed proxy via market data (tier 2)
  3. DeFi Llama   — TVL flows as sentiment proxy (tier 2)
  4. Twitter/X    — keyword sentiment (tier 2, requires API key)
  5. Polymarket   — prediction market sentiment via CLOB API (tier 3)

All sources fetch in parallel with independent timeout/fallback.
Inspired by worldmonitor's enrichment/signals.js pattern.
"""

from __future__ import annotations

import asyncio
import time
from datetime import datetime, timezone

from mantis.config import get_settings
from mantis.data.cache import CacheTier, get_cache
from mantis.data.providers import DataProvider, fetch_json
from mantis.data.signals import (
    Signal,
    SignalStrength,
    SignalType,
    classify_signal,
    compute_sentiment_from_signals,
    score_signal_strength,
)
from mantis.logging import get_agent_logger
from mantis.skills import Skill
from mantis.types import SentimentLabel, SentryData

logger = get_agent_logger()


# ── Helper: classify sentiment label ─────────────────────────────────────────

def _to_label(score: float) -> SentimentLabel:
    if score > 0.50:
        return SentimentLabel.VERY_BULLISH
    if score > 0.15:
        return SentimentLabel.BULLISH
    if score < -0.50:
        return SentimentLabel.VERY_BEARISH
    if score < -0.15:
        return SentimentLabel.BEARISH
    return SentimentLabel.NEUTRAL


# ── Data Providers ───────────────────────────────────────────────────────────

class CryptoPanicProvider(DataProvider):
    """
    CryptoPanic news API — real-time crypto news with community votes.
    Source tier: 1 (primary, purpose-built for crypto sentiment).
    """
    provider_name = "sentry:cryptopanic"
    cache_tier = CacheTier.HOT
    timeout_ms = 8_000

    async def _fetch(self) -> list[Signal] | None:
        settings = get_settings()
        if not settings.cryptopanic_api_key:
            return []

        keywords = settings.keyword_list
        filter_str = ",".join(kw.lower() for kw in keywords[:3])

        url = (
            f"https://cryptopanic.com/api/v1/posts/"
            f"?auth_token={settings.cryptopanic_api_key}"
            f"&currencies={filter_str}"
            f"&kind=news"
            f"&filter=hot"
        )

        data = await fetch_json(url, timeout_ms=self.timeout_ms)
        if not data or "results" not in data:
            return None

        signals: list[Signal] = []
        for item in data["results"][:20]:
            title = item.get("title", "")
            votes = item.get("votes", {})
            positive = votes.get("positive", 0)
            negative = votes.get("negative", 0)

            # Compute per-article sentiment from votes
            total_votes = positive + negative
            if total_votes > 0:
                sentiment = (positive - negative) / total_votes
            else:
                sentiment = 0.0

            published = item.get("published_at", "")
            recency_hours = 24.0
            if published:
                try:
                    pub_dt = datetime.fromisoformat(published.replace("Z", "+00:00"))
                    recency_hours = (datetime.now(timezone.utc) - pub_dt).total_seconds() / 3600
                except Exception:
                    pass

            signal_type = classify_signal(title)
            strength = score_signal_strength(
                engagement={"votes": total_votes},
                recency_hours=recency_hours,
                source_tier=1,
            )

            signals.append(Signal(
                type=signal_type,
                title=title,
                url=item.get("url", ""),
                source="CryptoPanic",
                source_tier=1,
                timestamp=published,
                strength=strength,
                sentiment_score=sentiment,
                engagement={"positive": positive, "negative": negative},
            ))

        return signals


class CoinGeckoSentimentProvider(DataProvider):
    """
    CoinGecko global market data as sentiment proxy.
    Uses market cap change and BTC dominance as indicators.
    Source tier: 2.
    """
    provider_name = "sentry:coingecko_sentiment"
    cache_tier = CacheTier.WARM
    timeout_ms = 8_000

    async def _fetch(self) -> list[Signal] | None:
        url = "https://api.coingecko.com/api/v3/global"
        data = await fetch_json(url, timeout_ms=self.timeout_ms)
        if not data or "data" not in data:
            return None

        global_data = data["data"]
        market_cap_change = global_data.get("market_cap_change_percentage_24h_usd", 0)

        # Derive sentiment from market cap change
        if market_cap_change > 5:
            sentiment = 0.7
        elif market_cap_change > 2:
            sentiment = 0.4
        elif market_cap_change > 0:
            sentiment = 0.15
        elif market_cap_change > -2:
            sentiment = -0.15
        elif market_cap_change > -5:
            sentiment = -0.4
        else:
            sentiment = -0.7

        signals = [Signal(
            type=SignalType.MARKET_MOVE,
            title=f"Global crypto market cap 24h change: {market_cap_change:+.2f}%",
            source="CoinGecko",
            source_tier=2,
            timestamp=datetime.now(timezone.utc).isoformat(),
            strength=score_signal_strength(recency_hours=0.5, source_tier=2),
            sentiment_score=sentiment,
            engagement={"market_cap_change_pct": round(market_cap_change, 2)},
            metadata={
                "btc_dominance": round(global_data.get("market_cap_percentage", {}).get("btc", 0), 2),
                "active_cryptos": global_data.get("active_cryptocurrencies", 0),
            },
        )]

        return signals


class DefiLlamaSentimentProvider(DataProvider):
    """
    DeFi Llama — TVL flows as a proxy for DeFi sentiment.
    Tracks TVL changes on Hedera to gauge ecosystem health.
    Source tier: 2.
    """
    provider_name = "sentry:defillama"
    cache_tier = CacheTier.WARM
    timeout_ms = 8_000

    async def _fetch(self) -> list[Signal] | None:
        # Fetch Hedera chain TVL
        url = "https://api.llama.fi/v2/historicalChainTvl/Hedera"
        data = await fetch_json(url, timeout_ms=self.timeout_ms)
        if not data or not isinstance(data, list) or len(data) < 2:
            return None

        # Latest vs 24h ago
        latest_tvl = data[-1].get("tvl", 0)
        day_ago_tvl = data[-2].get("tvl", 0) if len(data) >= 2 else latest_tvl

        tvl_change_pct = (
            ((latest_tvl - day_ago_tvl) / day_ago_tvl * 100)
            if day_ago_tvl > 0
            else 0
        )

        # TVL flowing in = bullish, flowing out = bearish
        if tvl_change_pct > 10:
            sentiment = 0.6
        elif tvl_change_pct > 3:
            sentiment = 0.3
        elif tvl_change_pct > 0:
            sentiment = 0.1
        elif tvl_change_pct > -3:
            sentiment = -0.1
        elif tvl_change_pct > -10:
            sentiment = -0.3
        else:
            sentiment = -0.6

        return [Signal(
            type=SignalType.LIQUIDITY_EVENT,
            title=f"Hedera DeFi TVL 24h change: {tvl_change_pct:+.2f}% (${latest_tvl / 1e6:.1f}M)",
            source="DeFi Llama",
            source_tier=2,
            timestamp=datetime.now(timezone.utc).isoformat(),
            strength=score_signal_strength(recency_hours=1, source_tier=2),
            sentiment_score=sentiment,
            engagement={"tvl_usd": round(latest_tvl, 2)},
            metadata={"tvl_change_pct": round(tvl_change_pct, 2)},
        )]


class TwitterSentimentProvider(DataProvider):
    """
    Twitter/X API v2 — keyword-based sentiment analysis.
    Source tier: 2 (requires API key).
    """
    provider_name = "sentry:twitter"
    cache_tier = CacheTier.HOT
    timeout_ms = 8_000

    async def _fetch(self) -> list[Signal] | None:
        settings = get_settings()
        if not settings.twitter_bearer_token:
            return []

        keywords = settings.keyword_list
        query = " OR ".join(keywords[:5])

        url = (
            f"https://api.twitter.com/2/tweets/search/recent"
            f"?query={query} lang:en -is:retweet"
            f"&max_results=20"
            f"&tweet.fields=created_at,public_metrics"
        )
        headers = {"Authorization": f"Bearer {settings.twitter_bearer_token}"}

        data = await fetch_json(url, timeout_ms=self.timeout_ms, headers=headers)
        if not data or "data" not in data:
            return None

        signals: list[Signal] = []
        for tweet in data["data"][:15]:
            text = tweet.get("text", "")
            metrics = tweet.get("public_metrics", {})

            signal_type = classify_signal(text)
            engagement = {
                "likes": metrics.get("like_count", 0),
                "retweets": metrics.get("retweet_count", 0),
                "replies": metrics.get("reply_count", 0),
            }

            created_at = tweet.get("created_at", "")
            recency_hours = 24.0
            if created_at:
                try:
                    dt = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                    recency_hours = (datetime.now(timezone.utc) - dt).total_seconds() / 3600
                except Exception:
                    pass

            signals.append(Signal(
                type=signal_type,
                title=text[:200],
                source="Twitter/X",
                source_tier=2,
                timestamp=created_at,
                strength=score_signal_strength(engagement=engagement, recency_hours=recency_hours, source_tier=2),
                engagement=engagement,
            ))

        return signals


class PolymarketSentimentProvider(DataProvider):
    """
    Polymarket CLOB API — prediction market sentiment.
    Fetches crypto-related markets near 50/50 as uncertainty signals.
    Source tier: 3.
    """
    provider_name = "sentry:polymarket"
    cache_tier = CacheTier.WARM
    timeout_ms = 8_000

    async def _fetch(self) -> list[Signal] | None:
        # Polymarket CLOB API — search for crypto markets
        url = "https://clob.polymarket.com/markets?limit=10&order=volume&ascending=false&tag=crypto"
        data = await fetch_json(url, timeout_ms=self.timeout_ms)
        if not data:
            return None

        # Handle both list and dict responses
        markets = data if isinstance(data, list) else data.get("data", [])
        if not markets:
            return []

        signals: list[Signal] = []
        for market in markets[:5]:
            question = market.get("question", "")
            tokens = market.get("tokens", [])
            volume = market.get("volume", "0")

            # Get the best price (probability) for the first outcome
            best_price = 0.5
            if tokens and isinstance(tokens, list):
                best_price = float(tokens[0].get("price", 0.5))

            # Markets near 50/50 = high uncertainty
            uncertainty = 1.0 - abs(best_price - 0.5) * 2

            signals.append(Signal(
                type=SignalType.SENTIMENT_SHIFT,
                title=f"[Polymarket] {question}",
                url=f"https://polymarket.com",
                source="Polymarket",
                source_tier=3,
                timestamp=datetime.now(timezone.utc).isoformat(),
                strength=score_signal_strength(
                    engagement={"volume": int(float(volume))},
                    recency_hours=1,
                    source_tier=3,
                ),
                sentiment_score=(best_price - 0.5) * 2,  # >0.5 = bullish outcome likely
                engagement={"volume": float(volume), "probability": best_price},
                metadata={"uncertainty": round(uncertainty, 3)},
            ))

        return signals


# ── Main Sentry Skill ────────────────────────────────────────────────────────

class SentrySkill(Skill):
    """
    Multi-source sentiment analysis using parallel data providers.
    Inspired by worldmonitor's Promise.all() signal aggregation pattern.
    """
    name = "sentry"
    version = "2.0.0"

    def __init__(self) -> None:
        cache = get_cache()
        self._providers = [
            CryptoPanicProvider(cache),
            CoinGeckoSentimentProvider(cache),
            DefiLlamaSentimentProvider(cache),
            TwitterSentimentProvider(cache),
            PolymarketSentimentProvider(cache),
        ]

    async def collect(self) -> SentryData:
        """Fetch signals from all providers in parallel, aggregate sentiment."""
        # Parallel fetch — each provider has its own timeout/fallback
        results = await asyncio.gather(
            *[self._safe_fetch(p) for p in self._providers],
            return_exceptions=False,
        )

        # Flatten all signals
        all_signals: list[Signal] = []
        source_count = 0
        for result in results:
            if result:
                all_signals.extend(result)
                source_count += 1

        # Sort by strength (critical first) then recency
        strength_order = {
            SignalStrength.CRITICAL: 0,
            SignalStrength.HIGH: 1,
            SignalStrength.MEDIUM: 2,
            SignalStrength.LOW: 3,
        }
        all_signals.sort(key=lambda s: strength_order.get(s.strength, 99))

        # Compute aggregate sentiment
        sentiment_score = compute_sentiment_from_signals(all_signals)
        label = _to_label(sentiment_score)

        # Top signals as strings for the LLM context
        top_signals = [
            f"[{s.source}:{s.strength.value}] {s.title[:120]}"
            for s in all_signals[:10]
        ]

        logger.info(
            f"Sentry: {len(all_signals)} signals from {source_count} sources — "
            f"sentiment={sentiment_score:.3f} ({label.value})"
        )

        return SentryData(
            score=round(sentiment_score, 4),
            label=label,
            top_signals=top_signals,
            source_count=source_count,
        )

    async def _safe_fetch(self, provider: DataProvider) -> list[Signal]:
        """Fetch from a provider with error isolation."""
        try:
            result = await provider.get()
            return result if result else []
        except Exception as exc:
            logger.warning(f"Sentry: {provider.provider_name} failed — {exc}")
            return []
