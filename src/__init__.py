"""
us-retail-sales-forecast
========================
Production-grade US retail sales demand forecasting package.

Modules:
    src.data.fred_client   — FRED API data fetching with retry logic
    src.models.ets         — Holt-Winters ETS model fitting
    src.models.diagnostics — Residual diagnostics and accuracy metrics
    src.evaluation.backtest — Walk-forward backtesting
    src.pipeline.runner    — End-to-end orchestration
    src.cli.run            — Command-line entry point
"""

__version__ = "1.0.0"
__author__ = "Akshay Kumar"
