"""Reconcile a pinned Kaggle BLS snapshot with the original 74-series scope."""
import csv
import hashlib
import io
import json
import zipfile
from common import ROOT, write_json

SOURCE = 'sadiqguru/us-bls-average-prices'
DIRECTORY = ROOT / 'data/raw/kaggle/2026-11-10'
ARCHIVE = DIRECTORY / 'us-bls-average-prices.zip'
OUTPUT = DIRECTORY / 'normalized_monthly.csv'


def reconcile(original, incoming):
    metadata = {r['series_id']: r for r in original}
    previous = {(r['series_id'], r['date']): r for r in original}
    result = {}
    for row in incoming:
        sid, date = row['series_id'], row['date']
        if sid not in metadata or date < '2015-01-01':
            continue
        if row['area_code'] != '0000' or row['seasonally_adjusted'].lower() != 'false':
            raise ValueError('Expected national, unadjusted observations')
        key = (sid, date)
        if key in result:
            raise ValueError(f'Duplicate observation: {key}')
        if not row['price_usd'].strip():
            continue  # Missing releases remain absent; never invent a price.
        price = float(row['price_usd'])
        if not 0 < price < float('inf'):
            raise ValueError(f'Invalid price: {key}')
        # Retain original display labels, units and category taxonomy by BLS ID.
        item = dict(metadata[sid])
        item.update(date=date, year=date[:4], month=str(int(date[5:7])), price=row['price_usd'])
        result[key] = item
    missing = previous.keys() - result.keys()
    if missing:
        raise ValueError(f'New snapshot omits {len(missing)} original observations')
    revised = sum(float(result[k]['price']) != float(v['price']) for k, v in previous.items())
    if revised:
        raise ValueError(f'{revised} historical prices changed; review revisions before refresh')
    return [result[k] for k in sorted(result)], {
        'original_rows': len(original), 'refreshed_rows': len(result),
        'added_rows': len(result) - len(previous), 'revised_rows': revised,
        'series_count': len(metadata), 'latest_date': max(r['date'] for r in result.values()),
    }


def main():
    with (ROOT / 'data/raw/kaggle/us_average_prices_monthly.csv').open() as f:
        original = list(csv.DictReader(f))
    expected = '4413aeaf1320c0d31554da4a25aff412b0f2011429a0c79015ce24861f975110'
    if hashlib.sha256(ARCHIVE.read_bytes()).hexdigest() != expected:
        raise ValueError('Kaggle archive hash differs from reviewed version 1')
    with zipfile.ZipFile(ARCHIVE) as z:
        incoming = csv.DictReader(io.TextIOWrapper(z.open('average_prices.csv'), encoding='utf-8'))
        rows, metrics = reconcile(original, incoming)
    with OUTPUT.open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(original[0]))
        writer.writeheader()
        writer.writerows(rows)
    metrics.update(dataset=SOURCE, version=1, retrieved_date='2026-11-10',
                   archive_sha256=hashlib.sha256(ARCHIVE.read_bytes()).hexdigest(),
                   url='https://www.kaggle.com/datasets/' + SOURCE,
                   download_url='https://www.kaggle.com/api/v1/datasets/download/' + SOURCE + '?datasetVersionNumber=1',
                   scope='Original 74 national BLS series; original labels and units retained.')
    write_json(DIRECTORY / 'manifest.json', metrics)
    write_json(ROOT / 'reports/kaggle_refresh.json', metrics)
    print(json.dumps(metrics, indent=2))


if __name__ == '__main__':
    main()
