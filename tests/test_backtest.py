"""
Tests for walk-forward backtesting.
"""

import numpy as np
import pandas as pd
import pytest

from src.evaluation.backtest import run_backtest


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_synthetic_series(n: int = 84) -> pd.Series:
    """
    Generate a synthetic monthly series suitable for backtesting.
    n=84 gives 72 training + 12 holdout observations.
    """
    rng = np.random.default_rng(123)
    t = np.arange(n)
    values = 300 + 2.0 * t + 20 * np.sin(2 * np.pi * t / 12) + rng.normal(0, 5, n)
    dates = pd.date_range(start="2000-01-01", periods=n, freq="MS")
    return pd.Series(values, index=dates)


# ---------------------------------------------------------------------------
# Basic structure tests
# ---------------------------------------------------------------------------

class TestBacktestStructure:
    @pytest.fixture(scope="class")
    def backtest_result(self):
        series = make_synthetic_series(84)
        return run_backtest(series, holdout_months=12)

    def test_returns_dict(self, backtest_result):
        assert isinstance(backtest_result, dict)

    def test_top_level_keys(self, backtest_result):
        required = ["train_dates", "test_dates", "actuals", "predictions",
                    "ci95_upper", "ci95_lower", "residuals", "metrics"]
        for key in required:
            assert key in backtest_result, f"Missing key: {key}"

    def test_metrics_keys(self, backtest_result):
        m = backtest_result["metrics"]
        for key in ["mape", "mae", "rmse", "n_test"]:
            assert key in m, f"Missing metrics key: {key}"

    def test_mape_is_positive_float(self, backtest_result):
        mape = backtest_result["metrics"]["mape"]
        assert isinstance(mape, float)
        assert mape > 0.0

    def test_mae_is_positive_float(self, backtest_result):
        mae = backtest_result["metrics"]["mae"]
        assert isinstance(mae, float)
        assert mae > 0.0

    def test_rmse_is_positive_float(self, backtest_result):
        rmse = backtest_result["metrics"]["rmse"]
        assert isinstance(rmse, float)
        assert rmse > 0.0

    def test_rmse_ge_mae(self, backtest_result):
        """RMSE >= MAE always holds (RMSE penalizes large errors more)."""
        m = backtest_result["metrics"]
        assert m["rmse"] >= m["mae"]

    def test_n_test_correct(self, backtest_result):
        assert backtest_result["metrics"]["n_test"] == 12

    def test_test_dates_length(self, backtest_result):
        assert len(backtest_result["test_dates"]) == 12

    def test_actuals_length(self, backtest_result):
        assert len(backtest_result["actuals"]) == 12

    def test_predictions_length(self, backtest_result):
        assert len(backtest_result["predictions"]) == 12

    def test_ci95_upper_above_lower(self, backtest_result):
        upper = backtest_result["ci95_upper"]
        lower = backtest_result["ci95_lower"]
        assert all(u > l for u, l in zip(upper, lower))

    def test_residuals_are_actuals_minus_predictions(self, backtest_result):
        actuals = np.array(backtest_result["actuals"])
        preds = np.array(backtest_result["predictions"])
        residuals = np.array(backtest_result["residuals"])
        expected = actuals - preds
        np.testing.assert_allclose(residuals, expected, rtol=1e-4)

    def test_test_dates_after_train_dates(self, backtest_result):
        last_train = pd.to_datetime(backtest_result["train_dates"][-1])
        first_test = pd.to_datetime(backtest_result["test_dates"][0])
        assert first_test > last_train


# ---------------------------------------------------------------------------
# Accuracy on synthetic series
# ---------------------------------------------------------------------------

class TestBacktestAccuracy:
    def test_mape_reasonable_on_smooth_series(self):
        """On a low-noise synthetic series, MAPE should be < 5%."""
        rng = np.random.default_rng(7)
        n = 84
        t = np.arange(n)
        # Very smooth, low noise
        values = 1000 + 3.0 * t + 50 * np.sin(2 * np.pi * t / 12) + rng.normal(0, 2, n)
        dates = pd.date_range(start="2000-01-01", periods=n, freq="MS")
        series = pd.Series(values, index=dates)
        result = run_backtest(series, holdout_months=12)
        assert result["metrics"]["mape"] < 5.0, \
            f"Expected MAPE < 5% on smooth series, got {result['metrics']['mape']:.2f}%"


# ---------------------------------------------------------------------------
# Error handling
# ---------------------------------------------------------------------------

class TestBacktestErrors:
    def test_series_too_short_raises(self):
        # Need at least 2*12 + 1 + 12 = 37 observations
        short = pd.Series(
            [300.0 + i for i in range(30)],
            index=pd.date_range("2000-01-01", periods=30, freq="MS")
        )
        with pytest.raises(ValueError, match="too short"):
            run_backtest(short, holdout_months=12)

    def test_different_holdout_periods(self):
        """Verify backtest works with holdout_months=6."""
        series = make_synthetic_series(84)
        result = run_backtest(series, holdout_months=6)
        assert result["metrics"]["n_test"] == 6
        assert len(result["test_dates"]) == 6
        assert result["metrics"]["mape"] > 0
