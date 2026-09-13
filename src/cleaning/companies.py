"""Typed, loss-aware cleaning. Future deadlines are valid; future observations are not."""
import re
import pandas as pd

DATE_MAP={'IncorporationDate':'incorporation_date','DissolutionDate':'dissolution_date','Accounts.NextDueDate':'accounts_due','Accounts.LastMadeUpDate':'accounts_made_up','ConfStmtNextDueDate':'confirmation_due','ConfStmtLastMadeUpDate':'confirmation_made_up'}
STATUS_GROUPS={'Active':'active','Active - Proposal to Strike off':'strike_off_proposal','Liquidation':'liquidation_unspecified','In Administration':'administration','In Administration/Administrative Receiver':'administration','ADMINISTRATION ORDER':'administration','Voluntary Arrangement':'voluntary_arrangement','Live but Receiver Manager on at least one charge':'receivership','Dissolved':'dissolved','RECEIVERSHIP':'receivership'}

def clean(df, reference):
    df=df.copy()
    df.columns=df.columns.str.strip()
    issues={}
    for col in df: df[col]=df[col].fillna('').astype(str).str.strip()
    if df.CompanyNumber.duplicated().any(): raise ValueError('Duplicate company number')
    valid=df.CompanyNumber.str.fullmatch(r'(?:[0-9]{8}|[A-Z]{2}[0-9]{6}|R[0-9]{7})')
    issues['invalid_company_numbers']=int((~valid).sum())
    if not valid.all(): raise ValueError('Invalid company numbers')
    for source,target in DATE_MAP.items():
        date=pd.to_datetime(df[source],format='%d/%m/%Y',errors='coerce')
        issues['invalid_'+target]=int((df[source].ne('') & date.isna()).sum())
        df[target]=date
    ref=pd.Timestamp(reference)
    for col in ['incorporation_date','dissolution_date','accounts_made_up','confirmation_made_up']:
        bad=df[col].gt(ref)
        issues['future_'+col]=int(bad.sum())
        df.loc[bad,col]=pd.NaT
    issues['missing_incorporation_date']=int(df.incorporation_date.isna().sum())
    df['status_group']=df.CompanyStatus.map(STATUS_GROUPS).fillna('unmapped')
    issues['unmapped_statuses']=df.loc[df.status_group.eq('unmapped'),'CompanyStatus'].value_counts().to_dict()
    for old,new in [('Mortgages.NumMortCharges','charge_count'),('Mortgages.NumMortOutstanding','outstanding_charges'),('Mortgages.NumMortPartSatisfied','part_satisfied_charges'),('Mortgages.NumMortSatisfied','satisfied_charges')]:
        values=pd.to_numeric(df[old],errors='coerce')
        invalid=values.isna()|values.lt(0)|values.mod(1).ne(0)
        issues['invalid_'+new]=int(invalid.sum())
        df[new]=values.mask(invalid)
    issues['charge_components_exceed_total']=int((df.outstanding_charges+df.part_satisfied_charges+df.satisfied_charges>df.charge_count).sum())
    issues['dissolution_before_incorporation']=int((df.dissolution_date<df.incorporation_date).sum())
    for col in ['accounts_made_up','confirmation_made_up']:
        issues[col+'_before_incorporation']=int((df[col]<df.incorporation_date).sum())
    issues['missing_accounts_due']=int(df.accounts_due.isna().sum())
    issues['missing_confirmation_due']=int(df.confirmation_due.isna().sum())
    issues['unknown_postcode_area']=int(df.postcode_area.eq('Unknown').sum())
    issues['duplicate_company_numbers']=int(df.CompanyNumber.duplicated().sum())
    df['company_number']=df.CompanyNumber
    df['company_name']=df.CompanyName
    df['sic_code']=df['SICCode.SicText_1'].str.extract(r'^(\d{5})',expand=False).fillna('Unknown')
    df['industry_label']=df['SICCode.SicText_1'].str.replace(r'^\d{5}\s*-\s*','',regex=True).replace('','Unknown')
    issues['missing_or_unparseable_primary_sic']=int(df.sic_code.eq('Unknown').sum())
    return df,issues
