# GitHub publication and future updates

Repository: https://github.com/Sarthak22102/uk-sme-distress-early-warning

The owner created the public repository. The reviewed project is prepared for publication onto its existing main branch, preserving the initial commit. Public Git includes code, documentation, aggregate reports and previews. Raw, input and processed company-level datasets are excluded from tracking.

## Reproduce from GitHub

```bash
git clone https://github.com/Sarthak22102/uk-sme-distress-early-warning.git
cd uk-sme-distress-early-warning
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-lock.txt
python -m src.pipeline all
python -m src.release_check
```

The monthly source rotates; see reproduce.md for archived-source requirements. A clone does not contain the private delivery sample. The Power BI deliverable is a build pack, not a native PBIX.

## Future contributions

Use a fresh clone of the published repository, create a feature branch, inspect changes and submit a pull request. The earlier delivery archive has separate local development history: do not force-push it over the published branch. Authenticate securely through GitHub CLI or Git Credential Manager; do not paste tokens into chat.

Never force-add data folders or API credentials. Re-run security and analytical checks before merging changes.
