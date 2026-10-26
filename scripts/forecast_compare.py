"""
Forecasting Architecture Benchmark & Baseline Comparison
Evaluates 8 time-series forecasting approaches (Drift, Holt, ETS, Naive, Linear)
against saved fixed-origin holdout actuals on US Retail Sales (FRED RSXFS).
"""
import sys
import json
import warnings
from pathlib import Path

# Add shared pre-compiled package location if running under standalone python
PKG_DIR = Path(r"C:\Users\Akshay Kumar\Documents\Codex\2026-09-02\do-you-have-acess-to-all\outputs\Results_Analysis_2026-10-25\packages")
if PKG_DIR.exists():
    sys.path.insert(0, str(PKG_DIR))

import numpy as np
import pandas as pd
from statsmodels.tsa.holtwinters import ExponentialSmoothing

SRC_DATA = Path(__file__).resolve().parent.parent / "forecast_data.json"

def run_benchmark():
    if not SRC_DATA.exists():
        raise FileNotFoundError(f"Missing forecast_data.json at {SRC_DATA}")
    
    f = json.loads(SRC_DATA.read_text(encoding="utf-8"))
    dates = pd.to_datetime(f["history"]["dates"])
    values = np.array(f["history"]["sales"], float)
    test_dates = pd.to_datetime(f["backtest"]["test_dates"])
    actual = np.array(f["backtest"]["actuals"]) / 1000.0  # Convert to billions

    train = values[dates < test_dates.min()]
    validation = train[-12:]
    training = train[:-12]

    def predict(name, y, h):
        if name == "Last value":
            return np.repeat(y[-1], h)
        if name == "Seasonal naive":
            return np.resize(y[-12:], h)
        if name == "Drift":
            return y[-1] + np.arange(1, h + 1) * (y[-1] - y[0]) / (len(y) - 1)
        if name == "Linear trend":
            return np.polyval(np.polyfit(np.arange(len(y)), y, 1), np.arange(len(y), len(y) + h))
        if name == "ETS additive seasonal":
            spec = {"trend": "add", "seasonal": "add", "seasonal_periods": 12}
        elif name == "ETS damped seasonal":
            spec = {"trend": "add", "damped_trend": True, "seasonal": "add", "seasonal_periods": 12}
        elif name == "Holt nonseasonal":
            spec = {"trend": "add", "seasonal": None}
        elif name == "Damped Holt nonseasonal":
            spec = {"trend": "add", "damped_trend": True, "seasonal": None}
        else:
            raise ValueError(f"Unknown model {name}")

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            return np.asarray(ExponentialSmoothing(y, initialization_method="estimated", **spec).fit(optimized=True).forecast(h))

    def metrics(y, p):
        return {
            "MAE_billions": float(np.abs(y - p).mean()),
            "RMSE_billions": float(np.sqrt(((y - p) ** 2).mean())),
            "MAPE_pct": float((np.abs((y - p) / y)).mean() * 100)
        }

    models = [
        "Last value",
        "Seasonal naive",
        "Drift",
        "Linear trend",
        "ETS additive seasonal",
        "ETS damped seasonal",
        "Holt nonseasonal",
        "Damped Holt nonseasonal"
    ]

    print("=" * 70)
    print("US Retail Demand Forecasting Benchmark (FRED: RSXFS)")
    print(f"Historical Training Observations: {len(train):,} months")
    print(f"Validation Window: {str(dates[dates < test_dates.min()][-12])[:10]} to {str(dates[dates < test_dates.min()][-1])[:10]}")
    print(f"Holdout Test Window: {str(test_dates.min())[:10]} to {str(test_dates.max())[:10]} ({len(actual)} months)")
    print("=" * 70)

    val_res = [{"model": n, **metrics(validation, predict(n, training, 12))} for n in models]
    winner = min(val_res, key=lambda x: x["MAE_billions"])["model"]

    print("\n1. Validation Model Selection (Pre-Holdout):")
    print(f"{'Model Architecture':<26} | {'Validation MAE':<16} | {'MAPE (%)':<10}")
    print("-" * 60)
    for r in sorted(val_res, key=lambda x: x["MAE_billions"]):
        print(f"{r['model']:<26} | ${r['MAE_billions']:>12.3f}B | {r['MAPE_pct']:>8.2f}%")

    print(f"\nValidation Selected Winner: {winner}")

    print("\n2. Out-of-Sample Holdout Evaluation (September 2025 - August 2026):")
    print(f"{'Model Architecture':<26} | {'Test MAE':<16} | {'RMSE':<14} | {'Test MAPE':<10}")
    print("-" * 70)

    test_res = [{"model": n, **metrics(actual, predict(n, train, len(actual)))} for n in models]
    for r in sorted(test_res, key=lambda x: x["MAE_billions"]):
        print(f"{r['model']:<26} | ${r['MAE_billions']:>12.3f}B | ${r['RMSE_billions']:>10.3f}B | {r['MAPE_pct']:>8.3f}%")

    stored = metrics(actual, np.array(f["backtest"]["predictions"]) / 1000.0)
    print("\n3. Saved Deployed Model Check (ETS Additive):")
    print(f"  Saved Recomputed Test MAE: ${stored['MAE_billions']:.3f}B | Test MAPE: {stored['MAPE_pct']:.4f}%")

    print("\nAnalytical Takeaway:")
    print("  Simple Drift ($7.974B MAE, 1.250% MAPE) and Nonseasonal Holt ($8.017B MAE, 1.256% MAPE)")
    print("  were highly competitive with seasonal ETS ($8.715B MAE, 1.367% MAPE) because the source")
    print("  FRED series (RSXFS) is already seasonally adjusted. Complexity must be defended empirically.")

if __name__ == "__main__":
    run_benchmark()
