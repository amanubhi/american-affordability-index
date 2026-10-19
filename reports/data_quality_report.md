# Milestone 1 — source audit

Retrieved October 19, 2026. No source data were cleaned, removed, interpolated, or reclassified. Objective: establish a defensible analytical scope before modeling.

## Available files

Source archive contains README.md (4,314 bytes) and these CSVs:

| File | Rows | Columns | Explicit nulls |
|---|---:|---:|---:|
| us_average_prices_item_summary.csv | 74 | 14 | 14 |
| us_average_prices_monthly.csv | 8,869 | 8 | 0 |
| us_average_prices_wide.csv | 139 | 75 | 1,417 |

See DATA_DICTIONARY.md for actual schemas and audit_metrics.json for all column types/null rates. Source CSVs total 889,430 bytes; archive and metadata are preserved in data/raw/.

## Coverage and grain

- 8,869 unique series-month observations; 74 items/series; 12 source categories; 15 unit labels.
- January 2015–July 2026: 139 calendar months. U.S. city average only, per documentation; no geographic field or retail microdata.
- 67 series start January 2015; one October 2015; one June 2016; five April 2018. 64 have all 12 months in 2015.
- 60 series reach July 2026. Four other series end April–June 2026; ten end earlier (2017–2022). Do not automatically call all 14 discontinued.
- Full grid: 10,286 potential cells; 1,417 absent (13.776%). Within each series' first/last observed month: 455 absent months across 65 series. Remaining 962 absences are outside observed endpoints.
- Three series have all 139 months. October 2025 has only three observations. The BLS egg response explicitly marks October 2025 unavailable due to the lapse in appropriations; reasons for all other gaps remain unverified.

## Validation results

- Zero duplicate full rows and zero duplicate (series_id, date) keys.
- Zero invalid dates, date/year/month mismatches, invalid numeric prices, or nonpositive prices.
- Each series has one item, unit and category label. This consistency does not establish semantic correctness.
- Zero wide/long price mismatches; matching 74-item universes.
- All 74 summary coverage/endpoints/extrema match monthly records. First/last 12-observation means match source rounded means within 0.00051. Calendar-window semantics still require correction before analysis.
- 36 consecutive-month movements exceed ±20%; retained in suspicious_movements.csv. Threshold is a review heuristic, not a statistical error test. No automatic outlier deletion or unsupported classification as genuine shocks.

## Issues requiring resolution before advanced work

1. Coffee mislabeled Beef; review every category and record proposed corrections without overwriting raw labels.
2. Multiple gallon spellings and weight/volume/package denominators require an explicit unit map. Orange juice's item label mentions a 12 oz can but its price unit is 16 oz; canned drinks similarly mention a multipack but are priced per 12 oz. Use verified price denominator, not inferred package size.
3. Internal missingness and overlapping aggregates prevent a naive fixed basket. Define completeness rules and eligible nonoverlapping items first.
4. Source narrative misstates endpoint range; source current flags cannot establish official publication status.
5. Source average-price estimates are not an official inflation index; national coverage is not geographically representative microdata.

## Provenance spot-check

BLS API series APU0000708111 (eggs), requested for 2025–2026: all 18 numeric months overlapping Kaggle matched exactly. October 2025 is unavailable in BLS and absent in Kaggle. August/September 2026 appear only in the reference response. This checks one series only; no comprehensive BLS reconciliation has been performed.

## Decisions

Use long file as canonical input. Preserve all source bytes and license metadata. All outputs here are audit evidence, not a cleaned dataset or business finding. No supplementary prices merged. Hold basket modeling, category rankings, correlations, scenarios and recommendations for later milestones.

Next: approve scope, then document the business question/method matrix, review taxonomy and unit mappings, and agree on missing-month and baseline rules before implementing the cleaning pipeline.
