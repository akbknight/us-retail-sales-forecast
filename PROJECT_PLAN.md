# Project Plan: US Retail Sales Forecast — Production Upgrade

## Objective

Upgrade the `us-retail-sales-forecast` repository from a single-file Python script to a production-grade, modular Python package with full documentation, backtesting, diagnostics, and a clean CLI interface.

---

## Phase 1: Modularization (src/ package)

Break the monolithic `forecast.py` into purpose-specific modules with clear interfaces:

| Module | Task | Status |
|--------|------|--------|
| `src/__init__.py` | Package init, version | Done |
| `src/data/fred_client.py` | FRED fetch with retry logic | Done |
| `src/models/ets.py` | ETS(A,A,A) fitting + docstrings | Done |
| `src/models/diagnostics.py` | Residual stats, Ljung-Box, MAPE/MAE/RMSE | Done |
| `src/evaluation/backtest.py` | Walk-forward backtesting | Done |
| `src/pipeline/runner.py` | End-to-end orchestration | Done |
| `src/cli/run.py` | argparse CLI entry point | Done |
| `forecast.py` (root shim) | Backward-compatible wrapper | Done |

---

## Phase 2: Configuration

| File | Purpose | Status |
|------|---------|--------|
| `configs/app/config.yaml` | All tunable parameters in one place | Done |
| `pyproject.toml` | Packaging, dependencies, tool config | Done |
| `requirements.txt` | Pin runtime and dev dependencies | Done |
| `Makefile` | Developer shortcuts: install, run, test, lint | Done |
| `.gitignore` | Standard Python ignores | Done |

---

## Phase 3: Documentation

| File | Purpose | Status |
|------|---------|--------|
| `docs/methodology.md` | Full model spec: ETS equations, MLE, prediction intervals, alternatives considered | Done |
| `docs/architecture.md` | Data flow diagram, module responsibilities | Done |
| `docs/decision_log.md` | Rationale for horizon, series choice, model choice, start date | Done |

---

## Phase 4: Reports and EDA

| File | Purpose | Status |
|------|---------|--------|
| `reports/research_notes.md` | MARTS survey methodology, Hyndman references, M4 competition results | Done |
| `reports/eda.md` | RSXFS trend, seasonality, GFC/COVID regime changes | Done |
| `reports/forecasting_results.md` | In-sample RMSE/AIC, backtest MAPE, 18-month forecast description | Done |

---

## Phase 5: Testing

| File | Tests | Status |
|------|-------|--------|
| `tests/test_ets.py` | compute_rmse, compute_mape, compute_mae with known inputs; run_forecast key structure | Done |
| `tests/test_backtest.py` | Backtest returns dict with metrics.mape > 0; accuracy on smooth synthetic series | Done |

---

## Phase 6: README upgrade

Upgrade README.md to flagship portfolio standard:
- ★★★★★ positioning
- Live demo link
- Key results table
- Technical methodology section
- Backtesting section
- Full tech stack
- Quick start with all options

Status: Done

---

## Constraints (maintained throughout)

- `index.html` not modified — this is the GitHub Pages live dashboard
- `forecast.py` at root is a shim, not deleted — backward compatibility preserved
- `forecast_data.json` tracked in git — pre-computed for GitHub Pages static serving
