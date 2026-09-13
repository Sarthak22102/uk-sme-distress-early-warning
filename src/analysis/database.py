from src.utils.security import sql_identifier
import re, sqlite3
from pathlib import Path
import pandas as pd

def load_database(df,f,s,reference,path='data/processed/platform.sqlite'):
    path=Path(path); path.parent.mkdir(parents=True,exist_ok=True)
    temp=path.with_suffix('.building.sqlite')
    temp.unlink(missing_ok=True)
    db=sqlite3.connect(temp)
    try:
        db.executescript(Path('database/schema.sql').read_text())
        def insert(name,frame):
            frame=frame.copy()
            for col in frame:
                if pd.api.types.is_datetime64_any_dtype(frame[col]): frame[col]=frame[col].dt.strftime('%Y-%m-%d')
            rows=frame.astype(object).where(frame.notna(),None).values.tolist()
            db.executemany(f'INSERT INTO {sql_identifier(name)} ({",".join(sql_identifier(c) for c in frame.columns)}) VALUES ({",".join("?" for _ in frame.columns)})',rows)
        insert('industry',df[['sic_code','industry_label']].drop_duplicates('sic_code'))
        g=df[['postcode_area']].drop_duplicates().copy(); g['geography_type']='Registered-office postcode area'; insert('geography',g)
        c=df[['company_number','company_name','incorporation_date','Accounts.AccountCategory','sic_code','postcode_area']].rename(columns={'Accounts.AccountCategory':'accounts_category'}); insert('companies',c)
        bridge=[]
        for _,row in df.iterrows():
            for pos in range(1,5):
                match=re.match(r'^(\d{5})',row[f'SICCode.SicText_{pos}'])
                if match: bridge.append((row.company_number,match[1],pos))
        insert('company_sic',pd.DataFrame(bridge,columns=['company_number','sic_code','position']))
        snap=df[['company_number','CompanyStatus','status_group']].rename(columns={'CompanyStatus':'company_status'}).copy(); snap['reference_date']=reference; insert('company_snapshots',snap)
        for name,cols in [('accounts_metadata',['accounts_due','accounts_made_up','confirmation_due','confirmation_made_up']),('charge_summary',['charge_count','outstanding_charges','part_satisfied_charges','satisfied_charges'])]:
            table=df[['company_number']+cols].copy(); table['reference_date']=reference; insert(name,table)
        insert('risk_features',f); insert('risk_scores',s)
        if db.execute('PRAGMA foreign_key_check').fetchall(): raise ValueError('Referential integrity failed')
        db.commit()
    finally: db.close()
    temp.replace(path)
