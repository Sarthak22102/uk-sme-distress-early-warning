# Methodology

## Decision and unit of analysis

Support an analyst prioritising registry-filing checks on a UK incorporated small-business proxy. A record is one company observed at one register snapshot. The release is cross-sectional: its early-warning intent is a research direction, not validated predictive capability.

## Population and sample

The source is the Companies House live-register Free Company Data Product, release label 2026-09-01, compiled through the preceding month end (reference date 2026-08-31). All seven alphabetically partitioned files are scanned. UK private limited companies with accounts category MICRO ENTITY, SMALL, MEDIUM or TOTAL EXEMPTION SMALL are eligible. This conservative proxy is not an official SME classification. It excludes many genuine SMEs with other filing categories, newly formed companies without accounts, sole traders, partnerships and dormant accounts. Medium entities are included where explicitly labelled; no missing employee counts, turnover or group ownership are inferred.

The DBT business-population SME definition uses 0–249 employees. Companies House accounting-size categories are a different construct and size thresholds have changed over time. This analysis does not use turnover or balance-sheet thresholds to retrospectively reclassify companies.

Choose the 30,000 smallest SHA256 hashes of `22102:company_number` across the eligible population. This seeded hash sample is independent of source order and repeatable without storing the full register in memory. It approximates equal-probability sampling within this restricted frame; it is not stratified or weighted to the UK economy. Reject duplicate sampled identifiers. Record every source hash and row reconciliation. Malformed rows are quarantined by field count with SHA256 fingerprints rather than silently repaired.

## Observation date and leakage

Use the snapshot reference date, not extraction date or today's date. Future due dates are valid and produce zero overdue days. Invalid/missing deadlines yield unknown values; a company needs both deadlines and status Active to be scored. Future made-up/incorporation dates are flagged and masked. Made-up dates refer to accounting/statement periods, not actual filing-submission dates.

No historical feature vector is reconstructed from today's mutable profile. Current status is used to route records into separate review queues, never to add score points or act as a training target. This avoids the circular claim that known liquidation was predicted. Snapshot publication lag means this release cannot establish what was available on the reference date in real time.

## Filing review index

For active companies with complete deadline information:

`accounts_days = max(reference_date − accounts_due, 0)`

`confirmation_days = max(reference_date − confirmation_due, 0)`

`score = round(60 × min(accounts_days / 180, 1) + 40 × min(confirmation_days / 90, 1), 2)`

Weights and caps are explicit analyst policy assumptions, not learned coefficients or empirical estimates. Accounts receive greater weight because the registry obligation relates to financial reporting, but that judgement is not validated as an insolvency association. Caps prevent very stale records dominating the queue. The underlying days remain available uncapped for investigation.

| Score | Label | Operational interpretation |
|---|---|---|
| 0 | No flagged deadline | Neither observed deadline is overdue; does not establish financial health |
| >0 and <40 | Watch | Limited weighted filing delay; verify routinely |
| >=40 and <70 | Elevated review | Material weighted filing delay; inspect obligations |
| >=70 | High review | Strong combined filing-delay signal; prioritise verification |
| Null | Not scored | Observed status is non-active or deadlines are incomplete |

The 70-point policy requires contribution from both signals because either component alone is capped below 70. It is not a probability threshold. Report the actual workload and distribution, then inspect predeclared alternatives (account weights 40/50/60/70/80 and thresholds 50/60/70/80/90). Do not optimise weights against status in the same snapshot. Jaccard similarity measures queue stability under changed policy, not prediction performance.

## Comparisons and uncertainty

Sector means, rates and percentiles use the first declared SIC and scored active denominator. Unknown categories remain visible; group rankings require at least 100 scored companies. Wilson 95% intervals describe binomial sampling variability conditional on the proxy frame; systematic errors are not covered. Sector ranks are exploratory, subject to multiple comparisons, and not tests of significance. Age standardisation uses sample weights for <5, 5–<10, 10–<20 and 20+ years, requiring at least 10 companies in every sector-age cell. This reduces one compositional difference without claiming causal adjustment.

Postcode areas are registered-office location proxies, not ONS regions, operating locations or measures of population density. No official regional mapping was acquired. Charges are financing context; a secured charge does not inherently imply distress and has no score weight. Cohort comparisons condition on inclusion in the current live register and are not survival curves.

## Outcome decision

No clean historical distress target is available in the acquired bulk snapshot. Dissolution is not synonymous with financial distress. Liquidation may be solvent or insolvent; the bulk status does not subtype it. Administration, receivership, voluntary arrangement, strike-off proposal and liquidation remain separate groups. Do not estimate logistic regression, AUC, precision, recall, calibration or survival without a dated outcome panel and point-in-time features. No model performance is reported.

Optional API extraction code supports future investigation but was not used for this release. Its tests use clearly synthetic API responses. No officer-turnover, filing-history, PSC, insolvency-event or charge-event feature is presented as acquired evidence.
