# US Retail Demand Forecasting Benchmark & Baseline Comparison

**Prepared:** October 2026 (Updated with Four-Origin 12-Month Horizon Suite)  
**Author:** Akshay Kumar  
**Target Codebase:** `us-retail-sales-forecast`  
**Evaluation Script:** `scripts/forecast_compare.py`  
**Data Series:** FRED `RSXFS` (Advance Retail Sales: Retail Trade and Food Services, Seasonally Adjusted)  
**Structured Output:** `reports/forecast_benchmark_results.json`

---

## 1. Executive Summary & Structured Case Study

### Core Analytical Case Study (Question → Evidence → Result → Recommendation → Limitation)

- **Question:** Does a complex seasonal state-space exponential smoothing architecture (`ETS(A,A,A)`) consistently outperform simpler econometric baselines on forward retail demand across multiple forecast origins?
- **Evidence:** Evaluated the Federal Reserve Economic Data (FRED) monthly US Advance Retail Sales series (`RSXFS`, 320 monthly observations, January 2000 – August 2026, seasonally adjusted). Conducted both an evaluation on the original historical holdout window (September 2025 – August 2026) and a retrospective 4-origin evaluation suite with a 12-month horizon (evaluating projections across Origin 1: 2022–2023, Origin 2: 2023–2024, Origin 3: 2024–2025, and Origin 4: 2025–2026) spanning post-pandemic inflationary shifts and normalization.
- **Result:**
  1. **Original Historical Holdout (Sep 2025–Aug 2026):** **Simple Drift** achieved **1.250% MAPE** ($7.974B MAE) and **Nonseasonal Holt** achieved **1.256% MAPE** ($8.017B MAE), outperforming Additive Seasonal ETS (1.367% MAPE, $8.715B MAE) and Seasonal Naive (3.739% MAPE, $23.640B MAE).
  2. **Retrospective Multi-Origin Evaluation (Four Origins with a 12-Month Horizon):** Across the four origins, **Nonseasonal Holt** achieved the lowest mean MAE at **$9.078B Mean MAE (1.515% Mean MAPE)**, followed closely by **Additive Seasonal ETS ($9.129B Mean MAE, 1.519% Mean MAPE)** and **Simple Drift ($9.224B Mean MAE, 1.539% Mean MAPE)**. The difference between the top three specifications is approximately 0.0245 percentage points ($0.146B MAE).
  3. **Production Model Verification:** Recomputation of the saved production pipeline output (`forecast_data.json`) verified the stored **1.2294% MAPE** ($7.830B MAE, $9.928B RMSE) calculation on the original historical holdout window.
- **Recommendation:** Adopt parsimonious nonseasonal baselines (Simple Drift or Nonseasonal Holt) as the primary evaluation standard for seasonally adjusted retail series. Benchmark seasonal models against drift and nonseasonal smoothing across multiple origins before assuming seasonal complexity is beneficial.
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

## 3. Retrospective Multi-Origin Evaluation Suite (Four Origins with a 12-Month Horizon)

Evaluated across four origins with a 12-month horizon (Origin 1: 2022–2023 · Origin 2: 2023–2024 · Origin 3: 2024–2025 · Origin 4: 2025–2026):

| Model Specification | Model Category | 4-Origin Mean MAE | 4-Origin Mean MAPE | 4-Origin Mean RMSE |
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

## 4. Per-Origin Detailed Results Breakdown

Full per-origin evaluation metrics across all four 12-month horizons:

| Model Specification | Origin 1: 2022–23 MAE (MAPE) | Origin 2: 2023–24 MAE (MAPE) | Origin 3: 2024–25 MAE (MAPE) | Origin 4: 2025–26 MAE (MAPE) | 4-Origin Mean MAE | 4-Origin Mean MAPE |
|:---|---:|---:|---:|---:|---:|---:|
| **Nonseasonal Holt** | $10.800B (1.858%) | $10.179B (1.739%) | $7.318B (1.206%) | $8.017B (1.256%) | **$9.078B** | **1.515%** |
| Additive Seasonal ETS | $10.128B (1.741%) | $9.266B (1.583%) | $8.406B (1.386%) | $8.715B (1.367%) | $9.129B | 1.519% |
| Simple Drift | $10.773B (1.853%) | $10.470B (1.789%) | $7.677B (1.266%) | $7.974B (1.250%) | $9.224B | 1.539% |
| Last Value (Random Walk) | $4.458B (0.768%) | $3.402B (0.582%) | $15.380B (2.535%) | $14.699B (2.304%) | $9.485B | 1.547% |
| Damped Seasonal ETS | $13.572B (2.333%) | $9.985B (1.705%) | $9.284B (1.531%) | $9.234B (1.449%) | $10.519B | 1.754% |
| Damped Nonseasonal Holt | $14.856B (2.553%) | $11.101B (1.896%) | $8.014B (1.321%) | $8.385B (1.314%) | $10.589B | 1.771% |
| Seasonal Naive | $15.690B (2.683%) | $5.620B (0.960%) | $18.347B (3.026%) | $23.639B (3.739%) | $15.824B | 2.602% |
| Linear Trend (Full History) | $85.656B (14.669%) | $61.643B (10.514%) | $57.051B (9.434%) | $58.262B (9.254%) | $65.653B | 10.967% |

### Empirical Nuance & Methodology Boundaries
1. **Narrow Margins:** The difference between Nonseasonal Holt (1.515% Mean MAPE), Additive Seasonal ETS (1.519% Mean MAPE), and Simple Drift (1.539% Mean MAPE) is approximately 0.0245 percentage points ($0.146B MAE) across 48 evaluated months. These small differences do not establish universal superiority or prove that seasonality is universally unhelpful across other series or disaggregate data.
2. **Regime Sensitivity:** In Origins 1 and 2, Additive Seasonal ETS achieved lower MAE than Holt and Drift, whereas in Origins 3 and 4, Holt and Drift achieved lower error.
3. **Retrospective Multi-Origin Comparison vs. Original Historical Holdout:** Multi-origin evaluation is a retrospective robustness analysis across four historical 12-month horizons. The final window (September 2025 – August 2026) represents the original historical holdout; having been repeatedly inspected during benchmarking and validation, it cannot serve as untouched out-of-sample evidence for subsequent model iterations or adjustments. Any future model changes must be evaluated on genuinely new data releases or a separately justified evaluation design.

---

## 5. Operational & Reproducibility Guide

To reproduce this benchmark directly:
```bash
py -3.14 scripts/forecast_compare.py
```
Outputs print validation rankings, locked holdout metrics, and 4-origin cross-validation results. All tables in this report are generated directly from `reports/forecast_benchmark_results.json`.
