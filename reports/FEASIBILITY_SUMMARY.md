> Historical Milestone 1 record. Current implementation and results are documented in README.md and reports/executive_summary.md.

# Expanded Milestone 1 — feasibility result

**Recommendation:** proceed with a renter-focused national affordability model and a separate state housing comparison, with official CPI/ACS/EIA as core sources and Kaggle item prices as a drilldown. Do not promise a 2015–2026 all-state essential-cost index.

## Verified findings

- The original full Kaggle audit remains unchanged: 74 national items, 8,869 records through July 2026; category errors and internal missingness require review.
- BLS returned 120 unique, valid, positive monthly observations in 2015–2024 for each of food-at-home CPI, rent CPI and all-items CPI. These are indexes, not dollar prices.
- EIA's published national regular-gasoline monthly table has 12 valid months per year in 2015–2025 and nine months in 2026 through September. No duplicate years or nonpositive project-period prices were found.
- ACS 2015/2024 definitions exist for household income, renter income, gross rent and rent-burden bands. Actual state data quality has not been assessed: a trial data query returned a Missing Key HTML page.
- The official 2025 ACS release is scheduled for October 29, 2026; 2024 is currently the provisional common complete-year endpoint. ACS standard 1-year 2020 estimates are unavailable; the experimental replacement should not be used as a standard comparable observation.

## Unresolved dependencies

Census data access; all intervening-year/state data validation; MOEs and sentinels; precise CE baseline spending/tenure inputs or an illustrative fallback; national housing definition; annual coverage decisions; optional Zillow file/license audit if retained. No affordability changes, rankings, budget totals or recommendations have been calculated.

## Files created or changed

Source registry; revised project scope; six-question analytical plan; eight milestones with acceptance criteria; source feasibility metrics; offline probe auditor; updated README/dictionary/limitations/provenance. Raw Kaggle files remain untouched; old README/scope archived. The user-provided blueprint is preserved as PROJECT_BLUEPRINT.md.

## Validation and next step

`python src/audit_sources.py` parses saved JSON/HTML and reproduces coverage/key checks without network access. `python src/audit_data.py` remains the Kaggle audit. The runtime used pandas 2.2.3; HTML parsing dependencies are pinned in requirements.txt.

Stop after source discovery. After approval, Milestone 2 builds reproducible collectors with credentials/configuration, validates responses and stores versioned raw snapshots. The reference probes here are limited feasibility evidence, not a production pipeline.

Sources and exact links are documented in SOURCE_REGISTRY.md; original source audit is in data_quality_report.md.
