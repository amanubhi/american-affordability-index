"""Shared interactive figure definitions for the app, website and exports."""
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

COLORS={'rent':'#c05a37','food':'#167d8d','gasoline':'#dfac38','income':'#173b61'}
LABELS={'rent':'Rent','food':'Food at home','gasoline':'Regular gasoline'}


def style(fig,title,source,height=440):
    fig.update_layout(title=dict(text=title,font=dict(size=23)),height=height,
        template='plotly_white',font=dict(family='Arial',size=13,color='#20364b'),
        margin=dict(l=55,r=30,t=90,b=90),paper_bgcolor='#fffdf9',plot_bgcolor='#fffdf9',
        legend=dict(orientation='h',y=1.12,title=None))
    fig.add_annotation(text=source,x=0,y=-.23,xref='paper',yref='paper',showarrow=False,xanchor='left',font=dict(size=10,color='#637180'))
    return fig


def overview(national):
    n=national[national.year<=int(national.dropna(subset=['affordability_index']).year.max())].sort_values('year')
    n=n.set_index('year').reindex(range(2015,int(n.year.max())+1)).reset_index()
    fig=go.Figure()
    for col,name,color in [('renter_income_index','Renter median income',COLORS['income']),('essential_cost_index','Modeled selected costs',COLORS['rent'])]:
        fig.add_scatter(x=n.year,y=n[col],mode='lines+markers',name=name,line=dict(color=color,width=3),connectgaps=False)
    fig.update_yaxes(title='2015 = 100')
    return style(fig,'Income growth versus a fixed budget of essentials','U.S. • 2015–2024 • Census ACS, BLS CPI, EIA • Illustrative budget; ACS 2020 gap')


def price_trends(prices):
    f=prices[prices.category.isin(['food','gasoline'])].copy()
    baseline=f[f.date.dt.year==2015].groupby('category').value.mean()
    f['index_2015']=f.value/f.category.map(baseline)*100
    fig=px.line(f,x='date',y='index_2015',color='category',color_discrete_map=COLORS)
    fig.update_yaxes(title='2015 annual average = 100')
    return style(fig,'Groceries and gasoline follow different price paths','U.S. • 2015–2026 • BLS food-at-home CPI / EIA regular gasoline • Monthly, NSA')


def waterfall(components,year=2024):
    c=components[components.year==year].sort_values('category')
    total=c.baseline_annual_usd.sum()
    fig=go.Figure(go.Waterfall(x=['2015',*[LABELS[x] for x in c.category],str(year)],
        y=[total,*c.contribution_usd,0],measure=['absolute',*['relative']*len(c),'total'],
        text=[f'${v:,.0f}' for v in [total,*c.contribution_usd,c.modeled_annual_usd.sum()]],textposition='outside',
        increasing=dict(marker=dict(color=COLORS['rent'])),totals=dict(marker=dict(color=COLORS['income']))))
    fig.update_yaxes(title='Modeled annual USD',rangemode='tozero')
    return style(fig,'Which categories added the most dollars?','U.S. • 2015–2024 • BLS CPI / EIA • Fixed illustrative baseline: $18,600/year')


def category_rankings(frame):
    f=frame.sort_values('median_item_change_pct')
    fig=px.bar(f,x='median_item_change_pct',y='category',orientation='h',text='eligible_items',color_discrete_sequence=[COLORS['food']])
    fig.update_traces(texttemplate='n=%{text}',textposition='outside')
    fig.update_xaxes(title='Median eligible item change (%)')
    return style(fig,'Grocery category changes depend on which items qualify','U.S. • 2015 vs 2024 annual means • Kaggle / BLS AP • 12 months required in both years',560)


def change_scatter(pairs):
    p=pairs.dropna();fig=px.scatter(p,x='gasoline',y='food',color_discrete_sequence=[COLORS['food']],hover_data=['date'],opacity=.65)
    fig.add_hline(y=0,line_color='#b4bdc5',line_width=1);fig.add_vline(x=0,line_color='#b4bdc5',line_width=1)
    fig.update_xaxes(title='Gasoline monthly change (%)');fig.update_yaxes(title='Food-at-home monthly change (%)')
    return style(fig,'Monthly movements test the relationship beyond price levels','U.S. • Consecutive monthly changes • BLS CPI / EIA • Association does not establish causation')


def shock_timeline(monthly):
    f=monthly[monthly.category.isin(['food','gasoline']) & monthly.monthly_change_pct.notna()]
    fig=px.line(f,x='date',y='monthly_change_pct',color='category',color_discrete_map=COLORS)
    for start,end,label in [('2020-03-01','2021-12-31','Pandemic period'),('2022-01-01','2023-12-31','Inflation / adjustment period')]:
        fig.add_vrect(x0=start,x1=end,fillcolor='#8092a0',opacity=.08,line_width=0,annotation_text=label,annotation_position='top left')
    fig.update_yaxes(title='Monthly change (%)')
    return style(fig,'Price shocks vary in timing and size','U.S. • 2015–2026 • BLS CPI / EIA • Period labels provide context, not causal attribution')


def scenario_chart(scenarios):
    fig=px.bar(scenarios,x='scenario',y='terminal_monthly_cost',text_auto='$.0f',
        color='scenario',color_discrete_map={'Low':COLORS['food'],'Baseline':COLORS['income'],'High':COLORS['rent']})
    fig.update_yaxes(title='Terminal monthly modeled cost (USD)',rangemode='tozero')
    date=pd.to_datetime(scenarios.reference_date.iloc[0]).strftime('%b %Y')
    return style(fig,'Three illustrative 12-month price paths',f'U.S. • From {date} price levels • Historical 2016–2024 growth quantiles • Scenarios, not forecasts')


def state_map(states,year,metric):
    f=states[states.year==year].copy();f['display']=f[metric]*100
    names={'renter_rent_proxy':'Rent / renter median income proxy','all_household_rent_proxy':'Rent / all-household median income proxy','burden_share':'Rent burden ≥30% among computable cases'}
    fig=px.choropleth(f,locations='abbreviation',locationmode='USA-states',color='display',scope='usa',
        hover_name='name',color_continuous_scale=['#d4e8e5','#448c91','#183e5b'],labels={'display':'Percent'})
    fig.update_geos(showlakes=False,bgcolor='#fffdf9')
    return style(fig,names[metric],f'50 U.S. states • {year} • Census ACS 1-year • Point estimates; uncertainty can affect ranks',550)
