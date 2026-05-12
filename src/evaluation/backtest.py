"""
Walk-Forward Backtesting
========================
Evaluates Holt-Winters ETS forecast accuracy using a walk-forward (rolling
origin) backtest design. The last N months of the series are held out as a
test set; the model is fit on the training portion and evaluated against actuals.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from src.models.ets import fit_ets
from src.models.diagnostics import compute_mape, compute_mae, compute_rmse


def run_backtest(
    series: pd.Series,
    holdout_months: int = 12,
    seasonal_periods: int = 12,
) -> dict:
    """
    Walk-forward backtest: hold out last N months, fit on remainder, evaluate.

    This simulates the real forecasting scenario — the model is trained only
    on data that would have been available at forecast time, then its
    predictions are compared to the subsequently observed actuals.

    Parameters
    ----------
    series : pd.Series
        Full monthly time series with DatetimeIndex. Values in millions of USD.
    holdout_months : int
        Number of months to hold out as the test set. Default: 12 (one year).
    seasonal_periods : int
        Seasonal cycle length for the ETS model. Default: 12 (monthly).

    Returns
    -------
    dict with keys:
        train_dates  : list[str] — ISO dates of the training period
        test_dates   : list[str] — ISO dates of the test (holdout) period
        actuals      : list[float] — held-out actual values (millions USD)
        predictions  : list[float] — model point forecasts for the test period
        ci95_upper   : list[float] — 95% prediction interval upper bound
        ci95_lower   : list[float] — 95% prediction interval lower bound
        residuals    : list[float] — actuals minus predictions
        metrics      : dict with keys:
            mape     : float — Mean Absolute Percentage Error (%)
            mae      : float — Mean Absolute Error (millions USD)
            rmse     : float — Root Mean Squared Error (millions USD)
            n_test   : int   — number of test observations

    Raises
    ------
    ValueError
        If the series is too short to accommodate the holdout period plus
        the minimum required training observations.

    Examples
    --------
    >>> from src.data.fred_client import fetch_fred_series
    >>> series = fetch_fred_series("RSXFS", start_date="2000-01-01")
    >>> results = run_backtest(series, holdout_months=12)
    >>> print(f"Backtest MAPE: {results['metrics']['mape']:.2f}%")
    """
    min_train = 2 * seasonal_periods + 1
    if len(series) < holdout_months + min_train:
        raise ValueError(
            f"Series too short: need at least {holdout_months + min_train} observations "
            f"(holdout={holdout_months} + min_train={min_train}); got {len(series)}."
        )

    train = series.iloc[:-holdout_months]
    test = series.iloc[-holdout_months:]

    # Fit on training data only
    fitted = fit_ets(train, seasonal_periods=seasonal_periods)
    forecast_vals = fitted.forecast(holdout_months)

    # Compute prediction intervals (95%): sigma * sqrt(h) scaling
    residual_std = float(np.std(fitted.resid))
    horizon_factors = np.sqrt(np.arange(1, holdout_months + 1))
    ci95_upper = (forecast_vals.values + 1.96 * residual_std * horizon_factors).tolist()
    ci95_lower = (forecast_vals.values - 1.96 * residual_std * horizon_factors).tolist()

    actuals = test.values.tolist()
    predictions = forecast_vals.values.tolist()
    residuals = (test.values - forecast_vals.values).tolist()

    mape = compute_mape(actuals, predictions)
    mae = compute_mae(actuals, predictions)
    rmse = compute_rmse(actuals, predictions)

    return {
        "train_dates": [d.strftime("%Y-%m-%d") for d in train.index],
        "test_dates": [d.strftime("%Y-%m-%d") for d in test.index],
        "actuals": [round(float(v), 2) for v in actuals],
        "predictions": [round(float(v), 2) for v in predictions],
        "ci95_upper": [round(v, 2) for v in ci95_upper],
        "ci95_lower": [round(v, 2) for v in ci95_lower],
        "residuals": [round(float(v), 2) for v in residuals],
        "metrics": {
            "mape": round(mape, 4),
            "mae": round(mae, 2),
            "rmse": round(rmse, 2),
            "n_test": holdout_months,
        },
    }
