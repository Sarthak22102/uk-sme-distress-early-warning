# Six-page Power BI report specification

Canvas: 1600 × 900. White background, navy #182C44, blue #1D5E86, light grey #F7F9FC. Watch amber #C28023; high review plum #8F365A. Use text labels as well as colour. Segoe UI 11–12pt body, 22–28pt KPIs. Top strip: report title, snapshot date, “Accounts-category proxy • Filing signals, not failure probability”. Left navigation consistent on every page. No red/green credit-rating metaphor.

## 1. Executive Review Overview

Question: how large is the current manual-review workload?

- KPI row: Companies Analysed, Scored Companies, High Review Companies, High Review %, Not Scored Companies.
- Left: horizontal band-count bars, with unscored displayed separately.
- Right: high-review share by primary SIC, minimum 100 scored; tooltip contains numerator and denominator.
- Bottom: score histogram with explicit zero bin, observed legal-status count table.
- Slicers: single reference date, SIC, registered-office postcode area, accounts category. Default all sectors/areas, scoreable active queue; headline analysed count must retain clear population label.
- Interactions: slicers filter all; selecting a band filters company list and workload, not sector/area benchmark bars (Edit interactions). Reset bookmark returns to all.

## 2. Sector Intelligence

Question: where are overdue-filing signals concentrated, and does sample composition matter?

- Ranked bar: high-review share by primary SIC; minimum 100 scored.
- Matrix: industry, analysed, scored, high, elevated, share, average score.
- Comparison: crude vs age-standardised shares from reports/age_standardised_sectors.csv. Use a separate disconnected comparison table; no assumption that it recomputes under slicers. Label “Full sample adjustment; fixed reference”.
- Tooltip: SIC description, both deadline counts, explicit denominator. Sector selection cross-filters company list. Company drill-through enabled.
- Statistical intervals: import sector_benchmarks.csv for a fixed full-sample interval table, explicitly unaffected by filters, or omit the table when filtering. Never attach fixed intervals to dynamically changing rates.

## 3. Geographic Intelligence

Question: which registered-office postcode areas have concentrated signals?

- Ranked area bars; matrix with counts and shares; unknown area retained separately.
- Use no choropleth: postcode areas are not ONS regions, registered-office locations can be agents, and population/area denominators were not acquired.
- Minimum 100 scored for ranking. Area selection filters sector distribution and company queue.
- Do not label counts as density or locations as company operations.

## 4. Filing Signals & Cohorts

Question: what observable filing patterns explain the workload?

- Accounts and confirmation overdue counts; both-deadlines count.
- Overdue-days scatter (accounts x, confirmation y), one point per company, capped axes clearly marked if applied.
- Filing severity matrix from SQL 06; incorporation-cohort bars using SQL 03. Label “Cross-sectional surviving-register cohorts”. Never present a cohort axis as historical risk movement.
- Outstanding-charge/status matrix from SQL 05, with note “Charges are financing context; no risk penalty”.
- Officer turnover, filing irregularity and dated charge events: unavailable in this bulk release; do not show zeros.

## 5. Company Investigation

Question: why is this company in the queue and what should an analyst verify?

- Single company search using DimCompany company_name plus company_number. Drill-through key company_number; keep all filters; Back button.
- Score, review band, status, eligibility/exclusion reason, age, primary SIC, registered-office area, accounts category.
- Waterfall: accounts_points + confirmation_points = risk_score. Do not display if unscored.
- Due-date table: accounts due, confirmation due, days overdue, last period made-up dates (these are not submission dates).
- Charge counts and peer means, withheld for small peer groups.
- Official record URL formed with company_number: https://find-and-update.company-information.service.gov.uk/company/NUMBER
- Prompt: verify current filings and extensions before drawing conclusions. No fabricated officer activity or filing timeline.

## 6. Methodology & Data Quality

Question: can this view be trusted for the intended review task?

- Import reports/quality.json or manually display verified figures from reports/data_quality.md.
- Source reference and retrieval dates, proxy definition, sample method, malformed exclusions, missing deadlines, unscored statuses.
- Score formula, weights, caps, thresholds, policy status; sensitivity workload table from reports/sensitivity.csv (fixed-sample label).
- Prominent limitations: single snapshot; no insolvency probability; no demonstrated early-warning lead time; educational/manual review only.

## Tooltip and filter contracts

Every rate includes scored denominator. Unscored is visible, not zero-filled. Primary SIC is the first supplied code, not necessarily largest revenue activity. Use dimension slicers, single-direction relationships and no implicit averages of percentages. Benchmark rankings exclude small groups without deleting those companies from overall totals.

## Native verification checklist

After building: compare all unfiltered KPIs with reports/summary.json; test one SIC and one postcode area against exported SQL counts; test one high-score, one zero-score and one unscored company; confirm waterfall additivity and leading zeros; test empty filter results; check company drill-through and Back; inspect all pages at 100%; refresh from a moved DataFolder. Save the verified PBIX yourself. This environment cannot claim these native checks were run.
