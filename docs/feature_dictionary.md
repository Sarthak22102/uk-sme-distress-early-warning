# Feature definitions and interpretation

All features are observed at the reference date in the source snapshot. Nulls mean unknown, not zero. Source provenance: docs/sources.md.

| Feature | Formula / definition | Source | Rationale | Limitation |
|---|---|---|---|---|
| age_years | (reference − incorporation) in days / 365.25 | IncorporationDate | Compare lifecycle composition | Age is not penalised; incorporation is not trading start |
| incorporation_cohort | Year of incorporation | IncorporationDate | Compare current-register cohorts | Survivorship-selected, not historical failure rates |
| accounts_overdue_days | max(reference − next accounts due, 0) | Accounts.NextDueDate | Detect apparent unfulfilled financial-reporting deadline | Not actual submission delay; extensions/update lag can matter |
| confirmation_overdue_days | max(reference − next confirmation due, 0) | ConfStmtNextDueDate | Detect apparent confirmation deadline delay | Administrative signal, not proof of financial problems |
| deadline_coverage | Number of nonmissing due dates / 2 | Both deadline fields | Expose score reliability/eligibility | Completeness does not establish correctness |
| score_eligible | status_group = active AND deadline_coverage = 1 | Status and deadlines | Separate existing legal-status review from filing triage | Excludes active strike-off proposals even if financially healthy |
| accounts_points | 60 × min(accounts_overdue_days / 180, 1) | Engineered days | Transparent primary policy component | Judgemental weight and cap |
| confirmation_points | 40 × min(confirmation_overdue_days / 90, 1) | Engineered days | Transparent secondary policy component | Judgemental weight and cap |
| risk_score | round(accounts_points + confirmation_points, 2) | Policy components | Order manual filing review | Uncalibrated; NOT a probability or financial rating |
| risk_band | 0 / (0,40) / [40,70) / [70,100] / null | Score | Translate policy into workload bands | No empirically established financial-distress cut-offs |
| primary_driver | Highest weighted nonzero component; accounts wins ties | Score components | Explain dominant contribution | Mathematical attribution, not causal explanation |
| secondary_driver | Both deadlines overdue, otherwise empty | Engineered days | Surface combined obligation problems | Empty is no second flagged component, not no other business risks |
| outstanding_charges | Source count of outstanding charges | Mortgages.NumMortOutstanding | Contextual financing exposure | No amount, maturity, covenants or distress inference |
| primary SIC | First supplied five-digit SIC | SICCode.SicText_1 | Mutually exclusive benchmark denominator | May not be principal revenue-generating activity |
| postcode_area | Leading 1–2 letters before numeric outward-code component | Registered postcode, precise postcode discarded | Coarse registered-office comparison | Not ONS region/operating footprint; malformed values become Unknown |
| sector_mean | Mean score among scored peers sharing primary SIC | SQL window AVG | Descriptive peer context | Suppressed below 100 peers; not sector failure probability |
| sector_percentile | SQL PERCENT_RANK ordered by score | SQL window function | Relative position with ties | Ties get same rank; tiny groups withheld |
| postcode_area_mean | Mean score among scored peers sharing area | SQL window AVG | Registered-area context | Unknown/small groups withheld; address agents distort location |

Not implemented as evidence: director resignation velocity, officer turnover, filing-frequency irregularity, historical regional/sector dissolution rates, time-to-event, previous company status and dated charge activity. Their requisite event histories were not acquired. No proxy values are fabricated for these gaps.
