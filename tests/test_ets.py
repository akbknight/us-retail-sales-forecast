"""
Tests for ETS model and diagnostic metrics.
"""

import numpy as np
import pandas as pd
import pytest

from src.models.diagnostics import compute_mape, compute_mae, compute_rmse
from src.models.ets import run_forecast, fit_ets


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_synthetic_series(n: int = 60) -> pd.Series:
    """
    Generate a synthetic monthly series with trend and seasonality.
    Deterministic: trend + seasonal + small noise.
    """
    rng = np.random.default_rng(42)
    t = np.arange(n)
    trend = 300 + 2.0 * t
    seasonal = 20 * np.sin(2 * np.pi * t / 12)
    noise = rng.normal(0, 5, n)
    values = trend + seasonal + noise
    dates = pd.date_range(start="2000-01-01", periods=n, freq="MS")
    return pd.Series(values, index=dates)


# ---------------------------------------------------------------------------
# compute_rmse
# ---------------------------------------------------------------------------

class TestComputeRmse:
    def test_perfect_forecast(self):
        a = [10.0, 20.0, 30.0]
        assert compute_rmse(a, a) == pytest.approx(0.0)

    def test_known_value(self):
        # errors = [1, 2, 3] -> MSE = (1+4+9)/3 = 14/3 -> RMSE = sqrt(14/3)
        actuals = [10.0, 20.0, 30.0]
        preds = [11.0, 22.0, 33.0]
        expected = np.sqrt((1 + 4 + 9) / 3)
        assert compute_rmse(actuals, preds) == pytest.approx(expected, rel=1e-6)

    def test_single_element(self):
        assert compute_rmse([5.0], [3.0]) == pytest.approx(2.0)

    def test_length_mismatch_raises(self):
        with pytest.raises(ValueError, match="same length"):
            compute_rmse([1, 2, 3], [1, 2])

    def test_numpy_arrays(self):
        a = np.array([1.0, 2.0, 3.0])
        p = np.array([1.5, 2.5, 3.5])
        expected = np.sqrt(0.25)
        assert compute_rmse(a, p) == pytest.approx(expected, rel=1e-6)


# ---------------------------------------------------------------------------
# compute_mape
# ---------------------------------------------------------------------------

class TestComputeMape:
    def test_perfect_forecast(self):
        a = [100.0, 200.0, 300.0]
        assert compute_mape(a, a) == pytest.approx(0.0)

    def test_known_value(self):
        # 10% error on each observation -> MAPE = 10%
        actuals = [100.0, 200.0, 300.0]
        preds = [110.0, 220.0, 330.0]
        assert compute_mape(actuals, preds) == pytest.approx(10.0, rel=1e-6)

    def test_asymmetric_errors(self):
        # errors: 10/100=10%, 0/200=0%, 30/300=10% -> mean=6.67%
        actuals = [100.0, 200.0, 300.0]
        preds = [110.0, 200.0, 270.0]
        expected = (10 / 100 + 0 / 200 + 30 / 300) / 3 * 100
        assert compute_mape(actuals, preds) == pytest.approx(expected, rel=1e-6)

    def test_zero_actual_raises(self):
        with pytest.raises(ValueError, match="zeros"):
            compute_mape([0.0, 100.0], [1.0, 100.0])

    def test_length_mismatch_raises(self):
        with pytest.raises(ValueError, match="same length"):
            compute_mape([1, 2], [1])


# ---------------------------------------------------------------------------
# compute_mae
# ---------------------------------------------------------------------------

class TestComputeMae:
    def test_perfect_forecast(self):
        assert compute_mae([10, 20, 30], [10, 20, 30]) == pytest.approx(0.0)

    def test_known_value(self):
        # |errors| = [1, 2, 3] -> MAE = 2.0
        assert compute_mae([10, 20, 30], [11, 22, 33]) == pytest.approx(2.0)


# ---------------------------------------------------------------------------
# run_forecast
# ---------------------------------------------------------------------------

class TestRunForecast:
    @pytest.fixture(scope="class")
    def forecast_result(self):
        series = make_synthetic_series(n=60)
        return run_forecast(series, n=18, ci_levels=[0.80, 0.95])

    def test_returns_dict(self, forecast_result):
        assert isinstance(forecast_result, dict)

    def test_required_keys(self, forecast_result):
        required = ["fitted_model", "forecast", "forecast_index", "residual_std", "horizon_factors", "ci"]
        for key in required:
            assert key in forecast_result, f"Missing key: {key}"

    def test_forecast_length(self, forecast_result):
        assert len(forecast_result["forecast"]) == 18

    def test_forecast_index_length(self, forecast_result):
        assert len(forecast_result["forecast_index"]) == 18

    def test_forecast_dates_after_history(self, forecast_result):
        series = make_synthetic_series(n=60)
        first_forecast_date = forecast_result["forecast_index"][0]
        last_history_date = series.index[-1]
        assert first_forecast_date > last_history_date

    def test_residual_std_positive(self, forecast_result):
        assert forecast_result["residual_std"] > 0

    def test_ci_keys_present(self, forecast_result):
        ci = forecast_result["ci"]
        assert 0.80 in ci
        assert 0.95 in ci

    def test_ci_upper_above_lower(self, forecast_result):
        ci = forecast_result["ci"]
        for level in [0.80, 0.95]:
            upper = ci[level]["upper"]
            lower = ci[level]["lower"]
            assert all(u > l for u, l in zip(upper, lower)), \
                f"Upper CI not above lower at level {level}"

    def test_95ci_wider_than_80ci(self, forecast_result):
        ci = forecast_result["ci"]
        width_95 = [u - l for u, l in zip(ci[0.95]["upper"], ci[0.95]["lower"])]
        width_80 = [u - l for u, l in zip(ci[0.80]["upper"], ci[0.80]["lower"])]
        assert all(w95 > w80 for w95, w80 in zip(width_95, width_80))

    def test_forecast_values_positive(self, forecast_result):
        # Synthetic series is always positive; forecast should be too
        assert all(v > 0 for v in forecast_result["forecast"].values)


# ---------------------------------------------------------------------------
# fit_ets validation
# ---------------------------------------------------------------------------

class TestFitEts:
    def test_too_short_raises(self):
        short_series = pd.Series(
            [100.0] * 10,
            index=pd.date_range("2000-01-01", periods=10, freq="MS")
        )
        with pytest.raises(ValueError, match="too short"):
            fit_ets(short_series, seasonal_periods=12)

    def test_fitted_values_length(self):
        series = make_synthetic_series(60)
        fitted = fit_ets(series)
        assert len(fitted.fittedvalues) == len(series)

    def test_aic_is_finite(self):
        series = make_synthetic_series(60)
        fitted = fit_ets(series)
        assert np.isfinite(fitted.aic)

    def test_resid_mean_near_zero(self):
        series = make_synthetic_series(60)
        fitted = fit_ets(series)
        # Residual mean should be close to zero for unbiased model
        assert abs(np.mean(fitted.resid)) < 5.0  # in series units
