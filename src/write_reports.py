"""Write the case study from computed evidence rather than prefilled claims."""
import json
import pandas as pd
from common import ROOT,PROCESSED,REPORTS

REPO='https://github.com/amanubhi/american-affordability-index'
SITE='https://american-affordability-index.sunlittuna11.chatgpt.site'


def main():
    f=json.loads((REPORTS/'findings.json').read_text());q=json.loads((REPORTS/'validation_results.json').read_text())
    sens=json.loads((REPORTS/'correlation_sensitivity.json').read_text())
    n=pd.read_parquet(PROCESSED/'mart_national.parquet');last=n[n.year==2024].iloc[0]
    c=pd.read_parquet(PROCESSED/'mart_components.parquet');c=c[c.year==2024]
    increase=last.modeled_annual_cost-last.baseline_annual_cost
    share=f['contributions_usd']['rent']/increase
    s=pd.read_parquet(PROCESSED/'mart_state_housing.parquet');s=s[s.year==2024].sort_values('renter_rent_proxy')
    low,high=s.iloc[0],s.iloc[-1]
    vol=pd.read_csv(REPORTS/'sql_results/item_volatility.csv')
    weights=pd.read_parquet(PROCESSED/'weight_sensitivity.parquet')
    def put(name,text):(REPORTS/name).write_text(text.strip()+'\n')
    contribution_rows='\n'.join(f'| {r.category.title()} | ${r.baseline_annual_usd:,.0f} | ${r.contribution_usd:,.0f} | {r.contribution_usd/increase:.1%} |' for r in c.itertuples())
    put('executive_summary.md',f'''# The American Affordability Index — executive case study

**Result:** Between 2015 and 2024, U.S. renter median household income increased **{f['renter_income_growth_pct']:.1f}%**, while the primary illustrative rent, food-at-home and gasoline budget increased **{f['modeled_cost_growth_pct']:.1f}%**. The resulting selected-essential affordability index is **{f['affordability_index']:.1f}** (2015=100), a modeled improvement of {f['affordability_index']-100:.1f}%.

This result does not establish that every renter or Americans overall became better off. Aggregate medians cover changing households, the budget is illustrative, and major expenses and taxes are omitted. The analysis did not force a cost-squeeze narrative onto contrary evidence.

## Business problem and approach

The question is whether income kept pace with selected essential costs, which expense drives modeled dollar pressure, and how housing pressure differs by state. The project combines frozen Census ACS 1-year Summary Files, BLS CPI-U, EIA regular gasoline and a separate Kaggle/BLS item-price drilldown. pandas normalizes sources; DuckDB SQL enforces grains and computes marts; SciPy performs descriptive relationship checks; Plotly/Streamlit and a public static companion expose results and scenarios.

The primary 2015 budget is $12,000 rent + $4,800 groceries + $1,800 gasoline annually. Each grows by its official price relative. Utilities are omitted because the national rent component uses rent CPI; gross rent including relevant utilities is reserved for the state housing comparison. The model is not a measured average household basket or an official inflation index.

## Six analytical answers

1. **Income versus costs:** renter median income rises from $35,863 to ${last.renter_income:,.0f}; modeled annual costs rise from $18,600 to ${last.modeled_annual_cost:,.0f}. Income grows {f['renter_income_growth_pct']-f['modeled_cost_growth_pct']:.1f} percentage points faster. Relative purchasing-power improvement is {f['affordability_index']-100:.1f}%, not that percentage-point gap.
2. **Dollar driver:** rent contributes ${f['contributions_usd']['rent']:,.0f}, or {share:.1%}, of the ${increase:,.0f} modeled annual increase. This reflects both its price relative and its large baseline weight.
3. **Housing pressure:** in 2024 the renter-aligned rent/income proxy ranges from {low.renter_rent_proxy:.1%} in {low['name']} to {high.renter_rent_proxy:.1%} in {high['name']}. Florida's directly estimated burden-band share is {high.burden_share:.1%} among cases where burden is computable, a distinct measure with a different denominator.
4. **Gasoline and grocery timing:** same-month level Pearson correlation is {sens['levels']['pearson']:.3f} (n={sens['levels']['n']}); consecutive-month change correlation is {sens['monthly_changes']['pearson']:.3f} (n={sens['monthly_changes']['n']}). Descriptive period correlations change sign. Lag searches and sensitivity checks do not identify a stable causal pass-through or validated forecast.
5. **Income-to-rent screening:** North Dakota has the lowest 2024 point-estimate renter rent/income proxy among the 50 states. That ranking is a screening result, not a recommendation on where to live. Published input MOEs appear in the dashboard; close ranks may be statistically indistinguishable. DC is separate.
6. **Restore 2015 affordability:** at 2024 modeled costs, required renter median income would be ${last.restore_income:,.0f}, versus observed ${last.renter_income:,.0f}. No increase is required under this model because the ratio already exceeds its 2015 level. The signed algebraic adjustment is {f['required_income_adjustment_pct']:+.1f}%; it is not a recommendation to reduce income.

## Dollar decomposition

| Component | Illustrative annual baseline | Increase by 2024 | Share of increase |
|---|---:|---:|---:|
{contribution_rows}

Rounding can prevent displayed dollars from adding exactly. Unrounded contributions reconcile in tests and exported data.

## Decisions supported

- **Consumers:** monitor rent when evaluating recurring commitments. It drives {share:.1%} of this model's increase, but households should replace the illustrative weights with their own budget. The simulator makes that sensitivity visible.
- **Grocery businesses:** monitor seasonal produce and eggs with month-aware comparisons. Among series with at least 60 valid changes, strawberries, grapes and eggs have monthly-change standard deviations of {vol.iloc[0].monthly_change_stddev_pp:.2f}, {vol.iloc[1].monthly_change_stddev_pp:.2f} and {vol.iloc[2].monthly_change_stddev_pp:.2f} percentage points. These NSA movements combine seasonality and other changes; they do not establish inventory risk or margins for any business.
- **Business planners:** stress-test rent, grocery and fuel assumptions separately. The historical-quantile paths produce terminal monthly modeled costs of ${f['scenario_terminal_monthly_costs']['Low']:,.0f}, ${f['scenario_terminal_monthly_costs']['Baseline']:,.0f} and ${f['scenario_terminal_monthly_costs']['High']:,.0f}, starting from September 2026 prices. They are illustrative joint scenarios, not forecast intervals or probabilities.
- **Housing researchers/policymakers:** use the direct ACS burden-band measure when assessing prevalence. A ratio of medians cannot substitute for household burden. Review local and population-specific data before policy or relocation decisions.

## Robustness, uncertainty and limitations

Alternative fixed budget weights yield affordability indexes from {weights.affordability_index.min():.1f} to {weights.affordability_index.max():.1f}; all four tested budgets exceed 100. This is a limited assumption sensitivity, not proof for all household budgets. Correlation sensitivity outputs include detrended levels, month-demeaned changes, common-CPI-deflated levels, shock exclusions, historical periods, lags 0–12 and 36-month rolling correlations. Common deflation can itself induce association.

ACS standard 2020 is absent. There are no annual 2025/2026 affordability estimates; the latest available common year on the October 19 snapshot is 2024. October 2025 CPI gaps prevent complete annual means under the strict rule. The separate Kaggle source ends July 2026. No national prices are relabeled as state prices. The project retains actual input MOEs but does not invent uncertainty intervals for derived ratios.

## Evidence and reproduction

Sources: [Census Summary Files](https://www.census.gov/programs-surveys/acs/data/summary-file.html), [BLS CPI API](https://www.bls.gov/developers/api_signature_v2.htm), [EIA regular gasoline](https://www.eia.gov/dnav/pet/hist/LeafHandler.ashx?n=PET&s=EMM_EPMR_PTE_NUS_DPG&f=M), [Kaggle/BLS AP](https://www.kaggle.com/datasets/harshitsama/us-grocery-and-gas-prices-2015-2026).

{q['source_resources']} official-source resources are hashed. All {q['acs_rows']:,} ACS observations pass key, coverage and burden-universe checks. SQL exports, findings JSON, data dictionaries and code reproduce every number above. Run `python src/run_pipeline.py` and `python -m pytest -q`. See the source registry and limitations for definitions.
''')
    put('linkedin_case_study.md',f'''# LinkedIn case study — ready-to-post draft

U.S. renter median income rose {f['renter_income_growth_pct']:.1f}% from 2015 to 2024. My illustrative budget of rent, groceries and gasoline rose {f['modeled_cost_growth_pct']:.1f}%.

That produces an affordability index of {f['affordability_index']:.1f}, with 2015 set to 100.

I built the American Affordability Index to investigate whether income kept pace with selected essentials, using official Census, BLS and EIA data. Python handles ingestion and validation; DuckDB SQL builds the analytical model; an interactive dashboard exposes the assumptions.

Three verified findings:

• Modeled purchasing power improved {f['affordability_index']-100:.1f}% under the primary fixed budget, despite higher prices.
• Rent contributed ${f['contributions_usd']['rent']:,.0f} of the ${increase:,.0f} annual modeled cost increase ({share:.1%}).
• Gasoline and grocery monthly price changes had a Pearson correlation of {sens['monthly_changes']['pearson']:.3f} across {sens['monthly_changes']['n']} valid month pairs. Their level correlation told a different story.

The practical value is transparent budget stress testing and state housing screening. The model uses illustrative weights and aggregate renter income. It excludes taxes and major expenses, so it cannot establish that every household became better off. Standard ACS data also leave a 2020 gap.

The dashboard lets users replace assumptions and inspect a separate state housing comparison.

Which omitted expense would most change the affordability picture for the households you work with?

Dashboard: {SITE}
Code and methodology: {REPO}

#DataAnalytics #SQL #Python #BusinessIntelligence

---
Prepared as a draft. No LinkedIn account was accessed and no post was sent. Share the carousel PDF alongside the post after reviewing its scope disclosures.
''')
    put('interview_preparation.md',f'''# Interview walkthrough

## Two-minute first-person draft

I selected affordability because price changes become more useful when connected to an explicit budget and income measure. I began with a Kaggle grocery/gas dataset and found it contained only national average prices, uneven histories and a coffee category error. That changed the scope.

I added official ACS, CPI and EIA sources. Census API data queries required a key, so I implemented the documented public Summary File route, including two different historical formats. I preserved raw snapshots and hashes, joined sequences through source geography records, retained margins of error and validated all 50 states, DC and the nation. I kept the 2020 ACS gap visible.

I used pandas for source normalization and DuckDB for facts, dimensions and separate national/state marts. SQL uses CTEs, CASE, LAG/LEAD, calendar joins, ranks and rolling windows. A monthly calendar prevents gaps from becoming false one-month changes, and complete-period checks prevent partial basket totals.

The surprising result was that renter median income grew {f['renter_income_growth_pct']:.1f}% while the primary illustrative selected-cost budget grew {f['modeled_cost_growth_pct']:.1f}% by 2024. I reported an affordability index of {f['affordability_index']:.1f} rather than forcing the original squeeze narrative. Rent still drove {share:.1%} of the modeled dollar increase.

The result supports budget stress testing, not broad welfare claims. I separated the state housing proxy from actual rent-burden prevalence, retained input MOEs and avoided causal gasoline claims. The dashboard lets users inspect the assumptions. With better data, I would add compatible household-type weights, taxes, healthcare and local prices, then validate whether conclusions survive those changes.

## Five realistic questions and answer notes

1. **Why can't you join national grocery prices to each state and call it a state cost-of-living index?** A join can be technically valid while creating false geographic precision. I keep state housing/income separate and label national price assumptions explicitly.
2. **How did you handle missing October 2025 values and the 2020 ACS gap?** No interpolation. Monthly changes require adjacent valid calendar months, annual means require 12 values, complete baskets require all items, and ACS-derived 2020 results remain missing.
3. **Why did you choose renter income rather than wages or all-household income?** It better aligns with a renter-focused housing model. Household income is not wages; all-household income remains a separate comparison. Changing aggregate populations remains a limitation.
4. **How do you know the affordability and contribution formulas are correct?** Baseline index must equal 100, SQL and Python independently agree, dollar contributions sum to total modeled change, national medians match national source observations, and simulator identity/invalid-input tests pass.
5. **What would make the gasoline/grocery correlation misleading?** Trends, seasonality, shocks, missing-month misalignment and multiple lag searches. Level Pearson r is {sens['levels']['pearson']:.3f}, versus {sens['monthly_changes']['pearson']:.3f} for monthly changes. Sensitivity checks do not establish causality or out-of-sample prediction.

## Demonstration order

Show the national timeline and scope labels, inspect the source quality report, open a SQL query and a reconciliation test, compare the two state housing measures, then change a simulator input. Finish with limitations and improvements rather than unsupported forecasts.
''')
    put('ANALYSIS_RESULTS.md',(REPORTS/'executive_summary.md').read_text()+'''\n## Machine-readable evidence map

| Claim | Primary outputs |
|---|---|
| Income/cost/index and restore ratio | findings.json; data/processed/mart_national.csv |
| Dollar contributions | data/processed/mart_components.csv; sql_results/basket_contributions.csv |
| State comparisons | data/processed/mart_state_housing.csv; mart_housing.csv includes DC/nation |
| Monthly relationship and sensitivities | correlation_sensitivity.json; lag_correlations.csv; rolling_correlations.csv |
| Item volatility/rankings | sql_results/item_volatility.csv; category_rankings.csv; item_rankings.csv |
| Scenario rates and outlay | data/processed/price_scenarios.csv |
| Budget sensitivity | data/processed/weight_sensitivity.csv |

All processed CSV paths are repository-relative to data/processed unless otherwise stated. Monthly sample counts vary by lag and valid coverage. No statistical forecast has been attempted.
''')
    print('Generated executive summary, analytical answers, LinkedIn draft and interview guide.')


if __name__=='__main__':main()
