"""Export the same validated results as a browser-only public companion."""
import json,shutil
import pandas as pd
import plotly.express as px
import plotly.io as pio
from plotly.offline import get_plotlyjs
from common import ROOT,PROCESSED,REPORTS
import charts


def main():
    load=lambda name:pd.read_parquet(PROCESSED/f'{name}.parquet')
    national=load('mart_national');prices=load('monthly_prices');components=load('mart_components')
    item=load('illustrative_item_basket');lag=load('lag_correlations')
    itemfig=px.line(item,x='date',y='monthly_cost')
    itemfig.update_yaxes(title='Monthly modeled USD')
    itemfig=charts.style(itemfig,'A separate basket of six everyday items','U.S. • 2015–July 2026 • Kaggle / BLS AP • Fixed quantities; incomplete months remain missing')
    lagfig=px.line(lag,x='lag_months',y=['pearson','spearman'],markers=True)
    lagfig.update_xaxes(title='Months gasoline leads grocery change')
    lagfig=charts.style(lagfig,'Lagged relationships are descriptive','U.S. • BLS CPI / EIA • Positive k pairs gas change t with grocery change t+k • No causal inference')
    figures={'overview':charts.overview(national),'waterfall':charts.waterfall(components),'trends':charts.price_trends(prices),
        'categories':charts.category_rankings(pd.read_csv(REPORTS/'sql_results/category_rankings.csv')),
        'scatter':charts.change_scatter(load('monthly_change_pairs')),'shocks':charts.shock_timeline(load('mart_monthly_price')),
        'scenarios':charts.scenario_chart(load('price_scenarios')),'lags':lagfig,'items':itemfig}
    asrecords=lambda f:json.loads(f.to_json(orient='records',date_format='iso'))
    gas=prices[prices.category=='gasoline'].sort_values('date').iloc[-1]
    dataset={'findings':json.loads((REPORTS/'findings.json').read_text()),'national':asrecords(national),
        'states':asrecords(load('mart_state_housing')),'dc':asrecords(load('mart_housing').query("geography_id=='11'")),
        'weights':asrecords(load('weight_sensitivity')),'correlations':json.loads((REPORTS/'correlation_sensitivity.json').read_text()),
        'gas_default':{'date':str(gas.date.date()),'value':float(gas.value)},
        'figures':{name:json.loads(pio.to_json(fig)) for name,fig in figures.items()}}
    out=ROOT/'web/dist';out.mkdir(parents=True,exist_ok=True)
    (out/'data.json').write_text(json.dumps(dataset,allow_nan=False,separators=(',',':')))
    for source,target in [('index.template.html','index.html'),('site.js','site.js'),('site.css','site.css')]:shutil.copyfile(ROOT/'web'/source,out/target)
    (out/'plotly.min.js').write_text(get_plotlyjs())
    manifest=ROOT/'web/.openai/hosting.json'
    if manifest.exists():
        obj=json.loads(manifest.read_text());obj['static']={'directory':'dist'};manifest.write_text(json.dumps(obj,indent=2)+'\n')
    print(f'Public companion exported: {out}')


if __name__=='__main__':main()
