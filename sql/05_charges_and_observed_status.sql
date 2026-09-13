-- Cross-sectional association only. Liquidation is not subtyped into solvent/insolvent.
SELECT CASE WHEN outstanding_charges IS NULL THEN 'Unknown' WHEN outstanding_charges=0 THEN 'None' ELSE 'One or more' END AS charge_group,
 status_group,COUNT(*) AS companies,
 1.0*COUNT(*)/SUM(COUNT(*)) OVER(PARTITION BY CASE WHEN outstanding_charges IS NULL THEN 'Unknown' WHEN outstanding_charges=0 THEN 'None' ELSE 'One or more' END) AS within_charge_group_share
FROM company_investigation GROUP BY charge_group,status_group ORDER BY charge_group,companies DESC;
