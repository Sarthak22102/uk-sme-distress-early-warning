-- Compare operational workloads at distinct overdue severities.
WITH flags AS (
 SELECT *,CASE WHEN accounts_overdue_days IS NULL THEN 'Unknown' WHEN accounts_overdue_days=0 THEN 'Current' WHEN accounts_overdue_days<=30 THEN '1-30 days' WHEN accounts_overdue_days<=90 THEN '31-90 days' ELSE '91+ days' END AS accounts_severity
 FROM company_investigation WHERE score_eligible=1
)
SELECT accounts_severity,COUNT(*) AS companies,SUM(confirmation_overdue_days>0) AS also_confirmation_overdue,AVG(age_years) AS mean_age_years,AVG(risk_score) AS mean_score
FROM flags GROUP BY accounts_severity;
