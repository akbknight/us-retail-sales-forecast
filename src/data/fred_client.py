"""
FRED Data Client
================
Fetches time-series data from the Federal Reserve Bank of St. Louis (FRED)
public CSV endpoint. No API key required.

Series documented here:
    RSXFS — Advance Retail Sales: Retail Trade and Food Services
    - Published by: U.S. Census Bureau, via FRED
    - Frequency:    Monthly (Month Start, MS)
    - Units:        Millions of Dollars, Seasonally Adjusted
    - Coverage:     January 1992 – present
    - Description:  Monthly survey of approximately 5,000+ retail firms.
                    Covers retail trade AND food services (broader than RSAFS).
                    Seasonally adjusted using the X-13ARIMA-SEATS method.
                    A key leading indicator of U.S. consumer spending (~70% of GDP).
    - FRED URL:     https://fred.stlouisfed.org/series/RSXFS
"""

from __future__ import annotations

import io
import time
import urllib.error
import urllib.request
import warnings
from typing import Optional

import pandas as pd

FRED_BASE_URL = "https://fred.stlouisfed.org/graph/fredgraph.csv"
DEFAULT_SERIES = "RSXFS"
DEFAULT_START = "2000-01-01"
MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 2.0


def fetch_fred_series(
    series_id: str = DEFAULT_SERIES,
    start_date: Optional[str] = DEFAULT_START,
    retries: int = MAX_RETRIES,
) -> pd.Series:
    """
    Download a FRED time series as a monthly pandas Series.

    Fetches from the FRED public CSV endpoint with exponential-backoff retry
    logic (up to ``retries`` attempts). The returned Series has a DatetimeIndex
    with monthly frequency (MS — Month Start).

    Parameters
    ----------
    series_id : str
        FRED series identifier, e.g. ``"RSXFS"`` or ``"RSAFS"``.
        Default: ``"RSXFS"`` (Advance Retail Sales: Retail Trade and Food Services).
    start_date : str or None
        ISO-format start date for filtering, e.g. ``"2000-01-01"``.
        Pass ``None`` to return the full series from FRED.
    retries : int
        Number of fetch attempts before raising. Default: 3.

    Returns
    -------
    pd.Series
        Monthly retail sales values in millions of dollars, indexed by date.
        Index dtype: DatetimeIndex (freq='MS').
        Values dtype: float64.

    Raises
    ------
    RuntimeError
        If all retry attempts fail.

    Examples
    --------
    >>> series = fetch_fred_series("RSXFS", start_date="2015-01-01")
    >>> series.head()
    date
    2015-01-01    430179.0
    2015-02-01    431952.0
    ...
    """
    url = f"{FRED_BASE_URL}?id={series_id}"
    last_exc: Optional[Exception] = None

    for attempt in range(1, retries + 1):
        try:
            with urllib.request.urlopen(url, timeout=30) as resp:
                raw = resp.read().decode("utf-8")
            break
        except (urllib.error.URLError, OSError) as exc:
            last_exc = exc
            if attempt < retries:
                wait = RETRY_DELAY_SECONDS * (2 ** (attempt - 1))
                warnings.warn(
                    f"FRED fetch attempt {attempt}/{retries} failed: {exc}. "
                    f"Retrying in {wait:.0f}s..."
                )
                time.sleep(wait)
    else:
        raise RuntimeError(
            f"Failed to fetch FRED series '{series_id}' after {retries} attempts. "
            f"Last error: {last_exc}"
        )

    df = pd.read_csv(
        io.StringIO(raw),
        parse_dates=["observation_date"],
    )
    df.columns = ["date", "value"]
    df = df.set_index("date").sort_index()

    # Drop missing / sentinel values (FRED uses '.' for missing)
    series = pd.to_numeric(df["value"], errors="coerce").dropna()
    series.index = pd.DatetimeIndex(series.index, freq="MS")

    if start_date is not None:
        series = series[start_date:]

    return series
