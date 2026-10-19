"""Shared project configuration. All published calculations use the frozen snapshot."""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = '2026-10-19'
RAW = ROOT/'data/raw'/SNAPSHOT
PROCESSED = ROOT/'data/processed'
REPORTS = ROOT/'reports'
YEARS = [2015,2016,2017,2018,2019,2021,2022,2023,2024]
TABLES = ['B19013','B25064','B25070','B25119']
CPI = {'food': 'CUUR0000SAF11', 'rent': 'CUUR0000SEHA', 'all_items': 'CUUR0000SA0'}
# Official Census reference, preserved verbatim. Exclude territories from default scope.
import csv
with (ROOT/'config/state_reference.txt').open() as source:
    STATES = [dict(fips=r['STATE'],abbreviation=r['STUSAB'],name=r['STATE_NAME'])
              for r in csv.DictReader(source,delimiter='|') if int(r['STATE'])<=56]
GEOGRAPHIES = [{'fips':'US','abbreviation':'US','name':'United States'},*STATES]


def write_json(path, obj):
    path.parent.mkdir(parents=True,exist_ok=True)
    temp=path.with_suffix(path.suffix+'.tmp')
    temp.write_text(json.dumps(obj,indent=2,allow_nan=False,default=str)+'\n')
    temp.replace(path)
