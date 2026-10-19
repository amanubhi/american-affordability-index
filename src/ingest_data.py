"""Acquire official public releases into an immutable, checksummed snapshot.

No Census API key required: this uses Census's documented public Summary Files.
Cached bytes are hash-verified. For a new vintage, pass --snapshot YYYY-MM-DD.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
import csv
from datetime import datetime, timezone
import hashlib
import io
import json
from pathlib import Path
import threading
import time
import zipfile
import requests
from common import ROOT, SNAPSHOT, YEARS, TABLES, CPI, GEOGRAPHIES, write_json

BASE = 'https://www2.census.gov/programs-surveys/acs/summary_file'


class Collector:
    def __init__(self, snapshot):
        self.root = ROOT/'data/raw'/snapshot
        self.manifest_path = self.root/'manifest.json'
        self.entries = json.loads(self.manifest_path.read_text()) if self.manifest_path.exists() else {}
        self.lock = threading.Lock()
        self.request_lock = threading.Lock()
        self.next_request = 0.0

    def fetch(self, name, url, kind):
        path = self.root/name
        if path.exists():
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            if name in self.entries and self.entries[name]['url']!=url:raise ValueError(f'Source URL changed for {name}')
            if name not in self.entries or self.entries[name]['sha256'] != digest:
                raise ValueError(f'Unregistered or modified snapshot file: {name}')
            return path
        error = None
        for attempt in range(5):
            try:
                with self.request_lock:
                    delay=max(0,self.next_request-time.monotonic())
                    if delay:time.sleep(delay)
                    self.next_request=time.monotonic()+0.8
                response = requests.get(url,timeout=90)
                if response.status_code==429:
                    retry_after=response.headers.get("Retry-After", "30")
                    delay=float(retry_after) if retry_after.isdigit() else 30.0
                    with self.request_lock:
                        self.next_request=max(self.next_request,time.monotonic()+delay)
                response.raise_for_status()
                body = response.content
                if kind == 'zip':
                    with zipfile.ZipFile(io.BytesIO(body)) as z:
                        if z.testzip(): raise ValueError(f'Invalid zip: {name}')
                elif kind == 'json':
                    obj=response.json()
                    if 'status' in obj and obj['status']!='REQUEST_SUCCEEDED':
                        raise ValueError(f'API status failed: {name}')
                elif kind == 'dat':
                    if not body.lstrip(b'#').startswith(b'GEO_ID|'): raise ValueError(f'Unexpected table schema: {name}')
                elif kind == 'lookup':
                    if b'Table ID' not in body[:200]: raise ValueError(f'Unexpected lookup: {name}')
                elif kind == 'geo':
                    if not body.startswith(b'ACSSF'): raise ValueError(f'Unexpected geography CSV: {name}')
                elif kind == 'html':
                    if b'Year' not in body or b'Gasoline' not in body: raise ValueError('Unexpected EIA HTML')
                path.parent.mkdir(parents=True,exist_ok=True)
                temp=path.with_suffix(path.suffix+'.part')
                temp.write_bytes(body);temp.replace(path)
                with self.lock:
                    self.entries[name]={'url':url,'sha256':hashlib.sha256(body).hexdigest(),
                        'bytes':len(body),'retrieved_utc':datetime.now(timezone.utc).isoformat(),
                        'content_type':response.headers.get('Content-Type'),'kind':kind}
                    write_json(self.manifest_path,dict(sorted(self.entries.items())))
                return path
            except (requests.RequestException,ValueError,zipfile.BadZipFile) as exc:
                error=exc
                if attempt<4:time.sleep(min(2**(attempt+1),30))
        raise RuntimeError(f'Download failed for {name}: {error}')


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--snapshot',default=SNAPSHOT)
    args=parser.parse_args();collector=Collector(args.snapshot)
    reference=collector.fetch('geography/state_reference.txt','https://www2.census.gov/geo/docs/reference/state.txt','reference')
    if reference.read_bytes()!=(ROOT/'config/state_reference.txt').read_bytes():raise ValueError('Geography reference changed; review required')
    jobs=[]
    # Sequence lookups supply year-specific offsets rather than hardcoded columns.
    for year in [2015,2016,2017]:
        name=f'acs/{year}/lookup.csv'
        path=collector.fetch(name,f'{BASE}/{year}/documentation/user_tools/ACS_1yr_Seq_Table_Number_Lookup.txt','lookup')
        rows=list(csv.DictReader(path.read_text(encoding='latin1').splitlines()))
        seqs=sorted({r['Sequence Number'] for r in rows if r['Table ID'] in TABLES and r['Start Position']})
        if len(seqs)!=3:raise ValueError(f'Unexpected sequence coverage {year}: {seqs}')
        for geo in GEOGRAPHIES:
            directory=geo['name'].replace(' ','');abbrev=geo['abbreviation'].lower()
            prefix=f'{BASE}/{year}/data/1_year_seq_by_state/{directory}'
            jobs.append((f'acs/{year}/{abbrev}/geo.csv',f'{prefix}/g{year}1{abbrev}.csv','geo'))
            for seq in seqs:
                jobs.append((f'acs/{year}/{abbrev}/{seq}.zip',f'{prefix}/{year}1{abbrev}{seq}000.zip','zip'))
    for year in [2018,2019,2021,2022,2023,2024]:
        prefix=f'{BASE}/{year}/prototype/1YRData' if year in [2018,2019] else f'{BASE}/{year}/table-based-SF/data/1YRData'
        for table in TABLES:
            # Prototype naming is confirmed from its public directory.
            filename=f'acsdt1y{year}-{table.lower()}.dat'
            jobs.append((f'acs/{year}/{table}.dat',f'{prefix}/{filename}','dat'))
    for label,sid in CPI.items():
        for start,end in [(2015,2024),(2025,2026)]:
            jobs.append((f'bls/{label}_{start}_{end}.json',f'https://api.bls.gov/publicAPI/v2/timeseries/data/{sid}?startyear={start}&endyear={end}','json'))
    jobs.append(('eia/regular_monthly.html','https://www.eia.gov/dnav/pet/hist/LeafHandler.ashx?n=PET&s=EMM_EPMR_PTE_NUS_DPG&f=M','html'))
    # Audit metadata in every standard ACS release, including intermediate years.
    for year in YEARS:
        for table in TABLES:
            jobs.append((f'acs/{year}/{table}_metadata.json',f'https://api.census.gov/data/{year}/acs/acs1/groups/{table}.json','json'))
    def run(job):return collector.fetch(*job)
    with ThreadPoolExecutor(max_workers=2) as pool:
        for i,_ in enumerate(pool.map(run,jobs),1):
            if i%75==0: print(f'Validated {i}/{len(jobs)} resources',flush=True)
    print(f'Ingestion complete: {len(collector.entries)} immutable resources in {collector.root}')


if __name__=='__main__':main()
