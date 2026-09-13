# Security review — 13 September 2026

Scope: local Python analytics pipeline, optional Companies House API client, CSV output, source archive ingestion, dependency set, Git history and CI workflow. This is a targeted review and automated scan, not a penetration test or guarantee of vulnerability-free software.

## Fixes implemented

| Finding | Change | Validation |
|---|---|---|
| API authentication could be forwarded by urllib redirects | Reject redirects for API and bulk-source requests; restrict API endpoint paths | Cross-origin and HTTP-downgrade regression tests |
| Formula-like company text could be evaluated when CSV exports are opened in spreadsheet software | Prefix dangerous text with an apostrophe in presentation exports; preserve source/SQLite values | Prefix/control-character tests and unchanged aggregate results |
| Python assert-based validation could disappear with optimisation | Replace production asserts with explicit exceptions | Regression test executes the guard under python -O |
| Download, archive expansion and API-response processing were unbounded | Partition download, ZIP size/ratio/member, API response and pagination limits; capped retry delay | Synthetic expansion-bomb, oversized response and excessive-total tests |
| Local manifest names could traverse outside the raw-data folder | Strict monthly filenames, snapshot validation, path containment and source symlink rejection | Traversal and symlink tests |
| API event links missing from records could become a non-null JSON string | Require nonempty link dictionaries before identifier serialisation | Missing-links regression test |
| CI used mutable Action tags and implicit token defaults | Verified commit pins, contents:read, no persisted checkout credentials and timeout | Workflow inspection |
| Reproduction resolved a broad dependency range | Pin tested runtime and transitive packages in requirements-lock.txt; CI and setup use the lock | pip-audit checked all 14 pinned distributions |
| SQL identifier construction warranted stronger defence | Validate and quote internal identifiers; continue parameter-binding data values | Malicious identifier rejection test and full database rebuild |

## Scan evidence

- `dependency_audit.json`: pip-audit 2.10.1 queried the Python package advisory service for the 14 pinned distributions. No known vulnerabilities were reported on this review date. The scan used a complete pinned dependency list with `--no-deps --disable-pip`; it did not omit transitive runtime packages. Hash-based package verification is not implemented.
- `bandit.json`: Bandit 1.9.4 scanned production Python. Its remaining B608 findings concern internally controlled, validated SQL identifiers. No public data enters executable SQL; row values are parameter-bound. B404/B603 findings concern Git subprocess calls with fixed argument arrays, no shell, a resolved executable path and Git-generated object IDs. These warnings are retained for inspection rather than suppressed or represented as a clean static scan.
- `release_check.json`: regression tests, score reconciliation, local Markdown links, tracked-data checks and secret-pattern scans of files and Git history.
- The full pipeline was rebuilt after the changes; the analytical summary matches the previously validated release.

## Remaining boundaries

- No live API credential was supplied; live authenticated API integration remains untested. Redirects now fail closed, including legitimate redirects that would need deliberate review.
- Treat local repository code/configuration and the Git executable as trusted. This is a local analyst application, not a multi-tenant service or hosted lending API.
- Original input CSVs are untrusted ingestion files. Import their fields explicitly as text if investigating them; use escaped presentation exports for spreadsheet viewing. An apostrophe is visible in some CSV consumers. Database source values and all numeric metrics are unchanged.
- Download hashes provide provenance and local integrity, not an independently signed Companies House authenticity proof. HTTPS remains required.
- Known-vulnerability databases change. Re-run dependency and code scans after upgrades. This audit does not cover Python/OS binaries or demonstrate absence of undisclosed vulnerabilities.
- No real API key was provided, and no matching credential patterns were found. Pattern scans cannot recognise every possible secret format.

Publication target: https://github.com/Sarthak22102/uk-sme-distress-early-warning . The owner has created the repository; publication preserves the reviewed code and excludes company-level datasets.
