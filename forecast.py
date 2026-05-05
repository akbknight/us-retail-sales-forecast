"""
US Retail Sales Demand Forecast
================================
Fetches FRED RSAFS series (Advance Retail & Food Services Sales, Seasonally Adjusted)
and applies Holt-Winters triple exponential smoothing to produce an 18-month forward
forecast with 80% and 95% predictive intervals.

Data source: Federal Reserve Bank of St. Louis (FRED)
Series:      RSAFS — https://fred.stlouisfed.org/series/RSAFS
Frequency:   Monthly, seasonally adjusted, millions of USD

Usage:
    pip install pandas statsmodels
    python forecast.py

Output: forecast_data.json (consumed by index.html dashboard)
"""

import io
import json
import urllib.request
import warnings

import numpy as np
import pandas as pd
from statsmodels.tsa.holtwinters import ExponentialSmoothing

warnings.filterwarnings("ignore")


FRED_URL = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=RSAFS"
ANALYSIS_START = "2015-01-01"
N_FORECAST = 18
OUTPUT_PATH = "forecast_data.json"


def fetch_fred_series(url: str) -> pd.Series:
    """Download a FRED series as a monthly pandas Series."""
    with urllib.request.urlopen(url) as resp:
        raw = resp.read().decode()
    df = pd.read_csv(io.StringIO(raw), parse_dates=["observation_date"])
    df.columns = ["date", "value"]
    df = df.set_index("date").sort_index()
    return df["value"]


def run_forecast(series: pd.Series, n: int) -> dict:
    """Fit Holt-Winters model and return forecast + confidence intervals."""
    model = ExponentialSmoothing(
        series,
        trend="add",
        seasonal="add",
        seasonal_periods=12,
        initialization_method="estimated",
    )
    fitted = model.fit(optimized=True)

    forecast = fitted.forecast(n)
    forecast_index = pd.date_range(
        start=series.index[-1] + pd.DateOffset(months=1),
        periods=n,
        freq="MS",
    )

    residual_std = float(np.std(fitted.resid))
    horizon_factors = np.sqrt(np.arange(1, n + 1))

    return {
        "fitted_model": fitted,
        "forecast": forecast,
        "forecast_index": forecast_index,
        "residual_std": residual_std,
        "horizon_factors": horizon_factors,
    }


def build_output(series: pd.Series, result: dict) -> dict:
    fm = result["fitted_model"]
    fc = result["forecast"]
    fi = result["forecast_index"]
    std = result["residual_std"]
    hf = result["horizon_factors"]
    n = len(fc)

    latest = float(series.iloc[-1])
    forecast_12m = float(fc.iloc[11])

    yoy_series = series["2018-01-01":].pct_change(12).dropna() * 100

    return {
        "summary": {
            "series": "Advance Retail & Food Services Sales",
            "ticker": "RSAFS",
            "source": "Federal Reserve Bank of St. Louis (FRED)",
            "source_url": "https://fred.stlouisfed.org/series/RSAFS",
            "units": "Billions of USD (Seasonally Adjusted)",
            "latest_value_billions": round(latest / 1000, 1),
            "latest_date": series.index[-1].strftime("%B %Y"),
            "forecast_12m_billions": round(forecast_12m / 1000, 1),
            "forecast_12m_date": fi[11].strftime("%B %Y"),
            "forecast_change_pct": round((forecast_12m - latest) / latest * 100, 2),
            "ci_95_lower_12m": round(float(fc.iloc[11] - 1.96 * std * np.sqrt(12)) / 1000, 1),
            "ci_95_upper_12m": round(float(fc.iloc[11] + 1.96 * std * np.sqrt(12)) / 1000, 1),
            "model": "Holt-Winters Triple Exponential Smoothing",
            "seasonal_periods": 12,
            "alpha": round(float(fm.params["smoothing_level"]), 4),
            "aic": round(float(fm.aic), 1),
            "rmse_billions": round(float(np.sqrt(np.mean(fm.resid ** 2))) / 1000, 2),
        },
        "history": {
            "dates": [d.strftime("%Y-%m-%d") for d in series.index],
            "sales": [round(float(v) / 1000, 2) for v in series],
            "fitted": [round(float(v) / 1000, 2) for v in fm.fittedvalues],
        },
        "forecast": {
            "dates": [d.strftime("%Y-%m-%d") for d in fi],
            "point": [round(float(v) / 1000, 2) for v in fc],
            "ci95u": [round(float(fc.iloc[i] + 1.96 * std * hf[i]) / 1000, 2) for i in range(n)],
            "ci95l": [round(float(fc.iloc[i] - 1.96 * std * hf[i]) / 1000, 2) for i in range(n)],
            "ci80u": [round(float(fc.iloc[i] + 1.28 * std * hf[i]) / 1000, 2) for i in range(n)],
            "ci80l": [round(float(fc.iloc[i] - 1.28 * std * hf[i]) / 1000, 2) for i in range(n)],
        },
        "yoy": {
            "dates": [d.strftime("%Y-%m-%d") for d in yoy_series.index],
            "pct": [round(float(v), 2) for v in yoy_series],
        },
    }


def main():
    print("Fetching FRED RSAFS data...")
    raw_series = fetch_fred_series(FRED_URL)
    series = raw_series[ANALYSIS_START:]

    print(f"Data: {series.index[0].strftime('%b %Y')} to {series.index[-1].strftime('%b %Y')} ({len(series)} months)")
    print("Fitting Holt-Winters model...")

    result = run_forecast(series, N_FORECAST)

    output = build_output(series, result)
    s = output["summary"]

    print(f"\nResults:")
    print(f"  Latest actual:  ${s['latest_value_billions']}B ({s['latest_date']})")
    print(f"  12m forecast:   ${s['forecast_12m_billions']}B ({s['forecast_12m_date']}) [{s['forecast_change_pct']:+.1f}%]")
    print(f"  95% CI at 12m:  ${s['ci_95_lower_12m']}B to ${s['ci_95_upper_12m']}B")
    print(f"  RMSE:           ${s['rmse_billions']}B")
    print(f"  AIC:            {s['aic']}")

    with open(OUTPUT_PATH, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nSaved: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
