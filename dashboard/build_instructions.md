# Build the native Power BI report

1. On Windows, install current Power BI Desktop from Microsoft's official download page. On macOS use an authorised Windows environment; the pipeline itself runs on macOS/Linux/Windows.
2. Reproduce the project with Python. Confirm reports/validation.json passes and keep reports/summary.json open for reconciliation.
3. Open a blank report. Disable auto date/time. Create the DataFolder text parameter ending with a path separator.
4. Open Transform Data → New Source → Blank Query. Paste the LoadCsv function from power_query.m, naming the query LoadCsv. It is a function, not one large combined M script.
5. Add three dimension queries with the separate expressions indicated in power_query.m. Preserve all identifiers as Text.
6. Add FactReview from its separate let block, then DimDate from its separate let block. Confirm null numeric values stay null. Close & Apply.
7. Create exactly the four relationships in data_model.md. Confirm both key sides are Text except DimDate and reference_date, which are Date.
8. Create measures one at a time from dax_measures.md; apply formats. Avoid summing raw risk_score.
9. Set the colour theme from theme.json. Build the six pages using dashboard_specification.md and wireframes.png.
10. Add primary SIC and postcode-area slicers from dimensions; reference-date slicer is single-select. Configure interactions and drill-through as specified.
11. Validate native totals, filters, empty states and company cards with the checklist. The exported PNG is a Python-rendered design reference using actual data, not a Power BI screenshot.
12. Save as uk-sme-distress-early-warning.pbix. Publish to Power BI Service only if you choose to share company-level data and have the required licence. Do not add the raw register ZIPs to GitHub.

Source: https://learn.microsoft.com/en-us/power-bi/fundamentals/desktop-get-the-desktop
