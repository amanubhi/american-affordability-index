"""README price-basket visual; uses observed monthly data, not annual income."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import FuncFormatter
import pandas as pd
from common import ROOT


def main():
    data = pd.read_csv(ROOT/'data/processed/illustrative_item_basket.csv', parse_dates=['date']).sort_values('date')
    valid = data.dropna(subset=['monthly_cost'])
    latest = valid.iloc[-1]
    fig, ax = plt.subplots(figsize=(13, 7), facecolor='#fffdf9')
    ax.set_facecolor('#fffdf9')
    ax.plot(data.date, data.monthly_cost, color='#147d89', linewidth=2.5)
    ax.scatter([latest.date], [latest.monthly_cost], color='#c56b35', s=65, zorder=4)
    ax.annotate(f"${latest.monthly_cost:,.2f}/month", (latest.date, latest.monthly_cost),
                xytext=(-12, 22), textcoords='offset points', ha='right', fontsize=13, fontweight='bold', color='#20364b')
    ax.set_ylabel('Illustrative monthly basket cost (USD)', color='#20364b')
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, _: f'${x:,.0f}'))
    ax.xaxis.set_major_locator(mdates.YearLocator(2))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    ax.grid(axis='y', alpha=.15)
    for side in ['top','right','left']:
        ax.spines[side].set_visible(False)
    fig.suptitle('The price of everyday essentials', x=.09, y=.96, ha='left', fontsize=25, fontweight='bold', color='#20364b')
    fig.text(.09, .885, f"January 2015–{latest.date.strftime('%B %Y')} | Fixed quantities | National average prices", fontsize=13, color='#596d7d')
    fig.text(.09, .08, 'Monthly quantities: 2 dozen eggs, 4 gal milk, 4 lb ground beef, 4 lb white bread, 4 lb bananas, 40 gal regular gasoline.', fontsize=9, color='#596d7d')
    fig.text(.09, .045, 'Source: Kaggle / BLS Average Prices, refreshed November 2026. Missing months remain gaps. 2026 is partial.', fontsize=9, color='#596d7d')
    fig.text(.09, .015, 'Illustrative item basket; excludes housing and other expenses. Separate from the income-based annual affordability index.', fontsize=9, color='#596d7d')
    fig.subplots_adjust(left=.09, right=.95, bottom=.19, top=.8)
    fig.savefig(ROOT/'visuals/08_item_basket_2026.png', dpi=180)
    plt.close(fig)


if __name__ == '__main__':
    main()
