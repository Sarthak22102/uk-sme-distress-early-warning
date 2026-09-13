-- How concentrated are filing review flags within each primary declared SIC?
-- Denominator: score-eligible ACTIVE companies, not every observed legal status.
WITH sector AS (
 SELECT sic_code, industry_label, COUNT(*) AS companies,
 SUM(risk_score IS NOT NULL) AS scored_companies,
 SUM(risk_band='High review') AS high_review,
 SUM(risk_band='Elevated review') AS elevated_review,
 AVG(risk_score) AS average_score
 FROM company_investigation GROUP BY sic_code,industry_label
), rates AS (
 SELECT *, 1.0*high_review/NULLIF(scored_companies,0) AS high_review_rate
 FROM sector
)
SELECT *, CASE WHEN scored_companies>=100 THEN DENSE_RANK() OVER (
 PARTITION BY (scored_companies>=100) ORDER BY high_review_rate DESC) END AS eligible_rank
FROM rates ORDER BY high_review_rate DESC;
