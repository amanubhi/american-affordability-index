"""Streamlit entrypoint. Run: streamlit run app.py"""
from pathlib import Path
import sys,json
sys.path.insert(0,str(Path(__file__).resolve().parent/'src'))
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from common import ROOT,PROCESSED
from build_basket import simulate
import charts

st.set_page_config(page_title='American Affordability Index',page_icon='📊',layout='wide')
st.markdown('''<style>.stApp {background:#fffdf9} h1,h2,h3 {color:#173b61} [data-testid="stMetricValue"] {color:#173b61} .block-container{max-width:1320px;padding-top:2rem} footer{display:none}</style>''',unsafe_allow_html=True)

@st.cache_data
def load(name):return pd.read_parquet(PROCESSED/f'{name}.parquet')

n=load('mart_national');components=load('mart_components');prices=load('monthly_prices');states=load('mart_state_housing')
findings=json.loads((ROOT/'reports/findings.json').read_text())
page=st.sidebar.radio('Explore',['Overview','State Housing','Cost Breakdown','Simulator'])
st.sidebar.caption('Frozen snapshot: 19 October 2026. Annual affordability: 2015–2024. Monthly prices: through September 2026 where available.')
st.sidebar.markdown('[Source code and methodology](https://github.com/amanubhi/american-affordability-index)')
st.title('The American Affordability Index')
st.caption('Selected essentials, transparent assumptions, and the income needed to afford them.')
if page=='Overview':
    st.subheader('Did renter income keep pace with selected essential costs?')
    st.caption('U.S. • 2015–2024 • ACS renter median income • Illustrative rent, grocery and gasoline budget')
    c=st.columns(4)
    for col,label,value in zip(c,['Modeled cost growth','Renter income growth','Affordability index','Largest dollar driver'],[f"{findings['modeled_cost_growth_pct']:.1f}%",f"{findings['renter_income_growth_pct']:.1f}%",f"{findings['affordability_index']:.1f}",findings['largest_cost_driver'].title()]):col.metric(label,value)
    st.plotly_chart(charts.overview(n),use_container_width=True)
    st.info('The index compares aggregate renter median income with a fixed illustrative budget. It covers rent, food at home and gasoline. It does not measure every household’s finances, take-home pay or all living costs.')
    st.markdown('**Budget:** $1,000 monthly rent, $400 groceries and $150 gasoline in 2015. Price relatives hold that budget structure fixed. Utilities and other costs are omitted. Above 100 indicates improved modeled purchasing power versus 2015.')
    st.dataframe(load('weight_sensitivity').round(2),hide_index=True,use_container_width=True)
    st.caption('Sensitivity uses alternative fixed weights, not statistical confidence intervals. ACS-dependent metrics are missing for 2020. Full methodology and sources are linked in the repository.')
    st.download_button('Download annual results',n.to_csv(index=False),'national_affordability.csv','text/csv')
elif page=='State Housing':
    st.subheader('Where is rent high relative to income?')
    left,right=st.columns(2)
    year=left.selectbox('Survey year',sorted(states.year.unique(),reverse=True))
    metric=right.selectbox('Housing measure',['renter_rent_proxy','all_household_rent_proxy','burden_share'],format_func=lambda x:{'renter_rent_proxy':'Rent / renter income proxy','all_household_rent_proxy':'Rent / all-household income proxy','burden_share':'Observed rent burden ≥30%'}[x])
    st.plotly_chart(charts.state_map(states,int(year),metric),use_container_width=True)
    st.caption('National grocery and gasoline averages are not part of these state rankings. Ratios of medians are proxies. Actual burden uses ACS B25070 and excludes not-computed cases. 2020 standard ACS 1-year is unavailable.')
    f=states[states.year==year].sort_values(metric)
    selected=st.selectbox('Inspect a state',sorted(f.name))
    r=f[f.name==selected].iloc[0];cols=st.columns(3)
    cols[0].metric('Median monthly gross rent',f'${r.monthly_gross_rent:,.0f}',help=f'Published 90% MOE: ±${r.gross_rent_moe:,.0f}')
    cols[1].metric('Renter median annual income',f'${r.renter_income:,.0f}',help=f'Published 90% MOE: ±${r.renter_income_moe:,.0f}')
    cols[2].metric('Observed burden share',f'{r.burden_share:.1%}')
    st.caption(f'Gross rent MOE ±${r.gross_rent_moe:,.0f}; renter income MOE ±${r.renter_income_moe:,.0f} (published 90%). Not-computed burden cases: {r.not_computed_share:.1%} of cash-rent units. Ratios/ranks have no derived confidence interval.')
    st.dataframe(f[['name','monthly_gross_rent','gross_rent_moe','renter_income','renter_income_moe','renter_rent_proxy','all_household_rent_proxy','burden_share']].round(4),hide_index=True,use_container_width=True)
    dc=load('mart_housing');dc=dc[(dc.geography_id=='11')&(dc.year==year)].iloc[0]
    st.caption(f'DC shown separately: rent/renter-income proxy {dc.renter_rent_proxy:.1%}; observed burden {dc.burden_share:.1%}. Statewide point estimates do not identify the best place to live or capture local conditions. Close ranks may be indistinguishable.')
    st.download_button('Download state results',f.to_csv(index=False),f'state_housing_{year}.csv','text/csv')
elif page=='Cost Breakdown':
    st.subheader('What changed the modeled budget?')
    st.plotly_chart(charts.waterfall(components),use_container_width=True)
    st.plotly_chart(charts.price_trends(prices),use_container_width=True)
    rankings=pd.read_csv(ROOT/'reports/sql_results/category_rankings.csv')
    st.plotly_chart(charts.category_rankings(rankings),use_container_width=True)
    st.caption('Category chart uses unweighted medians of eligible item changes, not official category inflation. Coffee and potato chips use reviewed category labels. Broad meat items overlap narrower items, so this chart is descriptive rather than a spending-weighted total.')
    st.plotly_chart(charts.change_scatter(load('monthly_change_pairs')),use_container_width=True)
    st.plotly_chart(charts.shock_timeline(load('mart_monthly_price')),use_container_width=True)
    corr=json.loads((ROOT/'reports/correlation_sensitivity.json').read_text())
    st.dataframe(pd.DataFrame(corr).T.round(3),use_container_width=True)
    st.caption('Detrended levels, seasonally demeaned changes, common-deflator and shock-period checks are descriptive sensitivities. Common deflation can itself induce association. Multiple lag comparisons do not establish a leading indicator or causation.')
    lag=load('lag_correlations');st.line_chart(lag.set_index('lag_months')[['pearson','spearman']])
    st.caption('Positive lag k pairs gasoline change in month t with grocery change in month t+k. Pair counts are exported in lag_correlations.csv.')
    item=load('illustrative_item_basket')
    fig=px.line(item,x='date',y='monthly_cost',labels={'monthly_cost':'Monthly USD'},title='Separate six-item illustrative basket')
    st.plotly_chart(fig,use_container_width=True)
    st.caption('Kaggle/BLS AP through July 2026. Fixed monthly quantities: 2 dozen eggs, 4 gallons milk, 4 lb ground beef, 4 lb white bread, 4 lb bananas, 40 gallons regular gasoline. Incomplete months remain missing. Separate from the main CPI-based model.')
else:
    st.subheader('What would it take to change your modeled budget?')
    st.caption('User-entered scenario • USD • Annual before-tax income and selected monthly expenses • No personal inputs are stored')
    col1,col2=st.columns(2)
    income=col1.number_input('Annual household income ($)',min_value=1000.,max_value=10000000.,value=60000.,step=1000.)
    rent=col1.number_input('Monthly rent ($)',min_value=0.,max_value=100000.,value=1500.,step=50.)
    food=col1.number_input('Monthly groceries ($)',min_value=0.,max_value=100000.,value=500.,step=25.)
    gallons=col1.number_input('Monthly gasoline consumption (US gallons)',min_value=0.,max_value=10000.,value=60.,step=5.)
    gas=prices[prices.category=='gasoline'].sort_values('date').iloc[-1]
    gas_price=col1.number_input('Gasoline price ($/US gallon)',min_value=0.,max_value=100.,value=float(gas.value),step=.1)
    st.caption(f'Gasoline default: EIA national monthly observation, {gas.date:%B %Y}, ${gas.value:.3f}/gallon. All other budget inputs are illustrative user assumptions.')
    ig=col2.slider('Income growth over 12 months (%)',-50.,50.,0.,step=.5)
    rg=col2.slider('Rent growth (%)',-50.,50.,3.,step=.5)
    fg=col2.slider('Grocery growth (%)',-50.,50.,3.,step=.5)
    gg=col2.slider('Gasoline growth (%)',-50.,100.,5.,step=.5)
    result=simulate(income,rent,food,gallons,gas_price,ig/100,rg/100,fg/100,gg/100)
    c=st.columns(3);c[0].metric('Current selected costs / income',f"{result['current_cost_share']:.1%}");c[1].metric('Scenario selected costs / income',f"{result['future_cost_share']:.1%}");c[2].metric('Scenario annual selected cost',f"${result['future_annual_cost']:,.0f}")
    st.write(f"Income needed to maintain your current ratio: ${result['income_needed_to_keep_ratio']:,.0f}" if result['income_needed_to_keep_ratio'] is not None else 'A zero-cost baseline has no defined cost ratio to restore.')
    st.caption('Outputs are terminal annualized amounts after the entered price changes. Remaining income does not represent disposable savings: taxes and omitted expenses still apply.')
    st.plotly_chart(charts.scenario_chart(load('price_scenarios')),use_container_width=True)
    st.dataframe(load('price_scenarios').round(2),hide_index=True,use_container_width=True)
    st.caption('Historical scenarios apply 25th/50th/75th percentiles of annual component growth in 2016–2024, jointly. They are not probability bounds or forecasts. Terminal annualized costs differ from next-12-month outlay, which assumes gradual monthly compounding.')
    restore=load('mart_national').dropna(subset=['affordability_index']).sort_values('year').iloc[-1]
    st.markdown(f"**Restore the 2015 national modeled ratio:** at {int(restore.year)} modeled costs, required renter median income would be ${restore.restore_income:,.0f}, compared with the observed ${restore.renter_income:,.0f}. Signed required change: {(restore.restore_income/restore.renter_income-1)*100:+.1f}%. A negative change means the model already exceeds its baseline affordability.")
