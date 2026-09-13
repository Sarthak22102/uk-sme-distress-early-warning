# Analytical data dictionary

Foreign keys are enabled during loading and validation. ISO dates are stored as TEXT in SQLite and explicitly typed as Date in Power BI. Nulls are preserved. See docs/feature_dictionary.md for formulas and limitations.

## industry
Grain: One first-declared SIC code observed in the sample. Primary key: sic_code. Rows: 604.

| Column | SQLite type | Meaning |
|---|---|---|
| sic_code | TEXT | Five-digit declared SIC as text; first listed code in company dimension; declared code in bridge. |
| industry_label | TEXT | Description accompanying first supplied SIC; Unknown when absent. |

Foreign-key columns: none.

## geography
Grain: One registered-office postcode area. Primary key: postcode_area. Rows: 123.

| Column | SQLite type | Meaning |
|---|---|---|
| postcode_area | TEXT | Coarse registered-office postcode area, not administrative region or operating location. |
| geography_type | TEXT | Fixed label identifying registered-office postcode-area grain. |

Foreign-key columns: none.

## companies
Grain: One sampled company. Primary key: company_number. Rows: 30,000.

| Column | SQLite type | Meaning |
|---|---|---|
| company_number | TEXT | Official company identifier. Text preserves leading zeros and legacy prefixes. |
| company_name | TEXT | Official company name for local investigation only; excluded from public aggregate exports. |
| incorporation_date | TEXT | Source incorporation date in ISO format; invalid/future observations masked. |
| accounts_category | TEXT | Source accounts category supporting the explicitly labelled SME proxy. |
| sic_code | TEXT | Five-digit declared SIC as text; first listed code in company dimension; declared code in bridge. |
| postcode_area | TEXT | Coarse registered-office postcode area, not administrative region or operating location. |

Foreign-key columns: postcode_area → geography.postcode_area; sic_code → industry.sic_code.

## company_sic
Grain: One company × supplied SIC position. Primary key: company_number, position. Rows: 39,954.

| Column | SQLite type | Meaning |
|---|---|---|
| company_number | TEXT | Official company identifier. Text preserves leading zeros and legacy prefixes. |
| sic_code | TEXT | Five-digit declared SIC as text; first listed code in company dimension; declared code in bridge. |
| position | INTEGER | Original supplied SIC position from one through four; avoids pretending secondary codes are primary. |

Foreign-key columns: company_number → companies.company_number.

## company_snapshots
Grain: One company × reference date. Primary key: company_number, reference_date. Rows: 30,000.

| Column | SQLite type | Meaning |
|---|---|---|
| company_number | TEXT | Official company identifier. Text preserves leading zeros and legacy prefixes. |
| reference_date | TEXT | Month-end snapshot reference date; not extraction date or real-time publication date. |
| company_status | TEXT | Unmodified official observed status description. |
| status_group | TEXT | Explicit analytical mapping; active, strike-off proposal, administration, liquidation_unspecified, receivership, voluntary_arrangement, dissolved or unmapped. |

Foreign-key columns: company_number → companies.company_number.

## accounts_metadata
Grain: One company × reference date. Primary key: company_number, reference_date. Rows: 30,000.

| Column | SQLite type | Meaning |
|---|---|---|
| company_number | TEXT | Official company identifier. Text preserves leading zeros and legacy prefixes. |
| reference_date | TEXT | Month-end snapshot reference date; not extraction date or real-time publication date. |
| accounts_due | TEXT | Next accounts deadline in the snapshot; future dates are legitimate. |
| accounts_made_up | TEXT | Last accounting period end; not receipt/submission date. |
| confirmation_due | TEXT | Next confirmation statement deadline, nullable. |
| confirmation_made_up | TEXT | Last statement made-up date; not receipt/submission date. |

Foreign-key columns: company_number → company_snapshots.company_number; reference_date → company_snapshots.reference_date.

## charge_summary
Grain: One company × reference date. Primary key: company_number, reference_date. Rows: 30,000.

| Column | SQLite type | Meaning |
|---|---|---|
| company_number | TEXT | Official company identifier. Text preserves leading zeros and legacy prefixes. |
| reference_date | TEXT | Month-end snapshot reference date; not extraction date or real-time publication date. |
| charge_count | INTEGER | Source total registered mortgage/charge count; nullable if invalid. |
| outstanding_charges | INTEGER | Source outstanding charge count; no amount or distress penalty. |
| part_satisfied_charges | INTEGER | Source partially satisfied charge count. |
| satisfied_charges | INTEGER | Source satisfied charge count. |

Foreign-key columns: company_number → company_snapshots.company_number; reference_date → company_snapshots.reference_date.

## risk_features
Grain: One company × reference date. Primary key: company_number, reference_date. Rows: 30,000.

| Column | SQLite type | Meaning |
|---|---|---|
| company_number | TEXT | Official company identifier. Text preserves leading zeros and legacy prefixes. |
| reference_date | TEXT | Month-end snapshot reference date; not extraction date or real-time publication date. |
| age_years | REAL | Days from incorporation to reference divided by 365.25; contextual only. |
| incorporation_cohort | INTEGER | Year of incorporation; current-register cohort, not observed historical population. |
| accounts_overdue_days | INTEGER | max(reference date − accounts due, 0); null if due date unknown. |
| confirmation_overdue_days | INTEGER | max(reference date − confirmation due, 0); null if due date unknown. |
| deadline_coverage | REAL | Known deadline count divided by two: 0, 0.5 or 1. |
| score_eligible | INTEGER | Integer boolean: active observed status and both deadlines known. |
| exclusion_reason | TEXT | Explanation when score is withheld; empty for eligible records. |

Foreign-key columns: company_number → company_snapshots.company_number; reference_date → company_snapshots.reference_date.

## risk_scores
Grain: One company × reference date. Primary key: company_number, reference_date. Rows: 30,000.

| Column | SQLite type | Meaning |
|---|---|---|
| company_number | TEXT | Official company identifier. Text preserves leading zeros and legacy prefixes. |
| reference_date | TEXT | Month-end snapshot reference date; not extraction date or real-time publication date. |
| accounts_points | REAL | Policy weighted capped accounts delay; null if not eligible. |
| confirmation_points | REAL | Policy weighted capped confirmation delay; null if not eligible. |
| risk_score | REAL | 0–100 uncalibrated filing-review index; null for unscored companies. |
| risk_band | TEXT | No flagged deadline, Watch, Elevated review, High review or Not scored. |
| primary_driver | TEXT | Highest weighted flagged component; no flagged deadline/not scored explicitly labelled. |
| secondary_driver | TEXT | Both deadlines overdue if applicable, otherwise empty. |
| score_version | TEXT | Policy version identifier for auditability. |

Foreign-key columns: company_number → company_snapshots.company_number; reference_date → company_snapshots.reference_date.

## Relationships and exports
Each company has one primary SIC and one area; dimensions filter many companies. Each company can have multiple dated observations in the schema; this release contains one. Every snapshot has exactly one accounts, charge, feature and score record, with nullable score values. The SIC bridge has up to four positions per company and is not used to multiply primary-sector denominators.

company_investigation is a validated one-row-per-company/date SQL view joining the analytical tables. Power BI consumes it as FactReview alongside the dimensions. CSV column types are specified in dashboard/power_query.m; do not let import inference convert identifiers to integers.