# Six-question analytical plan

Definitions are proposed until ingestion and validation pass. No findings are prefilled.

| Question / relevance | Required data | Method and metrics | Visual | Limits / decision |
|---|---|---|---|---|
| 1. Did income keep pace? / budget pressure | ACS renter/all-household income; food CPI, EIA gas, housing measure; baseline budget | Consistent-population income and modeled cost relatives, J−E growth gap plus A=100×J/E; comparable annual endpoints | Indexed annual timelines with 2020 gap | Medians are not the same households over time; selected costs and before-tax income. Supports budget/compensation context, not wage or welfare conclusions. |
| 2. Largest cost driver? / prioritize monitoring | Fixed baseline annual component budgets and price relatives | Dollar decomposition b_k(r_k−1), sum reconciliation, weight sensitivity | Waterfall with baseline budget disclosure | Contribution depends on scenario weights and matched housing concept. Supports budget planning, not observed national spending attribution. |
| 3. Housing pressure by state? / identify pressure | ACS B25064, B19013, B25119 and B25070, MOEs and annotations | Rent/income ratio alongside direct burden prevalence; explicit valid denominator | State map and uncertainty-aware dot plot | Ratio of medians differs from actual burden; statewide averages hide local variation. Supports housing-market screening. |
| 4. Did gasoline move first? / investigate timing | EIA monthly regular gas; BLS food-at-home CPI; optional item drilldown | Pearson/Spearman of levels versus consecutive changes; corr(gas change t, grocery change t+k), k=0…12 with positive k meaning gas leads; report pairs, rolling 36-month correlations; trend/season/shock sensitivities | Lag profile and change scatter | Overlapping windows, multiple comparisons, confounding and no causality. Supports monitoring hypotheses, not predictive claims without holdout validation. |
| 5. Favorable income/rent relationship? / geographic screening | Same-year ACS rent and renter income, MOEs | Rank ratio with direction disclosed and separate DC; sensitivity to all-household denominator and uncertainty | Sorted dot plot and map | Not best places to live; no complete state essential-cost index. Supports initial workforce/relocation research. |
| 6. Restore baseline affordability? / scenario planning | Baseline/current modeled costs and matched income; user adjustments | I*=I0×C/C0 and C*=C0×I/I0; compare signed required changes; validate identity at baseline | What-would-it-take simulator | User assumptions and historical aggregates separate; no reliable forecasts or confidence bands. Supports transparent budget stress tests. |

## Planned SQL value

Annual aggregations and coverage counts; LAG changes with calendar adjacency; CTEs to enforce grain/eligibility; geography and calendar joins; category contribution reconciliation; rolling price measures and ranks. National and state marts remain separate. Rank suppression/uncertainty notes belong with displayed outputs.

## Model and dashboard controls

Primary keys include source/series, geography and time as appropriate. Record source vintage, units, population, seasonality, price basis, coverage count and observation/scenario status. All dashboard KPI cards must show date, geography, population and model version. No live API keys in the front end. Avoid cartographic comparisons where a national-only series has been repeated across states.
