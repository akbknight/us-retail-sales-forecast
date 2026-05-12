"""
Model Diagnostics
=================
Residual analysis, Ljung-Box autocorrelation test, and point-forecast
accuracy metrics for ETS model evaluation.
"""

from __future__ import annotations

import math
from typing import Union

import numpy as np
import pandas as pd


# ---------------------------------------------------------------------------
# Residual analysis
# ---------------------------------------------------------------------------

def plot_residuals_data(residuals: Union[pd.Series, np.ndarray]) -> dict:
    """
    Compute summary statistics for model residuals suitable for plotting.

    Returns a dict (not a matplotlib figure) so the caller controls
    rendering — useful for JSON serialization and dashboard integration.

    Parameters
    ----------
    residuals : array-like
        One-step-ahead in-sample residuals from the fitted model.
        Typically ``fitted_model.resid``.

    Returns
    -------
    dict with keys:
        mean        : float — residual mean (should be ~0 for unbiased model)
        std         : float — residual standard deviation
        min         : float
        max         : float
        q25         : float — 25th percentile
        q50         : float — median
        q75         : float — 75th percentile
        skewness    : float — Pearson skewness
        kurtosis    : float — excess kurtosis (0 = normal)
        n           : int   — number of residuals
        values      : list  — residual values (for time-series plot)
        acf_lags    : list  — lag indices 1..20
        acf_values  : list  — sample ACF at each lag (for ACF bar chart)
    """
    r = np.asarray(residuals, dtype=float)
    r = r[~np.isnan(r)]
    n = len(r)
    mean = float(np.mean(r))
    std = float(np.std(r, ddof=1))
    q25, q50, q75 = float(np.percentile(r, 25)), float(np.percentile(r, 50)), float(np.percentile(r, 75))

    # Pearson skewness and excess kurtosis
    if std > 0:
        skewness = float(np.mean(((r - mean) / std) ** 3))
        kurtosis = float(np.mean(((r - mean) / std) ** 4) - 3.0)
    else:
        skewness = 0.0
        kurtosis = 0.0

    # Sample ACF up to lag 20
    max_lag = min(20, n // 2)
    acf_values = []
    for lag in range(1, max_lag + 1):
        cov = np.dot(r[lag:] - mean, r[:-lag] - mean) / n
        acf_values.append(float(cov / (std ** 2 + 1e-12)))

    return {
        "mean": round(mean, 4),
        "std": round(std, 4),
        "min": round(float(np.min(r)), 4),
        "max": round(float(np.max(r)), 4),
        "q25": round(q25, 4),
        "q50": round(q50, 4),
        "q75": round(q75, 4),
        "skewness": round(skewness, 4),
        "kurtosis": round(kurtosis, 4),
        "n": n,
        "values": [round(float(v), 4) for v in r],
        "acf_lags": list(range(1, max_lag + 1)),
        "acf_values": [round(v, 4) for v in acf_values],
    }


# ---------------------------------------------------------------------------
# Ljung-Box test
# ---------------------------------------------------------------------------

def ljung_box_test(residuals: Union[pd.Series, np.ndarray], lags: int = 12) -> dict:
    """
    Compute the Ljung-Box Q-statistic for residual autocorrelation.

    The null hypothesis is that residuals are white noise (no autocorrelation
    up to the specified number of lags). A p-value > 0.05 indicates we fail
    to reject the null — desirable for a well-specified model.

    The Q-statistic is:
        Q = n(n+2) * sum_{k=1}^{lags} [ rho_k^2 / (n-k) ]
    where rho_k is the sample ACF at lag k and n is the series length.
    Under H0, Q ~ chi-squared(lags).

    Parameters
    ----------
    residuals : array-like
        Model residuals (one-step-ahead forecast errors).
    lags : int
        Number of lags to include in the test. Typically 12 for monthly data.
        Default: 12.

    Returns
    -------
    dict with keys:
        q_statistic  : float — Ljung-Box Q value
        lags         : int   — number of lags tested
        p_value      : float — p-value under chi-squared(lags) distribution
        reject_h0    : bool  — True if p < 0.05 (significant autocorrelation)
        interpretation : str

    References
    ----------
    Ljung, G.M. & Box, G.E.P. (1978). "On a measure of lack of fit in time
    series models." Biometrika, 65(2), 297-303.
    """
    from scipy import stats as scipy_stats

    r = np.asarray(residuals, dtype=float)
    r = r[~np.isnan(r)]
    n = len(r)
    mean = np.mean(r)
    var = np.var(r, ddof=0)

    if var < 1e-12:
        return {"q_statistic": 0.0, "lags": lags, "p_value": 1.0,
                "reject_h0": False, "interpretation": "Zero-variance residuals."}

    # Compute ACF at each lag
    q = 0.0
    for k in range(1, lags + 1):
        rho_k = np.dot(r[k:] - mean, r[:-k] - mean) / (n * var)
        q += rho_k ** 2 / (n - k)
    q *= n * (n + 2)

    p_value = float(1.0 - scipy_stats.chi2.cdf(q, df=lags))
    reject = p_value < 0.05

    interpretation = (
        "Significant autocorrelation detected — model may be mis-specified."
        if reject
        else "No significant autocorrelation (p > 0.05) — residuals appear white noise."
    )

    return {
        "q_statistic": round(q, 4),
        "lags": lags,
        "p_value": round(p_value, 4),
        "reject_h0": reject,
        "interpretation": interpretation,
    }


# ---------------------------------------------------------------------------
# Accuracy metrics
# ---------------------------------------------------------------------------

def compute_mape(
    actuals: Union[pd.Series, np.ndarray],
    predictions: Union[pd.Series, np.ndarray],
) -> float:
    """
    Mean Absolute Percentage Error (MAPE).

        MAPE = 100 * mean(|actual - predicted| / |actual|)

    Parameters
    ----------
    actuals : array-like
        Observed values. Must not contain zeros (division by zero).
    predictions : array-like
        Forecast values, same length as actuals.

    Returns
    -------
    float
        MAPE as a percentage (e.g. 2.3 means 2.3%).

    Raises
    ------
    ValueError
        If any actual value is zero or arrays differ in length.
    """
    a = np.asarray(actuals, dtype=float)
    p = np.asarray(predictions, dtype=float)
    if len(a) != len(p):
        raise ValueError(f"actuals and predictions must have the same length: {len(a)} vs {len(p)}")
    if np.any(a == 0):
        raise ValueError("MAPE is undefined when actuals contain zeros.")
    return float(np.mean(np.abs((a - p) / a)) * 100)


def compute_mae(
    actuals: Union[pd.Series, np.ndarray],
    predictions: Union[pd.Series, np.ndarray],
) -> float:
    """
    Mean Absolute Error (MAE).

        MAE = mean(|actual - predicted|)

    Parameters
    ----------
    actuals : array-like
        Observed values.
    predictions : array-like
        Forecast values, same length as actuals.

    Returns
    -------
    float
        MAE in the same units as the input series.
    """
    a = np.asarray(actuals, dtype=float)
    p = np.asarray(predictions, dtype=float)
    if len(a) != len(p):
        raise ValueError(f"actuals and predictions must have the same length: {len(a)} vs {len(p)}")
    return float(np.mean(np.abs(a - p)))


def compute_rmse(
    actuals: Union[pd.Series, np.ndarray],
    predictions: Union[pd.Series, np.ndarray],
) -> float:
    """
    Root Mean Squared Error (RMSE).

        RMSE = sqrt(mean((actual - predicted)^2))

    RMSE penalizes large errors more than MAE due to the squaring.
    Expressed in the same units as the input series.

    Parameters
    ----------
    actuals : array-like
        Observed values.
    predictions : array-like
        Forecast values, same length as actuals.

    Returns
    -------
    float
        RMSE in the same units as the input series.
    """
    a = np.asarray(actuals, dtype=float)
    p = np.asarray(predictions, dtype=float)
    if len(a) != len(p):
        raise ValueError(f"actuals and predictions must have the same length: {len(a)} vs {len(p)}")
    return float(np.sqrt(np.mean((a - p) ** 2)))
