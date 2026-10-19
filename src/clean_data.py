"""Normalize both ACS Summary File formats and official price series.

Raw estimates, MOEs, sentinel/annotation strings and source labels survive cleaning.
"""
import csv
from io import StringIO
import json
import re
import zipfile
import pandas as pd
from common import ROOT, RAW, PROCESSED, REPORTS, YEARS, TABLES, CPI, GEOGRAPHIES, write_json


def parse_number(value):
    """Census sentinel strings/codes become null; preserve the raw value separately."""
    x=pd.to_numeric(str(value).replace(',',''),errors='coerce')
    return float(x) if pd.notna(x) and x>=0 else None


def lookup(year):
    rows=list(csv.DictReader((RAW/f'acs/{year}/lookup.csv').read_text(encoding='latin1').splitlines()))
    return {r['Table ID']:r for r in rows if r['Table ID'] in TABLES and r['Start Position']}


def normalize_acs():
    records=[]
    for year in YEARS:
        metadata={t:json.loads((RAW/f'acs/{year}/{t}_metadata.json').read_text())['variables'] for t in TABLES}
        if year<=2017:
            spec=lookup(year)
            for geo in GEOGRAPHIES:
                abbr=geo['abbreviation'].lower();directory=RAW/f'acs/{year}/{abbr}'
                geo_rows=list(csv.reader((directory/'geo.csv').read_text(encoding='latin1').splitlines()))
                geography=[r for r in geo_rows if r[2]==('010' if geo['fips']=='US' else '040') and r[3]=='00']
                if len(geography)!=1:raise ValueError(f'Ambiguous geography {year} {geo}')
                if geo['fips']!='US' and not geography[0][48].endswith('US'+geo['fips']):
                    raise ValueError(f'FIPS/reference mismatch: {year} {geo}')
                logrec=geography[0][4]
                for table in TABLES:
                    specrow=spec[table];seq=specrow['Sequence Number'];start=int(specrow['Start Position'])-1
                    n=int(specrow['Total Cells in Table'].split()[0])
                    with zipfile.ZipFile(directory/f'{seq}.zip') as archive:
                        by_type={}
                        for prefix in ['e','m']:
                            names=[n for n in archive.namelist() if n.startswith(prefix)]
                            rows=csv.reader(archive.read(names[0]).decode('latin1').splitlines())
                            matches=[r for r in rows if r[5]==logrec]
                            if len(matches)!=1:raise ValueError('Sequence/geography join failed')
                            by_type[prefix]=matches[0]
                    for i in range(1,n+1):
                        variable=f'{table}_{i:03d}E'
                        if variable not in metadata[table]:raise ValueError(f'Unknown variable {year} {variable}')
                        records.append([year,geo['fips'],table,variable,by_type['e'][start+i-1],by_type['m'][start+i-1],metadata[table][variable]['label'],'sequence'])
        else:
            for table in TABLES:
                frame=pd.read_csv(RAW/f'acs/{year}/{table}.dat',sep='|',dtype=str,keep_default_na=False)
                frame=frame.rename(columns={'#GEO_ID':'GEO_ID'})
                frame=frame.rename(columns={c:re.sub(r'_(\d{3})([EM])$',r'_\2\1',c) for c in frame.columns})
                geoid=frame.GEO_ID
                frame=frame[geoid.eq('0100000US')|geoid.str.match(r'^0400*US\d{2}$')].copy()
                frame['geography_id']=frame.GEO_ID.map(lambda s:'US' if s=='0100000US' else s[-2:])
                frame=frame[frame.geography_id.isin([g['fips'] for g in GEOGRAPHIES])]
                for _,row in frame.iterrows():
                    for col in frame.columns:
                        match=re.fullmatch(table+r'_E(\d{3})',col)
                        if not match:continue
                        i=match[1];variable=f'{table}_{i}E';mcol=f'{table}_M{i}'
                        if variable not in metadata[table]:raise ValueError(f'Unknown variable {year} {variable}')
                        records.append([year,row.geography_id,table,variable,row[col],row[mcol],metadata[table][variable]['label'],'table'])
    frame=pd.DataFrame(records,columns=['year','geography_id','table_id','variable','raw_estimate','raw_moe','variable_label','source_format'])
    frame['estimate']=frame.raw_estimate.map(parse_number)
    frame['moe_90']=frame.raw_moe.map(parse_number)
    frame['estimate_flag']=frame.estimate.isna()
    frame['moe_flag']=frame.moe_90.isna()
    frame['source']='Census ACS 1-year';frame['vintage']='2026-10-19'
    return frame


def normalize_prices():
    records=[]
    for label,sid in CPI.items():
        for start,end in [(2015,2024),(2025,2026)]:
            response=json.loads((RAW/f'bls/{label}_{start}_{end}.json').read_text())
            if response['status']!='REQUEST_SUCCEEDED':raise ValueError('BLS API failure')
            series=response['Results']['series']
            if len(series)!=1 or series[0]['seriesID']!=sid:raise ValueError('Unexpected BLS series')
            for row in series[0]['data']:
                if not re.fullmatch(r'M(0[1-9]|1[0-2])',row['period']):continue
                date=f"{row['year']}-{row['period'][1:]}-01"
                records.append([date,label,sid,'US','index (1982–84=100)',parse_number(row['value']),row['value'],json.dumps(row['footnotes']),'BLS CPI-U NSA'])
    tables=pd.read_html(StringIO((RAW/'eia/regular_monthly.html').read_text()))
    t=next(t for t in tables if list(t.columns)==['Year','Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'])
    t['Year']=pd.to_numeric(t.Year,errors='coerce');t=t[t.Year.between(2015,2026)]
    for _,r in t.iterrows():
        for month,col in enumerate(t.columns[1:],1):
            value=parse_number(r[col])
            if value is not None:
                records.append([f'{int(r.Year)}-{month:02d}-01','gasoline','EMM_EPMR_PTE_NUS_DPG','US','USD/US gallon',value,str(r[col]),'[]','EIA regular all formulations'])
    f=pd.DataFrame(records,columns=['date','category','series_id','geography_id','unit','value','raw_value','footnotes','source'])
    f['date']=pd.to_datetime(f.date);f['vintage']='2026-10-19'
    return f.sort_values(['category','date']).reset_index(drop=True)


def normalize_items():
    f=pd.read_csv(ROOT/'data/raw/kaggle/us_average_prices_monthly.csv',parse_dates=['date'])
    f=f.rename(columns={'category':'source_category','unit':'source_unit'})
    f['category']=f.source_category
    f.loc[f.item.str.startswith('Coffee,'),'category']='Drinks'
    f.loc[f.item.eq('Potato chips'),'category']='Pantry and snacks'
    f['unit']=f.source_unit.replace({'gal. (3.8 lit)':'US gallon','gallon/3.785 liters':'US gallon','gallon (3.785 liters)':'US gallon','lb. (453.6 gm)':'lb','doz.':'dozen','KWH':'kWh'})
    f['price']=pd.to_numeric(f.price,errors='raise')
    f['geography_id']='US';f['source']='Kaggle v2 / BLS AP'
    return f


def save(name,frame):
    PROCESSED.mkdir(parents=True,exist_ok=True)
    frame.to_parquet(PROCESSED/f'{name}.parquet',index=False)
    frame.to_csv(PROCESSED/f'{name}.csv',index=False)


def main():
    acs=normalize_acs();prices=normalize_prices();items=normalize_items()
    for name,frame in [('acs_observations',acs),('monthly_prices',prices),('item_prices',items)]:save(name,frame)
    geo=pd.DataFrame(GEOGRAPHIES).rename(columns={'fips':'geography_id'})
    geo['geography_type']=geo.geography_id.map(lambda x:'nation' if x=='US' else 'district' if x=='11' else 'state')
    save('geographies',geo)
    quality={'acs_rows':len(acs),'acs_estimate_nulls':int(acs.estimate.isna().sum()),'acs_moe_nulls':int(acs.moe_90.isna().sum()),
        'acs_duplicate_keys':int(acs.duplicated(['year','geography_id','variable']).sum()),
        'acs_geographies_by_year':acs.groupby('year').geography_id.nunique().to_dict(),
        'prices_rows':len(prices),'price_missing_values':int(prices.value.isna().sum()),
        'prices_nonpositive':int((prices.value<=0).sum()),'price_duplicate_keys':int(prices.duplicated(['series_id','date']).sum()),
        'price_coverage':{c:{'first':str(g.date.min().date()),'last':str(g.date.max().date()),'observed':int(g.value.notna().sum()),'missing':int(g.value.isna().sum())} for c,g in prices.groupby('category')},
        'item_rows':len(items),'item_category_corrections':int((items.category!=items.source_category).sum()),
        'decisions':['No interpolation or outlier deletion.','ACS 2020 intentionally absent.','Coffee to Drinks; potato chips to Pantry and snacks; source labels retained.','Mixed units never averaged.','Non-numeric/negative ACS sentinels retained as raw strings and normalized to null.']}
    write_json(REPORTS/'pipeline_quality.json',quality)
    print(json.dumps(quality,indent=2))


if __name__=='__main__':main()
