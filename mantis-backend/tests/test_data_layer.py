"""
Tests for the Data Infrastructure Layer — cache, providers, signals.
"""

import asyncio
import time

import pytest

from mantis.data.cache import CacheTier, DataCache
from mantis.data.signals import (
    Signal,
    SignalStrength,
    SignalType,
    classify_signal,
    compute_sentiment_from_signals,
    score_signal_strength,
)


# ── Cache Tests ──────────────────────────────────────────────────────────────

class TestDataCache:
    def setup_method(self):
        self.cache = DataCache()

    def test_set_and_get(self):
        self.cache.set("price:hbar", 0.095, CacheTier.HOT)
        assert self.cache.get("price:hbar") == 0.095

    def test_get_missing_key(self):
        assert self.cache.get("nonexistent") is None

    def test_ttl_expiration(self):
        """Manually expire a cache entry."""
        self.cache.set("test_key", "value", CacheTier.HOT)
        # Manually expire the entry
        entry = self.cache._store["test_key"]
        entry.expires_at = time.monotonic() - 1
        assert self.cache.get("test_key") is None

    def test_stale_while_revalidate(self):
        """Expired entries can still be read with allow_stale=True."""
        self.cache.set("test_key", "stale_value", CacheTier.HOT)
        entry = self.cache._store["test_key"]
        entry.expires_at = time.monotonic() - 1  # Expire it
        assert self.cache.get("test_key") is None  # Normal get returns None
        assert self.cache.get("test_key", allow_stale=True) == "stale_value"

    def test_negative_sentinel(self):
        """Negative cache prevents re-fetching failed sources."""
        self.cache.set_negative("bad_source", cooldown_seconds=60)
        assert self.cache.is_negatively_cached("bad_source") is True
        assert self.cache.get("bad_source") is None  # Never returns sentinel value

    def test_negative_sentinel_expires(self):
        self.cache.set_negative("bad_source", cooldown_seconds=1)
        # Manually expire
        entry = self.cache._store["bad_source"]
        entry.expires_at = time.monotonic() - 1
        assert self.cache.is_negatively_cached("bad_source") is False

    def test_batch_get_set(self):
        items = {"a": 1, "b": 2, "c": 3}
        self.cache.set_many(items, CacheTier.WARM)
        result = self.cache.get_many(["a", "b", "c", "d"])
        assert result == {"a": 1, "b": 2, "c": 3}

    def test_evict_expired(self):
        self.cache.set("keep", "value", CacheTier.WARM)
        self.cache.set("expire", "value", CacheTier.HOT)
        self.cache._store["expire"].expires_at = time.monotonic() - 1
        removed = self.cache.evict_expired()
        assert removed == 1
        assert self.cache.get("keep") == "value"
        assert self.cache.get("expire") is None

    def test_stats(self):
        self.cache.set("a", 1, CacheTier.HOT)
        self.cache.set("b", 2, CacheTier.WARM)
        self.cache.set_negative("c", cooldown_seconds=60)
        stats = self.cache.stats()
        assert stats["total_entries"] == 3
        assert stats["active_entries"] == 3
        assert stats["negative_entries"] == 1

    def test_delete(self):
        self.cache.set("key", "value", CacheTier.HOT)
        self.cache.delete("key")
        assert self.cache.get("key") is None

    def test_cache_tier_ttls(self):
        assert CacheTier.HOT.ttl == 60
        assert CacheTier.WARM.ttl == 300
        assert CacheTier.COLD.ttl == 3600


# ── Signal Classification Tests ──────────────────────────────────────────────

class TestSignalClassification:
    def test_classify_exploit(self):
        assert classify_signal("Major DeFi protocol drained of $50M") == SignalType.DEFI_EXPLOIT

    def test_classify_market_move(self):
        assert classify_signal("Bitcoin surges past $100K") == SignalType.MARKET_MOVE

    def test_classify_whale(self):
        assert classify_signal("Whale moves 500 million tokens") == SignalType.WHALE_ACTIVITY

    def test_classify_regulatory(self):
        assert classify_signal("SEC announces new crypto regulation") == SignalType.REGULATORY

    def test_classify_protocol(self):
        assert classify_signal("DEX launches V3 upgrade") == SignalType.PROTOCOL_UPDATE

    def test_classify_liquidity(self):
        assert classify_signal("Pool TVL increased significantly") == SignalType.LIQUIDITY_EVENT

    def test_classify_partnership(self):
        assert classify_signal("Major partnership between projects") == SignalType.PARTNERSHIP

    def test_classify_network(self):
        assert classify_signal("Hedera network update released") == SignalType.NETWORK_EVENT

    def test_classify_general(self):
        assert classify_signal("A dog played in the park") == SignalType.GENERAL


# ── Signal Scoring Tests ─────────────────────────────────────────────────────

class TestSignalScoring:
    def test_critical_signal(self):
        """High engagement + recent + tier 1 = critical."""
        strength = score_signal_strength(
            engagement={"votes": 500},
            recency_hours=0.5,
            source_tier=1,
        )
        assert strength == SignalStrength.CRITICAL

    def test_high_signal(self):
        strength = score_signal_strength(
            engagement={"likes": 30},
            recency_hours=3,
            source_tier=2,
        )
        assert strength == SignalStrength.HIGH

    def test_low_signal(self):
        """Old + low engagement + tertiary = low."""
        strength = score_signal_strength(
            engagement={"views": 2},
            recency_hours=48,
            source_tier=3,
        )
        assert strength == SignalStrength.LOW

    def test_no_engagement(self):
        strength = score_signal_strength(recency_hours=12, source_tier=2)
        assert strength in (SignalStrength.LOW, SignalStrength.MEDIUM)


# ── Sentiment Aggregation Tests ──────────────────────────────────────────────

class TestSentimentAggregation:
    def test_empty_signals(self):
        assert compute_sentiment_from_signals([]) == 0.0

    def test_bullish_signals(self):
        signals = [
            Signal(type=SignalType.PARTNERSHIP, sentiment_score=0.5, strength=SignalStrength.HIGH, source_tier=1),
            Signal(type=SignalType.PROTOCOL_UPDATE, sentiment_score=0.3, strength=SignalStrength.MEDIUM, source_tier=2),
        ]
        score = compute_sentiment_from_signals(signals)
        assert score > 0

    def test_bearish_signals(self):
        signals = [
            Signal(type=SignalType.DEFI_EXPLOIT, sentiment_score=-0.8, strength=SignalStrength.CRITICAL, source_tier=1),
        ]
        score = compute_sentiment_from_signals(signals)
        assert score < 0

    def test_mixed_signals(self):
        signals = [
            Signal(type=SignalType.PARTNERSHIP, sentiment_score=0.5, strength=SignalStrength.HIGH, source_tier=1),
            Signal(type=SignalType.DEFI_EXPLOIT, sentiment_score=-0.8, strength=SignalStrength.CRITICAL, source_tier=1),
        ]
        score = compute_sentiment_from_signals(signals)
        # Mixed — result depends on weighting
        assert -1.0 <= score <= 1.0

    def test_sentiment_bounds(self):
        """Sentiment should always be in [-1, 1]."""
        extreme_signals = [
            Signal(sentiment_score=1.0, strength=SignalStrength.CRITICAL, source_tier=1)
            for _ in range(10)
        ]
        score = compute_sentiment_from_signals(extreme_signals)
        assert -1.0 <= score <= 1.0
