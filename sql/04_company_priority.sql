-- Peer percentile reflects ties with PERCENT_RANK; not a probability of insolvency.
WITH peers AS (
 SELECT *,PERCENT_RANK() OVER(PARTITION BY sic_code ORDER BY risk_score) AS sector_percentile,
 AVG(risk_score) OVER(PARTITION BY sic_code) AS sector_mean,
 COUNT(*) OVER(PARTITION BY sic_code) AS sector_n,
 AVG(risk_score) OVER(PARTITION BY postcode_area) AS postcode_area_mean,
 COUNT(*) OVER(PARTITION BY postcode_area) AS postcode_area_n,
 ROW_NUMBER() OVER(ORDER BY risk_score DESC,company_number) AS review_rank
 FROM company_investigation WHERE risk_score IS NOT NULL
)
SELECT company_number,reference_date,risk_score,risk_band,primary_driver,secondary_driver,review_rank,
 CASE WHEN sector_n>=100 THEN sector_percentile END AS sector_percentile,
 CASE WHEN sector_n>=100 THEN sector_mean END AS sector_mean,
 CASE WHEN postcode_area_n>=100 AND postcode_area<>'Unknown' THEN postcode_area_mean END AS postcode_area_mean,
 sector_n,postcode_area_n
FROM peers ORDER BY review_rank;
