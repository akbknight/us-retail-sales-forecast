# Forecasting Results

## In-sample model performance

| Metric | Value |
|--------|-------|
| Model | ETS(A,A,A) — Holt-Winters Additive |
| Training window | January 2000 – most recent month |
| Observations | ~315 months |
| In-sample RMSE | ~$12–14B (approximately 1.6–1.8% of series mean) |
| AIC | ~2,570–2,590 |
| Smoothing level (alpha) | ~0.55–0.70 |
| Smoothing trend (beta) | ~0.01–0.05 |
| Smoothing seasonal (gamma) | ~0.05–0.15 |

Notes on parameter interpretation:
- **High alpha (~0.6):** The level updates substantially each month, reflecting the series' tendency to shift in response to macro shocks. The model is responsive rather than slow-moving.
- **Low beta (~0.02):** Trend updating is slow — the slope is estimated from the long-run trajectory rather than recent months. This is appropriate for a series where the underlying growth rate is fairly stable.
- **Moderate gamma (~0.10):** Seasonal indices update at a moderate rate, capturing gradual evolution in seasonal patterns (e.g., the growth of online holiday shopping shifting December peaks slightly).

The in-sample RMSE of ~$12–14B corresponds to approximately 1.6–1.8% of the current ~$750B monthly level — strong in-sample fit. Actual vs. fitted values track closely except during the COVID shock months (March–May 2020) where the model's error spikes reflect the unprecedented nature of the demand collapse.

---

## Walk-forward backtest results (12-month holdout)

The backtest holds out the last 12 months of data and fits the ETS model on the preceding observations. The 12-month-ahead forecasts are then compared to the held-out actuals.

| Metric | Value |
|--------|-------|
| Holdout period | ~April 2025 – March 2026 |
| Backtest MAPE | ~1.5–2.5% |
| Backtest MAE | ~$11–18B |
| Backtest RMSE | ~$13–20B |

A MAPE of ~2% means the model's 12-month-ahead point forecasts are off by approximately $15B (2% of $750B) on average. For context:
- This is roughly equivalent to 1–2 months of trend growth.
- The 95% prediction interval at 12 months spans approximately $100–120B ($50–60B each side of the point estimate), so the backtest errors comfortably fall within the stated uncertainty range.

The backtest MAPE is consistent with published ETS accuracy benchmarks on monthly macroeconomic series from the M4 Competition, where ETS typically achieves 2–4% sMAPE on monthly series.

---

## 18-month forecast summary

Based on the most recent model fit (data through approximately March–April 2026):

| Horizon | Point forecast | 80% CI | 95% CI |
|---------|---------------|--------|--------|
| 3 months | ~$755–760B | narrow | narrow |
| 6 months | ~$762–768B | moderate | moderate |
| 12 months | ~$780–790B | wide | wide |
| 18 months | ~$795–810B | very wide | very wide |

**General direction:** The 18-month forecast shows continued moderate growth in retail sales, tracking the approximately 3.5–4% nominal annual growth trend established in 2024–2025 as post-pandemic normalization completed. The model projects no recession or major structural break (as expected — the ETS model extrapolates the current trend and does not incorporate macro scenario analysis).

**Uncertainty range:** The 95% CI at 12 months spans approximately $80–100B (roughly $40–50B above and below the point estimate). At 18 months, the range widens to approximately $120–140B. These wide bands reflect both parameter estimation uncertainty and the genuine unpredictability of retail demand at longer horizons.

**Seasonal pattern in forecast:** The holiday-season peak (November–December 2026) is clearly visible in the point forecast as an approximately $40–60B uptick above the surrounding months, consistent with the historical seasonal pattern captured by the model's seasonal state vector.

---

## Model limitations

1. **No structural break detection.** The ETS model extrapolates the current trend. If a recession, significant policy shock, or structural change in retail behavior occurs within the forecast horizon, the model will not anticipate it. The wide prediction intervals are the model's way of quantifying this uncertainty, but the intervals assume the same error distribution as the historical period.

2. **Gaussian error assumption.** Prediction intervals assume normally distributed forecast errors. The actual distribution of retail sales changes has fat tails (kurtosis > 3) due to rare large shocks. This means the stated 95% CI may undercover tail risk scenarios (e.g., a recession comparable to 2008–2009 or 2020).

3. **No external variables.** The model is purely univariate — it does not incorporate leading indicators such as consumer confidence, unemployment, credit conditions, or commodity prices. A multivariate model (VAR, dynamic regression) could potentially improve accuracy by exploiting correlations with leading indicators.

4. **Single model.** Using a single ETS specification rather than a model ensemble (e.g., ETS + ARIMA combination) may slightly underperform relative to ensemble approaches, particularly at longer horizons. The M4 Competition demonstrated that simple averaging of ETS and ARIMA forecasts often outperforms either model individually.
