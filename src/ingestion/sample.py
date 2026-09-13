"""Order-independent bottom-k hash sample from every eligible register partition."""
from src.utils.security import require, source_path, check_archive
import hashlib, json, logging, zipfile, csv, io, tempfile
from pathlib import Path
import pandas as pd

CATEGORIES = ['MICRO ENTITY', 'SMALL', 'MEDIUM', 'TOTAL EXEMPTION SMALL']
KEEP = ['CompanyName','CompanyNumber','CompanyCategory','CompanyStatus','CountryOfOrigin','IncorporationDate','DissolutionDate','Accounts.NextDueDate','Accounts.LastMadeUpDate','Accounts.AccountCategory','ConfStmtNextDueDate','ConfStmtLastMadeUpDate','Mortgages.NumMortCharges','Mortgages.NumMortOutstanding','Mortgages.NumMortPartSatisfied','Mortgages.NumMortSatisfied','SICCode.SicText_1','SICCode.SicText_2','SICCode.SicText_3','SICCode.SicText_4','RegAddress.PostCode']

def sample(raw='data/raw', output='data/input', size=30000, seed=22102):
    raw, output = Path(raw), Path(output)
    output.mkdir(parents=True, exist_ok=True)
    manifest=json.loads((raw/'manifest.json').read_text())
    counts={'source_rows':0,'malformed_rows':0,'malformed_fingerprints':[], 'rows_scanned':0,'eligible_rows':0,'categories':{},'statuses':{}}
    best=pd.DataFrame()
    for f in manifest['files']:
        path=source_path(raw,f['name'],manifest['snapshot_label'])
        with path.open('rb') as stream:
            require(hashlib.file_digest(stream,'sha256').hexdigest()==f['sha256'], 'Source checksum changed')
        with zipfile.ZipFile(path) as z:
            check_archive(z)
            for member in z.namelist():
                if not member.lower().endswith('.csv'): continue
                with tempfile.TemporaryFile(mode='w+',encoding='utf-8',newline='') as staged:
                    writer=csv.writer(staged)
                    with z.open(member) as stream:
                        reader=csv.reader(io.TextIOWrapper(stream,encoding='utf-8-sig'))
                        header=next(reader); width=len(header); writer.writerow(header)
                        for row in reader:
                            counts['source_rows']+=1
                            if len(row)!=width:
                                counts['malformed_rows']+=1
                                counts['malformed_fingerprints'].append(hashlib.sha256(json.dumps(row).encode()).hexdigest())
                            else: writer.writerow(row)
                    staged.seek(0)
                    for df in pd.read_csv(staged,dtype=str,keep_default_na=False,chunksize=100000):
                        df.columns=df.columns.str.strip()
                        if not set(KEEP).issubset(df): raise ValueError('Source schema drift: missing expected columns')
                        counts['rows_scanned']+=len(df)
                        for col,key in [('Accounts.AccountCategory','categories'),('CompanyStatus','statuses')]:
                            for k,v in df[col].value_counts().items(): counts[key][k]=counts[key].get(k,0)+int(v)
                        df=df.loc[df['CompanyCategory'].eq('Private Limited Company') & df['CountryOfOrigin'].eq('United Kingdom') & df['Accounts.AccountCategory'].isin(CATEGORIES),KEEP].copy()
                        counts['eligible_rows']+=len(df)
                        df['sample_key']=df.CompanyNumber.map(lambda n: hashlib.sha256(f'{seed}:{n}'.encode()).hexdigest())
                        # Only retain postcode area; discard precise addresses and postcode immediately.
                        df['postcode_area']=df.pop('RegAddress.PostCode').str.upper().str.extract(r'^([A-Z]{1,2})\d',expand=False).fillna('Unknown')
                        best=pd.concat([best,df],ignore_index=True).sort_values(['sample_key','CompanyNumber']).head(size)
        logging.info('Scanned %s; eligible %s',f['name'],counts['eligible_rows'])
    if counts['source_rows']-counts['malformed_rows']!=counts['rows_scanned']: raise ValueError('Source row reconciliation failed')
    if best.CompanyNumber.duplicated().any(): raise ValueError('Duplicate sampled company numbers; investigate source before proceeding')
    best.sort_values('CompanyNumber').to_csv(output/'companies_sample.csv',index=False)
    manifest.update(counts)
    manifest.update({'sample_sha256':hashlib.sha256((output/'companies_sample.csv').read_bytes()).hexdigest(),'sample_size':len(best),'seed':seed,'sample_method':'smallest SHA256(seed:company_number), all partitions','proxy_categories':CATEGORIES})
    (output/'manifest.json').write_text(json.dumps(manifest,indent=2))
    return manifest
