"""Build a two-page executive brief and a six-page LinkedIn carousel."""
import json
from pathlib import Path
import pandas as pd
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph
from reportlab.lib.utils import ImageReader
from pypdf import PdfReader
from common import ROOT,PROCESSED,REPORTS

INK='#183b56';TEAL='#167d8d';RUST='#c05a37';PAPER='#fffdf9';MUTED='#596d7d'


def text(c,content,x,y,width,size=16,color=INK,font='Helvetica',leading=None):
    style=ParagraphStyle('text',fontName=font,fontSize=size,leading=leading or size*1.35,textColor=HexColor(color))
    p=Paragraph(content,style);_,h=p.wrap(width,2000);p.drawOn(c,x,y-h);return y-h


def background(c,w,h,page,total):
    c.setFillColor(HexColor(PAPER));c.rect(0,0,w,h,fill=1,stroke=0)
    c.setStrokeColor(HexColor('#dcded8'));c.line(44,52,w-44,52)
    c.setFillColor(HexColor(MUTED));c.setFont('Helvetica',9)
    c.drawString(44,33,'AMERICAN AFFORDABILITY INDEX  /  SNAPSHOT 19 OCTOBER 2026')
    c.drawRightString(w-44,33,f'{page} / {total}')


def image(c,path,x,y,width,height):
    c.drawImage(ImageReader(str(path)),x,y,width=width,height=height,preserveAspectRatio=True,anchor='c',mask='auto')


def main():
    out=ROOT/'output/pdf';out.mkdir(parents=True,exist_ok=True)
    f=json.loads((REPORTS/'findings.json').read_text());sens=json.loads((REPORTS/'correlation_sensitivity.json').read_text())
    n=pd.read_parquet(PROCESSED/'mart_national.parquet');r=n[n.year==2024].iloc[0]
    total=r.modeled_annual_cost-r.baseline_annual_cost;rent_share=f['contributions_usd']['rent']/total
    # Executive brief: two deliberately bounded pages, with linked source notes.
    path=out/'executive_brief.pdf';c=canvas.Canvas(str(path),pagesize=(612,792));c.setTitle('The American Affordability Index - Executive Brief')
    background(c,612,792,1,2)
    text(c,'RESEARCH BRIEF / U.S. / 2015-2024',44,746,524,10,TEAL,'Helvetica-Bold')
    y=text(c,'Income outpaced this selected-essential budget',44,710,524,30,INK,'Times-Roman')
    y=text(c,f'Renter median income grew <b>{f["renter_income_growth_pct"]:.1f}%</b>. The primary illustrative budget grew <b>{f["modeled_cost_growth_pct"]:.1f}%</b>.',44,y-18,524,17)
    y=text(c,f'The resulting affordability index is <b>{f["affordability_index"]:.1f}</b> (2015=100), or {f["affordability_index"]-100:.1f}% above baseline. This aggregate model does not establish that every renter became financially better off.',44,y-12,524,13)
    image(c,ROOT/'visuals/04_cost_contributions.png',35,245,542,245)
    y=text(c,'Rent drives the modeled dollar increase',44,232,524,20,INK,'Times-Roman')
    y=text(c,f'Rent adds ${f["contributions_usd"]["rent"]:,.0f}, or {rent_share:.1%}, of the ${total:,.0f} modeled annual increase. The result depends on the fixed budget weights.',44,y-10,524,13)
    text(c,'2015 annual assumptions: rent $12,000, groceries $4,800, gasoline $1,800. Official price relatives hold this structure fixed. Utilities, taxes, healthcare and other costs are omitted.',44,y-12,524,11,MUTED)
    c.showPage();background(c,612,792,2,2)
    text(c,'DECISIONS AND LIMITATIONS',44,746,524,10,TEAL,'Helvetica-Bold')
    y=text(c,'Use the model to test assumptions',44,710,524,29,INK,'Times-Roman')
    for title,body in [
        ('Budget monitoring',f'Replace the illustrative weights with household-specific inputs. Rent drives {rent_share:.1%} of this model\'s increase, but household circumstances can differ.'),
        ('State housing screening','Keep rent/income proxies separate from actual rent-burden prevalence. Retain published margins of error and avoid treating close state ranks as precise.'),
        ('Fuel and grocery planning',f'Monthly change Pearson correlation is {sens["monthly_changes"]["pearson"]:.3f}, versus {sens["levels"]["pearson"]:.3f} for levels. Descriptive lag tests do not demonstrate causation or forecasting value.'),
        ('Twelve-month stress tests',f'Historical-quantile paths from September 2026 price levels yield terminal modeled monthly costs of ${f["scenario_terminal_monthly_costs"]["Low"]:,.0f}, ${f["scenario_terminal_monthly_costs"]["Baseline"]:,.0f} and ${f["scenario_terminal_monthly_costs"]["High"]:,.0f}. These are assumptions, not forecast intervals.')]:
        y=text(c,title,44,y-20,524,15,TEAL,'Helvetica-Bold');y=text(c,body,44,y-7,524,12)
    y=text(c,'Coverage boundaries',44,y-22,524,15,TEAL,'Helvetica-Bold')
    y=text(c,'Annual affordability stops in 2024. Standard ACS 2020 is missing. National prices are not state prices. ACS households and the illustrative budget represent different statistical objects. Income includes more than wages and is before tax.',44,y-7,524,11)
    text(c,'Sources and reproducible methods: <link href="https://github.com/amanubhi/american-affordability-index">github.com/amanubhi/american-affordability-index</link><br/>Census ACS 1-year Summary Files, BLS CPI-U, EIA regular gasoline. Separate item drilldown: Kaggle/BLS AP.',44,118,524,9,MUTED)
    c.save()
    # Carousel: clean typographic pages with one message each.
    path=out/'linkedin_carousel.pdf';c=canvas.Canvas(str(path),pagesize=(720,900));c.setTitle('The American Affordability Index - LinkedIn Case Study')
    def page(number,kicker,title):
        background(c,720,900,number,6);text(c,kicker.upper(),48,843,624,11,TEAL,'Helvetica-Bold');return text(c,title,48,800,624,39,INK,'Times-Roman')
    y=page(1,'U.S. renter income / 2015-2024','Higher prices did not erase the gain in this modeled ratio')
    y=text(c,f'<b>{f["renter_income_growth_pct"]:.1f}%</b>',48,y-35,624,82,INK,'Helvetica-Bold',90)
    y=text(c,'Growth in renter median household income',48,y-7,624,21)
    y=text(c,f'<b>{f["modeled_cost_growth_pct"]:.1f}%</b>',48,y-35,624,82,RUST,'Helvetica-Bold',90)
    y=text(c,'Growth in the illustrative selected-essential budget',48,y-7,624,21)
    text(c,'The model covers rent, food at home and gasoline. It does not capture every expense or every household.',48,220,624,19,MUTED)
    text(c,'Sources: Census ACS 1-year, BLS CPI-U, EIA. Illustrative fixed budget.',48,100,624,11,MUTED);c.showPage()
    y=page(2,'One transparent ratio',f'Affordability index: {f["affordability_index"]:.1f}')
    y=text(c,'2015 = 100',48,y-16,624,25,TEAL)
    y=text(c,'Income relative to 2015 divided by modeled costs relative to 2015.',48,y-35,624,26)
    y=text(c,'Above 100 indicates improved modeled purchasing power for the selected costs.',48,y-30,624,24)
    y=text(c,'The 2015 budget: $1,000 monthly rent, $400 groceries, $150 gasoline. These are illustrative amounts, not an observed average household.',48,y-30,624,22)
    text(c,'Annual comparison stops in 2024. Standard ACS 2020 remains missing. Aggregate median income does not follow the same households over time.',48,205,624,18,MUTED)
    text(c,'Sources: Census ACS renter income; BLS / EIA price relatives. Model v1.',48,100,624,11,MUTED);c.showPage()
    y=page(3,'Dollar contributions / 2015-2024','Rent explains most of this model\'s increase')
    y=text(c,f'${f["contributions_usd"]["rent"]:,.0f}',48,y-24,624,76,RUST,'Helvetica-Bold',86)
    y=text(c,f'of a ${total:,.0f} modeled annual increase ({rent_share:.1%})',48,y-12,624,25)
    image(c,ROOT/'visuals/04_cost_contributions.png',28,230,664,300)
    text(c,'The contribution depends on rent\'s large starting weight as well as its price movement.',48,190,624,19,MUTED)
    text(c,'Sources: BLS rent / grocery CPI, EIA gasoline. Baseline $18,600/year.',48,100,624,11,MUTED);c.showPage()
    y=page(4,'State housing / 2024','A rent-to-income proxy is different from actual burden')
    y=text(c,'Florida: 38.5%',48,y-28,624,43,INK,'Helvetica-Bold')
    y=text(c,'Annualized median gross rent divided by renter median income.',48,y-14,624,23)
    y=text(c,'Florida: 62.1%',48,y-35,624,43,RUST,'Helvetica-Bold')
    y=text(c,'Share in rent-burden bands of 30% or more, among cases with a computable burden.',48,y-14,624,23)
    text(c,'Different denominators answer different questions. State point estimates carry uncertainty. National grocery and gasoline prices do not become state prices.',48,220,624,19,MUTED)
    text(c,'Source: Census ACS 1-year 2024, B25064 / B25119 and B25070.',48,100,624,11,MUTED);c.showPage()
    y=page(5,'Gasoline and groceries / monthly','Changing the metric changes the relationship')
    y=text(c,f'r = {sens["levels"]["pearson"]:.3f}',48,y-30,624,58,INK,'Helvetica-Bold')
    y=text(c,f'Price levels, {sens["levels"]["n"]} paired months',48,y-8,624,23)
    y=text(c,f'r = {sens["monthly_changes"]["pearson"]:.3f}',48,y-35,624,58,TEAL,'Helvetica-Bold')
    y=text(c,f'Consecutive monthly changes, {sens["monthly_changes"]["n"]} valid pairs',48,y-8,624,23)
    text(c,'Trends, seasonality and shock periods matter. Descriptive lags do not establish gasoline causing grocery inflation.',48,220,624,22,MUTED)
    text(c,'Sources: BLS food-at-home CPI / EIA regular gasoline, 2015-Sep 2026.',48,100,624,11,MUTED);c.showPage()
    y=page(6,'Reproducible analysis / decision support','Which assumptions would change your conclusion?')
    y=text(c,'Replace the budget weights. Inspect the state housing definition. Test income, rent, grocery and fuel scenarios.',48,y-30,624,25)
    y=text(c,'Python collects and validates the sources. DuckDB SQL builds the model. The dashboard exposes the assumptions.',48,y-30,624,23)
    y=text(c,'Omitted costs include taxes, healthcare, childcare and utilities. Selected-essential affordability is only part of financial well-being.',48,y-30,624,21,MUTED)
    text(c,'Explore the dashboard and inspect the methods:<br/><link href="https://github.com/amanubhi/american-affordability-index">github.com/amanubhi/american-affordability-index</link>',48,210,624,18,TEAL)
    text(c,'Sources: Census, BLS and EIA. No causal or reliable forecast claims.',48,100,624,11,MUTED);c.save()
    for name,expected in [('executive_brief.pdf',2),('linkedin_carousel.pdf',6)]:
        reader=PdfReader(out/name);assert len(reader.pages)==expected
        assert all(len(p.extract_text())>100 for p in reader.pages)
    print('Created executive_brief.pdf (2 pages) and linkedin_carousel.pdf (6 pages).')


if __name__=='__main__':main()
