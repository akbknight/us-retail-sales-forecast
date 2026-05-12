# Architecture

## Overview

The package follows a linear pipeline pattern: external data source -> model fitting -> diagnostics -> output. Each stage is a separate module with a well-defined interface.

## Data flow

```
FRED API (fred.stlouisfed.org)
        |
        v
src/data/fred_client.py
  fetch_fred_series(series_id, start_date)
  -> pd.Series (monthly, DatetimeIndex, freq='MS')
        |
        v
src/models/ets.py
  fit_ets(series) -> HoltWintersResultsWrapper
  run_forecast(series, n) -> dict {fitted_model, forecast, ci, ...}
        |
        +----> src/models/diagnostics.py
        |        plot_residuals_data(resid) -> dict
        |        ljung_box_test(resid) -> dict
        |        compute_mape / compute_mae / compute_rmse
        |
        +----> src/evaluation/backtest.py
                 run_backtest(series, holdout_months) -> dict {metrics, predictions, ...}
        |
        v
src/pipeline/runner.py
  run_pipeline(...) -> dict (assembled output payload)
        |
        v
forecast_data.json
  (consumed by index.html / Chart.js dashboard)
```

## Module responsibilities

| Module | Responsibility |
|--------|---------------|
| `src/data/fred_client.py` | HTTP fetch from FRED CSV endpoint, retry logic, parse to pd.Series |
| `src/models/ets.py` | ETS(A,A,A) model specification, MLE fitting, probabilistic forecast generation |
| `src/models/diagnostics.py` | Residual statistics, ACF, Ljung-Box Q-test, MAPE/MAE/RMSE |
| `src/evaluation/backtest.py` | Walk-forward holdout backtest, out-of-sample accuracy metrics |
| `src/pipeline/runner.py` | Orchestrates all stages; writes forecast_data.json |
| `src/cli/run.py` | argparse CLI; delegates to runner |
| `forecast.py` | Root-level shim; imports and calls `src.cli.run:main` |
| `index.html` | GitHub Pages dashboard; reads forecast_data.json via Chart.js |

## Key design decisions

- **No matplotlib dependency at runtime.** `plot_residuals_data()` returns a dict of values rather than a figure, keeping the core package lightweight. Visualization is handled by Chart.js in the browser.
- **JSON as the interface layer.** `forecast_data.json` decouples the Python computation from the JavaScript dashboard. The dashboard can be served statically without any Python runtime.
- **Retry logic in fred_client.** Exponential backoff with 3 attempts prevents transient network errors from failing CI/CD pipelines.
- **Compatibility shim.** `forecast.py` at root ensures that existing workflows (`python forecast.py`) continue to work without modification.
