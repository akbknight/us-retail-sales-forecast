"""
Pipeline Runner
===============
Orchestrates the full forecasting pipeline:
    1. Fetch RSXFS data from FRED
    2. Fit ETS(A,A,A) model
    3. Run residual diagnostics and Ljung-Box test
    4. Run walk-forward backtest
    5. Assemble and write forecast_data.json
"""

from __future__ import annotations

import json
import warnings
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd

from src.data.fred_client import fetch_fred_series
from src.models.ets import run_forecast
from src.models.diagnostics import plot_residuals_data, ljung_box_test
from src.evaluation.backtest import run_backtest

warnings.filterwarnings("ignore")

DEFAULT_SERIES_ID = "RSXFS"
DEFAULT_START = "2000-01-01"
DEFAULT_HORIZON = 18
DEFAULT_OUTPUT = "forecast_data.json"
DEFAULT_HOLDOUT = 12


def run_pipeline(
    series_id: str = DEFAULT_SERIES_ID,
    start_date: str = DEFAULT_START,
    horizon_months: int = DEFAULT_HORIZON,
    holdout_months: int = DEFAULT_HOLDOUT,
    output_path: str = DEFAULT_OUTPUT,
    verbose: bool = True,
) -> dict:
    """
    Run the full forecast pipeline and write output JSON.

    Parameters
    ----------
    series_id : str
        FRED series identifier. Default: ``"RSXFS"``.
    start_date : str
        ISO start date for the analysis window. Default: ``"2000-01-01"``.
    horizon_months : int
        Forecast horizon in months. Default: 18.
    holdout_months : int
        Number of months to hold out for backtesting. Default: 12.
    output_path : str
        Path for the output JSON file. Default: ``"forecast_data.json"``.
    verbose : bool
        Whether to print progress to stdout. Default: True.

    Returns
    -------
    dict
        The full output payload (also written to ``output_path``).
    """
    def log(msg: str) -> None:
        if verbose:
            print(msg)

    # ------------------------------------------------------------------
    # 1. Fetch data
    # ------------------------------------------------------------------
    log(f"Fetching FRED {series_id} data...")
    series = fetch_fred_series(series_id, start_date=start_date)
    log(f"Data: {series.index[0].strftime('%b %Y')} to {series.index[-1].strftime('%b %Y')} ({len(series)} months)")

    # ------------------------------------------------------------------
    # 2. Fit ETS and generate forecast
    # ------------------------------------------------------------------
    log("Fitting ETS(A,A,A) model...")
    result = run_forecast(series, n=horizon_months, ci_levels=[0.80, 0.95])
    fm = result["fitted_model"]
    fc = result["forecast"]
    fi = result["forecast_index"]
    std = result["residual_std"]
    hf = result["horizon_factors"]
    ci = result["ci"]

    # ------------------------------------------------------------------
    # 3. Diagnostics
    # ------------------------------------------------------------------
    log("Running diagnostics...")
    diag = plot_residuals_data(fm.resid)
    lb = ljung_box_test(fm.resid, lags=12)

    # ------------------------------------------------------------------
    # 4. Backtest
    # ------------------------------------------------------------------
    log(f"Running {holdout_months}-month walk-forward backtest...")
    backtest = run_backtest(series, holdout_months=holdout_months)
    log(f"  Backtest MAPE: {backtest['metrics']['mape']:.2f}%")
    log(f"  Backtest RMSE: {backtest['metrics']['rmse']:,.0f}M USD")

    # ------------------------------------------------------------------
    # 5. Assemble output
    # ------------------------------------------------------------------
    latest = float(series.iloc[-1])
    forecast_12m = float(fc.iloc[min(11, len(fc) - 1)])
    fi_12m = fi[min(11, len(fi) - 1)]

    yoy_series = series["2018-01-01":].pct_change(12).dropna() * 100

    n = len(fc)
    ci95 = ci[0.95]
    ci80 = ci[0.80]

    output = {
        "summary": {
            "series": "Advance Retail Sales: Retail Trade and Food Services",
            "ticker": series_id,
            "source": "U.S. Census Bureau via Federal Reserve Bank of St. Louis (FRED)",
            "source_url": f"https://fred.stlouisfed.org/series/{series_id}",
            "units": "Millions of Dollars, Seasonally Adjusted",
            "latest_value_millions": round(latest, 1),
            "latest_value_billions": round(latest / 1000, 1),
            "latest_date": series.index[-1].strftime("%B %Y"),
            "forecast_12m_billions": round(forecast_12m / 1000, 1),
            "forecast_12m_date": fi_12m.strftime("%B %Y"),
            "forecast_change_pct": round((forecast_12m - latest) / latest * 100, 2),
            "ci_95_lower_12m": round(float(fc.iloc[11] - 1.96 * std * np.sqrt(12)) / 1000, 1),
            "ci_95_upper_12m": round(float(fc.iloc[11] + 1.96 * std * np.sqrt(12)) / 1000, 1),
            "model": "ETS(A,A,A) — Holt-Winters Additive",
            "seasonal_periods": 12,
            "alpha": round(float(fm.params["smoothing_level"]), 4),
            "aic": round(float(fm.aic), 1),
            "rmse_billions": round(float(np.sqrt(np.mean(fm.resid ** 2))) / 1000, 2),
            "backtest_mape": backtest["metrics"]["mape"],
            "backtest_mae_billions": round(backtest["metrics"]["mae"] / 1000, 2),
            "backtest_rmse_billions": round(backtest["metrics"]["rmse"] / 1000, 2),
        },
        "history": {
            "dates": [d.strftime("%Y-%m-%d") for d in series.index],
            "sales": [round(float(v) / 1000, 2) for v in series],
            "fitted": [round(float(v) / 1000, 2) for v in fm.fittedvalues],
        },
        "forecast": {
            "dates": [d.strftime("%Y-%m-%d") for d in fi],
            "point": [round(float(v) / 1000, 2) for v in fc],
            "ci95u": [round(v / 1000, 2) for v in ci95["upper"]],
            "ci95l": [round(v / 1000, 2) for v in ci95["lower"]],
            "ci80u": [round(v / 1000, 2) for v in ci80["upper"]],
            "ci80l": [round(v / 1000, 2) for v in ci80["lower"]],
        },
        "yoy": {
            "dates": [d.strftime("%Y-%m-%d") for d in yoy_series.index],
            "pct": [round(float(v), 2) for v in yoy_series],
        },
        "diagnostics": {
            "residuals": diag,
            "ljung_box": lb,
        },
        "backtest": backtest,
    }

    # Write JSON
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)

    log(f"\nResults:")
    s = output["summary"]
    log(f"  Latest actual:  ${s['latest_value_billions']}B ({s['latest_date']})")
    log(f"  12m forecast:   ${s['forecast_12m_billions']}B ({s['forecast_12m_date']}) [{s['forecast_change_pct']:+.1f}%]")
    log(f"  95% CI at 12m:  ${s['ci_95_lower_12m']}B to ${s['ci_95_upper_12m']}B")
    log(f"  RMSE:           ${s['rmse_billions']}B")
    log(f"  AIC:            {s['aic']}")
    log(f"  Backtest MAPE:  {s['backtest_mape']:.2f}%")
    log(f"\nSaved: {output_path}")

    return output
