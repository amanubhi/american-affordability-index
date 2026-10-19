"""Seven publication-ready charts, plus interactive HTML versions."""
import json
import numpy as np
import pandas as pd
import plotly.express as px
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from common import ROOT,PROCESSED,REPORTS
import charts

COLORS=charts.COLORS


def main():
    out=ROOT/'visuals';out.mkdir(exist_ok=True)
    plt.rcParams.update({'text.parse_math':False,'font.family':'DejaVu Sans','font.size':12,'axes.spines.top':False,'axes.spines.right':False,'axes.spines.left':False,'axes.grid':True,'grid.alpha':.15,'axes.axisbelow':True,'figure.facecolor':'#fffdf9','axes.facecolor':'#fffdf9','text.color':'#20364b','axes.labelcolor':'#20364b'})
    load=lambda name:pd.read_parquet(PROCESSED/f'{name}.parquet')
    def finish(fig,name,title,subtitle,source):
        fig.suptitle(title,x=.09,y=.97,ha='left',fontsize=20,fontweight='bold')
        fig.text(.09,.91,subtitle,fontsize=11,color='#596d7d')
        fig.text(.09,.025,source,fontsize=9,color='#596d7d')
        fig.subplots_adjust(left=.25 if name=='02_category_rankings' else .1,right=.94,top=.84,bottom=.15)
        fig.savefig(out/f'{name}.png',dpi=180,facecolor=fig.get_facecolor())
        fig.savefig(out/f'{name}.svg',facecolor=fig.get_facecolor());plt.close(fig)
    p=load('monthly_prices');n=load('mart_national');c=load('mart_components')
    f=json.loads((REPORTS/'findings.json').read_text())
    fig,ax=plt.subplots(figsize=(13,7))
    for cat in ['food','gasoline']:
        x=p[p.category==cat].sort_values('date');base=x[x.date.dt.year==2015].value.mean()
        ax.plot(x.date,x.value/base*100,label=charts.LABELS[cat],color=COLORS[cat],linewidth=2)
    ax.axhline(100,color='#8a969e',linestyle='--',linewidth=1);ax.set_ylabel('2015 annual mean = 100');ax.legend(frameon=False)
    finish(fig,'01_indexed_prices','Gasoline swings more sharply than grocery prices','U.S. monthly series, 2015–September 2026; 2026 is partial','Source: BLS food-at-home CPI-U (NSA), EIA regular gasoline. Indexes rebased to calendar-2015 averages.')
    ranks=pd.read_csv(REPORTS/'sql_results/category_rankings.csv').sort_values('median_item_change_pct')
    fig,ax=plt.subplots(figsize=(13,8))
    ax.barh(ranks.category,ranks.median_item_change_pct,color=COLORS['food'])
    for i,r in enumerate(ranks.itertuples()):ax.text(r.median_item_change_pct+.5,i,f'{r.median_item_change_pct:.1f}%  (n={r.eligible_items})',va='center',fontsize=10)
    ax.set_xlim(0,max(ranks.median_item_change_pct)*1.35);ax.set_xlabel('Median eligible item price change (%)');ax.grid(axis='y',visible=False)
    finish(fig,'02_category_rankings','Grocery category changes vary across eligible items','2015 versus 2024 full calendar-year means; unweighted item medians','Source: Kaggle v2 / BLS AP. 12 valid months required in both years. Revised categories. Not official category inflation.')
    fig,ax=plt.subplots(figsize=(13,7));x=n[n.year<=2024].sort_values('year')
    ax.plot(x.year,x.modeled_annual_cost,color=COLORS['rent'],linewidth=3,marker='o');ax.yaxis.set_major_formatter(FuncFormatter(lambda x,_:f'${x:,.0f}'));ax.set_ylabel('Modeled annual selected-essential cost (USD)')
    finish(fig,'03_basket_cost','The fixed illustrative budget becomes more expensive',f"U.S., 2015–2024; ${f['modeled_baseline_annual_cost']:,.0f} to ${f['modeled_endpoint_annual_cost']:,.0f} per year",'Source: BLS CPI / EIA. 2015 baseline: rent $12,000; food $4,800; gasoline $1,800. Utilities and other costs omitted.')
    fig,ax=plt.subplots(figsize=(13,7));cc=c[c.year==2024].sort_values('category');base=cc.baseline_annual_usd.sum();total=base
    ax.bar('2015',base,color=COLORS['income'])
    for r in cc.itertuples():
        ax.bar(charts.LABELS[r.category],r.contribution_usd,bottom=total,color=COLORS[r.category]);ax.text(charts.LABELS[r.category],total+r.contribution_usd+250,f'+${r.contribution_usd:,.0f}',ha='center',fontsize=11);total+=r.contribution_usd
    ax.bar('2024',total,color=COLORS['income']);ax.text('2015',base+250,f'${base:,.0f}',ha='center');ax.text('2024',total+250,f'${total:,.0f}',ha='center');ax.set_ylim(0,total*1.14);ax.set_ylabel('Modeled annual USD');ax.yaxis.set_major_formatter(FuncFormatter(lambda x,_:f'${x:,.0f}'))
    finish(fig,'04_cost_contributions','Rent adds the most dollars under the primary budget weights','U.S., 2015–2024; fixed illustrative category budgets','Source: BLS CPI / EIA. Contributions depend on baseline weights; they do not describe observed household spending.')
    pairs=load('monthly_change_pairs').dropna();r=f['monthly_change_correlation']
    fig,ax=plt.subplots(figsize=(13,7));ax.scatter(pairs.gasoline,pairs.food,s=34,alpha=.6,color=COLORS['food']);ax.axhline(0,color='#7f8d96',linewidth=1);ax.axvline(0,color='#7f8d96',linewidth=1);ax.set_xlabel('Regular gasoline monthly change (%)');ax.set_ylabel('Food-at-home monthly change (%)')
    finish(fig,'05_monthly_relationship','Price-change relationships differ from price-level relationships',f"U.S., 2015–September 2026; Pearson r={r['pearson']:.3f}, n={r['n']} valid month pairs",'Source: BLS CPI / EIA. Consecutive monthly changes only. Association does not establish causation or forecasting value.')
    monthly=load('mart_monthly_price');fig,axes=plt.subplots(2,1,figsize=(13,8),sharex=True)
    for ax,cat in zip(axes,['gasoline','food']):
        x=monthly[(monthly.category==cat)&monthly.monthly_change_pct.notna()]
        ax.plot(x.date,x.monthly_change_pct,color=COLORS[cat],linewidth=1.7);ax.set_ylabel(charts.LABELS[cat]+'\nmonthly change (%)');ax.axhline(0,color='#8a969e',linewidth=1)
        top=x.loc[x.monthly_change_pct.abs().nlargest(1).index].iloc[0]
        ax.annotate(f'{top.date:%b %Y}: {top.monthly_change_pct:+.1f}%',xy=(top.date,top.monthly_change_pct),xytext=(-120 if top.date.year>=2025 else 20,15 if top.monthly_change_pct<0 else -30),textcoords='offset points',fontsize=10,arrowprops=dict(arrowstyle='-',color='#596d7d'))
    finish(fig,'06_shock_timeline','Large price movements occur at different times','U.S., 2015–September 2026; separate scales preserve grocery detail','Source: BLS CPI / EIA. Largest absolute observed monthly movement annotated per series. No causal event attribution.')
    scenarios=load('price_scenarios');fig,ax=plt.subplots(figsize=(13,7));ax.bar(scenarios.scenario,scenarios.terminal_monthly_cost,color=[COLORS['food'],COLORS['income'],COLORS['rent']]);ax.set_ylabel('Terminal monthly selected-essential cost (USD)');ax.yaxis.set_major_formatter(FuncFormatter(lambda x,_:f'${x:,.0f}'))
    for r in scenarios.itertuples():ax.text(r.scenario,r.terminal_monthly_cost+25,f'${r.terminal_monthly_cost:,.0f}',ha='center')
    ax.set_ylim(0,scenarios.terminal_monthly_cost.max()*1.14)
    finish(fig,'07_price_scenarios','Budget outcomes depend on the assumed price path','12-month stress tests starting from September 2026 price levels','Source: BLS CPI / EIA; 2016–2024 growth quantiles 25/50/75%, applied jointly. Illustrative scenarios, not forecasts.')
    htmls={'01_indexed_prices':charts.price_trends(p),'02_category_rankings':charts.category_rankings(ranks),'03_basket_cost':charts.style(px.line(n[n.year<=2024].sort_values('year'),x='year',y='modeled_annual_cost'),'Fixed illustrative basket cost','U.S. • 2015–2024 • BLS CPI / EIA • Modeled annual USD; illustrative budget'),'04_cost_contributions':charts.waterfall(c),'05_monthly_relationship':charts.change_scatter(pairs),'06_shock_timeline':charts.shock_timeline(monthly),'07_price_scenarios':charts.scenario_chart(scenarios)}
    for name,fig in htmls.items():fig.write_html(out/f'{name}.html',include_plotlyjs='directory')
    print('Exported seven PNG/SVG charts and interactive HTML counterparts.')


if __name__=='__main__':main()
