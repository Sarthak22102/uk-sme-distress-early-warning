# Data layout and privacy

- raw/: official ZIP files and acquisition manifest; ignored by Git.
- input/: deterministic real-company sample and source/sampling manifest; ignored by Git. The delivery bundle includes these for a quick local rebuild, but they are not intended for public Git publication.
- processed/: reproducible SQLite database and dashboard-ready CSVs; ignored by Git.
- ../reports/: aggregate findings, benchmarks, quality and source manifest suitable for the portfolio repository.

No street addresses, full postcodes, personal officer information or API keys are needed in analysis exports. Source company names and identifiers are retained only in local investigation data. Public aggregate exports contain no company-level queues.

Run `python -m src.pipeline all` to obtain and analyse the configured release while it remains on the official download site. For the bundled sample use `python -m src.pipeline build`. The sample is real, not synthetic. Tests use synthetic fixtures solely under tests/.

The source is a rotating monthly publication. If the specified release is removed, exact full-source reproduction requires your saved source ZIPs with matching SHA256 digests; the supplied real sample still reproduces its analytical results. For a new release update config/project.json deliberately and regenerate all results. Do not combine results from different snapshots.
