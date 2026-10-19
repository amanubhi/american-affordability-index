"""Milestone 1: read-only source audit; no cleaning or business analysis."""
from pathlib import Path
import hashlib
import json
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / 'data/raw/kaggle'
OUT = ROOT / 'reports'


def main():
    OUT.mkdir(exist_ok=True)
    frames = {p.name: pd.read_csv(p) for p in sorted(RAW.glob('*.csv'))}
    long = frames['us_average_prices_monthly.csv']
    wide = frames['us_average_prices_wide.csv']
    summary = frames['us_average_prices_item_summary.csv']
    dates = pd.to_datetime(long.date, errors='coerce')
    prices = pd.to_numeric(long.price, errors='coerce')
    calendar = pd.date_range(dates.min(), dates.max(), freq='MS')
    inventory = []
    for sid, g in long.groupby('series_id'):
        ds = pd.to_datetime(g.date).sort_values()
        internal = pd.date_range(ds.min(), ds.max(), freq='MS').difference(ds)
        inventory.append(dict(series_id=sid, item=g.item.iloc[0], unit=g.unit.iloc[0],
                              category=g.category.iloc[0], first_date=str(ds.min().date()),
                              last_date=str(ds.max().date()), n_months=len(g),
                              internal_missing_months=len(internal),
                              missing_dates=';'.join(internal.strftime('%Y-%m')),
                              baseline_2015_months=int((ds.dt.year == 2015).sum())))
    inv = pd.DataFrame(inventory)
    inv.to_csv(OUT / 'series_inventory.csv', index=False)
    grid = long.pivot(index='date', columns='item', values='price').sort_index()
    w = wide.set_index('date').sort_index().reindex(index=grid.index, columns=grid.columns)
    mismatches = int(((grid != w) & ~(grid.isna() & w.isna())).sum().sum())
    ordered = long.assign(parsed_date=dates).sort_values(['series_id','parsed_date'])
    ordered['previous_date'] = ordered.groupby('series_id').parsed_date.shift()
    ordered['previous_price'] = ordered.groupby('series_id').price.shift()
    consecutive = (ordered.parsed_date.dt.year*12+ordered.parsed_date.dt.month)-(ordered.previous_date.dt.year*12+ordered.previous_date.dt.month) == 1
    ordered['monthly_pct_change'] = (ordered.price/ordered.previous_price-1)*100
    flags = ordered[consecutive & (ordered.monthly_pct_change.abs() > 20)]
    flags.to_csv(OUT / 'suspicious_movements.csv', index=False)
    checks = []
    for _, s in summary.iterrows():
        g = long[long.item == s['item']].sort_values('date')
        first, last = g.iloc[0], g.iloc[-1]
        checks.append(dict(item=s['item'], coverage_matches=(s.n_months == len(g) and s.first_date == first.date and s.last_date == last.date),
                           endpoints_match=(s.first_price == first.price and s.last_price == last.price),
                           extrema_match=(s.min_price == g.price.min() and s.max_price == g.price.max()),
                           first12_observation_mean=round(g.price.head(12).mean(),3),
                           last12_observation_mean=round(g.price.tail(12).mean(),3)))
    pd.DataFrame(checks).to_csv(OUT / 'summary_checks.csv', index=False)
    metrics = dict(files={n:dict(rows=len(f),columns=list(f.columns),dtypes={c:str(t) for c,t in f.dtypes.items()},missing={c:int(v) for c,v in f.isna().sum().items()},missing_rate_pct={c:round(float(v)*100,3) for c,v in f.isna().mean().items()}) for n,f in frames.items()},
                   date_min=str(dates.min().date()),date_max=str(dates.max().date()),calendar_months=len(calendar),
                   items=long.item.nunique(),series=long.series_id.nunique(),categories=long.category.nunique(),
                   category_items=inv.groupby('category').size().to_dict(),units=sorted(long.unit.unique()),
                   exact_duplicates=int(long.duplicated().sum()),grain_duplicates=int(long.duplicated(['series_id','date']).sum()),
                   invalid_dates=int(dates.isna().sum()),invalid_prices=int(prices.isna().sum()),nonpositive_prices=int((prices<=0).sum()),
                   date_component_mismatches=int(((dates.dt.year!=long.year)|(dates.dt.month!=long.month)|(dates.dt.day!=1)).sum()),
                   inconsistent_series_metadata=int((long.groupby('series_id')[['item','unit','category']].nunique()>1).any(axis=1).sum()),
                   full_grid_absences=int(len(calendar)*len(inv)-len(long)),internal_missing_months=int(inv.internal_missing_months.sum()),
                   series_with_internal_gaps=int((inv.internal_missing_months>0).sum()),
                   latest_month_series=int((inv.last_date == str(dates.max().date())).sum()),
                   full_2015_series=int((inv.baseline_2015_months==12).sum()),
                   complete_full_history_series=int((inv.n_months==len(calendar)).sum()),
                   monthly_observation_counts=long.groupby('date').size().to_dict(),
                   wide_long_cell_mismatches=mismatches,summary_check_failures={k:int((~pd.DataFrame(checks)[k]).sum()) for k in ['coverage_matches','endpoints_match','extrema_match']},
                   movements_over_20pct=len(flags),sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(RAW.iterdir())})
    (OUT/'audit_metrics.json').write_text(json.dumps(metrics,indent=2)+'\n')
    print(json.dumps({k:v for k,v in metrics.items() if k not in ['files','monthly_observation_counts','sha256']},indent=2))
    print('Missing cells:', {n: int(f.isna().sum().sum()) for n,f in frames.items()})
    print(inv[['item','category']].to_string(index=False))


if __name__ == '__main__':
    main()
