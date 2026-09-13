// Create parameter DataFolder (Text) e.g. C:\Projects\uk-sme-distress-early-warning\data\processed\
// Create a blank query named LoadCsv containing this function:
(fileName as text) as table =>
let
    Source = Csv.Document(File.Contents(DataFolder & fileName), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    TextColumns = Table.TransformColumnTypes(Headers,List.Transform(Table.ColumnNames(Headers), each {_,type text}))
in TextColumns

// Separate query: DimCompany
// LoadCsv("companies.csv")
// Separate query: DimIndustry
// LoadCsv("industry.csv")
// Separate query: DimGeography
// LoadCsv("geography.csv")

// Separate query: FactReview (paste the following let block in its own query)
/*
let
    Source=LoadCsv("company_investigation.csv"),
    Nulls=Table.ReplaceValue(Source,"",null,Replacer.ReplaceValue,Table.ColumnNames(Source)),
    Types=Table.TransformColumnTypes(Nulls,{
        {"reference_date",type date},{"incorporation_date",type date},
        {"accounts_due",type date},{"confirmation_due",type date},
        {"accounts_made_up",type date},{"confirmation_made_up",type date},
        {"age_years",type number},{"incorporation_cohort",Int64.Type},
        {"accounts_overdue_days",Int64.Type},{"confirmation_overdue_days",Int64.Type},
        {"deadline_coverage",type number},{"score_eligible",Int64.Type},
        {"risk_score",type number},{"accounts_points",type number},{"confirmation_points",type number},
        {"charge_count",Int64.Type},{"outstanding_charges",Int64.Type}},"en-GB")
in Types
*/

// Separate query: DimDate
/*
let
    Dates=Table.Distinct(Table.SelectColumns(FactReview,{"reference_date"})),
    Renamed=Table.RenameColumns(Dates,{{"reference_date","Date"}})
in Renamed
*/
