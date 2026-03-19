"""
Tests for the Oracle Skill volatility computation.
"""

from mantis.skills.oracle import _compute_realized_vol, _classify_vol
from mantis.types import VolatilityLabel


class TestVolatility:
    def test_classify_low(self):
        assert _classify_vol(0.10) == VolatilityLabel.LOW
        assert _classify_vol(0.34) == VolatilityLabel.LOW

    def test_classify_medium(self):
        assert _classify_vol(0.35) == VolatilityLabel.MEDIUM
        assert _classify_vol(0.59) == VolatilityLabel.MEDIUM

    def test_classify_high(self):
        assert _classify_vol(0.60) == VolatilityLabel.HIGH
        assert _classify_vol(0.89) == VolatilityLabel.HIGH

    def test_classify_extreme(self):
        assert _classify_vol(0.90) == VolatilityLabel.EXTREME
        assert _classify_vol(1.50) == VolatilityLabel.EXTREME

    def test_realized_vol_empty(self):
        assert _compute_realized_vol([]) == 0.0

    def test_realized_vol_single(self):
        assert _compute_realized_vol([100.0]) == 0.0

    def test_realized_vol_stable(self):
        """Constant prices should give zero volatility."""
        prices = [100.0] * 100
        vol = _compute_realized_vol(prices)
        assert vol == 0.0

    def test_realized_vol_some_movement(self):
        """Slightly varying prices should give low but non-zero vol."""
        prices = [100.0 + (i * 0.01) for i in range(100)]
        vol = _compute_realized_vol(prices)
        assert vol > 0
        assert vol < 1.0
