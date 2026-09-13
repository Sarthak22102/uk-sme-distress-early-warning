# Portfolio material — evidence-based wording

## GitHub repository description
Python/SQL platform analysing UK company filing signals, with transparent review scoring, validated pipelines and a six-page Power BI build pack.

## Three CV bullets

- Built a reproducible Python and SQL pipeline scanning 5,689,368 Companies House records and sampling 30,000 companies into a nine-table analytical model, with source checksums and explicit malformed-row handling.
- Engineered an interpretable filing-review index for 26,785 active companies, identifying 66 high-priority review records and validating score calculations independently in SQL.
- Developed seven analytical SQL queries and a six-page Power BI build pack with DAX, Power Query, sector/geographic benchmarks and sensitivity analysis, documenting the limits of cross-sectional distress indicators.

## LinkedIn project description

I built the UK SME Distress Early-Warning Platform to explore what public company data can—and cannot—tell us about business risk. The Python/SQL pipeline scans official Companies House data and analyses a reproducible sample of 30,000 companies. It includes a relational analytical model, explicit data-quality checks, an interpretable filing-review score, sector and registered-office-area comparisons, and a six-page Power BI build pack.

A key finding was the clustering of filing delays: confirmation deadlines were overdue for 38.00% of companies with an accounts delay, compared with 3.77% without one. I treated this as an observational filing pattern, not evidence that the platform predicts insolvency. The project includes source provenance, reproducible SQL, sensitivity checks and documented limitations.

## Tell me about this project

“I wanted to understand whether public registry data could help an analyst prioritise companies for further review. I processed the official Companies House snapshot and built a reproducible 30,000-company sample using an explicit SME proxy. I created a SQL data model and a transparent score based on overdue filing deadlines, with company-level explanations and a Power BI build pack. The most important judgement was avoiding an unsupported prediction claim: one snapshot cannot prove early-warning performance, and dissolution is not the same as financial distress. I validated the pipeline, found clustered filing delays and showed how policy choices change the review queue.”

## Technical interview talking points

- **Architecture:** chunked ZIP ingestion → row audit and seeded hash sample → typed Python cleaning → nine SQLite tables → features and policy score → SQL comparisons → validated CSV exports and Power BI design.
- **Sampling:** all source partitions are alphabetical, so a first-file sample would be biased. Bottom-k SHA256 makes selection deterministic and independent of ordering. Explain the restricted proxy frame and why it is not representative of all UK SMEs.
- **SQL:** joins preserve company/date grain; CTEs define valid denominators; window functions add peer means, percentiles and ranks. Cohort queries use LAG and pooled windows but are explicitly cross-sectional. Historical transition SQL returns unknown with one snapshot.
- **Python:** modules separate acquisition, cleaning, feature engineering, scoring and analysis. Missing dates stay missing; legitimate future deadlines are not errors. Checksum verification and fail-fast constraints protect reproducibility.
- **Methodology:** capped 60/40 filing-delay weights are an explicit review policy. Status is a separate queue. The score is not trained, calibrated or labelled a probability. Weight/threshold sensitivity measures workload stability.
- **Validation:** unit tests cover dates, identifiers, duplicates, monotonicity, score boundaries, missingness and mocked API pagination. Independent SQL recomputes score arithmetic from due dates and reconciles totals.
- **Business insight:** filing delays cluster. The cross-sectional prevalence ratio is 10.08; this suggests checking both obligations together, without inferring causation or insolvency.
- **BI:** dimensional import model, explicit measures, separate unscored counts, denominator-aware rates, company drill-through design. Native PBIX execution is not claimed.
- **Limitations:** live-register survivorship, SME proxy, missing financial statements, registered-office geography, sparse subgroup events, policy sensitivity and no outcome panel.
- **Next experiment:** collect prospective snapshots with publication timestamps and dated outcomes; set a prediction horizon, exclude information unavailable at scoring, create chronological splits, compare a baseline and assess PR-AUC, recall/precision and calibration only then.

Do not describe this as a deployed lending model, claim a native Power BI dashboard has been built, or invent business savings, accuracy or default-prediction performance.
