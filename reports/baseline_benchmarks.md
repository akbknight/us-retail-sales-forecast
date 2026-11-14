# US Retail Demand Forecasting Benchmark & Baseline Comparison

**Prepared:** October 2026 (Updated with Multi-Origin Evaluation Suite)  
**Author:** Akshay Kumar  
**Target Codebase:** `us-retail-sales-forecast`  
**Evaluation Script:** `scripts/forecast_compare.py`  
**Data Series:** FRED `RSXFS` (Advance Retail Sales: Retail Trade and Food Services, Seasonally Adjusted)  
**Structured Output:** `reports/forecast_benchmark_results.json`

---

## 1. Executive Summary & Structured Case Study

### Core Analytical Case Study (Question → Evidence → Result → Recommendation → Limitation)

- **Question:** Does a complex seasonal state-space exponential smoothing architecture (`ETS(A,A,A)`) consistently outperform simpler econometric baselines on forward retail demand across multiple forecast origins?
- **Evidence:** Evaluated the Federal Reserve Economic Data (FRED) monthly US Advance Retail Sales series (`RSXFS`, 320 monthly observations, January 2000 – August 2026, seasonally adjusted). Conducted both a locked 12-month fixed-origin holdout (September 2025 – August 2026) and a 4-horizon multi-origin evaluation suite (evaluating 12-month ahead projections across 2022–2023, 2023–2024, 2024–2025, and 2025–2026) spanning distinct post-pandemic inflationary and normalization regimes.
- **Result:**
  1. **Fixed Holdout (Sep 2025–Aug 2026):** **Simple Drift** achieved **1.250% MAPE** ($7.974B MAE) and **Nonseasonal Holt** achieved **1.256% MAPE** ($8.017B MAE), outperforming Additive Seasonal ETS (1.367% MAPE, $8.715B MAE) and Seasonal Naive (3.739% MAPE, $23.640B MAE).
  2. **Multi-Origin Cross-Validation (4 Horizons: 2022–2026):** Across all 4 historical forecast origins, **Nonseasonal Holt** achieved the lowest overall average error at **$9.078B Avg MAE (1.515% Avg MAPE)**, followed by **Additive Seasonal ETS ($9.129B Avg MAE, 1.519% Avg MAPE)** and **Simple Drift ($9.224B Avg MAE, 1.539% Avg MAPE)**. Nonseasonal state-space smoothing and drift baselines performed within 0.02% MAPE of the full seasonal specification across all four regimes.
  3. **Production Model Verification:** Recomputation of the saved production pipeline output (`forecast_data.json`) verified the stored **1.2294% MAPE** ($7.830B MAE, $9.928B RMSE) calculation on the 12-month holdout window.
- **Recommendation:** Adopt parsimonious nonseasonal baselines (Simple Drift or Nonseasonal Holt) as the primary evaluation standard for seasonally adjusted retail series. Do not assume seasonal complexity adds value without benchmarking against drift and state-space smoothing across multiple origins.
- **Limitation:** Findings apply to the seasonally adjusted FRED `RSXFS` aggregate series. Macroeconomic regime shifts, sudden fiscal stimulus shocks, or disaggregated category-level volatility may require alternative structural or exogenous covariates.

---

## 2. 8-Model Fixed-Origin Holdout Table (Sep 2025 – Aug 2026)

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

## 3. Multi-Origin Cross-Validation Suite (4 Horizons: 2022–2026)

Evaluated across 4 expanding 12-month forecast horizons (Origin 1: 2022–2023 · Origin 2: 2023–2024 · Origin 3: 2024–2025 · Origin 4: 2025–2026):

| Model Specification | Model Category | 4-Origin Avg MAE | 4-Origin Avg MAPE | 4-Origin Avg RMSE |
|:---|:---|---:|---:|---:|
| **Nonseasonal Holt** | State-Space Smoothing | **$9.078B** | **1.515%** | $10.583B |
| Additive Seasonal ETS | Full State-Space ETS | $9.129B | 1.519% | $10.629B |
| Simple Drift | Empirical Baseline | $9.224B | 1.539% | $10.728B |
| Last Value (Random Walk) | Naive Baseline | $9.485B | 1.547% | $11.322B |
| Damped Seasonal ETS | Full State-Space ETS | $10.519B | 1.754% | $12.260B |
| Damped Nonseasonal Holt | State-Space Smoothing | $10.589B | 1.771% | $12.300B |
| Seasonal Naive | Seasonal Baseline | $15.824B | 2.602% | $18.363B |
| Linear Trend (Full History) | Global Trend | $65.653B | 10.967% | $65.936B |

---

## 4. Operational & Reproducibility Guide

To reproduce this benchmark directly:
```bash
py -3.14 scripts/forecast_compare.py
```
Outputs print validation rankings, locked holdout metrics, and 4-origin cross-validation results. All tables in this report are generated directly from `reports/forecast_benchmark_results.json`.
