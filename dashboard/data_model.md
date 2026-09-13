# Power BI semantic model

Use Import mode. This deliverable contains a native Power BI build pack, not a fabricated PBIX. Windows Power BI Desktop is required to assemble and verify the native report.

| Power BI table | Export | Grain | Key |
|---|---|---|---|
| DimCompany | companies.csv | Company | company_number (Text, preserve leading zeros) |
| DimIndustry | industry.csv | Primary declared SIC | sic_code (Text) |
| DimGeography | geography.csv | Registered-office postcode area | postcode_area (Text) |
| DimDate | M query supplied | Reference date | Date |
| FactReview | company_investigation.csv | Company × reference date | company_number + reference_date |

Relationships, all active, one-to-many and single direction:

1. DimIndustry[sic_code] → DimCompany[sic_code]
2. DimGeography[postcode_area] → DimCompany[postcode_area]
3. DimCompany[company_number] → FactReview[company_number]
4. DimDate[Date] → FactReview[reference_date]

Do not join all nine SQLite tables directly in Power BI: the prepared fact avoids ambiguous fact-to-fact filtering. SQL retains the richer normalised model. Hide duplicate company and dimension attributes in FactReview. Use dimension fields in slicers. Hide raw summable scores; use measures. Disable auto date/time.

The optional company_sic bridge preserves secondary SIC codes in SQL. It is not connected in this primary-SIC report, so each company contributes once to sector totals. A separate multi-SIC report would require explicit distinct counts and overlapping-category warnings.

Only one snapshot exists. Do not show time-change KPIs, risk-entry counts, historical distress rates or predictive-performance visuals. A source refresh replaces the current release; it does not construct a historical panel.
