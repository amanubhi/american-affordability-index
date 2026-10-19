# Interview walkthrough

## Two-minute first-person draft

I selected affordability because price changes become more useful when connected to an explicit budget and income measure. I began with a Kaggle grocery/gas dataset and found it contained only national average prices, uneven histories and a coffee category error. That changed the scope.

I added official ACS, CPI and EIA sources. Census API data queries required a key, so I implemented the documented public Summary File route, including two different historical formats. I preserved raw snapshots and hashes, joined sequences through source geography records, retained margins of error and validated all 50 states, DC and the nation. I kept the 2020 ACS gap visible.

I used pandas for source normalization and DuckDB for facts, dimensions and separate national/state marts. SQL uses CTEs, CASE, LAG/LEAD, calendar joins, ranks and rolling windows. A monthly calendar prevents gaps from becoming false one-month changes, and complete-period checks prevent partial basket totals.

The surprising result was that renter median income grew 51.8% while the primary illustrative selected-cost budget grew 40.6% by 2024. I reported an affordability index of 108.0 rather than forcing the original squeeze narrative. Rent still drove 74.4% of the modeled dollar increase.

The result supports budget stress testing, not broad welfare claims. I separated the state housing proxy from actual rent-burden prevalence, retained input MOEs and avoided causal gasoline claims. The dashboard lets users inspect the assumptions. With better data, I would add compatible household-type weights, taxes, healthcare and local prices, then validate whether conclusions survive those changes.

## Five realistic questions and answer notes

1. **Why can't you join national grocery prices to each state and call it a state cost-of-living index?** A join can be technically valid while creating false geographic precision. I keep state housing/income separate and label national price assumptions explicitly.
2. **How did you handle missing October 2025 values and the 2020 ACS gap?** No interpolation. Monthly changes require adjacent valid calendar months, annual means require 12 values, complete baskets require all items, and ACS-derived 2020 results remain missing.
3. **Why did you choose renter income rather than wages or all-household income?** It better aligns with a renter-focused housing model. Household income is not wages; all-household income remains a separate comparison. Changing aggregate populations remains a limitation.
4. **How do you know the affordability and contribution formulas are correct?** Baseline index must equal 100, SQL and Python independently agree, dollar contributions sum to total modeled change, national medians match national source observations, and simulator identity/invalid-input tests pass.
5. **What would make the gasoline/grocery correlation misleading?** Trends, seasonality, shocks, missing-month misalignment and multiple lag searches. Level Pearson r is 0.751, versus -0.073 for monthly changes. Sensitivity checks do not establish causality or out-of-sample prediction.

## Demonstration order

Show the national timeline and scope labels, inspect the source quality report, open a SQL query and a reconciliation test, compare the two state housing measures, then change a simulator input. Finish with limitations and improvements rather than unsupported forecasts.
