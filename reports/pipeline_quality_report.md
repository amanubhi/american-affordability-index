# Production data-quality report

Snapshot: October 19, 2026. Raw sources were preserved unchanged. This expands the original Kaggle-only audit in data_quality_report.md.

| Source/table | Rows | Coverage | Null/duplicate outcome |
|---|---:|---|---|
| ACS facts | 7,488 | 52 geographies × nine standard years × 16 variables | 0 missing selected estimates/MOEs; 0 duplicate keys |
| National price facts | 564 | Four series, January 2015–September 2026 | Three October 2025 CPI nulls; 0 duplicate keys/nonpositive numerical prices |
| Original item observations | 8,869 | 74 series, January 2015–July 2026 | No blank cells/duplicates; 1,417 absent full-grid cells, 455 internal missing months |

## Transformations and decisions

- Both ACS formats use year-specific definitions. Older sequences join source geography LOGRECNO and verified FIPS. Newer tables normalize explicit header variants. All source estimate/MOE strings and labels remain available.
- Standard 2020 ACS remains absent. All nine included years have nation, 50 states and DC. The selected ACS panel has no sentinel-derived nulls, though the parser handles them explicitly.
- All 468 burden universes reconcile. Actual burden prevalence excludes not-computed cases; their share is displayed.
- Dates normalize to reference-month starts. Dates, year/month convenience fields and numeric source prices are validated. No outliers are deleted.
- October 2025 CPI values remain null. Annual means require 12 valid months. Calendar-safe monthly changes and rolling windows do not skip over missing months.
- Coffee is mapped from Beef to Drinks; potato chips from Vegetables to Pantry and snacks. 261 records receive category corrections, with original labels retained. No other speculative taxonomy changes are applied.
- Unit normalization retains source units. Basket configuration is checked against the actual price denominator before costs are computed. Mixed dollar units are never averaged across items.
- The six-item basket is complete for 138 of 139 source-window months; an incomplete month has no total. It is separate from the main CPI-based category model.
- Thirty-six original item movements above an absolute 20% month-to-month threshold remain review flags, not automatically identified errors. Item volatility uses valid consecutive changes and discloses seasonal influence.

## Evidence

695 immutable official-source resources are hash-checked. Named SQL results, pipeline_quality.json, validation_results.json, original audit_metrics.json, series_inventory.csv, suspicious_movements.csv and meaningful data/model tests support these findings. See VALIDATION.md for application/PDF checks and the live-browser verification limitation.
