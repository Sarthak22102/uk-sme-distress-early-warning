# Reproduce and refresh

## Requirements

Python 3.12 is the tested runtime. The implementation uses Python 3.11+ standard-library functionality. Dependencies are constrained in requirements.txt and the reviewed environment is pinned in requirements-lock.txt; tested direct versions are recorded in reports/environment.json. SQLite is bundled with Python. No database server or API key is required for the bulk analysis. A normal personal computer with several GB free disk space can run the chunked pipeline; no runtime/RAM benchmark is claimed.

## Setup

```bash
cd uk-sme-distress-early-warning
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-lock.txt
```

Windows PowerShell activation: `.venv\Scripts\Activate.ps1`.

## Quick rebuild from the delivered real sample

The delivery archive includes data/input/companies_sample.csv and its manifest; they remain ignored by Git.

```bash
python -m src.pipeline build
python -m unittest discover -s tests -v
python -m src.pipeline validate
```

Build cleans typed source fields, creates the database, derives features/scores, exports every table/query, generates findings/figures and runs reconciliation checks. The sample SHA256 is verified before use. It contains real official records with address minimisation, not synthetic examples.

## Full-source reproduction from a Git clone

```bash
python -m src.pipeline download
python -m src.pipeline sample
python -m src.pipeline build
python -m unittest discover -s tests -v
```

Or `python -m src.pipeline all`. Download all partitions. Download caching uses local ZIPs validated for CRC and SHA256 manifest provenance. The sampler verifies SHA256 again. Each partition is parsed into a temporary validated CSV, with malformed rows counted and fingerprinted; staging uses disk, then pandas chunks. No source-row truncation, first-part sampling or alphabetical sampling.

The official monthly URL rotates. If this release is unavailable, the downloader stops explicitly. Retain the downloaded ZIPs for exact source reproduction, or use the delivered sample. To refresh, change snapshot in config/project.json to an explicitly selected official release, regenerate all stages, review source schema/quality and rerun tests. No refreshed result should inherit the previous release's findings text.

## Additional commands

```bash
python -m src.pipeline export
python -m src.pipeline validate
```

Intermediate cleaning, features, scoring and loading are independently importable modules. The build orchestrator orders them consistently rather than requiring error-prone manual staging.

## Optional API investigation

Use a Companies House developer account to obtain an API key and set COMPANIES_HOUSE_API_KEY through an environment/secret manager. The project does not load .env files automatically. Never paste the key into chat or commit it. Then:

```bash
python -m src.pipeline enrich --company-number 00000001
```

Replace the number with a valid selected company. API extraction is date-cached after complete pagination, rate-limited and retried. Missing endpoints and changed collection totals fail explicitly. This optional client has mocked tests only; live authentication/enrichment was not run. The client uses endpoint links as stable charge identifiers when modern charge codes are unavailable. It is not connected to the score in this release.

## Power BI

Follow dashboard/build_instructions.md. Native Power BI execution requires Windows and was not available here. Source exports and SQL totals are validated; DAX, native rendering and report interactions require the specified Desktop checks.

## Run validity

A successful final build plus unit tests is the release gate. A later failed command invalidates the current attempted refresh; do not publish mixed old/new exports. Review reports/quality.json, reports/validation.json and reports/findings.md after each refresh. Rebuild outputs rather than editing CSVs by hand.

Security: presentation CSV exports prefix formula-like text with an apostrophe. Original values remain in the SQLite database and checksum-verified input sample. Treat raw/input CSV as untrusted ingestion files, not spreadsheets to double-click.
