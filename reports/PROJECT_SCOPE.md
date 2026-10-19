# American Affordability Index — implemented scope v1

This design was approved for implementation through Milestone 8. The primary model, separate state housing product and illustrative fallback budget are now implemented. Historical proposed choices below are resolved in METHODOLOGY.md. This supersedes the earlier grocery/gas-only scope. Original scope and README are archived under `reports/archive/cost_of_living_m1/`; original Kaggle audit remains valid.

## Decision and population

Investigate whether median household income kept pace with a transparent modeled cost of selected essentials. Household income includes more than wages; do not call its growth wage growth or conclude Americans are financially better off overall. Taxes, transfers, wealth, debt, household composition and omitted essentials are not fully captured.

Recommend a **renter-focused first model** (rent, food at home, regular gasoline) using renter median household income where available. Show all-household median income as a separately labeled comparison. Owner affordability requires a distinct mortgage/tenure design. The project name is a portfolio brand, not an official index.

## Two products and a price extension

1. **National annual affordability:** 2015–2024 provisionally, with 2020 missing for ACS-dependent metrics. Use official food-at-home CPI and EIA gasoline; finalize rent proxy and baseline budgets after audit. Final years are the intersection of verified inputs, not assumed from the title.
2. **State annual housing comparison:** 50 states; display DC separately and exclude Puerto Rico from the default comparison. Use zero-padded Census FIPS, ACS 1-year rent and income/MOEs. Do not create state grocery or gasoline prices from national values. National figures must be retrieved at national geography, never averaged from state medians.
3. **Monthly price context through 2026:** independent latest date per source; Kaggle ends July 2026 and inspected EIA ends September 2026. Partial-year price charts are not current-year affordability estimates. A combined monthly gas/item analysis uses the actual common window and valid consecutive observations.

No Zillow/listings input is required for first release. CE weights are conditional; a fully explicit illustrative budget is an acceptable fallback, clearly labeled. No income-quintile or household-type conclusions without compatible population-specific inputs.

## Metric contract — proposed, no values calculated

For category k, baseline annual budget b_k and price relative r_kt = P_kt/P_k,2015:

- C_t = Σ b_k × r_kt, a modeled annual selected-essential cost. b_k must be nonnegative and in consistent annual USD. Baseline weights are fixed, versioned and shown to users.
- Essential Cost Index E_t = 100 × C_t/C_2015.
- Income Index J_t = 100 × I_t/I_2015, using same population definition through time.
- American Affordability Index A_t = 100 × (I_t/I_2015)/(C_t/C_2015). Above 100 means modeled purchasing power improved relative to baseline; it does not establish financial well-being.
- Dollar contribution ΔC_kt = b_k × (r_kt − 1); contributions must sum to C_t − C_2015. Their percentage shares can be negative or exceed 100% when components offset.
- State rent/income proxy = 12 × B25064_001E / B19013_001E. Preferred renter-aligned alternative uses B25119_003E. Both are ratios of medians, not the median of household-level ratios.
- Observed burden prevalence (30% or more) = Σ B25070_007E…010E / (B25070_001E − B25070_011E). Denominator excludes not-computed cases; report those exclusions and verify universe. This includes the 30% threshold, rather than claiming strictly greater than 30%.
- Restore 2015 affordability: required income I*_t = I_2015 × C_t/C_2015; required cost C*_t = C_2015 × I_t/I_2015. Show percentage adjustment relative to current I_t or C_t; preserve signed values if already above baseline.

Price indexes supply relatives, not dollars: category dollar contributions require documented baseline dollars. An item basket Σ q_i p_it is a separate drilldown model; do not combine its grocery total with food-at-home CPI spending a second time.

## Integration and methodological rules

Use annual means only when all 12 required monthly values are valid; retain count/coverage flags. Never silently interpolate. Annual ACS income is a survey-period estimate, with within-year dollar adjustment; each year's income is expressed in that year's dollars, not a common constant-dollar series. Additional real-dollar conversion needs one declared base year and deflator, applied once.

ACS median gross rent is paid gross rent including relevant utilities, while rent CPI and Zillow asking rents have different concepts. State rent levels may change with unit mix. If using gross rent in the national model, label it a rent-level proxy, not a pure fixed-quality price relative; do not add utilities already included. If using rent CPI, baseline rent spending must match its scope and omitted utility costs must be explicit. Final housing definition is a Milestone 3 acceptance requirement.

CE spending is for consumer units and means; ACS income is household medians. CE-informed weights do not make their combination an observed typical household budget. Run documented weight/tenure sensitivities; keep all-household and renter inputs distinct. Retain ACS MOEs (generally 90%) and annotations; avoid precise rank claims for statistically indistinguishable estimates. Do not fabricate combined confidence intervals without justified propagation.

## Deliverable boundaries

Streamlit is the intended public application, with Overview, State Housing, Cost Breakdown and Simulator pages. The simulator distinguishes user inputs, observed prices and scenario assumptions. Build/deployment occur in later milestones. No site, cloud account, remote repository or automation has been created in this milestone.
