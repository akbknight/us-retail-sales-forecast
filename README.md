# US Retail Sales Demand Forecast

18-month forward forecast for US Retail & Food Services Sales using Holt-Winters triple exponential smoothing on real Federal Reserve data. Live dashboard at [akbknight.github.io/us-retail-sales-forecast](https://akbknight.github.io/us-retail-sales-forecast/).

## What this project does

This project applies statistical time-series forecasting to US monthly retail sales data (FRED series RSAFS) to project 18 months of demand with quantified uncertainty. The forecast answers a concrete business question: given the current trajectory of consumer spending, what is the most likely retail market size through the end of 2027, and how wide is the uncertainty band?

The model fits Holt-Winters triple exponential smoothing to 135 months of seasonally adjusted data (Jan 2015–Mar 2026), then projects forward with horizon-scaled 80% and 95% predictive intervals. The interactive dashboard shows historical data, model fit quality, the 18-month forecast, and year-over-year growth rates — including the COVID-19 demand shock (−19.7% YoY in April 2020) and the subsequent stimulus-driven recovery (+51.9% YoY in April 2021).

## Key results

| Metric | Value |
|---|---|
| Latest actual (Mar 2026) | $752.1B |
| 12-month forecast (Mar 2027) | $789.2B |
| Projected change | +4.9% |
| 95% confidence interval at 12m | $705B – $873B |
| In-sample RMSE | $12.4B (1.65% of mean) |
| Model AIC | 2,577 |

## Advanced analytics features

- **Demand forecasting:** 18-month horizon with Holt-Winters additive trend + seasonal model
- **Uncertainty quantification:** horizon-scaled predictive intervals (80% and 95%) derived from residual standard deviation
- **Scenario context:** annotated COVID-19 shock and base-effect recovery in the YoY chart
- **Model validation:** in-sample fit quality chart (actual vs. fitted) with RMSE and AIC reporting
- **Business interpretation:** point estimate and confidence range framed for procurement, inventory, and planning decisions

## Tech stack

| Layer | Technology |
|---|---|
| Data | FRED API / RSAFS series |
| Analysis | Python 3, statsmodels, pandas, numpy |
| Dashboard | Chart.js 4, plain HTML/CSS/JS |
| Deployment | GitHub Pages |

## How to run

```bash
# Clone the repository
git clone https://github.com/akbknight/us-retail-sales-forecast.git
cd us-retail-sales-forecast

# Install dependencies
pip install pandas statsmodels

# Fetch fresh FRED data and regenerate forecast
python forecast.py
# Outputs: forecast_data.json

# Open the dashboard
# Simply open index.html in a browser — no build step required
```

**Requirements:** Python 3.9+. No API key needed — the script fetches public CSV data from `fred.stlouisfed.org`.

## Data source

**Federal Reserve Bank of St. Louis (FRED)**
Series: RSAFS — Advance Retail and Food Services Sales, Not Adjusted for Inflation
URL: https://fred.stlouisfed.org/series/RSAFS
License: Public domain. FRED data is free and open to the public.

## Methodology

The Holt-Winters model (also called triple exponential smoothing) is appropriate for this data because retail sales exhibits:
- A clear long-run upward trend
- Strong annual seasonality (Q4 holiday peak)
- Level shifts driven by macro shocks (COVID-19, stimulus)

Parameters (α, β, γ) are estimated by maximum likelihood optimization. Predictive intervals scale with √h where h is the forecast horizon, reflecting increasing uncertainty at longer horizons. The 95% CI at 12 months spans $705B–$873B — a range wide enough to capture plausible downside scenarios while the central estimate of $789B represents the model's best single-number projection.

## Skills demonstrated

- **Time-series forecasting:** Holt-Winters ETS model, parameter optimization, in-sample diagnostics
- **Uncertainty quantification:** horizon-scaled predictive intervals, 80% and 95% coverage
- **Business analytics:** translating a statistical forecast into procurement and market-sizing language
- **Data visualization:** Chart.js multi-dataset overlay with confidence bands, annotation overlays, dark/light mode
- **Reproducible analysis:** clean Python script that fetches fresh data on every run

## Author

**Akshay Kumar**
[linkedin.com/in/akshaykumardl](https://www.linkedin.com/in/akshaykumardl/)
