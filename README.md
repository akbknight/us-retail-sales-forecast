# US Retail Sales Demand Forecast Engine

> [!IMPORTANT]
> **Flagship Econometric Forecasting Engine · Part of the Akshay Kumar Technical Portfolio Ecosystem**  
> 🌐 **Executive Portfolio:** [https://akbknight.github.io/](https://akbknight.github.io/) · 💼 **LinkedIn:** [linkedin.com/in/akshaykumardl](https://www.linkedin.com/in/akshaykumardl/) · 📄 **Curriculum Vitae:** [Download PDF (369 KB)](https://akbknight.github.io/assets/Akshay_Resume.pdf)

[![Live Dashboard](https://img.shields.io/badge/Live%20Dashboard-GitHub%20Pages-0284c7?style=flat-square&logo=github)](https://akbknight.github.io/us-retail-sales-forecast/)
[![Model Spec](https://img.shields.io/badge/Model-ETS(A%2CA%2CA)%20State--Space-10b981?style=flat-square)](https://www.statsmodels.org/)
[![Data Source](https://img.shields.io/badge/Data%20Source-Federal%20Reserve%20(FRED)-blue?style=flat-square)](https://fred.stlouisfed.org/series/RSXFS)
[![Horizon](https://img.shields.io/badge/Horizon-18%20Months%20Forward-8b5cf6?style=flat-square)](https://akbknight.github.io/us-retail-sales-forecast/)
[![Backtest Accuracy](https://img.shields.io/badge/Backtest%20MAPE-~2.0%25-f59e0b?style=flat-square)](https://akbknight.github.io/us-retail-sales-forecast/)
[![Author](https://img.shields.io/badge/Author-Akshay%20Kumar-09090b?style=flat-square&logo=linkedin)](https://www.linkedin.com/in/akshaykumardl/)
[![License: MIT](https://img.shields.io/badge/License-MIT-gray?style=flat-square)](LICENSE)

An 18-month forward predictive demand modeling engine for **U.S. Retail & Food Services Sales (RSXFS)** using Holt-Winters triple exponential smoothing in state-space form on Federal Reserve (FRED) time-series data. Features 80% and 95% predictive confidence intervals, walk-forward out-of-sample backtesting, Ljung-Box residual diagnostics, and an interactive client-side dashboard.

👉 **Launch Live Dashboard:** **[https://akbknight.github.io/us-retail-sales-forecast/](https://akbknight.github.io/us-retail-sales-forecast/)**

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
| Latest actual (Aug 2026) | $646.3B |
| 12-month forecast (Aug 2027) | $662.3B |
| Projected change | +2.5% |
| 95% confidence interval at 12m | $612.6B – $712.1B |
| In-sample RMSE | $7.3B (1.13% of mean) |
| Model AIC | 5,728 |
| 12-month backtest MAPE | ~2.0% (1.23% holdout) |

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
| MAPE | ~2.0% (1.23% holdout) |
| MAE | $7.8B |
| RMSE | $9.9B |

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

## 👤 Author & Strategic Portfolio

**Akshay Kumar**  
STEM MBA Candidate · Business Analytics & AI · American University Kogod School of Business  
Business Analyst, U.S. Embassy, India  
- **Executive Portfolio:** [https://akbknight.github.io/](https://akbknight.github.io/)  
- **LinkedIn Profile:** [linkedin.com/in/akshaykumardl](https://www.linkedin.com/in/akshaykumardl/)  
- **Direct Résumé:** [Download PDF (369 KB)](https://akbknight.github.io/assets/Akshay_Resume.pdf)  
- **Email:** [ak8335a@american.edu](mailto:ak8335a@american.edu)


---

## 🔬 Econometric Benchmark & Baseline Evaluation (5-Element Case Study)

- **Question:** Does a complex seasonal state-space exponential smoothing architecture (`ETS(A,A,A)`) consistently outperform simpler econometric baselines on monthly retail sales demand?
- **Evidence:** Evaluated FRED monthly US Advance Retail Sales series (`RSXFS`, 1992–2026, 320 monthly observations, seasonally adjusted). Chronologically evaluated 8 candidate forecasting methods across a 12-month pre-holdout validation window (September 2024 – August 2025) and a locked 12-month out-of-sample holdout (September 2025 – August 2026).
- **Result:** On the pre-holdout validation window, **Nonseasonal Holt** achieved the lowest error ($7.318B MAE, 1.21% MAPE), followed closely by a **Simple Drift Baseline** ($7.677B MAE, 1.27% MAPE). On the locked 12-month holdout (Sep 2025–Aug 2026), **Simple Drift** achieved **1.250% MAPE** ($7.974B MAE) and **Nonseasonal Holt** achieved **1.256% MAPE** ($8.017B MAE), outperforming Additive Seasonal ETS (1.367% MAPE, $8.715B MAE) and Seasonal Naive (3.739% MAPE, $23.640B MAE). Recomputation of the saved pipeline output (`forecast_data.json`) reproduced the stored **1.2294% MAPE** ($7.830B MAE) calculation on this 12-month fixed-origin window.
- **Recommendation:** Do not claim 24-month rolling superiority without evaluating multiple forecast origins. Adopt parsimonious nonseasonal baselines (Simple Drift or Nonseasonal Holt) as the primary evaluation standard for seasonally adjusted retail series before justifying complex multi-parameter models.
- **Limitation:** The benchmark is evaluated on a single fixed-origin 12-month holdout and does not model rolling walk-forward origins, sudden macroeconomic regime shifts, or supply chain shocks. One possible explanation for why nonseasonal baselines were competitive is that RSXFS is already seasonally adjusted prior to publication; however, this is an empirical hypothesis rather than a proven causal finding.

| Model Specification | Validation MAE | Validation MAPE | Holdout Test MAE | Holdout Test MAPE | Test RMSE |
|:---|---:|---:|---:|---:|---:|
| **Simple Drift (Baseline)** | $7.677B | 1.27% | **$7.974B** | **1.250%** | $10.571B |
| **Nonseasonal Holt** | **$7.318B** | **1.21%** | **$8.017B** | **1.256%** | $10.650B |
| **Damped Nonseasonal Holt** | $8.014B | 1.32% | $8.386B | 1.314% | $11.195B |
| **Additive Seasonal ETS** | $8.406B | 1.39% | $8.715B | 1.367% | $11.137B |
| **Damped Seasonal ETS** | $9.284B | 1.53% | $9.235B | 1.449% | $11.803B |
| **Last Value (Random Walk)** | $15.380B | 2.54% | $14.700B | 2.305% | $18.977B |
| **Seasonal Naive** | $18.347B | 3.03% | $23.640B | 3.739% | $25.475B |
| **Linear Trend (Full History)** | $57.051B | 9.43% | $58.262B | 9.254% | $58.851B |

### Reproducibility & Source Verification:
- **Reproduce Locally:** Run `py -3.12 scripts/forecast_compare.py` to recompute all validation rankings and holdout scores directly.
- **Full Report:** See [`reports/baseline_benchmarks.md`](reports/baseline_benchmarks.md).
