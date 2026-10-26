# US Retail Demand Forecasting Benchmark & Baseline Comparison

**Prepared:** October 2026  
**Author:** Akshay Kumar  
**Target Codebase:** `us-retail-sales-forecast`  
**Evaluation Script:** `scripts/forecast_compare.py`  
**Data Series:** FRED `RSXFS` (Advance Retail Sales: Retail Trade and Food Services, Seasonally Adjusted)  
**Structured Output:** `reports/forecast_benchmark_results.json`

---

## 1. Executive Summary & Structured Case Study

### Core Analytical Case Study (Question → Evidence → Result → Recommendation → Limitation)

- **Question:** Does a complex seasonal state-space exponential smoothing architecture (`ETS(A,A,A)`) consistently outperform simpler econometric baselines on forward retail demand?
- **Evidence:** Evaluated the Federal Reserve Economic Data (FRED) monthly US Advance Retail Sales series (`RSXFS`, January 2000 – August 2026, 320 monthly observations, seasonally adjusted; series truncated from 1992 to avoid pre-2000 benchmark revision uncertainty). Chronologically evaluated 8 candidate forecasting methods across a 12-month pre-holdout validation window (September 2024 – August 2025) and a locked 12-month out-of-sample evaluation holdout (September 2025 – August 2026), alongside an 18-month forward operational projection horizon (September 2026 – February 2028).
- **Result:** On the pre-holdout validation window, **Nonseasonal Holt** achieved the lowest error ($7.318B MAE, 1.21% MAPE), followed closely by a **Simple Drift Baseline** ($7.677B MAE, 1.27% MAPE). On the locked 12-month holdout (Sep 2025–Aug 2026), **Simple Drift** achieved **1.250% MAPE** ($7.974B MAE) and **Nonseasonal Holt** achieved **1.256% MAPE** ($8.017B MAE), outperforming Additive Seasonal ETS (1.367% MAPE, $8.715B MAE) and Seasonal Naive (3.739% MAPE, $23.640B MAE). Recomputation of the saved pipeline output (`forecast_data.json`) reproduced the stored **1.2294% MAPE** ($7.830B MAE) calculation on this 12-month fixed-origin window.
- **Recommendation:** Do not claim 24-month rolling superiority without evaluating multiple forecast origins. Adopt parsimonious nonseasonal baselines (Simple Drift or Nonseasonal Holt) as the primary evaluation standard for seasonally adjusted retail series before justifying complex multi-parameter models.
- **Limitation:** The benchmark is evaluated on a single fixed-origin 12-month holdout and does not model rolling walk-forward origins, sudden macroeconomic regime shifts, or supply chain shocks. One possible explanation for why nonseasonal baselines were competitive is that `RSXFS` is already seasonally adjusted prior to publication; however, this is an empirical hypothesis rather than a proven causal finding.

---

## 2. 8-Model Comparative Benchmark Table

| Model Specification | Model Category | Validation MAE | Validation MAPE | Holdout Test MAE | Holdout Test MAPE | Out-of-Sample RMSE |
|:---|:---|---:|---:|---:|---:|---:|
| **Simple Drift** | Empirical Baseline | $7.677B | 1.27% | **$7.974B** | **1.250%** | $10.571B |
| **Nonseasonal Holt** | State-Space Smoothing | **$7.318B** | **1.21%** | **$8.017B** | **1.256%** | $10.650B |
| **Damped Nonseasonal Holt** | State-Space Smoothing | $8.014B | 1.32% | $8.386B | 1.314% | $11.195B |
| **Additive Seasonal ETS** | Full State-Space ETS | $8.406B | 1.39% | $8.715B | 1.367% | $11.137B |
| **Damped Seasonal ETS** | Full State-Space ETS | $9.284B | 1.53% | $9.235B | 1.449% | $11.803B |
| **Last Value (Random Walk)** | Naive Baseline | $15.380B | 2.54% | $14.700B | 2.305% | $18.977B |
| **Seasonal Naive** | Seasonal Baseline | $18.347B | 3.03% | $23.640B | 3.739% | $25.475B |
| **Linear Trend (Full History)** | Global Trend | $57.051B | 9.43% | $58.262B | 9.254% | $58.851B |

---

## 3. Operational & Reproducibility Guide

To reproduce this benchmark directly:
```bash
py -3.12 scripts/forecast_compare.py
```
Outputs print validation rankings, holdout test metrics, and verify saved predictions against actuals. All tables in this report are generated directly from `reports/forecast_benchmark_results.json`.
