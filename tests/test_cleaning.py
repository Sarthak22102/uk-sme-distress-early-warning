import unittest
import pandas as pd
from src.cleaning.companies import clean,DATE_MAP

def row():
    r={'CompanyNumber':'00000001','CompanyName':'SYNTHETIC TEST ONLY','CompanyStatus':'Active','postcode_area':'Unknown','SICCode.SicText_1':'62020 - Information technology consultancy activities'}
    for col in DATE_MAP:r[col]=''
    r['IncorporationDate']='01/01/2020'
    for col in ['NumMortCharges','NumMortOutstanding','NumMortPartSatisfied','NumMortSatisfied']:r['Mortgages.'+col]='0'
    return r
class CleaningTests(unittest.TestCase):
    def test_legacy_registration(self):
        r=row();r['CompanyNumber']='R0000001';self.assertEqual(clean(pd.DataFrame([r]),'2026-08-31')[1]['invalid_company_numbers'],0)
    def test_leading_zero_preserved(self):self.assertEqual(clean(pd.DataFrame([row()]),'2026-08-31')[0].company_number.iloc[0],'00000001')
    def test_duplicates_stop(self):
        with self.assertRaises(ValueError):clean(pd.DataFrame([row(),row()]),'2026-08-31')
    def test_invalid_number_stops(self):
        r=row();r['CompanyNumber']='1234'
        with self.assertRaises(ValueError):clean(pd.DataFrame([r]),'2026-08-31')
    def test_bad_due_date_unknown(self):
        r=row();r['Accounts.NextDueDate']='31/02/2026';df,q=clean(pd.DataFrame([r]),'2026-08-31');self.assertEqual(q['invalid_accounts_due'],1);self.assertTrue(pd.isna(df.accounts_due.iloc[0]))
    def test_future_deadline_valid(self):
        r=row();r['Accounts.NextDueDate']='31/12/2026';df,q=clean(pd.DataFrame([r]),'2026-08-31');self.assertEqual(str(df.accounts_due.iloc[0].date()),'2026-12-31')
    def test_future_observation_masked(self):
        r=row();r['Accounts.LastMadeUpDate']='31/12/2026';df,q=clean(pd.DataFrame([r]),'2026-08-31');self.assertEqual(q['future_accounts_made_up'],1);self.assertTrue(pd.isna(df.accounts_made_up.iloc[0]))
    def test_negative_charge_unknown(self):
        r=row();r['Mortgages.NumMortCharges']='-1';df,q=clean(pd.DataFrame([r]),'2026-08-31');self.assertEqual(q['invalid_charge_count'],1);self.assertTrue(pd.isna(df.charge_count.iloc[0]))
    def test_unknown_status_preserved(self):
        r=row();r['CompanyStatus']='New legal category';df,q=clean(pd.DataFrame([r]),'2026-08-31');self.assertEqual(df.status_group.iloc[0],'unmapped');self.assertIn('New legal category',q['unmapped_statuses'])
    def test_receivership_mapping(self):
        r=row();r['CompanyStatus']='RECEIVERSHIP';self.assertEqual(clean(pd.DataFrame([r]),'2026-08-31')[0].status_group.iloc[0],'receivership')
if __name__=='__main__':unittest.main()
