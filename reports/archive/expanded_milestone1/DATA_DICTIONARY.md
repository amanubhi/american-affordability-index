# Data dictionary — source version 2

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

## Expanded project: official source definitions

These additions separate observed reference-response schemas from proposed analytical fields. No integrated affordability table exists yet.

### BLS CPI API responses (observed)

Three saved `bls_*_2015_2024.json` files under `data/reference/feasibility/` contain `status`, `responseTime`, `message`, and `Results.series[]`. Each series object has `seriesID` and `data[]`. Data records contain `year` (string), `period` (`M01`–`M12`), `periodName` (month name), `value` (numeric string), and `footnotes` (list of code/text objects; preserve when present). API metadata and footnotes are not separate observations. Reject a failed status or unexpected series ID even if HTTP returns 200. M13, if returned in later requests, is an annual statistic and must not be counted as a month.

| seriesID | Concept | Unit / adjustment | Proposed use |
|---|---|---|---|
| CUUR0000SAF11 | CPI-U food at home | Index, 1982–84=100, NSA | National grocery price relative |
| CUUR0000SEHA | CPI-U rent of primary residence | Index, 1982–84=100, NSA | Candidate national rent price relative |
| CUUR0000SA0 | CPI-U all items | Index, 1982–84=100, NSA | General inflation sensitivity |

Rebase to 2015 only after selecting a documented annual/monthly rule. Do not add index point levels to dollar prices. Geography is U.S. city average, not a state.

### EIA published monthly table (observed)

Saved HTML contains several nested layout tables. Select the table with exactly `Year, Jan, Feb, Mar, Apr, May, Jun, Jul, Aug, Sep, Oct, Nov, Dec`; do not assume the first HTML table is data. `Year` is the calendar year; each month cell is a nominal USD/US gallon regular-all-formulations national retail gasoline average. Empty cells and source `NA`, `W`, `-`, `--` markers are not zeros; preserve their meaning before numeric conversion in production. Series: EMM_EPMR_PTE_NUS_DPG. Proposed canonical key: (series_id, geography_id, reference_month). Source XLS is preserved separately but not parsed in this feasibility audit. An EIA API JSON response would have a different schema and is not yet audited.

### ACS definitions (actual metadata inspected; values pending)

2015 and 2024 `groups/{table}.json` metadata contain `variables`, keyed by variable code, with label, concept, group and predicate type. Full year-specific definitions are preserved and summarized in `source_feasibility_metrics.json`. These are definitions, not state observations.

| Estimate code | Definition / unit | Population / caution |
|---|---|---|
| B19013_001E | Median annual household money income, survey-year USD | All households; not wages, not disposable income |
| B25119_003E | Median annual renter-household income, survey-year USD | Renter-occupied households; preferred aligned denominator |
| B25064_001E | Median monthly gross rent, USD | Renter-occupied units paying cash rent; includes applicable utility costs |
| B25070_001E | Total renter-occupied units paying cash rent | Count, includes not-computed burden cases |
| B25070_002E…006E | Rent/income bands below 30% | Counts; do not treat band edges as observed ratios |
| B25070_007E | 30.0–34.9% | Count |
| B25070_008E | 35.0–39.9% | Count |
| B25070_009E | 40.0–49.9% | Count |
| B25070_010E | 50.0% or more | Count, includes exactly 50% |
| B25070_011E | Not computed | Count; excluded from specified burden denominator and separately reported |

For each estimate `...E`, corresponding `...M` is its published margin of error, and `...EA`/`...MA` are annotations where supplied. Preserve all. Proposed `NAME`, zero-padded `state`, year and product/vintage fields identify geography/time; their actual returned data schema is pending a successful data request. National retrieval uses a national geography query, not `state:*` and not an average of medians. Sentinel codes and nulls must be audited before arithmetic; their actual incidence is unknown.

### Proposed derived outputs (not observed fields)

`modeled_annual_cost_usd`, `essential_cost_index_2015`, `income_index_2015`, `affordability_index_2015`, `rent_income_proxy`, `rent_burden_share`, category dollar contributions and restore-baseline scenario outputs follow PROJECT_SCOPE.md. Baseline budget/quantity inputs need `assumption_id`, population, unit, source or illustrative flag and model version. None are present in the original data. CE and Zillow fields are intentionally undefined until an exact table/file is selected and audited.
