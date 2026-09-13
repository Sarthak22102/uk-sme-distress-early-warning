"""Download all official snapshot partitions; resumable by verified local ZIP cache."""
from src.utils.security import source_opener, snapshot_date, source_path, check_archive, require
import argparse
import hashlib
import json
import logging
import re
import time
import urllib.request
import zipfile
from datetime import datetime, timezone
from pathlib import Path

BASE = 'https://download.companieshouse.gov.uk/'

def download(destination, snapshot):
    snapshot_date(snapshot)
    opener = source_opener()
    destination = Path(destination)
    destination.mkdir(parents=True, exist_ok=True)
    with opener.open(BASE + 'en_output.html', timeout=60) as r:
        payload = r.read(1024*1024+1)
        require(len(payload)<=1024*1024, 'Index exceeds size limit')
        index = payload.decode()
    names = sorted(set(re.findall(r'BasicCompanyData-' + re.escape(snapshot) + r'-part\d+_\d+\.zip', index)))
    if not names:
        raise ValueError('Requested snapshot unavailable. Download archived files yourself or choose the current release explicitly.')
    expected = int(re.search(r'_(\d+)\.zip', names[0])[1])
    if len(names) != expected:
        raise ValueError('Incomplete partition listing')
    manifest = {'snapshot_label': snapshot, 'reference_date': str(__import__('datetime').date.fromisoformat(snapshot) - __import__('datetime').timedelta(days=1)), 'retrieved_at': datetime.now(timezone.utc).isoformat(), 'index_url': BASE + 'en_output.html', 'files': []}
    for name in names:
        path = source_path(destination, name, snapshot)
        if not path.exists():
            for attempt in range(4):
                try:
                    logging.info('Downloading %s', name)
                    require(not path.with_suffix('.partial').is_symlink(), 'Partial file must not be a symlink')
                    with opener.open(BASE + name, timeout=60) as r, path.with_suffix('.partial').open('wb') as f:
                        downloaded = 0
                        while chunk := r.read(1024 * 1024):
                            downloaded += len(chunk)
                            require(downloaded<=512*1024**2, 'Download exceeds partition size limit')
                            f.write(chunk)
                    path.with_suffix('.partial').replace(path)
                    break
                except Exception:
                    if attempt == 3:
                        raise
                    time.sleep(2 ** attempt)
        with zipfile.ZipFile(path) as z:
            check_archive(z)
            if z.testzip() is not None:
                raise ValueError('Corrupt ZIP: ' + name)
        digest = hashlib.file_digest(path.open('rb'), 'sha256').hexdigest()
        manifest['files'].append({'name': name, 'url': BASE + name, 'bytes': path.stat().st_size, 'sha256': digest})
        logging.info('Verified %s', name)
    (destination / 'manifest.json').write_text(json.dumps(manifest, indent=2))
    return manifest

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
    p = argparse.ArgumentParser()
    p.add_argument('--snapshot', required=True)
    p.add_argument('--destination', default='data/raw')
    args = p.parse_args()
    download(args.destination, args.snapshot)
