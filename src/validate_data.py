"""Fail-fast quality gates before SQL modeling; write measured quality evidence."""
import hashlib
import json
import pandas as pd
from common import ROOT,RAW,PROCESSED,REPORTS,YEARS,GEOGRAPHIES,write_json


def require(condition,message):
    if not condition:raise ValueError(message)


def main():
    manifest=json.loads((RAW/'manifest.json').read_text())
    for name,entry in manifest.items():
        require(hashlib.sha256((RAW/name).read_bytes()).hexdigest()==entry['sha256'],f'Raw hash mismatch {name}')
    a=pd.read_parquet(PROCESSED/'acs_observations.parquet')
    p=pd.read_parquet(PROCESSED/'monthly_prices.parquet')
    items=pd.read_parquet(PROCESSED/'item_prices.parquet')
    expected_geo={g['fips'] for g in GEOGRAPHIES}
    require(len(expected_geo)==52,'Expected nation, 50 states and DC')
    require(len(a)==52*9*16,'Incorrect full ACS panel size')
    require(not a.duplicated(['year','geography_id','variable']).any(),'Duplicate ACS key')
    require(set(a.year)==set(YEARS),'Unexpected ACS years')
    for year,g in a.groupby('year'):
        require(set(g.geography_id)==expected_geo,f'Missing geography {year}')
        require(g.groupby('geography_id').size().eq(16).all(),f'Incomplete ACS variables {year}')
    require(a.estimate.notna().all(),'Missing ACS estimates; review before modeling')
    require(not p.duplicated(['series_id','date']).any(),'Duplicate price key')
    require((p.value.dropna()>0).all(),'Impossible price/index value')
    require(not items.duplicated(['series_id','date']).any(),'Duplicate item key')
    require((items.price>0).all(),'Nonpositive item prices')
    require(items.groupby('series_id').unit.nunique().max()==1,'Changing item price units')
    wide=a.pivot(index=['year','geography_id'],columns='variable',values='estimate')
    total=wide.B25070_001E
    parts=wide[[f'B25070_{i:03d}E' for i in range(2,12)]].sum(axis=1)
    require((total==parts).all(),'ACS burden bands do not reconcile to universe')
    require((wide.B25070_011E<total).all(),'No computable burden denominator')
    for category,g in p[p.date.dt.year.between(2015,2024)].groupby('category'):
        require(g.groupby(g.date.dt.year).value.count().eq(12).all(),f'Incomplete historical category: {category}')
    counts={'checks_passed':True,'source_resources':len(manifest),'acs_rows':len(a),'acs_expected_rows':52*9*16,
        'acs_state_year_rows':51*9,'acs_national_year_rows':9,'acs_missing_estimates':int(a.estimate.isna().sum()),
        'acs_missing_moes':int(a.moe_90.isna().sum()),'burden_universe_reconciliations':len(wide),
        'price_missing_values':int(p.value.isna().sum()),'source_bytes':sum(x['bytes'] for x in manifest.values())}
    write_json(REPORTS/'validation_results.json',counts);print(json.dumps(counts,indent=2))


if __name__=='__main__':main()
