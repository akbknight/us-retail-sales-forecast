# Decision Log

Rationale for key modeling and design choices.

---

## 1. Why an 18-month forecast horizon?

**Decision:** Forecast 18 months forward.

**Rationale:** The 18-month horizon sits in a practical sweet spot for business planning:

- Shorter than 18 months (e.g., 6-month): Too narrow for annual procurement planning, inventory positioning, or capital allocation decisions.
- Longer than 18 months (e.g., 36 months): Forecast accuracy degrades significantly for seasonal ETS models beyond roughly 24 months because small slope estimation errors compound quadratically and structural breaks (recessions, policy shifts) become increasingly likely.

The 18-month horizon covers approximately 1.5 seasonal cycles, which is sufficient to capture one full holiday season (Q4) in the forecast window — the single largest demand peak in U.S. retail. This makes the forecast actionable for supply chain and demand planning teams operating on 12–18 month procurement lead times.

---

## 2. Why Holt-Winters ETS over SARIMA?

**Decision:** Use ETS(A,A,A) rather than SARIMA(p,d,q)(P,D,Q)12.

**Rationale:**

1. **Fewer parameters.** ETS(A,A,A) has 3 smoothing parameters (alpha, beta, gamma) plus initialization states. A full SARIMA(1,1,1)(1,1,1)12 has 4 autoregressive/moving-average parameters plus seasonal counterparts — greater risk of overfitting on a single series.

2. **Probabilistic justification.** ETS has a formal state-space representation (Hyndman et al., 2008) that gives clean, well-calibrated prediction intervals via the `sqrt(h)` variance growth formula. SARIMA prediction intervals require numerical simulation or asymptotic approximations that can be poorly calibrated at long horizons.

3. **Empirical performance.** In the M4 Competition (Makridakis et al., 2020), ETS models outperformed SARIMA on monthly macroeconomic series in the majority of cases as measured by scaled MAPE. The M4 dataset includes many series structurally similar to RSXFS.

4. **Interpretability.** The three state variables (level, trend, seasonal) have direct economic interpretations. Smoothing parameters quantify how quickly the model adapts to new information — relevant for communicating model behavior to business stakeholders.

SARIMA is not wrong here — it is a reasonable alternative — but ETS offers a better accuracy/complexity/interpretability tradeoff for this specific use case.

---

## 3. Why RSXFS rather than RSAFS?

**Decision:** Use RSXFS (Retail Trade + Food Services) rather than RSAFS (Retail Trade only).

**Rationale:**

- **RSXFS** includes NAICS 441–459 (retail trade) plus NAICS 722 (food services and drinking places: restaurants, bars, catering).
- **RSAFS** excludes food services.

For economic trend analysis, RSXFS is the more appropriate series because:

1. Food services account for approximately 13–15% of total retail spending and exhibit strong cyclical behavior correlated with overall consumer confidence.
2. Including food services produces a broader consumption signal that better tracks the trajectory of U.S. personal consumption expenditures (PCE), the primary driver of GDP growth.
3. RSXFS is the headline series most commonly cited in financial news and Federal Reserve communications. Forecasting the headline series maximizes the practical relevance of the output.

RSAFS would be appropriate for analysis specifically focused on goods retailing (e.g., studying inventory cycles) rather than overall consumer demand.

---

## 4. Why start the analysis window at January 2000?

**Decision:** Truncate the RSXFS historical series to begin January 1, 2000 (full series available from January 1992).

**Rationale:**

1. **Y2K disruption.** The 1998–1999 period exhibits unusual inventory stocking and spending patterns driven by Y2K preparation. Including this period introduces non-representative volatility that can bias the ETS parameter estimates.

2. **Pre-internet retail structure.** The retail industry before 2000 had fundamentally different channel structure — minimal e-commerce, different competitive dynamics, different seasonal patterns. The structural break introduced by the rise of online retail (Amazon IPO: 1997; meaningful revenue share: ~2001–2003) makes pre-2000 data of limited value for forecasting post-2020 retail trends.

3. **Sample length.** The 2000–present window provides approximately 300 monthly observations — more than sufficient for stable MLE estimation of ETS parameters and robust walk-forward backtesting.

4. **Data quality.** Census Bureau benchmark revisions in the early 2000s introduced retrospective corrections to the 1992–1999 period. Starting at 2000 avoids data quality uncertainty from those revisions.
