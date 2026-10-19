"""Audit saved feasibility probes offline; does not collect or integrate data."""
from pathlib import Path
from io import StringIO
import json
import hashlib
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
REF = ROOT / 'data/reference/feasibility'


def main():
    results = {'retrieval_date': '2026-10-19', 'acs_metadata': {}, 'bls': {}}
    for year in [2015, 2024]:
        for group in ['B19013', 'B25064', 'B25070', 'B25119']:
            data = json.loads((REF/f'acs{year}_{group}.json').read_text())
            results['acs_metadata'][f'{year}_{group}'] = {
                k: {'label': v['label'], 'type': v.get('predicateType')}
                for k, v in data['variables'].items()
                if k.startswith(group+'_')}
    for sid in ['CUUR0000SA0', 'CUUR0000SAF11', 'CUUR0000SEHA']:
        data = json.loads((REF/f'bls_{sid}_2015_2024.json').read_text())
        assert data['status'] == 'REQUEST_SUCCEEDED', sid
        rows = pd.DataFrame(data['Results']['series'][0]['data'])
        rows = rows[rows.period.str.match(r'M(0[1-9]|1[0-2])$')].copy()
        rows['price'] = pd.to_numeric(rows.value, errors='coerce')
        keys = rows.year + '-' + rows.period.str[1:]
        expected = set(pd.date_range('2015-01-01','2024-12-01',freq='MS').strftime('%Y-%m'))
        results['bls'][sid] = {'rows': len(rows), 'missing_expected_months': sorted(expected-set(keys)),
            'duplicates': int(keys.duplicated().sum()), 'invalid_values': int(rows.price.isna().sum()),
            'nonpositive_values': int((rows.price <= 0).sum())}
    tables = pd.read_html(StringIO((REF/'eia_regular_monthly.html').read_text()))
    table = next(t for t in tables if list(t.columns) == ['Year','Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'])
    table['Year'] = pd.to_numeric(table.Year, errors='coerce')
    table = table[table.Year.between(2015,2026)].copy()
    years = {}
    for _, row in table.iterrows():
        values = pd.to_numeric(row.iloc[1:], errors='coerce')
        years[str(int(row.Year))] = {'observed_months': int(values.notna().sum()),
            'missing_months': list(values.index[values.isna()]),
            'nonpositive_values': int((values<=0).sum())}
    results['eia_regular_gasoline'] = {'series': 'EMM_EPMR_PTE_NUS_DPG', 'unit': 'USD/US gallon',
        'geography': 'United States', 'frequency': 'monthly', 'year_coverage': years,
        'duplicate_years': int(table.Year.duplicated().sum())}
    results['acs_data_query'] = {'status': 'missing_key_html', 'state_values_audited': False}
    results['sha256'] = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(REF.iterdir()) if p.is_file()}
    output = ROOT/'reports/source_feasibility_metrics.json'
    output.write_text(json.dumps(results,indent=2)+'\n')
    print(json.dumps({k:v for k,v in results.items() if k not in ['sha256','acs_metadata']},indent=2))


if __name__ == '__main__':
    main()
