# Findings from the completed analysis

Reference date: 2026-08-31. These are sample observations, not UK SME population estimates.

- Scanned 5,689,368 source rows across every partition; quarantined 2 malformed records. The accounts-category proxy contained 1,875,337 eligible rows; the deterministic sample contains 30,000 companies.
- 26,785 active companies have both deadlines and are scored; 3,215 records remain unscored because of observed status or incomplete deadline information.
- 66 companies (0.25% of scored companies) meet the policy's high-review threshold. 179 are elevated review, 1,005 watch and 25,535 have no flagged deadline. No flagged deadline does not mean financially healthy.
- 250 scored companies show an accounts deadline before the reference date; 1,095 show an overdue confirmation deadline; 95 show both.
- The largest observed high-review share among primary SIC groups with at least 100 scored companies is 59200 (Sound recording and music publishing activities): 2/106, or 1.89%. This is a descriptive ranking with multiple-comparison and sector-composition caveats.
- Registered-office postcode area LU has the largest observed share among eligible areas: 3/184, or 1.63%. This is not an operating-region measure or a population-density statistic.

## Analytical interpretation

Confirmation deadlines are overdue for 95/250 companies with an accounts delay (38.00%), compared with 1,000/26,535 without one (3.77%). The cross-sectional prevalence ratio is 10.08 (approximate 95% log-Wald interval 8.51–11.95). This supports investigating clustered filing problems; it does not demonstrate financial distress or causal direction.

The leading sector has only 2 high-review observations and the leading postcode area only 3. Those descriptive rankings are fragile, with wide intervals, and should not be presented as reliable rankings of UK business failure risk.

The index can prioritise manual checks of overdue registry obligations. It cannot establish financial distress from these observations. Accounts and confirmation delays are score components, so their relationship with the score is mechanical and is not presented as predictive evidence.

`deadline_association.csv` compares confirmation lateness across accounts-lateness groups independently of the score. `age_standardised_sectors.csv` checks sector composition against a common age mix; cells with fewer than 10 observations are withheld. `sensitivity.csv` reports how weights and thresholds change workload and selected-company overlap. Wilson intervals in benchmark exports describe binomial sampling uncertainty conditional on this proxy and selection; they do not correct coverage, filing errors or ranking selection.

## Questions this release cannot answer

No historical adverse-outcome labels, officer-event panel or dated charge history was acquired. We therefore make no claim about predictive power, governance instability before failure, causal drivers, survival probabilities, emerging sectors or companies entering high risk. Current liquidation is not automatically financial insolvency, and dissolved companies are not the live-register sampling frame.

## Action

Use the high-review queue to verify current records, deadline extensions and filings manually. Review already-observed legal statuses in a separate queue. Collect prospective snapshots and legally obtained event histories before testing an early-warning model.
