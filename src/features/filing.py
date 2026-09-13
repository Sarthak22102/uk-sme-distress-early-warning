import pandas as pd

def features(df,reference):
    ref=pd.Timestamp(reference)
    f=pd.DataFrame({'company_number':df.company_number,'reference_date':reference})
    f['age_years']=(ref-df.incorporation_date).dt.days/365.25
    f['incorporation_cohort']=df.incorporation_date.dt.year.astype('Int64')
    for prefix in ['accounts','confirmation']:
        f[prefix+'_overdue_days']=(ref-df[prefix+'_due']).dt.days.clip(lower=0).astype('Int64')
    f['deadline_coverage']=(df.accounts_due.notna().astype(int)+df.confirmation_due.notna().astype(int))/2
    f['score_eligible']=df.status_group.eq('active') & f.deadline_coverage.eq(1)
    f['exclusion_reason']=''
    f.loc[~df.status_group.eq('active'),'exclusion_reason']='Observed status requires separate review'
    f.loc[df.status_group.eq('active') & f.deadline_coverage.lt(1),'exclusion_reason']='Incomplete deadline data'
    return f
