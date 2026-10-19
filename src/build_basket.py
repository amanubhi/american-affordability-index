"""Fixed illustrative item basket and pure simulator arithmetic."""
import json
import math
import numpy as np
import pandas as pd
from common import ROOT,PROCESSED
from clean_data import save


def simulate(income, monthly_rent, monthly_groceries, monthly_gallons, gas_price,
             income_growth=0, rent_growth=0, food_growth=0, gas_growth=0):
    values=[income,monthly_rent,monthly_groceries,monthly_gallons,gas_price]
    if not all(math.isfinite(x) and x>=0 for x in values) or income<=0:
        raise ValueError('Income must be positive and cost inputs finite and nonnegative.')
    growths=[income_growth,rent_growth,food_growth,gas_growth]
    if not all(math.isfinite(x) and x>-1 for x in growths):raise ValueError('Growth rates must exceed -100%.')
    current=12*(monthly_rent+monthly_groceries+monthly_gallons*gas_price)
    future=12*(monthly_rent*(1+rent_growth)+monthly_groceries*(1+food_growth)+monthly_gallons*gas_price*(1+gas_growth))
    next_income=income*(1+income_growth)
    return dict(current_annual_cost=current,future_annual_cost=future,current_cost_share=current/income,
        future_cost_share=future/next_income,current_remaining=income-current,future_remaining=next_income-future,
        income_needed_to_keep_ratio=income*future/current if current>0 else None)


def restore_baseline(baseline_income,baseline_cost,current_income,current_cost):
    if min(baseline_income,baseline_cost,current_income,current_cost)<=0:raise ValueError('Inputs must be positive.')
    return dict(required_income=baseline_income*current_cost/baseline_cost,
        required_cost=baseline_cost*current_income/baseline_income)


def main():
    config=json.loads((ROOT/'config/budget.json').read_text())
    f=pd.read_parquet(PROCESSED/'item_prices.parquet')
    specs=pd.DataFrame(config['item_basket']).rename(columns={'unit':'expected_source_unit'})
    g=f.merge(specs,on='series_id',validate='many_to_one')
    if not g.source_unit.eq(g.expected_source_unit).all():raise ValueError('Basket unit mismatch')
    calendar=pd.date_range(f.date.min(),f.date.max(),freq='MS')
    wide=g.pivot(index='date',columns='series_id',values='price').reindex(calendar)
    quantities=specs.set_index('series_id').quantity_per_month
    costs=wide.mul(quantities,axis=1)
    total=costs.sum(axis=1,min_count=len(specs))
    basket=pd.DataFrame({'date':calendar,'monthly_cost':total,'valid_items':wide.notna().sum(axis=1)})
    base=total[total.index.year==2015]
    if base.notna().sum()!=12:raise ValueError('Incomplete 2015 item basket baseline')
    basket['index_2015']=100*basket.monthly_cost/base.mean()
    save('illustrative_item_basket',basket)
    latest=total.dropna().index.max()
    baseline=costs[costs.index.year==2015].mean()
    result=specs.merge(g[['series_id','item','category','unit']].drop_duplicates(),on='series_id',validate='one_to_one')
    result['baseline_monthly_cost']=result.series_id.map(baseline)
    result['latest_monthly_cost']=result.series_id.map(costs.loc[latest])
    result['dollar_change']=result.latest_monthly_cost-result.baseline_monthly_cost
    result['endpoint']=latest
    save('item_basket_contributions',result)
    print(f'Item basket: {len(specs)} mutually distinct items, {basket.monthly_cost.notna().sum()} complete months; no missing-cost sums.')


if __name__=='__main__':main()
