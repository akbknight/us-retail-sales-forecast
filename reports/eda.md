# Exploratory Data Analysis: RSXFS

## Series overview

**Series:** RSXFS — Advance Retail Sales: Retail Trade and Food Services, Seasonally Adjusted
**Publisher:** U.S. Census Bureau via FRED
**Full series span:** January 1992 – present (~400 monthly observations as of 2026)
**Analysis window:** January 2000 – present (~315 observations)
**Units:** Millions of Dollars

---

## Long-run trend

The series exhibits a clear, persistent upward trend throughout the analysis window:

- **Jan 2000:** approximately $290,000M ($290B)
- **Pre-GFC peak (Oct 2007):** approximately $407,000M ($407B)
- **Pre-COVID peak (Jan 2020):** approximately $530,000M ($530B)
- **2026 level:** approximately $750,000M ($750B)

Compound annual growth rate (CAGR) over the full 2000–2026 window: approximately 3.7% nominal per year. In real terms (deflated by CPI), the CAGR is approximately 1.5–2.0%, consistent with long-run trend U.S. real consumer spending growth.

The trend is not a smooth line — it is interrupted by two major structural breaks and exhibits post-break level shifts (not just temporary deviations).

---

## Seasonal pattern

Despite the X-13 seasonal adjustment applied by the Census Bureau, a distinct residual seasonal pattern remains in the adjusted series:

- **Peak:** November–December (Q4 holiday season). The December reading typically exceeds the surrounding months by $30–60B in the adjusted series. In the raw (unadjusted) series, the December premium exceeds $100B.
- **Trough:** January (post-holiday spending pullback, consumer credit hangover). January typically prints $20–40B below December in the adjusted series.
- **Secondary uptick:** August–September (back-to-school spending, late-summer auto sales).
- **Amplitude:** Seasonal swings in the adjusted series are approximately $50–70B in absolute dollar terms throughout the 2010s–2020s — relatively stable in absolute terms (supporting the additive seasonal specification).

---

## Notable regime changes

### 2008–2009 Global Financial Crisis

The GFC produced a prolonged decline of approximately 11% peak-to-trough in RSXFS, running from October 2007 to June 2009 (approximately 20 months). Key characteristics:

- The decline was gradual relative to COVID (not a single-month shock).
- Recovery was slow: RSXFS did not recover its pre-GFC peak until approximately mid-2011.
- The GFC decline is visible as a sustained flat/declining segment in the ETS fitted values.

### 2020 COVID-19 shock and recovery

The single most dramatic structural break in the history of the series:

- **March 2020:** -8.7% month-over-month (lockdown onset)
- **April 2020:** -19.5% month-over-month (full lockdown; historically unprecedented)
- **May 2020:** +18.5% month-over-month (partial reopening + first stimulus checks)

The V-shaped recovery was unusually rapid, driven by federal fiscal stimulus (CARES Act, Consolidated Appropriations Act, American Rescue Plan) and a shift in consumer spending from services to goods. By August 2020, RSXFS had recovered its pre-COVID level — a recovery roughly 5x faster than the post-GFC recovery.

### 2021–2022 post-pandemic surge

Stimulus-amplified demand, combined with supply constraints and reopening, produced the strongest sustained growth in RSXFS since the 1990s:

- Year-over-year growth peaked at approximately +51% in April 2021 (base effect from April 2020 collapse).
- Underlying demand (stripping the base effect) was approximately +20–25% above pre-COVID trend through mid-2021.
- This surge was partially driven by goods substitution (consumers spending stimulus on physical goods instead of services like restaurants and travel), creating a temporary goods demand supercycle.

### 2022–2023 normalization

As stimulus effects faded and the Federal Reserve raised rates aggressively (5.25 percentage points between March 2022 and July 2023), retail growth decelerated. Month-over-month readings turned volatile, with several negative months in 2022–2023. By 2024, the series had normalized to approximately 3–4% nominal annual growth — near its long-run trend.

---

## Stationarity assessment

RSXFS is non-stationary in levels (clear upward trend). First differencing (month-over-month changes) produces a roughly stationary series with mean approximately +$1.5–2.0B/month and standard deviation approximately $10–15B. An augmented Dickey-Fuller test on the first-differenced series typically rejects the unit root null (p < 0.01), confirming I(1) behavior. The ETS model handles non-stationarity implicitly via the adaptive level and trend states — no explicit differencing is required.

---

## Distribution of month-over-month changes

Approximately symmetric around a positive mean, with heavy tails due to COVID and GFC shocks. The kurtosis of monthly changes is elevated (excess kurtosis ~ 5–8) relative to a normal distribution, meaning extreme months occur more frequently than a normal distribution would predict. This fat-tailed behavior is important for interpreting prediction intervals: the ETS intervals based on Gaussian error assumptions may understate tail risk.
