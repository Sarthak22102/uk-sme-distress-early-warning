-- Registered-office postcode AREA, not residence, operations, UK region or density.
WITH areas AS (
 SELECT postcode_area,COUNT(*) AS companies,COUNT(risk_score) AS scored_companies,
 SUM(risk_band='High review') AS high_review,AVG(risk_score) AS average_score
 FROM company_investigation GROUP BY postcode_area
)
SELECT *,1.0*high_review/NULLIF(scored_companies,0) AS high_review_rate,
 CASE WHEN scored_companies>=100 AND postcode_area<>'Unknown' THEN 'Benchmarkable' ELSE 'Small or unknown geography' END AS benchmark_status
FROM areas ORDER BY high_review_rate DESC;
