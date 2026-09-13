"""Policy index, not estimated probability. Legal status is excluded from score."""
import pandas as pd

def score(features,config):
    s=features[['company_number','reference_date']].copy()
    a=features.accounts_overdue_days.astype(float).clip(upper=config['accounts_cap_days'])/config['accounts_cap_days']*config['accounts_weight']
    c=features.confirmation_overdue_days.astype(float).clip(upper=config['confirmation_cap_days'])/config['confirmation_cap_days']*config['confirmation_weight']
    eligible=features.score_eligible
    s['accounts_points']=a.where(eligible)
    s['confirmation_points']=c.where(eligible)
    s['risk_score']=(a+c).round(2).where(eligible)
    s['risk_band']=s.risk_score.map(lambda x: band(x,config))
    s['primary_driver']=['Not scored' if not ok else ('No observed overdue deadline' if x+y==0 else ('Accounts deadline overdue' if x>=y else 'Confirmation deadline overdue')) for x,y,ok in zip(a,c,eligible)]
    s['secondary_driver']=['Both deadlines overdue' if ok and x>0 and y>0 else '' for x,y,ok in zip(a,c,eligible)]
    s['score_version']=config['score_version']
    return s

def band(value,config):
    if pd.isna(value): return 'Not scored'
    if value==0: return 'No flagged deadline'
    if value<config['watch_threshold']: return 'Watch'
    if value<config['high_threshold']: return 'Elevated review'
    return 'High review'
