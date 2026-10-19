# The American Affordability Index — executive case study

**Result:** Between 2015 and 2024, U.S. renter median household income increased **51.8%**, while the primary illustrative rent, food-at-home and gasoline budget increased **40.6%**. The resulting selected-essential affordability index is **108.0** (2015=100), a modeled improvement of 8.0%.

This result does not establish that every renter or Americans overall became better off. Aggregate medians cover changing households, the budget is illustrative, and major expenses and taxes are omitted. The analysis did not force a cost-squeeze narrative onto contrary evidence.

## Business problem and approach

The question is whether income kept pace with selected essential costs, which expense drives modeled dollar pressure, and how housing pressure differs by state. The project combines frozen Census ACS 1-year Summary Files, BLS CPI-U, EIA regular gasoline and a separate Kaggle/BLS item-price drilldown. pandas normalizes sources; DuckDB SQL enforces grains and computes marts; SciPy performs descriptive relationship checks; Plotly/Streamlit and a public static companion expose results and scenarios.

The primary 2015 budget is $12,000 rent + $4,800 groceries + $1,800 gasoline annually. Each grows by its official price relative. Utilities are omitted because the national rent component uses rent CPI; gross rent including relevant utilities is reserved for the state housing comparison. The model is not a measured average household basket or an official inflation index.

## Six analytical answers

1. **Income versus costs:** renter median income rises from $35,863 to $54,446; modeled annual costs rise from $18,600 to $26,154. Income grows 11.2 percentage points faster. Relative purchasing-power improvement is 8.0%, not that percentage-point gap.
2. **Dollar driver:** rent contributes $5,623, or 74.4%, of the $7,554 modeled annual increase. This reflects both its price relative and its large baseline weight.
3. **Housing pressure:** in 2024 the renter-aligned rent/income proxy ranges from 23.6% in North Dakota to 38.5% in Florida. Florida's directly estimated burden-band share is 62.1% among cases where burden is computable, a distinct measure with a different denominator.
4. **Gasoline and grocery timing:** same-month level Pearson correlation is 0.751 (n=140); consecutive-month change correlation is -0.073 (n=138). Descriptive period correlations change sign. Lag searches and sensitivity checks do not identify a stable causal pass-through or validated forecast.
5. **Income-to-rent screening:** North Dakota has the lowest 2024 point-estimate renter rent/income proxy among the 50 states. That ranking is a screening result, not a recommendation on where to live. Published input MOEs appear in the dashboard; close ranks may be statistically indistinguishable. DC is separate.
6. **Restore 2015 affordability:** at 2024 modeled costs, required renter median income would be $50,428, versus observed $54,446. No increase is required under this model because the ratio already exceeds its 2015 level. The signed algebraic adjustment is -7.4%; it is not a recommendation to reduce income.

## Dollar decomposition

| Component | Illustrative annual baseline | Increase by 2024 | Share of increase |
|---|---:|---:|---:|
| Food | $4,800 | $1,274 | 16.9% |
| Gasoline | $1,800 | $657 | 8.7% |
| Rent | $12,000 | $5,623 | 74.4% |

Rounding can prevent displayed dollars from adding exactly. Unrounded contributions reconcile in tests and exported data.

## Decisions supported

- **Consumers:** monitor rent when evaluating recurring commitments. It drives 74.4% of this model's increase, but households should replace the illustrative weights with their own budget. The simulator makes that sensitivity visible.
- **Grocery businesses:** monitor seasonal produce and eggs with month-aware comparisons. Among series with at least 60 valid changes, strawberries, grapes and eggs have monthly-change standard deviations of 11.67, 11.17 and 9.59 percentage points. These NSA movements combine seasonality and other changes; they do not establish inventory risk or margins for any business.
- **Business planners:** stress-test rent, grocery and fuel assumptions separately. The historical-quantile paths produce terminal monthly modeled costs of $2,405, $2,429 and $2,509, starting from September 2026 prices. They are illustrative joint scenarios, not forecast intervals or probabilities.
- **Housing researchers/policymakers:** use the direct ACS burden-band measure when assessing prevalence. A ratio of medians cannot substitute for household burden. Review local and population-specific data before policy or relocation decisions.

## Robustness, uncertainty and limitations

Alternative fixed budget weights yield affordability indexes from 106.2 to 111.1; all four tested budgets exceed 100. This is a limited assumption sensitivity, not proof for all household budgets. Correlation sensitivity outputs include detrended levels, month-demeaned changes, common-CPI-deflated levels, shock exclusions, historical periods, lags 0–12 and 36-month rolling correlations. Common deflation can itself induce association.

ACS standard 2020 is absent. There are no annual 2025/2026 affordability estimates; the latest available common year on the October 19 snapshot is 2024. October 2025 CPI gaps prevent complete annual means under the strict rule. The separate Kaggle source ends July 2026. No national prices are relabeled as state prices. The project retains actual input MOEs but does not invent uncertainty intervals for derived ratios.

## Evidence and reproduction

Sources: [Census Summary Files](https://www.census.gov/programs-surveys/acs/data/summary-file.html), [BLS CPI API](https://www.bls.gov/developers/api_signature_v2.htm), [EIA regular gasoline](https://www.eia.gov/dnav/pet/hist/LeafHandler.ashx?n=PET&s=EMM_EPMR_PTE_NUS_DPG&f=M), [Kaggle/BLS AP](https://www.kaggle.com/datasets/harshitsama/us-grocery-and-gas-prices-2015-2026).

695 official-source resources are hashed. All 7,488 ACS observations pass key, coverage and burden-universe checks. SQL exports, findings JSON, data dictionaries and code reproduce every number above. Run `python src/run_pipeline.py` and `python -m pytest -q`. See the source registry and limitations for definitions.
