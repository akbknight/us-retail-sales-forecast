"""
forecast.py — Compatibility shim
=================================
This root-level script exists for backward compatibility and quick usage.
The full modular implementation lives in src/.

    src/data/fred_client.py   — FRED data fetching with retry logic
    src/models/ets.py         — Holt-Winters ETS(A,A,A) fitting
    src/models/diagnostics.py — Residual diagnostics and accuracy metrics
    src/evaluation/backtest.py — Walk-forward backtesting
    src/pipeline/runner.py    — End-to-end orchestration
    src/cli/run.py            — CLI entry point

Usage (unchanged from v0):
    pip install -r requirements.txt
    python forecast.py
    python forecast.py --series RSXFS --start 2000-01-01 --horizon 18

For the full CLI with all options:
    python -m src.cli.run --help

Output: forecast_data.json (consumed by index.html dashboard)
"""

from src.cli.run import main

if __name__ == "__main__":
    main()
