.PHONY: install run backtest test lint clean help

# Default target
help:
	@echo "US Retail Sales Forecast — available targets:"
	@echo "  make install   Install Python dependencies"
	@echo "  make run       Fetch FRED data and run 18-month forecast"
	@echo "  make backtest  Run walk-forward backtest only"
	@echo "  make test      Run pytest test suite"
	@echo "  make lint      Lint with ruff"
	@echo "  make clean     Remove __pycache__ and .pytest_cache"

install:
	pip install -r requirements.txt

run:
	python forecast.py

backtest:
	python -c "from src.data.fred_client import fetch_fred_series; \
	           from src.evaluation.backtest import run_backtest; \
	           import json; \
	           s = fetch_fred_series('RSXFS', start_date='2000-01-01'); \
	           r = run_backtest(s, holdout_months=12); \
	           print('Backtest MAPE:', r['metrics']['mape'], '%'); \
	           print('Backtest RMSE:', r['metrics']['rmse'], 'M USD'); \
	           print('Backtest MAE: ', r['metrics']['mae'],  'M USD')"

test:
	python -m pytest tests/ -v

lint:
	ruff check src/ tests/ forecast.py

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true
