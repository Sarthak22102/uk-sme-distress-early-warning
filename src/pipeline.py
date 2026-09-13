"""CLI orchestrator. Each stage is explicit; `build` starts from a real input sample."""
from src.utils.security import require, safe_frame, sql_identifier
import argparse,json,logging,sqlite3,sys,hashlib
from pathlib import Path
import pandas as pd
from src.ingestion.bulk import download
from src.ingestion.sample import sample
from src.cleaning.companies import clean
from src.features.filing import features
from src.scoring.index import score
from src.analysis.database import load_database

def build():
    config=json.loads(Path('config/project.json').read_text())
    manifest=json.loads(Path('data/input/manifest.json').read_text())
    if manifest['snapshot_label']!=config['snapshot']: raise ValueError('Config/source snapshot mismatch')
    if hashlib.sha256(Path('data/input/companies_sample.csv').read_bytes()).hexdigest()!=manifest['sample_sha256']: raise ValueError('Sample checksum mismatch')
    reference=manifest['reference_date']
    df=pd.read_csv('data/input/companies_sample.csv',dtype=str,keep_default_na=False)
    cleaned,quality=clean(df,reference)
    f=features(cleaned,reference); s=score(f,config)
    load_database(cleaned,f,s,reference)
    Path('reports').mkdir(exist_ok=True)
    quality.update({'input_rows':len(df),'feature_rows':len(f),'score_rows':len(s),'scored_companies':int(s.risk_score.notna().sum()),'source_malformed_rows':manifest['malformed_rows'],'api_enrichment':'not used; credentials not supplied'})
    Path('reports/quality.json').write_text(json.dumps(quality,indent=2))
    Path('reports/source_manifest.json').write_text(json.dumps(manifest,indent=2))
    export()
    from src.analysis.report import analyse
    analyse()
    validate()
    from src.analysis.documentation import generate
    generate()
    from src.analysis.wireframes import generate as wireframes
    wireframes()
    logging.info('Build, analysis and validation complete')

def export():
    out=Path('data/processed');out.mkdir(exist_ok=True)
    with sqlite3.connect(out/'platform.sqlite') as db:
        for table in ['companies','industry','geography','company_sic','company_snapshots','accounts_metadata','charge_summary','risk_features','risk_scores','company_investigation']:
            safe_frame(pd.read_sql_query('SELECT * FROM '+sql_identifier(table),db)).to_csv(out/(table+'.csv'),index=False)
        for sql in sorted(Path('sql').glob('*.sql')):
            safe_frame(pd.read_sql_query(sql.read_text(),db)).to_csv(out/(sql.stem+'.csv'),index=False)

def validate():
    config=json.loads(Path('config/project.json').read_text())
    with sqlite3.connect('data/processed/platform.sqlite') as db:
        db.execute('PRAGMA foreign_keys=ON')
        require(not db.execute('PRAGMA foreign_key_check').fetchall(), "Validation failed: not db.execute('PRAGMA foreign_key_check').fetchall()")
        df=pd.read_sql_query('SELECT * FROM company_investigation',db)
        require(len(df)==df.company_number.nunique(), 'Validation failed: len(df)==df.company_number.nunique()')
        # Independent SQL recalculation from raw due dates, not Python feature columns.
        errors=db.execute('''SELECT COUNT(*) FROM company_investigation WHERE score_eligible=1 AND ABS(risk_score - ROUND(?*MIN(?,MAX(0,julianday(reference_date)-julianday(accounts_due)))/? + ?*MIN(?,MAX(0,julianday(reference_date)-julianday(confirmation_due)))/?,2))>0.011''',(float(config['accounts_weight']),config['accounts_cap_days'],float(config['accounts_cap_days']),float(config['confirmation_weight']),config['confirmation_cap_days'],float(config['confirmation_cap_days']))).fetchone()[0]
        require(errors==0, 'SQL/Python score disagreement')
        band_errors=db.execute("SELECT COUNT(*) FROM risk_scores WHERE risk_band != CASE WHEN risk_score IS NULL THEN 'Not scored' WHEN risk_score=0 THEN 'No flagged deadline' WHEN risk_score<? THEN 'Watch' WHEN risk_score<? THEN 'Elevated review' ELSE 'High review' END",(config['watch_threshold'],config['high_threshold'])).fetchone()[0]
        require(band_errors==0, 'Risk band mismatch')
        for filename in ['02_geographic_review','03_lifecycle_cohorts']:
            require(int(pd.read_csv('data/processed/'+filename+'.csv').companies.sum())==len(df), 'Grouped totals mismatch')
        require(df.loc[df.status_group.ne('active'),'risk_score'].isna().all(), "Validation failed: df.loc[df.status_group.ne('active'),'risk_score'].isna().all()")
        require(df.loc[df.deadline_coverage.lt(1),'risk_score'].isna().all(), "Validation failed: df.loc[df.deadline_coverage.lt(1),'risk_score'].isna().all()")
        require(df.risk_score.dropna().between(0,100).all(), 'Validation failed: df.risk_score.dropna().between(0,100).all()')
        sectors=pd.read_csv('data/processed/01_sector_review.csv')
        require(int(sectors.companies.sum())==len(df), 'Validation failed: int(sectors.companies.sum())==len(df)')
        require(int(sectors.high_review.sum())==int(df.risk_band.eq('High review').sum()), "Validation failed: int(sectors.high_review.sum())==int(df.risk_band.eq('High review').sum())")
        require(len(pd.read_csv('data/processed/company_investigation.csv'))==len(df), "Validation failed: len(pd.read_csv('data/processed/company_investigation.csv'))==len(df)")
        require(df.reference_date.nunique()==1, 'Validation failed: df.reference_date.nunique()==1')
        transitions=pd.read_csv('data/processed/07_snapshot_transitions.csv')
        require(transitions.previous_score.isna().all(), 'Validation failed: transitions.previous_score.isna().all()')
        result={'foreign_keys':'pass','company_grain':'pass','sql_python_score_reconciliation':'pass','score_exclusions':'pass','score_range':'pass','band_assignment':'pass','geography_and_cohort_totals':'pass','sector_reconciliation':'pass','export_reconciliation':'pass','single_snapshot_no_change_claims':'pass','live_api':'not executed','native_power_bi':'build pack only; not runtime validated'}
        Path('reports/validation.json').write_text(json.dumps(result,indent=2))
    return result

def main():
    logging.basicConfig(level=logging.INFO,format='%(asctime)s %(levelname)s %(message)s')
    p=argparse.ArgumentParser();p.add_argument('command',choices=['download','sample','build','export','validate','all','enrich']);p.add_argument('--company-number')
    args=p.parse_args(); config=json.loads(Path('config/project.json').read_text())
    if args.command in ['download','all']: download('data/raw',config['snapshot'])
    if args.command in ['sample','all']: sample(size=config['sample_size'],seed=config['seed'])
    if args.command in ['build','all']: build()
    if args.command=='export': export()
    if args.command=='validate': print(json.dumps(validate(),indent=2))
    if args.command=='enrich':
        if not args.company_number: p.error('--company-number required')
        from src.ingestion.api import CompaniesHouseClient
        CompaniesHouseClient().enrich(args.company_number)

if __name__=='__main__':
    try: main()
    except Exception:
        logging.exception('Pipeline failed; outputs are not approved for release')
        sys.exit(1)
