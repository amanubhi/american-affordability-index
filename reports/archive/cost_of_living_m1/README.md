# The American Cost-of-Living Squeeze

Selected U.S. grocery and gasoline prices, January 2015–July 2026.

**Status: Milestone 1 complete; approval required before Milestone 2.** No business analysis, basket estimates or recommendations have been produced.

## Business problem

Investigate how national average price movements would change the cost of a consistent, illustrative grocery and gasoline basket. The source contains prices, not household purchases, quantities or incomes.

## Data and audit findings

[Kaggle version 2](https://www.kaggle.com/datasets/harshitsama/us-grocery-and-gas-prices-2015-2026), compiled by Harshit Kumar from BLS Average Price Data; Kaggle labels it CC0. Original source files and metadata are preserved.

- 8,869 item-month records, 74 series, 12 source categories; national monthly estimates.
- January 2015–July 2026; 2026 is incomplete.
- No explicit blanks or duplicate series-month keys in the long file, but 1,417 missing cells on the full grid, including 455 within observed series histories.
- Coffee is mislabeled Beef. Only three series span all 139 months without gaps.
- Wide/long observed values reconcile. A direct BLS egg-series spot-check matched all 18 overlapping numeric months in 2025–2026.

These are data-audit findings, not conclusions about household cost increases.

## Documentation

- [Audit and unresolved issues](reports/data_quality_report.md)
- [Data dictionary](reports/DATA_DICTIONARY.md)
- [Limitations](reports/DATA_LIMITATIONS.md)
- [Recommended scope](reports/PROJECT_SCOPE.md)
- [Provenance and license](reports/PROVENANCE.md)
- [Per-series coverage and units](reports/series_inventory.csv)

## Planned investigation

Item price changes since 2015; reviewed item/category rankings; illustrative basket dollar contributions; gasoline/grocery change relationships; historical shocks; transparent future budget scenarios. Methodology will use pandas preparation, DuckDB SQL, fixed quantities, coverage checks and Python charts after scope approval. No forecasts or causal claims are implied.

## Reproduce Milestone 1

Python 3.11+ with pandas. From this repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python src/audit_data.py
```

The script reads preserved raw CSVs and regenerates audit JSON/CSV evidence under reports/. It does not clean data or run later analysis. Markdown reports are reviewed interpretations of those outputs. No Kaggle credentials are required for the local audit. See provenance for retrieval endpoints. Requirements pin the pandas version used during verification.

## Repository structure

`data/raw/` immutable source snapshot; `data/reference/` separate BLS check; `reports/` documentation and audit outputs; `src/audit_data.py` reproducible audit. `data/processed/`, `notebooks/`, `sql/`, `visuals/`, `tests/` are reserved for approved later milestones. Cleaning scripts, SQL, notebook, visuals, executive summary, LinkedIn post and interview materials will be added when their milestones are reached.

## Visualizations, recommendations and limitations

Visualizations and evidence-based recommendations are pending analysis. Current decision: restrict scope to selected national prices and an illustrative basket. Regional household burden, causal pass-through and actual expenditure changes are unsupported. Average-price changes can reflect sample/product mix as well as price movements; see limitations before interpretation.

Next milestone: define business methodologies and resolve taxonomy, units and missing-month rules. Work stops here pending approval.
