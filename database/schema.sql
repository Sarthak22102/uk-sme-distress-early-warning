PRAGMA foreign_keys=ON;
CREATE TABLE industry (sic_code TEXT PRIMARY KEY, industry_label TEXT NOT NULL);
CREATE TABLE geography (postcode_area TEXT PRIMARY KEY, geography_type TEXT NOT NULL);
CREATE TABLE companies (company_number TEXT PRIMARY KEY, company_name TEXT NOT NULL, incorporation_date TEXT, accounts_category TEXT, sic_code TEXT REFERENCES industry(sic_code), postcode_area TEXT REFERENCES geography(postcode_area));
CREATE TABLE company_sic (company_number TEXT REFERENCES companies(company_number), sic_code TEXT, position INTEGER CHECK(position BETWEEN 1 AND 4), PRIMARY KEY(company_number,position));
CREATE TABLE company_snapshots (company_number TEXT REFERENCES companies(company_number), reference_date TEXT, company_status TEXT, status_group TEXT, PRIMARY KEY(company_number,reference_date));
CREATE TABLE accounts_metadata (company_number TEXT, reference_date TEXT, accounts_due TEXT, accounts_made_up TEXT, confirmation_due TEXT, confirmation_made_up TEXT, PRIMARY KEY(company_number,reference_date), FOREIGN KEY(company_number,reference_date) REFERENCES company_snapshots(company_number,reference_date));
CREATE TABLE charge_summary (company_number TEXT, reference_date TEXT, charge_count INTEGER, outstanding_charges INTEGER, part_satisfied_charges INTEGER, satisfied_charges INTEGER, PRIMARY KEY(company_number,reference_date), FOREIGN KEY(company_number,reference_date) REFERENCES company_snapshots(company_number,reference_date));
CREATE TABLE risk_features (company_number TEXT, reference_date TEXT, age_years REAL, incorporation_cohort INTEGER, accounts_overdue_days INTEGER, confirmation_overdue_days INTEGER, deadline_coverage REAL, score_eligible INTEGER, exclusion_reason TEXT, PRIMARY KEY(company_number,reference_date), FOREIGN KEY(company_number,reference_date) REFERENCES company_snapshots(company_number,reference_date));
CREATE TABLE risk_scores (company_number TEXT, reference_date TEXT, accounts_points REAL, confirmation_points REAL, risk_score REAL CHECK(risk_score BETWEEN 0 AND 100 OR risk_score IS NULL), risk_band TEXT, primary_driver TEXT, secondary_driver TEXT, score_version TEXT, PRIMARY KEY(company_number,reference_date), FOREIGN KEY(company_number,reference_date) REFERENCES company_snapshots(company_number,reference_date));
CREATE INDEX scores_band ON risk_scores(reference_date,risk_band);
CREATE VIEW company_investigation AS
SELECT c.*,i.industry_label,s.reference_date,s.company_status,s.status_group,f.age_years,f.incorporation_cohort,f.accounts_overdue_days,f.confirmation_overdue_days,f.deadline_coverage,f.score_eligible,f.exclusion_reason,r.accounts_points,r.confirmation_points,r.risk_score,r.risk_band,r.primary_driver,r.secondary_driver,a.accounts_due,a.confirmation_due,a.accounts_made_up,a.confirmation_made_up,h.charge_count,h.outstanding_charges
FROM companies c JOIN industry i USING(sic_code)
JOIN company_snapshots s USING(company_number)
JOIN risk_features f USING(company_number,reference_date)
JOIN risk_scores r USING(company_number,reference_date)
JOIN accounts_metadata a USING(company_number,reference_date)
JOIN charge_summary h USING(company_number,reference_date);
