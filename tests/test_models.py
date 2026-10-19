import json
import numpy as np
import pandas as pd
import pytest
import duckdb
from common import ROOT,PROCESSED
from build_basket import simulate,restore_baseline
from clean_data import parse_number

@pytest.mark.parametrize('raw',['-666666666','-999999999','**','N','(X)',''])
def test_census_missing_codes_are_not_money(raw):
    assert parse_number(raw) is None


def test_zero_growth_simulator_identity():
    r=simulate(60000,1000,400,60,3)
    assert r['current_annual_cost']==r['future_annual_cost']==18960
    assert r['income_needed_to_keep_ratio']==60000


def test_simulator_accounts_for_gallons_and_growth():
    r=simulate(60000,1000,400,60,3,.1,.02,.03,.2)
    assert r['future_annual_cost']==pytest.approx(12*(1020+412+216))
    assert r['future_cost_share']==pytest.approx(r['future_annual_cost']/66000)

@pytest.mark.parametrize('args',[(0,1,1,1,1),(-1,1,1,1,1),(60000,-10,1,1,1),(60000,1,1,float('inf'),1)])
def test_invalid_simulator_inputs_rejected(args):
    with pytest.raises(ValueError):simulate(*args)


def test_zero_cost_scenario_has_no_restore_ratio():
    assert simulate(60000,0,0,0,0)['income_needed_to_keep_ratio'] is None


def test_restore_baseline_algebra():
    r=restore_baseline(40000,20000,50000,30000)
    assert r['required_income']==60000
    assert r['required_cost']==25000
    assert r['required_income']/30000==40000/20000


def test_baseline_and_component_reconciliation():
    n=pd.read_parquet(PROCESSED/'mart_national.parquet')
    c=pd.read_parquet(PROCESSED/'mart_components.parquet')
    baseline=n[n.year==2015].iloc[0]
    assert baseline.affordability_index==pytest.approx(100)
    assert baseline.essential_cost_index==pytest.approx(100)
    for r in n[n.modeled_annual_cost.notna()].itertuples():
        x=c[c.year==r.year]
        assert x.contribution_usd.sum()==pytest.approx(r.modeled_annual_cost-r.baseline_annual_cost)
        assert len(x)==3
    assert n[n.year==2020].affordability_index.isna().all()
    assert n[n.year>=2025].affordability_index.isna().all()


def test_national_median_not_state_average():
    a=pd.read_parquet(PROCESSED/'acs_observations.parquet')
    n=pd.read_parquet(PROCESSED/'mart_national.parquet')
    source=a[(a.geography_id=='US')&(a.variable=='B25119_003E')].set_index('year').estimate
    for r in n[n.renter_income.notna()].itertuples():assert r.renter_income==source[r.year]


def test_no_partial_item_basket_sum():
    b=pd.read_parquet(PROCESSED/'illustrative_item_basket.parquet')
    assert b[b.valid_items<6].monthly_cost.isna().all()
    assert b[b.valid_items==6].monthly_cost.notna().all()


def test_calendar_lag_and_rolling_are_missing_safe():
    m=pd.read_parquet(PROCESSED/'mart_monthly_price.parquet')
    food=m[m.category=='food'].set_index('date')
    for date in [pd.Timestamp('2025-10-01'),pd.Timestamp('2025-11-01')]:
        assert pd.isna(food.loc[date,'monthly_change_pct'])
    assert pd.isna(food.loc['2015-11-01','rolling_12mo'])
    assert food.loc['2015-12-01','rolling_12mo']>0


def test_state_model_has_50_states_and_separate_dc():
    s=pd.read_parquet(PROCESSED/'mart_state_housing.parquet')
    assert s.groupby('year').geography_id.nunique().eq(50).all()
    assert not s.geography_id.isin(['US','11','72']).any()
    assert s.burden_share.between(0,1).all()
    assert s[['renter_income_moe','gross_rent_moe']].notna().all().all()


def test_sql_and_python_affordability_agree():
    n=pd.read_parquet(PROCESSED/'mart_national.parquet').set_index('year')
    for _,r in n.dropna(subset=['affordability_index']).iterrows():
        expected=100*(r.renter_income/n.loc[2015,'renter_income'])/(r.modeled_annual_cost/n.loc[2015,'modeled_annual_cost'])
        assert r.affordability_index==pytest.approx(expected)


def test_scenario_growth_and_outlay_reproduce():
    s=pd.read_parquet(PROCESSED/'price_scenarios.parquet')
    assert (s.modeled_next_12mo_outlay>0).all()
    assert s.terminal_annualized_cost.is_monotonic_increasing
    assert set(s.scenario)=={'Low','Baseline','High'}


def test_official_geography_names_and_fips_agree():
    g=pd.read_parquet(PROCESSED/'geographies.parquet').set_index('geography_id')
    assert len(g)==52
    assert g.loc['21','name']=='Kentucky'
    assert g.loc['22','name']=='Louisiana'
    assert g.loc['23','name']=='Maine'
    assert g.loc['24','name']=='Maryland'
    assert g.loc['11','geography_type']=='district'


def test_published_national_acs_reference_values():
    h=pd.read_parquet(PROCESSED/'mart_housing.parquet')
    r=h[(h.year==2024)&(h.geography_id=='US')].iloc[0]
    assert r.household_income==81604
    assert r.renter_income==54446
