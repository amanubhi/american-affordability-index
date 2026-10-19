"""Reproducible descriptive statistics, sensitivity checks and price scenarios."""
import json
import numpy as np
import pandas as pd
from scipy import stats
from common import ROOT,PROCESSED,REPORTS,write_json
from clean_data import save


def correlation(a,b):
    pairs=pd.concat([a.rename('a'),b.rename('b')],axis=1).dropna()
    if len(pairs)<3 or pairs.nunique().min()<2:return {'n':len(pairs),'pearson':None,'spearman':None}
    return {'n':len(pairs),'pearson':float(stats.pearsonr(pairs.a,pairs.b).statistic),
        'spearman':float(stats.spearmanr(pairs.a,pairs.b).statistic)}


def main():
    monthly=pd.read_parquet(PROCESSED/'mart_monthly_price.parquet')
    levels=monthly.pivot(index='date',columns='category',values='value').sort_index()
    latest=min(levels[c].last_valid_index() for c in ['food','gasoline','rent'])
    levels=levels.loc[:latest]
    change=levels.pct_change(fill_method=None)*100
    records=[]
    for lag in range(13):
        result=correlation(change.gasoline,change.food.shift(-lag))
        records.append({'lag_months':lag,**result})
    save('lag_correlations',pd.DataFrame(records))
    rolling=change.gasoline.rolling(36,min_periods=36).corr(change.food)
    save('rolling_correlations',pd.DataFrame({'date':rolling.index,'pearson_36mo':rolling.values}))
    pairs=levels[['gasoline','food']].dropna();time=np.array([(d-levels.index.min()).days for d in pairs.index])
    residuals={c:pairs[c]-np.polyval(np.polyfit(time,pairs[c],1),time) for c in pairs}
    seasonal=change[['gasoline','food']].copy()
    for c in seasonal:seasonal[c]=seasonal[c]-seasonal[c].groupby(seasonal.index.month).transform('mean')
    real=levels[['gasoline','food']].div(levels.all_items,axis=0)
    sensitivity={'levels':correlation(levels.gasoline,levels.food),'monthly_changes':correlation(change.gasoline,change.food),
        'linear_detrended_levels':correlation(residuals['gasoline'],residuals['food']),
        'month_demeaned_changes':correlation(seasonal.gasoline,seasonal.food),
        'common_cpi_deflated_levels':correlation(real.gasoline,real.food),
        'exclude_2020_2023_changes':correlation(change.loc[~change.index.year.isin(range(2020,2024)),'gasoline'],change.loc[~change.index.year.isin(range(2020,2024)),'food'])}
    for label,start,end in [('pre_pandemic',2015,2019),('pandemic',2020,2021),('shock_adjustment',2022,2023),('recent',2024,2026)]:
        subset=change.loc[(change.index.year>=start)&(change.index.year<=end)]
        sensitivity[label]=correlation(subset.gasoline,subset.food)
    write_json(REPORTS/'correlation_sensitivity.json',sensitivity)
    save('monthly_change_pairs',change[['gasoline','food']].reset_index())
    annual=pd.read_parquet(PROCESSED/'mart_annual_price.parquet')
    annual_wide=annual.pivot(index='year',columns='category',values='annual_price').sort_index()
    growth=annual_wide.pct_change(fill_method=None).loc[2016:2024,['rent','food','gasoline']]
    config=json.loads((ROOT/'config/budget.json').read_text())
    baseline=annual_wide.loc[2015]
    current={k:v*levels.loc[latest,k]/baseline[k] for k,v in config['annual_baseline_usd'].items()}
    scenarios=[]
    for label,q in [('Low',.25),('Baseline',.5),('High',.75)]:
        rates={k:float(growth[k].quantile(q)) for k in current}
        terminal=sum(v*(1+rates[k]) for k,v in current.items())
        outlay=sum(sum(v/12*(1+rates[k])**(month/12) for k,v in current.items()) for month in range(1,13))
        scenarios.append({'scenario':label,'historical_quantile':q,'reference_date':latest,'current_annualized_cost':sum(current.values()),
            'terminal_annualized_cost':terminal,'terminal_monthly_cost':terminal/12,'modeled_next_12mo_outlay':outlay,
            **{f'{k}_growth_pct':v*100 for k,v in rates.items()}})
    save('price_scenarios',pd.DataFrame(scenarios))
    national=pd.read_parquet(PROCESSED/'mart_national.parquet').sort_values('year')
    endpoint=int(national.dropna(subset=['affordability_index']).year.max())
    components=pd.read_parquet(PROCESSED/'mart_components.parquet')
    final=components[components.year==endpoint].copy()
    base_income=float(national.loc[national.year==2015,'renter_income'].iloc[0])
    end_income=float(national.loc[national.year==endpoint,'renter_income'].iloc[0])
    weights={**config['sensitivity_weights'],'primary':config['annual_baseline_usd']}
    sensitivity_weights=[]
    for name,budgets in weights.items():
        c0=sum(budgets.values());c1=sum(budgets[r.category]*r.price_relative for r in final.itertuples())
        sensitivity_weights.append({'budget':name,'baseline_cost':c0,'endpoint_cost':c1,'cost_growth_pct':100*(c1/c0-1),
            'affordability_index':100*(end_income/base_income)/(c1/c0)})
    save('weight_sensitivity',pd.DataFrame(sensitivity_weights))
    last=national[national.year==endpoint].iloc[0]
    findings={'baseline_year':2015,'endpoint_year':endpoint,'monthly_reference':str(latest.date()),
        'renter_income_growth_pct':100*(last.renter_income/base_income-1),'modeled_cost_growth_pct':last.essential_cost_index-100,
        'affordability_index':last.affordability_index,'modeled_baseline_annual_cost':last.baseline_annual_cost,
        'modeled_endpoint_annual_cost':last.modeled_annual_cost,'required_income_for_2015_ratio':last.restore_income,
        'required_income_adjustment_pct':100*(last.restore_income/last.renter_income-1),
        'largest_cost_driver':str(final.loc[final.contribution_usd.idxmax(),'category']),
        'contributions_usd':{r.category:float(r.contribution_usd) for r in final.itertuples()},
        'monthly_change_correlation':sensitivity['monthly_changes'],
        'scenario_reference_annualized_cost':sum(current.values()),
        'scenario_terminal_monthly_costs':{r['scenario']:r['terminal_monthly_cost'] for r in scenarios}}
    write_json(REPORTS/'findings.json',findings)
    print(json.dumps(findings,indent=2))


if __name__=='__main__':main()
