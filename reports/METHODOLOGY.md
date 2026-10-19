# Methodology and model decisions

## Grain and population

National prices: series × month. ACS: geography × survey year × variable. National affordability joins only national annual facts. State housing joins same-state/same-year rent and income. Nationwide medians come from the nation record, never the mean of state medians. All selected ACS variables are inspected in every included release; their raw labels and MOEs survive normalization.

## Model equations

For selected category k and fixed illustrative 2015 annual budget b_k:

`r_kt = annual_price_kt / annual_price_k,2015`

`C_t = sum(b_k * r_kt)`

`E_t = 100 * C_t / C_2015`

`J_t = 100 * renter_income_t / renter_income_2015`

`A_t = 100 * (J_t / E_t)`

`category dollar increase = b_k * (r_kt - 1)`

The baseline is 100. Dollar contributions reconcile exactly before rounding. Annual means require 12 valid monthly observations, with all modeled components present. Raw category price/index levels are never averaged across units. All-items CPI is excluded from the modeled basket and used only for an optional common-deflator sensitivity. Deflating both income and costs by the same index cancels in their ratio.

## Baseline assumptions

Primary: rent $12,000, food $4,800, gasoline $1,800/year. These are illustrative choices. Sensitivity uses equal, higher-rent and higher-food/fuel weights, holding the baseline total $18,600 fixed. Rent uses rent-of-primary-residence CPI and excludes utilities. Food uses food-at-home CPI. Gasoline uses EIA regular/all formulations. A fixed gasoline budget combined with the 2015 price implies a fixed annual gallons amount; the CPI components model a fixed category structure rather than a directly observed item purchase list.

The separate item model uses six nonoverlapping AP selections and explicit monthly quantities in config/budget.json. A missing item invalidates that month's total. No utility, diesel, broad gasoline aggregate or overlapping broad meat series enters that basket.

## Housing measures

`rent/renter-income proxy = 12 * median monthly gross rent / renter median annual income`

The all-household variant uses B19013. Both are ratios of aggregate medians, not median household-level burdens. Actual burden prevalence is `(B25070_007 + 008 + 009 + 010) / (001 - 011)`. Bands at 30% or more are included, not strictly greater than 30%. The not-computed fraction is separately reported. All bands reconcile to the source total for every geography/year. DC is displayed separately from 50-state point-estimate ranks.

Published 90% input MOEs are retained. Derived ratio/rank/burden-share CIs are not estimated without a justified covariance/propagation method. Rankings are descriptive screening, not best-place-to-live recommendations.

## Monthly and relationship methods

A complete calendar grid prevents LAG from treating distant observations as adjacent months. Percentage change uses consecutive valid months only. Rolling prices require 3/12 valid observations; rolling correlations require 36 paired changes. Lag k correlates gasoline change at t with food change at t+k, for k=0…12. Every lag carries its valid sample count.

Pearson/Spearman are descriptive. Sensitivities include a linear trend removed from levels, mean calendar-month change removed, common-CPI deflation, excluding 2020–2023, and separate historical periods. They do not control for every confounder, serial dependence, revised data or multiple lag searches. No causality or trained predictive model is claimed.

## Scenario methods

Low/Baseline/High take the 25th/50th/75th percentiles of complete annual component price growth in 2016–2024. Each category's quantile is applied jointly. Reference costs are the primary budget repriced at September 2026 monthly price levels relative to calendar-2015 averages.

Terminal annualized cost is `sum(reference_component_annualized * (1 + category_growth))`. Terminal monthly cost divides by 12. Next-12-month outlay assumes gradual compounding and sums month m=1…12 of `reference_component_annualized / 12 * (1+growth)^(m/12)`. These outputs have different meanings and are labeled separately. Income in the user simulator is a user input, not a contemporaneous 2026 observation.

Restore-baseline arithmetic uses `required_income = I_2015 * C_t/C_2015`, or `required_cost = C_2015 * I_t/I_2015`. If affordability already exceeds 100, no income increase is required. Negative required changes are algebraic margins, not recommendations to reduce income.

## Reproducibility and tests

Frozen raw snapshots, source hashes, pandas cleaning, SQL model and named query exports, independent formula checks, app/simulator tests, rendered charts/PDFs and an executed notebook support the result. CI rebuilds from retained public snapshots without secrets. Refresh is explicit, never a hidden live dashboard query. See VALIDATION.md for the current run and the browser-visual-QA limit.
