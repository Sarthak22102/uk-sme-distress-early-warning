"""Regenerate quantitative README, portfolio text and dictionary from the final database."""
from src.utils.security import sql_identifier
import json,platform,sqlite3
from pathlib import Path
import pandas as pd,numpy,matplotlib

DESCRIPTIONS={
'company_number':'Official company identifier. Text preserves leading zeros and legacy prefixes.',
'company_name':'Official company name for local investigation only; excluded from public aggregate exports.',
'incorporation_date':'Source incorporation date in ISO format; invalid/future observations masked.',
'accounts_category':'Source accounts category supporting the explicitly labelled SME proxy.',
'sic_code':'Five-digit declared SIC as text; first listed code in company dimension; declared code in bridge.',
'industry_label':'Description accompanying first supplied SIC; Unknown when absent.',
'postcode_area':'Coarse registered-office postcode area, not administrative region or operating location.',
'geography_type':'Fixed label identifying registered-office postcode-area grain.',
'position':'Original supplied SIC position from one through four; avoids pretending secondary codes are primary.',
'reference_date':'Month-end snapshot reference date; not extraction date or real-time publication date.',
'company_status':'Unmodified official observed status description.',
'status_group':'Explicit analytical mapping; active, strike-off proposal, administration, liquidation_unspecified, receivership, voluntary_arrangement, dissolved or unmapped.',
'accounts_due':'Next accounts deadline in the snapshot; future dates are legitimate.',
'accounts_made_up':'Last accounting period end; not receipt/submission date.',
'confirmation_due':'Next confirmation statement deadline, nullable.',
'confirmation_made_up':'Last statement made-up date; not receipt/submission date.',
'charge_count':'Source total registered mortgage/charge count; nullable if invalid.',
'outstanding_charges':'Source outstanding charge count; no amount or distress penalty.',
'part_satisfied_charges':'Source partially satisfied charge count.',
'satisfied_charges':'Source satisfied charge count.',
'age_years':'Days from incorporation to reference divided by 365.25; contextual only.',
'incorporation_cohort':'Year of incorporation; current-register cohort, not observed historical population.',
'accounts_overdue_days':'max(reference date − accounts due, 0); null if due date unknown.',
'confirmation_overdue_days':'max(reference date − confirmation due, 0); null if due date unknown.',
'deadline_coverage':'Known deadline count divided by two: 0, 0.5 or 1.',
'score_eligible':'Integer boolean: active observed status and both deadlines known.',
'exclusion_reason':'Explanation when score is withheld; empty for eligible records.',
'accounts_points':'Policy weighted capped accounts delay; null if not eligible.',
'confirmation_points':'Policy weighted capped confirmation delay; null if not eligible.',
'risk_score':'0–100 uncalibrated filing-review index; null for unscored companies.',
'risk_band':'No flagged deadline, Watch, Elevated review, High review or Not scored.',
'primary_driver':'Highest weighted flagged component; no flagged deadline/not scored explicitly labelled.',
'secondary_driver':'Both deadlines overdue if applicable, otherwise empty.',
'score_version':'Policy version identifier for auditability.'}
GRAINS={'industry':'One first-declared SIC code observed in the sample','geography':'One registered-office postcode area','companies':'One sampled company','company_sic':'One company × supplied SIC position','company_snapshots':'One company × reference date','accounts_metadata':'One company × reference date','charge_summary':'One company × reference date','risk_features':'One company × reference date','risk_scores':'One company × reference date'}

def generate():
    r=Path('reports');s=json.loads((r/'summary.json').read_text());q=json.loads((r/'quality.json').read_text());a=json.loads((r/'association_summary.json').read_text())
    env={'python':platform.python_version(),'sqlite':sqlite3.sqlite_version,'pandas':pd.__version__,'numpy':numpy.__version__,'matplotlib':matplotlib.__version__}
    (r/'environment.json').write_text(json.dumps(env,indent=2))
    with sqlite3.connect('data/processed/platform.sqlite') as db:
        lines=['# Analytical data dictionary','', 'Foreign keys are enabled during loading and validation. ISO dates are stored as TEXT in SQLite and explicitly typed as Date in Power BI. Nulls are preserved. See docs/feature_dictionary.md for formulas and limitations.','']
        for table,grain in GRAINS.items():
            info=db.execute(f'PRAGMA table_info({table})').fetchall();fks=db.execute(f'PRAGMA foreign_key_list({table})').fetchall();keys=[x[1] for x in sorted(info,key=lambda x:x[5]) if x[5]]
            lines.extend([f'## {table}',f'Grain: {grain}. Primary key: {", ".join(keys)}. Rows: {db.execute("SELECT COUNT(*) FROM "+sql_identifier(table)).fetchone()[0]:,}.','', '| Column | SQLite type | Meaning |','|---|---|---|'])
            for x in info:lines.append(f'| {x[1]} | {x[2]} | {DESCRIPTIONS[x[1]]} |')
            lines.extend(['','Foreign-key columns: '+('; '.join(f'{x[3]} → {x[2]}.{x[4]}' for x in fks) if fks else 'none')+'.',''])
        lines.extend(['## Relationships and exports','Each company has one primary SIC and one area; dimensions filter many companies. Each company can have multiple dated observations in the schema; this release contains one. Every snapshot has exactly one accounts, charge, feature and score record, with nullable score values. The SIC bridge has up to four positions per company and is not used to multiply primary-sector denominators.','', 'company_investigation is a validated one-row-per-company/date SQL view joining the analytical tables. Power BI consumes it as FactReview alongside the dimensions. CSV column types are specified in dashboard/power_query.m; do not let import inference convert identifiers to integers.'])
        Path('database/data_dictionary.md').write_text('\n'.join(lines))
    lines=['# Data-quality results','',f'Real sample at {s["reference_date"]}. Raw full-register audit: {s["source_rows"]:,} records; {s["malformed_rows"]:,} quarantined for invalid CSV field counts. Sample: {s["companies_analysed"]:,}.', '', '| Check | Result |','|---|---|']
    for key,value in q.items():lines.append(f'| {key} | {json.dumps(value)} |')
    lines += ['', '## Treatment and scope', 'Missing confirmation deadlines are retained; affected active companies are unscored. Missing/unparseable primary SICs remain Unknown and are not dropped from totals. Registered-office areas with missing/unparseable postcodes remain Unknown. Due dates in the future are valid; historical observation dates in the future are flagged and masked. The source RECEIVERSHIP label is explicitly mapped. A legitimate legacy R-prefixed company identifier is preserved after official-source verification.', '', 'Duplicate-company and chronology checks apply to the selected sample, not every field of the full register. Full-register validation covers source ZIP integrity, field counts, partition completeness and row reconciliation. Missingness/outlier claims are sample-scoped. The outlier_profile.csv report records min, median, p95, p99, max and missingness for age, charges and delay days. Unusually old incorporation does not itself imply an error; outliers are retained, while the score caps are explicit policy assumptions.', '', 'Filings, officer events and API completeness were not measured in the real-data run. Optional API pagination is tested with synthetic fixtures; no empty API response is treated as an observed zero.']
    (r/'data_quality.md').write_text('\n'.join(lines))
    readme=f'''# UK SME Distress Early-Warning Platform
### Business Failure & Financial Risk Intelligence

**A reproducible registry-filing review platform for prioritising manual investigation—not a validated insolvency predictor.**

Built by **Sarthak Manjarekar** · Python · SQL / SQLite · Power BI build pack

## The question
Can public company characteristics and filing signals reveal patterns worth investigating? This release answers the filing-priority question using a transparent index; historical failure prediction remains unsupported by the acquired data.

## Evidence in 60 seconds

| Actual result | Value |
|---|---:|
| Official source rows scanned | {s['source_rows']:,} |
| Accounts-category proxy population | {s['eligible_population']:,} |
| Reproducible company sample | {s['companies_analysed']:,} |
| Active companies with complete scoring inputs | {s['scored_companies']:,} |
| High review priority | {s['high_review']:,} ({s['high_review_share']:.2%} of scored companies) |
| Malformed source rows explicitly quarantined | {s['malformed_rows']:,} |

Snapshot reference: **{s['reference_date']}**. Real Companies House data; no synthetic analytical results.

![Executive reference visual](dashboard/screenshots/executive_preview.png)
*Python-rendered reference visual using actual results. A native PBIX was not created; the six-page Power BI build pack is included.*

## What the analysis found

- Confirmation deadlines were overdue in **38.00%** of companies with an accounts delay, versus **3.77%** without one; cross-sectional prevalence ratio **{a['risk_ratio']:.2f}**. This is filing-behaviour association, not financial-distress prediction.
- The policy selects **{s['high_review']:,}** high-review and **{s['elevated_review']:,}** elevated-review companies. **{s['not_scored']:,}** companies are explicitly unscored.
- Leading sector/area rates have very few flagged observations and wide uncertainty. Do not interpret them as reliable UK failure-risk rankings.

[Full findings](reports/findings.md) · [Sensitivity](reports/sensitivity.csv) · [Data quality](reports/data_quality.md)

## Architecture

```mermaid
flowchart TD
    A["Official ZIPs and source audit"] --> B["Seeded 30,000-company sample"]
    B --> C["Typed Python transformations"]
    C --> D["Nine-table SQLite model"]
    D --> E["Transparent score and seven SQL analyses"]
    E --> F["Validated exports and Power BI design"]
```

[ER diagram](docs/architecture.md) · [Data dictionary](database/data_dictionary.md) · [Feature definitions](docs/feature_dictionary.md)

## Method

Scan all alphabetic partitions; use deterministic bottom-k SHA256 sampling. The SME proxy uses selected accounts categories, not an official employee-based classification. Score active companies with both deadlines using capped accounts and confirmation overdue days (60/40 policy weights). Status, age, industry, geography and charges do not add unsupported risk penalties. No historical targets, train/test split, AUC or probability claims are manufactured.

SQL demonstrates CTEs, joins, conditional aggregation, date arithmetic, window means, PERCENT_RANK, ranking, LAG/LEAD and pooled cohort calculations. Analysis adds Wilson intervals, age standardisation and weight/threshold sensitivity.

## Reproduce

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-lock.txt
python -m src.pipeline all
python -m unittest discover -s tests -v
```

No API key or database server required. From the delivered real sample, use `python -m src.pipeline build`. Source URLs rotate monthly; exact source reproduction requires retained ZIPs or the delivered checksum-verified sample. [Setup, refresh and optional API instructions](docs/reproduce.md).

## Repository guide

| Directory | Contents |
|---|---|
| src/ | Ingestion, cleaning, features, scoring, SQL loading, reports |
| sql/ | Seven business-focused analytical queries |
| database/ | Enforced schema and column-level dictionary |
| tests/ | Synthetic unit fixtures plus real-build reconciliation |
| dashboard/ | Six-page Power BI specification, DAX, M, theme, wireframes |
| reports/ | Actual findings, source provenance, quality and robustness |
| docs/ | Architecture, feature definitions, reproduction, publication, portfolio text |

[Build Power BI](dashboard/build_instructions.md) · [Validation](reports/validation.json) · [CV and interview material](docs/portfolio.md)

## Limitations and next steps

Single live-register snapshot; incomplete SME coverage; no financial ratios or officer histories; registered-office areas are not operating regions. The score is an uncalibrated review policy, not a lending or investment recommendation. Code is MIT; source data has separate terms. Public Git excludes raw and company-level data.

Next: collect prospective snapshots, obtain dated API histories securely, map official administrative geography and validate time-aligned outcomes before considering predictive models. [Methodology](reports/methodology.md) · [Limitations](reports/limitations.md) · [Official sources](docs/sources.md).
'''
    # Derive even display percentages from the generated association table.
    assoc=pd.read_csv(r/'deadline_association.csv')
    readme=readme.replace('**38.00%**',f'**{assoc.iloc[1].confirmation_overdue_share:.2%}**').replace('**3.77%**',f'**{assoc.iloc[0].confirmation_overdue_share:.2%}**')
    Path('README.md').write_text(readme)
    portfolio=f'''# Portfolio material — evidence-based wording

## GitHub repository description
Python/SQL platform analysing UK company filing signals, with transparent review scoring, validated pipelines and a six-page Power BI build pack.

## Three CV bullets

- Built a reproducible Python and SQL pipeline scanning {s['source_rows']:,} Companies House records and sampling {s['companies_analysed']:,} companies into a nine-table analytical model, with source checksums and explicit malformed-row handling.
- Engineered an interpretable filing-review index for {s['scored_companies']:,} active companies, identifying {s['high_review']:,} high-priority review records and validating score calculations independently in SQL.
- Developed seven analytical SQL queries and a six-page Power BI build pack with DAX, Power Query, sector/geographic benchmarks and sensitivity analysis, documenting the limits of cross-sectional distress indicators.

## LinkedIn project description

I built the UK SME Distress Early-Warning Platform to explore what public company data can—and cannot—tell us about business risk. The Python/SQL pipeline scans official Companies House data and analyses a reproducible sample of {s['companies_analysed']:,} companies. It includes a relational analytical model, explicit data-quality checks, an interpretable filing-review score, sector and registered-office-area comparisons, and a six-page Power BI build pack.

A key finding was the clustering of filing delays: confirmation deadlines were overdue for {assoc.iloc[1].confirmation_overdue_share:.2%} of companies with an accounts delay, compared with {assoc.iloc[0].confirmation_overdue_share:.2%} without one. I treated this as an observational filing pattern, not evidence that the platform predicts insolvency. The project includes source provenance, reproducible SQL, sensitivity checks and documented limitations.

## Tell me about this project

“I wanted to understand whether public registry data could help an analyst prioritise companies for further review. I processed the official Companies House snapshot and built a reproducible {s['companies_analysed']:,}-company sample using an explicit SME proxy. I created a SQL data model and a transparent score based on overdue filing deadlines, with company-level explanations and a Power BI build pack. The most important judgement was avoiding an unsupported prediction claim: one snapshot cannot prove early-warning performance, and dissolution is not the same as financial distress. I validated the pipeline, found clustered filing delays and showed how policy choices change the review queue.”

## Technical interview talking points

- **Architecture:** chunked ZIP ingestion → row audit and seeded hash sample → typed Python cleaning → nine SQLite tables → features and policy score → SQL comparisons → validated CSV exports and Power BI design.
- **Sampling:** all source partitions are alphabetical, so a first-file sample would be biased. Bottom-k SHA256 makes selection deterministic and independent of ordering. Explain the restricted proxy frame and why it is not representative of all UK SMEs.
- **SQL:** joins preserve company/date grain; CTEs define valid denominators; window functions add peer means, percentiles and ranks. Cohort queries use LAG and pooled windows but are explicitly cross-sectional. Historical transition SQL returns unknown with one snapshot.
- **Python:** modules separate acquisition, cleaning, feature engineering, scoring and analysis. Missing dates stay missing; legitimate future deadlines are not errors. Checksum verification and fail-fast constraints protect reproducibility.
- **Methodology:** capped 60/40 filing-delay weights are an explicit review policy. Status is a separate queue. The score is not trained, calibrated or labelled a probability. Weight/threshold sensitivity measures workload stability.
- **Validation:** unit tests cover dates, identifiers, duplicates, monotonicity, score boundaries, missingness and mocked API pagination. Independent SQL recomputes score arithmetic from due dates and reconciles totals.
- **Business insight:** filing delays cluster. The cross-sectional prevalence ratio is {a['risk_ratio']:.2f}; this suggests checking both obligations together, without inferring causation or insolvency.
- **BI:** dimensional import model, explicit measures, separate unscored counts, denominator-aware rates, company drill-through design. Native PBIX execution is not claimed.
- **Limitations:** live-register survivorship, SME proxy, missing financial statements, registered-office geography, sparse subgroup events, policy sensitivity and no outcome panel.
- **Next experiment:** collect prospective snapshots with publication timestamps and dated outcomes; set a prediction horizon, exclude information unavailable at scoring, create chronological splits, compare a baseline and assess PR-AUC, recall/precision and calibration only then.

Do not describe this as a deployed lending model, claim a native Power BI dashboard has been built, or invent business savings, accuracy or default-prediction performance.
'''
    Path('docs/portfolio.md').write_text(portfolio)
