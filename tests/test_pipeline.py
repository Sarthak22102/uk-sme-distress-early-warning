"""Synthetic fixtures are confined to tests; never included in analysis outputs."""
import json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import pandas as pd
from src.features.filing import features
from src.scoring.index import score,band
from src.ingestion.api import CompaniesHouseClient
from src.cleaning.companies import clean

CONFIG=json.loads(Path('config/project.json').read_text())

def fixture(status='active',a='2026-08-31',c='2026-08-31'):
    return pd.DataFrame({'company_number':['00000001'],'incorporation_date':[pd.Timestamp('2020-01-01')],'accounts_due':[pd.Timestamp(a)],'confirmation_due':[pd.Timestamp(c)],'status_group':[status]})

class ScoreTests(unittest.TestCase):
    def run_score(self,df):return score(features(df,'2026-08-31'),CONFIG).iloc[0]
    def test_due_today_not_late(self):self.assertEqual(self.run_score(fixture()).risk_score,0)
    def test_future_due_not_late(self):self.assertEqual(self.run_score(fixture(a='2027-01-01')).risk_score,0)
    def test_one_day_late(self):self.assertAlmostEqual(self.run_score(fixture(a='2026-08-30')).risk_score,.33)
    def test_caps(self):self.assertEqual(self.run_score(fixture(a='2020-01-01',c='2020-01-01')).risk_score,100)
    def test_status_never_becomes_feature(self):self.assertTrue(pd.isna(self.run_score(fixture(status='liquidation_unspecified')).risk_score))
    def test_missing_not_zero(self):self.assertTrue(pd.isna(self.run_score(fixture(a=None)).risk_score))
    def test_boundaries(self):
        for value,expected in [(0,'No flagged deadline'),(.01,'Watch'),(39.99,'Watch'),(40,'Elevated review'),(69.99,'Elevated review'),(70,'High review'),(100,'High review'),(None,'Not scored')]:self.assertEqual(band(value,CONFIG),expected)
    def test_monotone(self):
        last=-1
        for days in [0,1,30,90,180,365]:
            s=self.run_score(fixture(a=str((pd.Timestamp('2026-08-31')-pd.Timedelta(days=days)).date()))).risk_score
            self.assertGreaterEqual(s,last);last=s
    def test_repeatable(self):self.assertEqual(self.run_score(fixture()).to_dict(),self.run_score(fixture()).to_dict())

class APITests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.client=CompaniesHouseClient(key='synthetic-test-key',cache=self.tmp.name,interval=0)
    def tearDown(self):self.tmp.cleanup()
    def test_pagination(self):
        with patch.object(self.client,'get',side_effect=[{'total_count':2,'items':[{'id':1}]},{'total_count':2,'items':[{'id':2}]}]): self.assertEqual(len(self.client.pages('/company/00000001/filing-history','id')),2)
    def test_duplicate_detection(self):
        with patch.object(self.client,'get',return_value={'total_count':2,'items':[{'id':1},{'id':1}]}):
            with self.assertRaises(ValueError):self.client.pages('/company/00000001/filing-history','id')
    def test_missing_page(self):
        with patch.object(self.client,'get',return_value={'total_count':2,'items':[]}):
            with self.assertRaises(ValueError):self.client.pages('/company/00000001/filing-history','id')
    def test_changing_collection(self):
        with patch.object(self.client,'get',side_effect=[{'total_count':2,'items':[{'id':1}]},{'total_count':3,'items':[{'id':2}]}]):
            with self.assertRaises(ValueError):self.client.pages('/company/00000001/filing-history','id')
    def test_external_url_rejected(self):
        with self.assertRaises(ValueError):self.client.get('https://example.com')

class SourceTests(unittest.TestCase):
    def test_hash_order_independent(self):
        import hashlib
        ids=['00000001','00000002','00000003']
        def select(xs):return sorted(xs,key=lambda n:hashlib.sha256(f'22102:{n}'.encode()).hexdigest())[:2]
        self.assertEqual(select(ids),select(list(reversed(ids))))
    def test_real_build_if_available(self):
        if not Path('data/processed/platform.sqlite').exists():self.skipTest('Requires real build; CI uses unit tests only')
        from src.pipeline import validate
        self.assertEqual(validate()['sql_python_score_reconciliation'],'pass')

if __name__=='__main__':unittest.main()
