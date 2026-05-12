"""
CLI Entry Point
===============
Command-line interface for the US Retail Sales Forecast pipeline.

Usage
-----
    python -m src.cli.run
    python -m src.cli.run --series RSXFS --start 2000-01-01 --horizon 18
    python -m src.cli.run --output my_forecast.json --quiet

Or via the root shim:
    python forecast.py
"""

from __future__ import annotations

import argparse
import sys

from src.pipeline.runner import run_pipeline


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="retail-forecast",
        description=(
            "Fetch FRED retail sales data and run Holt-Winters 18-month forecast. "
            "Outputs forecast_data.json consumed by the Chart.js dashboard."
        ),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--series", default="RSXFS",
        help="FRED series ID (RSXFS = Retail Trade + Food Services; RSAFS = Retail only)"
    )
    parser.add_argument(
        "--start", default="2000-01-01",
        help="ISO start date for analysis window"
    )
    parser.add_argument(
        "--horizon", type=int, default=18,
        help="Forecast horizon in months"
    )
    parser.add_argument(
        "--holdout", type=int, default=12,
        help="Holdout months for walk-forward backtest"
    )
    parser.add_argument(
        "--output", default="forecast_data.json",
        help="Output JSON file path"
    )
    parser.add_argument(
        "--quiet", action="store_true",
        help="Suppress progress output"
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    run_pipeline(
        series_id=args.series,
        start_date=args.start,
        horizon_months=args.horizon,
        holdout_months=args.holdout,
        output_path=args.output,
        verbose=not args.quiet,
    )


if __name__ == "__main__":
    main()
