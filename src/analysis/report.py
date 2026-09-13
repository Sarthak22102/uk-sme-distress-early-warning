"""Evidence-backed descriptive analysis, robustness checks and reproducible figures."""
from src.utils.security import safe_frame
import json, math, sqlite3, textwrap
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter

def wilson(k,n):
    if not n:return (None,None)
    z=1.95996398454;p=k/n;den=1+z*z/n
    centre=(p+z*z/(2*n))/den
    half=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/den
    return centre-half,centre+half

def analyse():
    reports=Path('reports');figs=Path('dashboard/screenshots');figs.mkdir(parents=True,exist_ok=True)
    config=json.loads(Path('config/project.json').read_text())
    manifest=json.loads(Path('data/input/manifest.json').read_text())
    with sqlite3.connect('data/processed/platform.sqlite') as db: df=pd.read_sql_query('SELECT * FROM company_investigation',db)
    eligible=df[df.risk_score.notna()].copy()
    outlier_rows=[]
    for column in ['age_years','charge_count','outstanding_charges','accounts_overdue_days','confirmation_overdue_days']:
        values=df[column].dropna()
        outlier_rows.append({'field':column,'observed_n':len(values),'missing_n':int(df[column].isna().sum()),'min':float(values.min()),'median':float(values.median()),'p95':float(values.quantile(.95)),'p99':float(values.quantile(.99)),'max':float(values.max()),'treatment':'Retained; contextual outlier is not automatically erroneous'})
    pd.DataFrame(outlier_rows).to_csv(reports/'outlier_profile.csv',index=False)

    sector=pd.read_csv('data/processed/01_sector_review.csv')
    geo=pd.read_csv('data/processed/02_geographic_review.csv')
    for table,name in [(sector,'sector_benchmarks'),(geo,'geographic_benchmarks')]:
        intervals=[wilson(k,n) for k,n in zip(table.high_review,table.scored_companies)]
        table['wilson_lower']=[v[0] for v in intervals];table['wilson_upper']=[v[1] for v in intervals]
        safe_frame(table).to_csv(f'data/processed/{name}.csv',index=False)
        safe_frame(table).to_csv(reports/(name+'.csv'),index=False)
    top_sector=sector[sector.scored_companies.ge(100)].sort_values(['high_review_rate','sic_code'],ascending=[False,True]).head(1)
    top_geo=geo[geo.scored_companies.ge(100)&geo.postcode_area.ne('Unknown')].sort_values(['high_review_rate','postcode_area'],ascending=[False,True]).head(1)
    summary={'reference_date':manifest['reference_date'],'source_rows':manifest['source_rows'],'malformed_rows':manifest['malformed_rows'],'eligible_population':manifest['eligible_rows'],'companies_analysed':len(df),'scored_companies':len(eligible),'not_scored':int(df.risk_score.isna().sum()),'high_review':int(eligible.risk_band.eq('High review').sum()),'elevated_review':int(eligible.risk_band.eq('Elevated review').sum()),'watch':int(eligible.risk_band.eq('Watch').sum()),'no_flagged_deadline':int(eligible.risk_score.eq(0).sum()),'mean_score':float(eligible.risk_score.mean()),'median_score':float(eligible.risk_score.median()),'accounts_overdue':int(eligible.accounts_overdue_days.gt(0).sum()),'confirmation_overdue':int(eligible.confirmation_overdue_days.gt(0).sum()),'both_overdue':int((eligible.accounts_overdue_days.gt(0)&eligible.confirmation_overdue_days.gt(0)).sum()),'status_counts':{k:int(v) for k,v in df.status_group.value_counts().items()},'top_sector':top_sector.to_dict('records'),'top_postcode_area':top_geo.to_dict('records')}
    summary['high_review_share']=summary['high_review']/len(eligible)
    (reports/'summary.json').write_text(json.dumps(summary,indent=2))
    # Predeclared sensitivity variants. Actual overlap and review workload, not model metrics.
    base=set(eligible.loc[eligible.risk_score.ge(70),'company_number'])
    robustness=[]
    for weight in [40,50,60,70,80]:
        alt=weight*eligible.accounts_overdue_days.clip(upper=180)/180+(100-weight)*eligible.confirmation_overdue_days.clip(upper=90)/90
        selected=set(eligible.loc[alt.round(2).ge(70),'company_number'])
        robustness.append({'accounts_weight':weight,'confirmation_weight':100-weight,'threshold':70,'review_count':len(selected),'jaccard_vs_base':len(base&selected)/len(base|selected) if base|selected else 1})
    for threshold in [50,60,80,90]:
        selected=set(eligible.loc[eligible.risk_score.ge(threshold),'company_number'])
        robustness.append({'accounts_weight':60,'confirmation_weight':40,'threshold':threshold,'review_count':len(selected),'jaccard_vs_base':len(base&selected)/len(base|selected) if base|selected else 1})
    pd.DataFrame(robustness).to_csv(reports/'sensitivity.csv',index=False)
    # Leave-one-signal-out prevents interpreting constructed score associations as discoveries.
    relationship=[]
    for a in [False,True]:
        sub=eligible[eligible.accounts_overdue_days.gt(0).eq(a)]
        k=int(sub.confirmation_overdue_days.gt(0).sum());n=len(sub);lo,hi=wilson(k,n)
        relationship.append({'accounts_overdue':a,'companies':n,'confirmation_overdue':k,'confirmation_overdue_share':k/n if n else None,'wilson_lower':lo,'wilson_upper':hi})
    pd.DataFrame(relationship).to_csv(reports/'deadline_association.csv',index=False)
    rr=(relationship[1]['confirmation_overdue']/relationship[1]['companies'])/(relationship[0]['confirmation_overdue']/relationship[0]['companies'])
    se=math.sqrt(1/relationship[1]['confirmation_overdue']-1/relationship[1]['companies']+1/relationship[0]['confirmation_overdue']-1/relationship[0]['companies'])
    association={'risk_ratio':rr,'log_wald_lower':math.exp(math.log(rr)-1.959964*se),'log_wald_upper':math.exp(math.log(rr)+1.959964*se),'interpretation':'Cross-sectional confirmation-delay prevalence ratio; not financial distress or causation'}
    (reports/'association_summary.json').write_text(json.dumps(association,indent=2))
    # Standardise major sectors to the sample's age mix (descriptive, not causal adjustment).
    eligible['age_band']=pd.cut(eligible.age_years,[-np.inf,5,10,20,np.inf],labels=['0-5','5-10','10-20','20+'],right=False)
    age_weights=eligible.age_band.value_counts(normalize=True,sort=False)
    adjusted=[]
    for sic,sub in eligible.groupby('sic_code'):
        if len(sub)<100:continue
        cells=sub.groupby('age_band',observed=False).agg(n=('company_number','size'),high=('risk_band',lambda s:int(s.eq('High review').sum())))
        complete=bool(cells.n.ge(10).all())
        adjusted.append({'sic_code':sic,'n':len(sub),'crude_high_share':float(sub.risk_band.eq('High review').mean()),'age_standardised_high_share':float(((cells.high/cells.n)*age_weights).sum()) if complete else None,'adequate_age_cells':complete})
    pd.DataFrame(adjusted).to_csv(reports/'age_standardised_sectors.csv',index=False)
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.spines.top':False,'axes.spines.right':False,'axes.labelcolor':'#25354a','text.color':'#182c44'})
    fig=plt.figure(figsize=(16,10),facecolor='#f7f9fc')
    fig.text(.055,.945,'UK SME Distress Early-Warning',fontsize=25,weight='bold')
    fig.text(.055,.908,f'Filing review intelligence  |  {summary["reference_date"]}  |  Accounts-category proxy',fontsize=12,color='#52657c')
    metrics=[('Companies analysed',f'{len(df):,}'),('Scored active companies',f'{len(eligible):,}'),('High review priority',f'{summary["high_review"]:,}'),('High review share',f'{summary["high_review_share"]:.2%}')]
    for i,(label,value) in enumerate(metrics):
        x=.055+i*.24;fig.text(x,.845,value,fontsize=25,weight='bold');fig.text(x,.811,label,fontsize=11,color='#52657c')
    ax=fig.add_axes([.17,.43,.275,.30]);bands=['No flagged deadline','Watch','Elevated review','High review'];counts=[int(eligible.risk_band.eq(x).sum()) for x in bands]
    ax.barh(bands[::-1],counts[::-1],color=['#8f365a','#c28023','#587b9e','#1d5e86']);ax.set_title('Review workload',loc='left',weight='bold');ax.set_xlabel('Scored companies')
    for j,v in enumerate(counts[::-1]):ax.text(v+max(counts)*.015,j,f'{v:,}',va='center',fontsize=10)
    ax.set_xlim(0,max(counts)*1.2)
    ax=fig.add_axes([.59,.43,.35,.30]);top=sector[sector.scored_companies.ge(100)].sort_values('high_review_rate',ascending=False).head(6).iloc[::-1]
    ax.barh(top.sic_code.astype(str),top.high_review_rate,color='#1d5e86');ax.set_title('High review share by SIC (95% Wilson)' ,loc='left',weight='bold');ax.xaxis.set_major_formatter(PercentFormatter(1));ax.set_xlabel('Scored companies; minimum 100 per SIC')
    ax.errorbar(top.high_review_rate,range(len(top)),xerr=[top.high_review_rate-top.wilson_lower,top.wilson_upper-top.high_review_rate],fmt='none',ecolor='#25354a',capsize=3)
    ax=fig.add_axes([.075,.115,.37,.22]);ax.hist(eligible.risk_score,bins=np.arange(0,105,5),color='#1d5e86',rwidth=.95);ax.set_title('Score distribution',loc='left',weight='bold');ax.set_xlabel('Policy index (0–100)');ax.set_ylabel('Companies')
    ax=fig.add_axes([.59,.115,.35,.22]);top=geo[geo.scored_companies.ge(100)&geo.postcode_area.ne('Unknown')].sort_values('high_review_rate',ascending=False).head(5).iloc[::-1];ax.barh(top.postcode_area,top.high_review_rate,color='#1d5e86');ax.set_title('Registered-office postcode areas',loc='left',weight='bold');ax.xaxis.set_major_formatter(PercentFormatter(1));ax.set_xlabel('High review share; minimum 100 scored')
    fig.text(.055,.038,'Reference visual generated in Python • Power BI build pack supplied • Not a failure probability or lending recommendation',fontsize=10,color='#52657c')
    fig.savefig(figs/'executive_preview.png',dpi=150);plt.close(fig)
    ts=summary['top_sector'][0];tg=summary['top_postcode_area'][0]
    report=f'''# Findings from the completed analysis

Reference date: {summary['reference_date']}. These are sample observations, not UK SME population estimates.

- Scanned {summary['source_rows']:,} source rows across every partition; quarantined {summary['malformed_rows']:,} malformed records. The accounts-category proxy contained {summary['eligible_population']:,} eligible rows; the deterministic sample contains {len(df):,} companies.
- {len(eligible):,} active companies have both deadlines and are scored; {summary['not_scored']:,} records remain unscored because of observed status or incomplete deadline information.
- {summary['high_review']:,} companies ({summary['high_review_share']:.2%} of scored companies) meet the policy's high-review threshold. {summary['elevated_review']:,} are elevated review, {summary['watch']:,} watch and {summary['no_flagged_deadline']:,} have no flagged deadline. No flagged deadline does not mean financially healthy.
- {summary['accounts_overdue']:,} scored companies show an accounts deadline before the reference date; {summary['confirmation_overdue']:,} show an overdue confirmation deadline; {summary['both_overdue']:,} show both.
- The largest observed high-review share among primary SIC groups with at least 100 scored companies is {ts['sic_code']} ({ts['industry_label']}): {ts['high_review']:,}/{ts['scored_companies']:,}, or {ts['high_review_rate']:.2%}. This is a descriptive ranking with multiple-comparison and sector-composition caveats.
- Registered-office postcode area {tg['postcode_area']} has the largest observed share among eligible areas: {tg['high_review']:,}/{tg['scored_companies']:,}, or {tg['high_review_rate']:.2%}. This is not an operating-region measure or a population-density statistic.

## Analytical interpretation

Confirmation deadlines are overdue for {relationship[1]['confirmation_overdue']:,}/{relationship[1]['companies']:,} companies with an accounts delay ({relationship[1]['confirmation_overdue_share']:.2%}), compared with {relationship[0]['confirmation_overdue']:,}/{relationship[0]['companies']:,} without one ({relationship[0]['confirmation_overdue_share']:.2%}). The cross-sectional prevalence ratio is {rr:.2f} (approximate 95% log-Wald interval {association['log_wald_lower']:.2f}–{association['log_wald_upper']:.2f}). This supports investigating clustered filing problems; it does not demonstrate financial distress or causal direction.

The leading sector has only {ts['high_review']:,} high-review observations and the leading postcode area only {tg['high_review']:,}. Those descriptive rankings are fragile, with wide intervals, and should not be presented as reliable rankings of UK business failure risk.

The index can prioritise manual checks of overdue registry obligations. It cannot establish financial distress from these observations. Accounts and confirmation delays are score components, so their relationship with the score is mechanical and is not presented as predictive evidence.

`deadline_association.csv` compares confirmation lateness across accounts-lateness groups independently of the score. `age_standardised_sectors.csv` checks sector composition against a common age mix; cells with fewer than 10 observations are withheld. `sensitivity.csv` reports how weights and thresholds change workload and selected-company overlap. Wilson intervals in benchmark exports describe binomial sampling uncertainty conditional on this proxy and selection; they do not correct coverage, filing errors or ranking selection.

## Questions this release cannot answer

No historical adverse-outcome labels, officer-event panel or dated charge history was acquired. We therefore make no claim about predictive power, governance instability before failure, causal drivers, survival probabilities, emerging sectors or companies entering high risk. Current liquidation is not automatically financial insolvency, and dissolved companies are not the live-register sampling frame.

## Action

Use the high-review queue to verify current records, deadline extensions and filings manually. Review already-observed legal statuses in a separate queue. Collect prospective snapshots and legally obtained event histories before testing an early-warning model.
'''
    (reports/'findings.md').write_text(report)
