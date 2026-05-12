# Research Notes

## U.S. Census Bureau retail survey methodology

The Advance Monthly Retail Trade Survey (MARTS) is the primary source of RSXFS data. Key methodological details:

- **Sample:** Approximately 5,500 retail and food service firms selected via probability proportional to size (PPS) sampling. Larger firms are sampled with certainty; smaller firms are sampled at rates proportional to their estimated sales volume.
- **Coverage:** All establishments classified under NAICS retail trade (441–459) and food services (722).
- **Collection method:** Electronic and mail questionnaires; Census Bureau follows up non-respondents by phone.
- **Publication timing:** Released approximately 12 days after the reference month ends (hence "advance" — a preliminary estimate revised in subsequent months). The advance estimate is revised twice: once in the following month's advance release, and again in the Annual Retail Trade Survey.
- **Revision magnitude:** Advance-to-final revisions average approximately 0.2–0.4 percentage points in month-over-month growth rate terms.

Reference: https://www.census.gov/retail/marts/about_the_surveys.html

---

## ETS forecasting literature

### Primary reference

**Hyndman, R.J. & Athanasopoulos, G. (2021). *Forecasting: Principles and Practice*, 3rd ed.**
OTexts: Melbourne, Australia. https://otexts.com/fpp3/

This is the definitive free online textbook for applied time-series forecasting. Chapter 8 covers exponential smoothing comprehensively, including ETS state-space models, MLE parameter estimation, and prediction interval derivation. The R `forecast` and `fable` packages implement the methods described. Chapter 9 covers ARIMA for comparison.

### State-space formulation

**Hyndman, R.J., Koehler, A.B., Ord, J.K., Snyder, R.D. (2008). *Forecasting with Exponential Smoothing: The State Space Approach*. Springer.**

The theoretical foundation for ETS models as formal state-space systems. Derives prediction interval formulas and establishes conditions for model admissibility. The `sqrt(h)` variance growth formula used in this project comes from this work.

---

## M4 Competition results

**Makridakis, S., Spiliotis, E., Assimakopoulos, V. (2020). "The M4 Competition: 100,000 time series and 61 forecasting methods." *International Journal of Forecasting*, 36(1), 54-74.**

Key findings relevant to this project:

- The M4 Competition evaluated 61 forecasting methods on 100,000 time series across multiple frequencies and domains.
- For **monthly** series in the **macro/economic** category (most similar to RSXFS), ETS methods achieved lower scaled MAE (sMAPE and MASE) than ARIMA/SARIMA in the majority of cases.
- The top-performing methods were ensemble approaches (Theta, combination forecasts), but ETS as a standalone model ranked in the upper quartile.
- Neural network models (LSTM, etc.) did not outperform ETS on monthly macroeconomic series in M4 — the simplicity of ETS is a feature, not a bug, for well-behaved economic time series.
- **Implication for this project:** ETS(A,A,A) is an empirically validated choice for monthly retail sales forecasting, not merely a textbook example.

---

## Retail sales economic context

### RSXFS as a GDP leading indicator

U.S. retail and food services sales represent approximately 30–35% of personal consumption expenditures (PCE) in the national accounts. PCE itself accounts for approximately 68–70% of U.S. GDP. Therefore, RSXFS is one of the highest-frequency, most timely indicators of the dominant driver of U.S. economic growth.

The Federal Open Market Committee (FOMC) monitors retail sales releases closely when assessing consumer spending momentum. Month-over-month changes of more than +/-0.3% in core retail sales (excluding autos and gas) typically generate meaningful financial market reactions.

### COVID-19 structural break

The April 2020 COVID-19 shock produced the largest single-month decline in RSXFS in the history of the modern survey: approximately -19% month-over-month. The subsequent recovery, amplified by federal stimulus payments (CARES Act: $1,200/person March 2020; American Rescue Plan: $1,400/person March 2021), produced a +20% YoY surge in April–May 2021.

This creates a significant base-effect distortion in year-over-year growth rates for 2020–2021. The ETS model handles the COVID shock by updating its level parameter aggressively (high alpha) in response to the outlier. Whether to treat COVID months as outliers (and adjust them out) is a modeling judgment call; this project uses the raw adjusted data.

### Seasonal patterns in RSXFS

The largest seasonal peak in seasonally-adjusted RSXFS occurs in November–December (Q4 holiday season). Even after X-13 seasonal adjustment, a residual December-over-November pattern typically remains. The January dip (post-holiday spending pullback) is the largest seasonal trough. Back-to-school spending in August produces a secondary seasonal uptick in non-durable goods and clothing retail.

### Long-run trend

From January 2000 to early 2026, RSXFS grew from approximately $290B/month to approximately $750B/month — roughly a 2.6x increase in nominal terms over 25 years, or approximately 3.9% compound annual growth. In real (inflation-adjusted) terms, the growth rate is closer to 1.5–2.0% annually, broadly consistent with long-run real U.S. GDP growth.
