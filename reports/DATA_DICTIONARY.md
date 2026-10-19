# Data dictionary — implemented model v1

All production outputs use the October 19, 2026 snapshot. Tables below exist and are validated. Original Kaggle source variables follow afterward. Historical proposed-field notes are archived.

## Analysis-ready files and SQL tables

| File / table | Grain / size | Main fields and meanings |
|---|---|---|
| acs_observations / fact_acs | year × geography × variable; 7,488 rows | year (survey year), geography_id (zero-padded FIPS or US), table_id, variable (Census code, e.g. B25119_003E), raw_estimate/raw_moe (source text), estimate (numeric), moe_90 (published 90% MOE), variable_label (year-specific source definition), estimate_flag/moe_flag (normalization to null), source_format, source, vintage. |
| monthly_prices / fact_price | series × reference month, national; 564 rows including 3 explicit missing values | date (month start), category, series_id, geography_id=US, unit, value (numeric or null), raw_value, footnotes, source, vintage. Food/rent/all-items are CPI indexes; gasoline is USD/US gallon. |
| item_prices / fact_item_price | BLS AP series × month; 8,869 observed rows | Original date/year/month/item/price/series_id; source_category/source_unit retained; reviewed category and normalized unit; geography_id=US, source. |
| geographies / dim_geography | One per nation/state/DC; 52 rows | geography_id, abbreviation, name, geography_type (nation/state/district). Official reference excludes territories from this scope. |
| dim_calendar | Calendar month; 144 rows | date/year/month, January 2015–December 2026. Unobserved future grid months are not economic data. |
| dim_category | Four national indicators | category, display label, unit. all_items is a deflator/sensitivity input, not a basket component. |
| model_budget | Three illustrative components | category, baseline_annual_usd. Values are assumptions from config/budget.json, not a source dataset. |
| mart_annual_price | year × category; 48 rows | observed_months, observed_mean, min/max, annual_price (only if all 12 months valid), baseline_2015, index_2015. Partial years retain coverage, never a full-year price. |
| mart_housing | geography × standard ACS year; 468 rows | household_income, renter_income, monthly_gross_rent and their published MOEs; cash_rent_units, not_computed_units, burdened_units, burden_band_count, burden_share, not_computed_share; both rent/income proxies; source geography labels. |
| mart_state_housing | 50 states × nine years; 450 rows | Housing metrics plus point-estimate renter_proxy_rank. Excludes nation/DC; DC remains available in mart_housing. Ranks do not incorporate derived uncertainty. |
| mart_components | year × modeled category; 36 rows | annual_price, observed_months, baseline_annual_usd, price_relative, modeled_annual_usd, contribution_usd. Incomplete annual prices produce nulls. |
| mart_national | Calendar year; 12 rows | modeled_annual_cost, baseline_annual_cost, renter/all-household income/index, essential_cost_index, affordability_index, restore_income, restore_cost, geography_id. 2020 affordability is null; 2025/2026 affordability is null. |
| mart_monthly_price | month × national category; 576 rows | value, previous_value, monthly_change_pct, complete rolling_3mo/rolling_12mo and supporting counts. Grid adjacency prevents missing-month jumps. |
| illustrative_item_basket | 139 source-window months | date, monthly_cost (only if all six prices available), valid_items, index_2015. Separate illustrative item basket, not the main budget. |
| item_basket_contributions | Six selected AP items | Quantity/unit, item/category, baseline/latest monthly cost, dollar_change, endpoint. First baseline is the full 2015 mean; endpoint is latest complete source month. |
| lag_correlations | Lags 0–12 | lag_months, n valid pairs, Pearson, Spearman. Positive lag means gasoline t paired with grocery t+k. |
| rolling_correlations | Reference month | pearson_36mo, requires all 36 paired changes. |
| price_scenarios | Low/Baseline/High | Historical quantile, reference_date, component growth rates, current/terminal annualized costs, terminal monthly cost and gradual-compounding next-12-month outlay. Scenarios are assumptions. |
| weight_sensitivity | Four fixed budgets | baseline/endpoint costs, cost_growth_pct and affordability_index. No probability/CI interpretation. |

All production Parquet files have CSV counterparts under data/processed/. Derived formulas and population cautions are in PROJECT_SCOPE.md and METHODOLOGY.md.

## Exact ACS selections

B19013_001E is all-household median annual money income; B25119_003E is renter median annual income. Values in each ACS year are in that year's dollars, not a constant-dollar series across years. B25064_001E is monthly median gross rent for cash-rent units, including applicable utilities. Each estimate's M field supplies its published MOE, in dollars or counts as appropriate.

B25070: 001 total cash-rent units; 002 less than 10%; 003 10–14.9%; 004 15–19.9%; 005 20–24.9%; 006 25–29.9%; 007 30–34.9%; 008 35–39.9%; 009 40–49.9%; 010 50% or more; 011 not computed. Counts in 002…011 reconcile to 001. Burden share is (007+008+009+010)/(001−011). Raw estimate and MOE text preserve source symbols/sentinels; the selected panel has zero missing estimates/MOEs after inspection.

## Exact price selections

CUUR0000SAF11: food-at-home CPI-U; CUUR0000SEHA: rent-of-primary-residence CPI-U; CUUR0000SA0: all-items CPI-U. Each is national/U.S. city average, monthly, NSA, index 1982–84=100. EMM_EPMR_PTE_NUS_DPG: EIA U.S. regular/all-formulations gasoline, nominal USD/US gallon. Series never splice dollar levels between BLS and EIA.

BLS raw JSON records: year, period (M01–M12), periodName, value (string), footnotes. The source API status and seriesID are checked; M13 is excluded. October 2025 is missing in each CPI response. EIA raw HTML data table uses Year, Jan…Dec; monthly data are reshaped without inventing absent observations. Prototype ACS headers #GEO_ID and table_001E are normalized to the later GEO_ID / table_E001 format before extraction. Sequence offsets are read per release and matched through LOGRECNO.

## Original Kaggle file dictionary

### Source version 2

## Canonical monthly file

`data/raw/kaggle/us_average_prices_monthly.csv`: 8,869 rows, 8 columns. Unique key verified: (`series_id`, `date`). All fields have zero explicit nulls. The geography is constant U.S. city average per source documentation, not a column.

| Variable | Observed type | Meaning and use |
|---|---|---|
| date | ISO date string | Reference month, stored as its first day; not a daily price or release date. |
| year | integer | Calendar year; verified against date. |
| month | integer | Calendar month 1–12; verified against date. |
| item | string | Published item description; 74 unique labels, including narrow items and overlapping aggregates. Not a retail SKU. |
| unit | string | Denominator of USD price; 15 distinct labels. Preserve exact units until a reviewed conversion map exists. |
| category | string | 12 source groupings; not verified as an official BLS taxonomy. Coffee is incorrectly classified as Beef. |
| price | decimal | Nominal USD per stated unit; positive throughout. Average retail price estimate, not a price index, expenditure, or individual transaction. |
| series_id | string | 74 BLS AP series identifiers, each mapping to one item/unit/category in this snapshot. Use as stable join key. |

## Wide file

`us_average_prices_wide.csv`: 139 rows, 75 columns. `date` has the same semantics as above and is unique; the other 74 columns are item names, each containing nominal USD per the unit in the monthly file. The exhaustive mapping of item columns to series and units is in `series_inventory.csv`. Contains 1,417 null price cells (13.776% of 10,286 possible cells). All observed prices reconcile exactly with the long file. It is another representation, not additional observations.

## Summary file

`us_average_prices_item_summary.csv`: 74 rows, 14 columns, one per unique item. Units/category have the same meanings as above. No `series_id`; join through the verified unique item mapping.

| Variable | Type | Meaning / caution |
|---|---|---|
| item, unit, category | string | Source labels; same category concern as monthly file. |
| first_date, last_date | ISO date string | Earliest/latest observed month of that item, not uniform across items. |
| first_price, last_price | decimal | Prices on those endpoint months; not seasonally adjusted. |
| n_months | integer | Number of observed records, not elapsed calendar months. |
| min_price, max_price | decimal | Observed extrema over available item history. |
| avg_first_12mo, avg_last_12mo | decimal | Match means of first/last 12 available observations to 0.001; gaps mean these can span more than 12 calendar months. |
| pct_change_12mo_avg | decimal, nullable | Source percentage change; 14 nulls (18.919%). Recompute from monthly data using explicitly defined calendar windows in later work. |
| is_current | boolean | Source flag: 60 True, 14 False. Indicates reaching snapshot endpoint in this file; does not prove official discontinuation. |

Coverage, endpoint, and extrema fields reconcile for all 74 items. No other summary fields are missing. Rounded means should not be used to reconstruct exact percentage changes.

## Audit outputs (not analytical datasets)

- `series_inventory.csv`: series metadata, first/last month, observed count, internal missing month count and dates, number of observations in calendar 2015.
- `audit_metrics.json`: schema, null counts/rates, validations, coverage, category counts, and SHA-256 raw-file fingerprints.
- `summary_checks.csv`: item-level coverage/endpoint/extrema checks and unrounded-source first/last-12-observation means rounded to three decimals.
- `suspicious_movements.csv`: original records plus parsed date, previous observed date/price, monthly percent change; only consecutive calendar months with absolute change >20%. Review flags, not errors.
