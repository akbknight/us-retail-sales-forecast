"""
Holt-Winters ETS Model
======================
Fits an ETS(A,A,A) — Error: Additive, Trend: Additive, Seasonal: Additive —
state-space model to a monthly time series and generates probabilistic forecasts.

Model specification
-------------------
ETS(A,A,A) is the additive Holt-Winters model. The state equations are:

    Level:    l_t = alpha * (y_t - s_{t-m}) + (1 - alpha) * (l_{t-1} + b_{t-1})
    Trend:    b_t = beta  * (l_t - l_{t-1}) + (1 - beta)  * b_{t-1}
    Seasonal: s_t = gamma * (y_t - l_{t-1} - b_{t-1}) + (1 - gamma) * s_{t-m}

where:
    y_t  — observed value at time t
    l_t  — level component
    b_t  — trend (slope) component
    s_t  — seasonal component
    m    — number of seasons per year (12 for monthly data)
    alpha — level smoothing parameter (0 < alpha < 1)
    beta  — trend smoothing parameter (0 < beta < 1)
    gamma — seasonal smoothing parameter (0 < gamma < 1)

The h-step-ahead point forecast is:
    y_hat_{t+h} = l_t + h * b_t + s_{t+h-m}

Why additive (not multiplicative)?
------------------------------------
Retail sales (RSXFS) exhibits roughly *stable* seasonal amplitude relative to
the trend level — the November/December holiday peak adds a roughly constant
dollar amount above the trend each year, rather than a constant *percentage*.
This makes the additive specification appropriate. A multiplicative seasonal
model would be better if the seasonal swings grew proportionally with the
series level.

Parameter estimation
--------------------
Parameters (alpha, beta, gamma, initial level, initial trend, initial seasonal
states) are estimated jointly by **maximum likelihood estimation (MLE)**,
maximizing the Gaussian log-likelihood of the one-step-ahead forecast errors.
The statsmodels `ExponentialSmoothing.fit(optimized=True)` call runs numerical
optimization (L-BFGS-B) over the parameter space.

Model selection
---------------
**AIC** (Akaike Information Criterion) is used for model comparison:
    AIC = -2 * log(L) + 2 * k
where L is the maximized likelihood and k is the number of estimated
parameters. Lower AIC indicates a better bias-variance tradeoff.

Prediction intervals
--------------------
Following Hyndman et al. (2008) "Forecasting with Exponential Smoothing:
The State Space Approach", the variance of the h-step-ahead forecast error
grows approximately as:
    Var(e_{t+h}) ≈ sigma^2 * h
so the standard deviation scales as sigma * sqrt(h), where sigma is the
residual standard deviation from the fitted model. The (1-alpha)*100%
prediction interval is:
    y_hat_{t+h} +/- z_{alpha/2} * sigma * sqrt(h)

For 95% CI: z = 1.96; for 80% CI: z = 1.28.

References
----------
- Hyndman, R.J. & Athanasopoulos, G. (2021). *Forecasting: Principles and
  Practice*, 3rd ed. OTexts. https://otexts.com/fpp3/
- Hyndman, R.J., Koehler, A.B., Ord, J.K., Snyder, R.D. (2008).
  *Forecasting with Exponential Smoothing: The State Space Approach*.
  Springer.
"""

from __future__ import annotations

from typing import Optional

import numpy as np
import pandas as pd
from statsmodels.tsa.holtwinters import ExponentialSmoothing, HoltWintersResultsWrapper


def fit_ets(
    series: pd.Series,
    trend: str = "add",
    seasonal: str = "add",
    seasonal_periods: int = 12,
    initialization_method: str = "estimated",
) -> HoltWintersResultsWrapper:
    """
    Fit a Holt-Winters ETS model to a time series via MLE.

    Parameters
    ----------
    series : pd.Series
        Monthly time series with DatetimeIndex. Values in any consistent units.
    trend : str
        Trend component type. ``"add"`` (additive) or ``"mul"`` (multiplicative).
        Default: ``"add"``.
    seasonal : str
        Seasonal component type. ``"add"`` or ``"mul"``. Default: ``"add"``.
    seasonal_periods : int
        Number of periods in a seasonal cycle. 12 for monthly data. Default: 12.
    initialization_method : str
        How to initialize state parameters. ``"estimated"`` estimates them via
        MLE along with the smoothing parameters. Default: ``"estimated"``.

    Returns
    -------
    HoltWintersResultsWrapper
        Fitted model object with attributes: ``.params``, ``.aic``, ``.resid``,
        ``.fittedvalues``, ``.forecast()``.

    Raises
    ------
    ValueError
        If ``series`` has fewer than ``2 * seasonal_periods`` observations
        (minimum required for ETS initialization).
    """
    min_obs = 2 * seasonal_periods
    if len(series) < min_obs:
        raise ValueError(
            f"Series too short: need at least {min_obs} observations for "
            f"seasonal_periods={seasonal_periods}; got {len(series)}."
        )

    model = ExponentialSmoothing(
        series,
        trend=trend,
        seasonal=seasonal,
        seasonal_periods=seasonal_periods,
        initialization_method=initialization_method,
    )
    return model.fit(optimized=True)


def run_forecast(
    series: pd.Series,
    n: int = 18,
    ci_levels: Optional[list[float]] = None,
) -> dict:
    """
    Fit ETS(A,A,A) and generate an n-step probabilistic forecast.

    Parameters
    ----------
    series : pd.Series
        Monthly historical series (DatetimeIndex, freq='MS').
    n : int
        Forecast horizon in months. Default: 18.
    ci_levels : list of float, optional
        Confidence levels for prediction intervals, e.g. [0.80, 0.95].
        Default: [0.80, 0.95].

    Returns
    -------
    dict with keys:
        fitted_model    : HoltWintersResultsWrapper
        forecast        : pd.Series — point forecasts (length n)
        forecast_index  : pd.DatetimeIndex — forecast dates
        residual_std    : float — residual std dev (sigma)
        horizon_factors : np.ndarray — sqrt(1..n) for CI scaling
        ci              : dict mapping level -> {"upper": list, "lower": list}
    """
    if ci_levels is None:
        ci_levels = [0.80, 0.95]

    fitted = fit_ets(series)
    forecast = fitted.forecast(n)
    forecast_index = pd.date_range(
        start=series.index[-1] + pd.DateOffset(months=1),
        periods=n,
        freq="MS",
    )

    residual_std = float(np.std(fitted.resid))
    horizon_factors = np.sqrt(np.arange(1, n + 1))

    # Compute prediction intervals for each requested CI level
    from scipy import stats as scipy_stats

    ci = {}
    for level in ci_levels:
        z = float(scipy_stats.norm.ppf(0.5 + level / 2))
        margin = z * residual_std * horizon_factors
        ci[level] = {
            "upper": (forecast.values + margin).tolist(),
            "lower": (forecast.values - margin).tolist(),
        }

    return {
        "fitted_model": fitted,
        "forecast": forecast,
        "forecast_index": forecast_index,
        "residual_std": residual_std,
        "horizon_factors": horizon_factors,
        "ci": ci,
    }
