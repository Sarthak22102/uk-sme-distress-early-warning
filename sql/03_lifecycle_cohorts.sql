-- Cross-sectional surviving-register cohorts. NOT failure rates or longitudinal trends.
WITH cohort AS (
 SELECT incorporation_cohort,COUNT(*) AS companies,COUNT(risk_score) AS scored_companies,
 SUM(accounts_overdue_days>0 AND score_eligible=1) AS accounts_overdue,
 SUM(confirmation_overdue_days>0 AND score_eligible=1) AS confirmation_overdue,
 AVG(risk_score) AS average_score
 FROM company_investigation GROUP BY incorporation_cohort
)
SELECT *,1.0*accounts_overdue/NULLIF(scored_companies,0) AS accounts_overdue_rate,
 LAG(average_score) OVER(ORDER BY incorporation_cohort) AS preceding_cohort_average,
 SUM(accounts_overdue) OVER(ORDER BY incorporation_cohort ROWS BETWEEN 2 PRECEDING AND CURRENT ROW)*1.0 /
 NULLIF(SUM(scored_companies) OVER(ORDER BY incorporation_cohort ROWS BETWEEN 2 PRECEDING AND CURRENT ROW),0) AS three_cohort_pooled_rate
FROM cohort ORDER BY incorporation_cohort;
