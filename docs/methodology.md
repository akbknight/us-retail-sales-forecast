# Methodology

## Dataset: RSXFS

**Series:** RSXFS — Advance Retail Sales: Retail Trade and Food Services
**Publisher:** U.S. Census Bureau, distributed via FRED (Federal Reserve Bank of St. Louis)
**Frequency:** Monthly (Month Start, MS)
**Units:** Millions of Dollars, Seasonally Adjusted
**Coverage:** January 1992 to present

### Survey design

RSXFS is derived from the Advance Monthly Retail Trade Survey (MARTS), a probability-based sample survey of approximately 5,500 retail and food service firms in the United States. The Census Bureau stratifies the sample by industry and firm size. Estimates are published approximately 12 days after the reference month ends, making it one of the fastest high-frequency economic releases in the U.S. statistical system.

The series covers all retail trade sectors (NAICS 441–459) plus food services and drinking places (NAICS 722). This makes RSXFS broader than RSAFS (which excludes food services) and a better proxy for total consumer spending in the goods-and-services economy.

### Seasonal adjustment

The Census Bureau applies X-13ARIMA-SEATS to produce seasonally adjusted figures. X-13 is the U.S. government's official seasonal adjustment software, which combines ARIMA model-based signal extraction with SEATS (Signal Extraction in ARIMA Time Series). Seasonal factors are revised annually. All values used in this project are seasonally adjusted — meaning the regular holiday-season and summer patterns have already been removed from the raw data. The Holt-Winters model then re-captures the residual seasonality that remains after X-13 adjustment, which corresponds to within-year cyclical patterns still present in the adjusted series.

---

## Model: ETS(A,A,A)

ETS(A,A,A) is the fully additive Holt-Winters model — additive error, additive trend, additive seasonality.

### State equations

At each time step t, the model maintains three state variables:

**Level (l_t):**
```
l_t = alpha * (y_t - s_{t-m}) + (1 - alpha) * (l_{t-1} + b_{t-1})
```

**Trend / slope (b_t):**
```
b_t = beta * (l_t - l_{t-1}) + (1 - beta) * b_{t-1}
```

**Seasonal index (s_t):**
```
s_t = gamma * (y_t - l_{t-1} - b_{t-1}) + (1 - gamma) * s_{t-m}
```

Where:
- `y_t` — observed value at time t
- `m = 12` — number of periods per seasonal cycle (monthly data)
- `alpha` — level smoothing weight (0 < alpha < 1)
- `beta` — trend smoothing weight (0 < beta < 1)
- `gamma` — seasonal smoothing weight (0 < gamma < 1)

### h-step-ahead point forecast

```
y_hat_{t+h|t} = l_t + h * b_t + s_{t + h - m * ceil(h/m)}
```

The forecast extrapolates the current level, adds h multiples of the current slope, and adds the seasonal index for the corresponding month.

### Why additive vs. multiplicative?

The multiplicative specification would model seasonal swings as proportional to the level — i.e., a 10% seasonal peak every December. The additive specification models seasonal swings as fixed dollar amounts above the trend.

For RSXFS, the December holiday peak adds roughly $50–70B above the monthly trend in most years. This amount has been relatively stable in absolute dollar terms across the 2000–2026 sample (even as the trend level doubled), making the additive specification the better fit. A multiplicative seasonal model would over-predict the seasonal amplitude in recent years and under-predict it in earlier years.

---

## Parameter estimation

All model parameters — alpha, beta, gamma, initial level, initial trend, and 12 initial seasonal indices — are estimated simultaneously by **maximum likelihood estimation (MLE)**. The log-likelihood under the assumed Gaussian error distribution is:

```
log L = -n/2 * log(2*pi) - n/2 * log(sigma^2) - 1/(2*sigma^2) * sum(e_t^2)
```

where `e_t = y_t - y_hat_{t|t-1}` are the one-step-ahead forecast errors. The statsmodels `ExponentialSmoothing.fit(optimized=True)` call maximizes this via L-BFGS-B numerical optimization with box constraints (0 < alpha, beta, gamma < 1).

---

## Model selection: AIC

When comparing multiple candidate models (e.g., ETS vs. SARIMA, different initialization methods), the **Akaike Information Criterion** is used:

```
AIC = -2 * log(L_hat) + 2 * k
```

Where `L_hat` is the maximized log-likelihood and `k` is the number of free parameters. AIC balances goodness-of-fit against model complexity — lower is better. For ETS(A,A,A) with estimated initialization, k = 3 (smoothing params) + 1 (sigma) + 1 (level) + 1 (trend) + 12 (seasonal states) = 18.

---

## Prediction intervals

Following Hyndman, Koehler, Ord & Snyder (2008), the variance of the h-step-ahead forecast error for ETS(A,A,A) grows approximately as:

```
Var(e_{t+h}) ≈ sigma^2 * h
```

where sigma is the in-sample residual standard deviation. This gives the standard deviation of the forecast error as `sigma * sqrt(h)`, so prediction intervals are:

```
y_hat_{t+h} +/- z_{alpha/2} * sigma * sqrt(h)
```

For 95% CI: z = 1.96. For 80% CI: z = 1.28.

The sqrt(h) scaling reflects increasing uncertainty at longer horizons — each additional month compounds parameter estimation uncertainty and structural uncertainty.

---

## Walk-forward backtesting

### Design

The last 12 months of the series are held out as the test set. The ETS model is fit on the remaining observations (training set). The fitted model generates 12 one-step-through-12-step-ahead forecasts. These are compared to the held-out actuals.

### Why walk-forward?

Walk-forward backtesting simulates the actual forecasting scenario — the model never sees future data during training. Simple in-sample metrics (RMSE on fitted values) are optimistic because the model was fit on those same observations. Backtesting provides an honest estimate of out-of-sample accuracy.

### Metrics

| Metric | Formula | Interpretation |
|--------|---------|----------------|
| MAPE | 100 * mean(\|actual - pred\| / \|actual\|) | Percentage error, scale-free |
| MAE  | mean(\|actual - pred\|) | Average absolute error in millions USD |
| RMSE | sqrt(mean((actual - pred)^2)) | Penalizes large errors; same units as series |

---

## Alternative models considered

**SARIMA(1,1,1)(1,1,1)12:** A valid alternative. SARIMA with seasonal differencing can capture the stochastic seasonal pattern. However, ETS has fewer parameters to tune (3 vs. up to 8 in SARIMA), has a clearer probabilistic (state-space) interpretation, and performed comparably or better on monthly retail series in the M3 and M4 forecasting competitions. SARIMA also requires stationarity checks and careful lag selection.

**Simple exponential smoothing (SES):** Too restrictive — SES models only the level (no trend, no seasonality). Given the clear upward trend and seasonal pattern in RSXFS, SES would produce systematically biased forecasts at any horizon beyond a few months.

**Facebook Prophet:** A Bayesian structural time series model with flexible seasonality and changepoint detection. Useful for irregular or complex seasonal patterns. For RSXFS — a well-behaved monthly series with simple annual seasonality — ETS achieves comparable accuracy with far fewer dependencies and greater interpretability.

---

## References

1. Hyndman, R.J. & Athanasopoulos, G. (2021). *Forecasting: Principles and Practice*, 3rd ed. OTexts. https://otexts.com/fpp3/
2. Hyndman, R.J., Koehler, A.B., Ord, J.K., Snyder, R.D. (2008). *Forecasting with Exponential Smoothing: The State Space Approach*. Springer.
3. Makridakis, S., Spiliotis, E., Assimakopoulos, V. (2020). "The M4 Competition: 100,000 time series and 61 forecasting methods." *International Journal of Forecasting*, 36(1), 54-74.
4. U.S. Census Bureau. "Advance Monthly Retail Trade Survey." https://www.census.gov/retail/index.html
