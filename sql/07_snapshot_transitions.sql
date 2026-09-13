-- Requires >=2 prospective snapshots in a retained warehouse. One release has no transitions.
-- The standard single-release rebuild does not append: see longitudinal roadmap.
WITH history AS (
 SELECT company_number,reference_date,risk_score,risk_band,
 LAG(risk_score) OVER(PARTITION BY company_number ORDER BY reference_date) AS previous_score,
 LAG(risk_band) OVER(PARTITION BY company_number ORDER BY reference_date) AS previous_band,
 LEAD(reference_date) OVER(PARTITION BY company_number ORDER BY reference_date) AS next_observation
 FROM risk_scores
)
SELECT *,risk_score-previous_score AS score_change,
 CASE WHEN previous_band IS NULL THEN NULL WHEN risk_band='High review' AND previous_band<>'High review' THEN 1 ELSE 0 END AS entered_high_review
FROM history;
