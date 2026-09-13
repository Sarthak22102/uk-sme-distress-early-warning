"""Optional public API client. Not required by the validated bulk-only analysis.
Never log auth, never persist officer names/addresses/DOBs, never treat errors as zero.
"""
from src.utils.security import source_opener, require
import base64,hashlib,json,logging,os,time,urllib.error,urllib.request
from datetime import datetime,timezone
from pathlib import Path

class CompaniesHouseClient:
    BASE='https://api.company-information.service.gov.uk'
    def __init__(self,key=None,cache='data/raw/api',timeout=30,interval=.6):
        self.key=key or os.environ.get('COMPANIES_HOUSE_API_KEY')
        if not self.key: raise ValueError('Set COMPANIES_HOUSE_API_KEY securely in your environment')
        self.cache=Path(cache); self.cache.mkdir(parents=True,exist_ok=True)
        self.opener=source_opener()
        self.timeout=timeout; self.interval=interval; self.last=0
    def get(self,path):
        # Cache is date-scoped; only selected non-personal endpoint fields are cached by enrich().
        import re
        if not re.fullmatch(r'/company/(?:[0-9]{8}|[A-Z]{2}[0-9]{6}|R[0-9]{7})(?:/(?:filing-history|officers|charges))?(?:\?items_per_page=100&start_index=[0-9]+)?',path): raise ValueError('Invalid API path')
        for attempt in range(5):
            time.sleep(max(0,self.interval-(time.monotonic()-self.last)))
            self.last=time.monotonic()
            auth=base64.b64encode((self.key+':').encode()).decode()
            req=urllib.request.Request(self.BASE+path,headers={'Authorization':'Basic '+auth})
            try:
                with self.opener.open(req,timeout=self.timeout) as response:
                    body=response.read(5*1024*1024+1)
                    require(len(body)<=5*1024*1024, 'API response exceeds size limit')
                    return json.loads(body)
            except urllib.error.HTTPError as e:
                if e.code==404: raise LookupError('Company endpoint not found') from None
                if e.code not in (429,500,502,503,504) or attempt==4: raise RuntimeError(f'API HTTP {e.code}; incomplete extraction') from None
                delay=e.headers.get('Retry-After','')
                time.sleep(min(float(delay),300) if delay.isdigit() else (300 if e.code==429 else 2**attempt))
            except (TimeoutError,urllib.error.URLError):
                if attempt==4: raise RuntimeError('API transport failure; incomplete extraction') from None
                time.sleep(2**attempt)
    def pages(self,path,id_field):
        output=[]; start=0; expected=None; seen=set()
        while True:
            result=self.get(path+f'?items_per_page=100&start_index={start}')
            total=result.get('total_count',result.get('total_results'))
            require(isinstance(total,int) and not isinstance(total,bool) and 0<=total<=100000, 'Invalid or excessive pagination total')
            if expected is not None and total!=expected: raise ValueError('Collection changed during extraction; retry later')
            expected=total; items=result.get('items',[])
            for item in items:
                key=item.get(id_field)
                if id_field=='links':
                    require(isinstance(key,dict) and bool(key), 'Missing event links')
                    key=json.dumps(key,sort_keys=True)
                if key is None or key in seen: raise ValueError('Missing or duplicate event identifier')
                seen.add(key); output.append(item)
            start+=len(items)
            if start>=expected: break
            if not items: raise ValueError('Incomplete pagination')
        if len(output)!=expected: raise ValueError('Pagination count mismatch')
        return output
    def enrich(self,company_number):
        import re
        if not re.fullmatch(r'(?:\d{8}|[A-Z]{2}\d{6}|R\d{7})',company_number): raise ValueError('Invalid company number')
        today=datetime.now(timezone.utc).date().isoformat()
        target=self.cache/f'{company_number}_{today}.json'
        if target.exists(): return json.loads(target.read_text())
        root='/company/'+company_number
        filings=self.pages(root+'/filing-history','transaction_id')
        officers=self.pages(root+'/officers','links')
        charges=self.pages(root+'/charges','links')
        result={'company_number':company_number,'extracted_at':datetime.now(timezone.utc).isoformat(),'complete':True,
         'filings':[{k:x.get(k) for k in ['transaction_id','date','type','category']} for x in filings],
         'officers':[{'officer_key':hashlib.sha256(json.dumps(x.get('links'),sort_keys=True).encode()).hexdigest(),'role':x.get('officer_role'),'appointed_on':x.get('appointed_on'),'resigned_on':x.get('resigned_on')} for x in officers],
         'charges':[{'charge_key':hashlib.sha256(json.dumps(x.get('links'),sort_keys=True).encode()).hexdigest(),**{k:x.get(k) for k in ['charge_code','created_on','delivered_on','satisfied_on','status']}} for x in charges]}
        temporary=target.with_suffix('.partial')
        with temporary.open('w',encoding='utf-8') as stream:
            os.chmod(temporary,0o600)
            json.dump(result,stream,indent=2)
        temporary.replace(target)
        return result
