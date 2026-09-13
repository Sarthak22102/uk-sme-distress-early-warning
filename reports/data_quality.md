# Data-quality results

Real sample at 2026-08-31. Raw full-register audit: 5,689,368 records; 2 quarantined for invalid CSV field counts. Sample: 30,000.

| Check | Result |
|---|---|
| invalid_company_numbers | 0 |
| invalid_incorporation_date | 0 |
| invalid_dissolution_date | 0 |
| invalid_accounts_due | 0 |
| invalid_accounts_made_up | 0 |
| invalid_confirmation_due | 0 |
| invalid_confirmation_made_up | 0 |
| future_incorporation_date | 0 |
| future_dissolution_date | 0 |
| future_accounts_made_up | 0 |
| future_confirmation_made_up | 0 |
| missing_incorporation_date | 0 |
| unmapped_statuses | {} |
| invalid_charge_count | 0 |
| invalid_outstanding_charges | 0 |
| invalid_part_satisfied_charges | 0 |
| invalid_satisfied_charges | 0 |
| charge_components_exceed_total | 0 |
| dissolution_before_incorporation | 0 |
| accounts_made_up_before_incorporation | 0 |
| confirmation_made_up_before_incorporation | 0 |
| missing_accounts_due | 0 |
| missing_confirmation_due | 9 |
| unknown_postcode_area | 7 |
| duplicate_company_numbers | 0 |
| missing_or_unparseable_primary_sic | 132 |
| input_rows | 30000 |
| feature_rows | 30000 |
| score_rows | 30000 |
| scored_companies | 26785 |
| source_malformed_rows | 2 |
| api_enrichment | "not used; credentials not supplied" |

## Treatment and scope
Missing confirmation deadlines are retained; affected active companies are unscored. Missing/unparseable primary SICs remain Unknown and are not dropped from totals. Registered-office areas with missing/unparseable postcodes remain Unknown. Due dates in the future are valid; historical observation dates in the future are flagged and masked. The source RECEIVERSHIP label is explicitly mapped. A legitimate legacy R-prefixed company identifier is preserved after official-source verification.

Duplicate-company and chronology checks apply to the selected sample, not every field of the full register. Full-register validation covers source ZIP integrity, field counts, partition completeness and row reconciliation. Missingness/outlier claims are sample-scoped. The outlier_profile.csv report records min, median, p95, p99, max and missingness for age, charges and delay days. Unusually old incorporation does not itself imply an error; outliers are retained, while the score caps are explicit policy assumptions.

Filings, officer events and API completeness were not measured in the real-data run. Optional API pagination is tested with synthetic fixtures; no empty API response is treated as an observed zero.