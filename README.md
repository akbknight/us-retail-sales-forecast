# US Retail Sales Demand Forecast

**Flagship project. Production-grade time-series forecasting package.**

18-month probabilistic forecast for US Retail Sales (RSXFS) using a Holt-Winters ETS(A,A,A) state-space model on FRED data, with walk-forward backtesting, residual diagnostics, and an interactive live dashboard.

**Live dashboard:** https://akbknight.github.io/us-retail-sales-forecast/

---

## What it forecasts

**Series:** RSXFS — Advance Retail Sales: Retail Trade and Food Services
**Published by:** U.S. Census Bureau, via FRED (Federal Reserve Bank of St. Louis)
**Units:** Millions of dollars, seasonally adjusted, monthly
**FRED link:** https://fred.stlouisfed.org/series/RSXFS

RSXFS is the broadest monthly retail indicator — it covers all retail trade plus food services (~5,000+ surveyed firms), making it the headline series cited by the Federal Reserve and financial press. It represents approximately 30-35% of U.S. personal consumption expenditures and is a key leading indicator of GDP growth.

---

## Key results

| Metric | Value |
|---|---|
| Latest actual (Mar 2026) | $752.1B |
| 12-month forecast (Mar 2027) | $789.2B |
| Projected change | +4.9% |
| 95% confidence interval at 12m | $705B - $873B |
| In-sample RMSE | $12.4B (1.65% of mean) |
| Model AIC | 2,577 |
| 12-month backtest MAPE | ~2.0% |

---

## Technical methodology

The model is **ETS(A,A,A)** — additive error, additive trend, additive seasonality (Holt-Winters triple exponential smoothing in state-space form).

**Why additive?** RSXFS has a roughly stable seasonal amplitude in dollar terms across the 2000-2026 sample (the December holiday peak adds ~$50-70B above trend regardless of the trend level), making the additive specification appropriate over multiplicative.

**Parameter estimation:** All parameters (smoothing weights alpha, beta, gamma; plus initialization states) are estimated jointly by maximum likelihood (MLE) via L-BFGS-B optimization, minimizing the Gaussian negative log-likelihood of one-step-ahead forecast errors.

**Prediction intervals:** Based on the Hyndman et al. (2008) state-space formulation — forecast error variance grows as sigma^2 * h, giving sqrt(h)-scaled intervals. The 95% CI uses z=1.96; the 80% CI uses z=1.28.

Full methodology: [docs/methodology.md](docs/methodology.md)
Modeling decisions: [docs/decision_log.md](docs/decision_log.md)

---

## Backtesting

Walk-forward backtest: the model is trained on all data except the final 12 months, then generates 12-month-ahead point forecasts compared to the held-out actuals.

| Backtest metric | Value |
|---|---|
| Holdout period | 12 months |
| MAPE | ~2.0% |
| MAE | ~$13-15B |
| RMSE | ~$15-18B |

A ~2% MAPE is consistent with published ETS benchmarks on monthly macroeconomic series from the M4 Competition (Makridakis et al., 2020), where ETS ranked in the upper quartile of 61 methods on monthly economic series.

Full results: [reports/forecasting_results.md](reports/forecasting_results.md)

---

## Quick start

```bash
# Clone
git clone https://github.com/akbknight/us-retail-sales-forecast.git
cd us-retail-sales-forecast

# Install dependencies
pip install -r requirements.txt
# or: make install

# Run the forecast (fetches live FRED data, writes forecast_data.json)
python forecast.py
# or: make run

# Full CLI options
python -m src.cli.run --help
python -m src.cli.run --series RSXFS --start 2000-01-01 --horizon 18

# Run backtest only
make backtest

# Run tests
make test
```

**Requirements:** Python 3.9+. No API key needed — FRED provides public CSV data at `fred.stlouisfed.org`.

---

## Project structure

```
src/
  data/fred_client.py      — FRED fetch with retry logic (3 attempts, exponential backoff)
  models/ets.py            — ETS(A,A,A) fitting with full state-space docstring
  models/diagnostics.py    — Residual stats, Ljung-Box Q-test, MAPE/MAE/RMSE
  evaluation/backtest.py   — Walk-forward 12-month holdout backtest
  pipeline/runner.py       — Orchestrates all stages; writes forecast_data.json
  cli/run.py               — argparse CLI entry point
forecast.py                — Root shim (backward compatible, delegates to src/)
configs/app/config.yaml    — All tunable parameters
docs/
  methodology.md           — ETS equations, MLE, prediction intervals, alternatives
  architecture.md          — Data flow and module diagram
  decision_log.md          — Why 18 months, why ETS, why RSXFS, why 2000 start
reports/
  research_notes.md        — MARTS survey, Hyndman references, M4 competition
  eda.md                   — Trend, seasonality, GFC/COVID regime changes
  forecasting_results.md   — In-sample and backtest model performance
tests/
  test_ets.py              — Metrics tests with known inputs; forecast structure tests
  test_backtest.py         — Backtest structure, accuracy, and error handling tests
index.html                 — Chart.js interactive dashboard (GitHub Pages)
```

---

## Tech stack

| Layer | Technology |
|---|---|
| Data source | FRED API — RSXFS series (U.S. Census Bureau) |
| Statistical model | Python 3, statsmodels (ExponentialSmoothing), scipy |
| Data wrangling | pandas, numpy |
| Testing | pytest |
| Dashboard | Chart.js 4, plain HTML/CSS/JS |
| Deployment | GitHub Pages (index.html + forecast_data.json) |
| Packaging | pyproject.toml (PEP 517/518) |

---

## Data source

**Federal Reserve Bank of St. Louis (FRED)**
Series: RSXFS — Advance Retail Sales: Retail Trade and Food Services
URL: https://fred.stlouisfed.org/series/RSXFS
License: Public domain. FRED data is free and unrestricted.

Note: This project uses RSXFS (includes food services, the broader headline series) rather than RSAFS (retail only). See [docs/decision_log.md](docs/decision_log.md) for rationale.

---

## Author

**Akshay Kumar**
[linkedin.com/in/akshaykumardl](https://www.linkedin.com/in/akshaykumardl/)
