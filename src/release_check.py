"""Release gates: tests, arithmetic, local links, tracked-data and secret-pattern checks.
Pattern scans reduce risk but do not prove absence of every possible secret format.
"""
from src.utils.security import require
import io,json,re,subprocess,unittest,shutil
from pathlib import Path
from src.pipeline import validate

PATTERNS=[re.compile(r'gh[pousr]_[A-Za-z0-9]{30,}'),re.compile(r'github_pat_[A-Za-z0-9_]{30,}'),re.compile(r'sk-[A-Za-z0-9_-]{30,}'),re.compile(r'-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----'),re.compile(r'(?m)^COMPANIES_HOUSE_API_KEY\s*=\s*\S+')]

def secret_scan(content,label):
    for pattern in PATTERNS:
        if pattern.search(content):raise ValueError('Potential credential detected in '+label)

def main():
    root=Path.cwd()
    git_binary=shutil.which('git')
    require(git_binary is not None, 'Git executable is required for release checks')
    require((root/'config/project.json').exists(), 'Run from repository root')
    validate()
    suite=unittest.defaultTestLoader.discover('tests')
    stream=io.StringIO();result=unittest.TextTestRunner(stream=stream,verbosity=1).run(suite)
    if not result.wasSuccessful():raise ValueError(stream.getvalue())
    candidates=[]
    for path in root.rglob('*'):
        if not path.is_file() or any(part in {'.git','.venv','__pycache__'} for part in path.relative_to(root).parts):continue
        if path.suffix in {'.py','.sql','.json','.md','.yml','.m','.txt'} or path.name=='.env.example':
            if path.is_relative_to(root/'data'):continue
            secret_scan(path.read_text(),str(path.relative_to(root)));candidates.append(path)
    broken=[];link_count=0
    for path in candidates:
        if path.suffix!='.md':continue
        for target in re.findall(r'!?\[[^\]]*\]\(([^)]+)\)',path.read_text()):
            if target.startswith(('https:','http:','#','mailto:')):continue
            link_count+=1
            if not (path.parent/target.split('#')[0]).exists():broken.append((str(path),target))
    if broken:raise ValueError('Broken local Markdown links: '+repr(broken))
    history_blobs=0;tracked_count=0
    if (root/'.git').exists():
        tracked=subprocess.check_output([git_binary,'ls-files','-z']).decode().split('\0')
        for name in filter(None,tracked):
            tracked_count+=1
            if name.startswith(('data/raw/','data/input/','data/processed/')) and not name.endswith('.gitkeep'):raise ValueError('Company-level data tracked: '+name)
            if Path(name).name.startswith('.env') and Path(name).name!='.env.example':raise ValueError('Environment secret file tracked')
        commits=subprocess.run([git_binary,'rev-parse','--verify','HEAD'],capture_output=True)
        if commits.returncode==0:
            for entry in subprocess.check_output([git_binary,'rev-list','--objects','--all']).decode().splitlines():
                sha=entry.split(' ',1)[0]
                kind=subprocess.check_output([git_binary,'cat-file','-t',sha]).decode().strip()
                if kind=='blob':
                    blob=subprocess.check_output([git_binary,'cat-file','-p',sha]);history_blobs+=1
                    try:secret_scan(blob.decode('utf-8'),sha)
                    except UnicodeDecodeError:pass
    receipt={'decision':'Ready within validated bulk-analysis scope; native Power BI and live API remain unverified','tests_run':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'skipped':len(result.skipped),'local_markdown_links_checked':link_count,'source_files_scanned_for_secret_patterns':len(candidates),'tracked_files_checked':tracked_count,'git_history_blobs_scanned':history_blobs,'credential_scan':'No matching credential patterns; no real API key was provided','publication':'GitHub target: https://github.com/Sarthak22102/uk-sme-distress-early-warning','external_links':'Core official references verified during research; rotating downloads and target repository availability can change'}
    print(json.dumps(receipt,indent=2))
    Path('reports/release_check.json').write_text(json.dumps(receipt,indent=2))

if __name__=='__main__':main()
