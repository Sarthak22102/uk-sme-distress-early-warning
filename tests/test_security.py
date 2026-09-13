"""Regression tests for security boundaries; only synthetic payloads are used."""
import io
import subprocess
import sys
import tempfile
import unittest
import urllib.request
import zipfile
from pathlib import Path
from unittest.mock import patch
from src.utils.security import require, RejectRedirects, safe_cell, source_path, snapshot_date, check_archive
from src.ingestion.api import CompaniesHouseClient

class SecurityTests(unittest.TestCase):
    def test_cross_origin_redirect_rejected(self):
        request=urllib.request.Request('https://api.company-information.service.gov.uk/company/00000001')
        with self.assertRaises(ValueError):
            RejectRedirects().redirect_request(request,None,302,'Moved',{},'https://example.invalid/')
    def test_https_downgrade_rejected(self):
        request=urllib.request.Request('https://api.company-information.service.gov.uk/company/00000001')
        with self.assertRaises(ValueError):
            RejectRedirects().redirect_request(request,None,302,'Moved',{},'http://api.company-information.service.gov.uk/')
    def test_formula_prefixes_escaped(self):
        for value in ['=1+1','+1+1','-1+1','@SUM(1)',' \t=1+1','\ttext','＝1+1']:
            self.assertTrue(safe_cell(value).startswith("'"))
    def test_normal_values_preserved(self):
        for value in ['Company Ltd','00000001',-3,0,None,'']:
            self.assertEqual(safe_cell(value),value)
    def test_source_traversal_rejected(self):
        with self.assertRaises(ValueError):source_path('/tmp','../../example.zip','2026-09-01')
    def test_source_symlink_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            name='BasicCompanyData-2026-09-01-part1_7.zip'
            (Path(directory)/name).symlink_to('/tmp/absent.zip')
            with self.assertRaises(ValueError):source_path(directory,name,'2026-09-01')
    def test_snapshot_path_rejected(self):
        with self.assertRaises(ValueError):snapshot_date('../../2026-09-01')
    def test_check_survives_optimisation(self):
        result=subprocess.run([sys.executable,'-O','-c','from src.utils.security import require; require(False,"expected")'],capture_output=True)
        self.assertNotEqual(result.returncode,0)
        self.assertIn(b'expected',result.stderr)
    def test_compression_bomb_rejected(self):
        stream=io.BytesIO()
        with zipfile.ZipFile(stream,'w',zipfile.ZIP_DEFLATED) as z:z.writestr('test.csv','0'*1000000)
        stream.seek(0)
        with zipfile.ZipFile(stream) as z:
            with self.assertRaises(ValueError):check_archive(z)
    def test_valid_csv_archive_accepted(self):
        stream=io.BytesIO()
        with zipfile.ZipFile(stream,'w') as z:z.writestr('test.csv','a,b\n1,2\n')
        stream.seek(0)
        with zipfile.ZipFile(stream) as z:check_archive(z)
    def test_oversized_api_body_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            client=CompaniesHouseClient(key='synthetic-test-key',cache=directory,interval=0)
            with patch.object(client.opener,'open',return_value=io.BytesIO(b' '* (5*1024*1024+1))):
                with self.assertRaises(ValueError):client.get('/company/00000001/charges')
    def test_excessive_total_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            client=CompaniesHouseClient(key='synthetic-test-key',cache=directory,interval=0)
            with patch.object(client,'get',return_value={'total_count':100001,'items':[]}):
                with self.assertRaises(ValueError):client.pages('/company/00000001/charges','links')
    def test_missing_links_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            client=CompaniesHouseClient(key='synthetic-test-key',cache=directory,interval=0)
            with patch.object(client,'get',return_value={'total_count':1,'items':[{}]}):
                with self.assertRaises(ValueError):client.pages('/company/00000001/charges','links')
    def test_sql_identifier_injection_rejected(self):
        from src.utils.security import sql_identifier
        with self.assertRaises(ValueError):sql_identifier('companies; DROP TABLE companies')
        self.assertEqual(sql_identifier('company_number'),'"company_number"')
