# DAX measures

Create these measures in FactReview. Set counts to whole numbers, score to 2 decimals and proportions to 2 decimal percentages. Reference-date slicer must be single-select. Every measure respects company, sector, area and status context unless explicitly described. Blank score is not zero.

```dax
Companies Analysed = DISTINCTCOUNT(FactReview[company_number])

Scored Companies =
CALCULATE([Companies Analysed], KEEPFILTERS(FactReview[score_eligible] = 1))

Not Scored Companies = [Companies Analysed] - [Scored Companies]

High Review Companies =
CALCULATE([Companies Analysed], KEEPFILTERS(FactReview[risk_band] = "High review"))

Elevated Review Companies =
CALCULATE([Companies Analysed], KEEPFILTERS(FactReview[risk_band] = "Elevated review"))

High Review % = DIVIDE([High Review Companies], [Scored Companies])

Average Review Score = AVERAGE(FactReview[risk_score])

Accounts Overdue Companies =
CALCULATE([Scored Companies], KEEPFILTERS(FactReview[accounts_overdue_days] > 0))

Confirmation Overdue Companies =
CALCULATE([Scored Companies], KEEPFILTERS(FactReview[confirmation_overdue_days] > 0))

Both Deadlines Overdue =
CALCULATE([Scored Companies], KEEPFILTERS(FactReview[accounts_overdue_days] > 0),
KEEPFILTERS(FactReview[confirmation_overdue_days] > 0))

Deadline Coverage % = AVERAGE(FactReview[deadline_coverage])

Benchmarkable High Review % =
IF([Scored Companies] >= 100, [High Review %], BLANK())

Selected Company Score =
IF(HASONEVALUE(DimCompany[company_number]), MAX(FactReview[risk_score]), BLANK())

Selected Company Driver =
IF(HASONEVALUE(DimCompany[company_number]), SELECTEDVALUE(FactReview[primary_driver]), "Select one company")

Sector Peer Mean =
VAR SectorCode = SELECTEDVALUE(DimCompany[sic_code])
RETURN IF(HASONEVALUE(DimCompany[company_number]),
    CALCULATE([Average Review Score], REMOVEFILTERS(DimCompany),
        REMOVEFILTERS(FactReview[risk_band]),
        TREATAS({SectorCode}, DimCompany[sic_code])))

Sector Peer Count =
VAR SectorCode = SELECTEDVALUE(DimCompany[sic_code])
RETURN IF(HASONEVALUE(DimCompany[company_number]),
    CALCULATE([Scored Companies], REMOVEFILTERS(DimCompany),
        REMOVEFILTERS(FactReview[risk_band]),
        TREATAS({SectorCode}, DimCompany[sic_code])))

Display Sector Peer Mean = IF([Sector Peer Count] >= 100, [Sector Peer Mean], BLANK())

Snapshot Label = FORMAT(SELECTEDVALUE(DimDate[Date]), "dd mmm yyyy")
```

Sector and geographic rates use the same High Review % measure with the appropriate dimension in context. Never average subgroup percentages. To show benchmark peers nationally, disable geography interactions on the company investigation peer card or remove the geography filter deliberately; default above retains report context. The SQL peer export provides unconditional snapshot-wide peer means with a minimum sample size.

No Risk Score Change, Companies Entering High Risk, Historical Distress Rate, AUC or calibration measure is provided: this release cannot support them. DAX has been reviewed against the model specification but has not been executed in Power BI Desktop in this environment.
