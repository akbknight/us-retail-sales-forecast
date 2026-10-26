# US Retail Demand Forecasting Benchmark & Baseline Comparison

**Prepared:** October 2026  
**Author:** Akshay Kumar  
**Target Codebase:** `us-retail-sales-forecast`  
**Evaluation Script:** `scripts/forecast_compare.py`  
**Data Series:** FRED `RSXFS` (Advance Retail Sales: Retail Trade and Food Services, Seasonally Adjusted)

---

## 1. Executive Summary & Evaluation Context

Does a complex state-space exponential smoothing model with seasonality (`ETS(A,A,A)`) consistently outperform simpler econometric baselines on forward retail demand?

To establish empirical rigor, we benchmarked **eight forecasting methods** across a pre-holdout validation window (September 2024 – August 2025) and a locked 12-month out-of-sample holdout (September 2025 – August 2026).

### Key Empirical Findings
1. **Validation Selection:** On the 12-month pre-holdout validation window, **Nonseasonal Holt** achieved the lowest error ($7.318B MAE, 1.21% MAPE), followed closely by a **Simple Drift Baseline** ($7.677B MAE, 1.27% MAPE).
2. **Holdout Test Accuracy:** On the held-out 12 months:
   - **Simple Drift:** $7.974B MAE (1.250% MAPE)
   - **Nonseasonal Holt:** $8.017B MAE (1.256% MAPE)
   - **Damped Nonseasonal Holt:** $8.386B MAE (1.314% MAPE)
   - **Additive Seasonal ETS:** $8.715B MAE (1.367% MAPE)
   - **Damped Seasonal ETS:** $9.235B MAE (1.449% MAPE)
   - **Last Observed Value:** $14.700B MAE (2.305% MAPE)
   - **Seasonal Naive:** $23.640B MAE (3.739% MAPE)
3. **Saved Output Verification:** Recomputation of the saved `forecast_data.json` artifacts reproduces **1.2294% MAPE**, **$7.830B MAE**, and **$9.928B RMSE**.
4. **Methodological Clarification:** The evaluation is a **fixed-origin 12-month holdout**, not rolling walk-forward retraining. Furthermore, because the source series is already seasonally adjusted by the U.S. Census Bureau, nonseasonal models (Holt and Drift) perform as well or better than seasonal variants without unnecessary parameter overhead.

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
Outputs print validation rankings, holdout test metrics, and verify saved predictions against actuals.
