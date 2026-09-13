# Security and trusted use

See [the reviewed findings and remaining limitations](reports/security_review.md).

Install the tested dependency set with `python -m pip install -r requirements-lock.txt`. Re-run `python -m src.release_check` after changes. Keep API credentials in the environment and out of Git. Use the escaped presentation exports when opening data in spreadsheet software; raw input is retained for ingestion and provenance.

Do not publish credentials or personal data when reporting a problem. If GitHub private vulnerability reporting is enabled for the repository, use that channel for sensitive reports. This project is a local educational analytics application and must not independently determine high-impact decisions.
