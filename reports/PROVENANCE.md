# Snapshot provenance and chain of custody

**Reference retrieval date: October 19, 2026.** No source bytes were edited. Dates below are observation periods, not publication timestamps.

## Original Kaggle snapshot

Source: [Harshit Kumar's dataset](https://www.kaggle.com/datasets/harshitsama/us-grocery-and-gas-prices-2015-2026), version 2, updated September 6, 2026 at 16:50:39 UTC according to preserved metadata. Kaggle displays CC0. Source archive and API metadata remain in data/raw/; extracted original README and three CSVs remain in data/raw/kaggle/. SHA-256 checks are in reports/audit_metrics.json.

The compiler describes BLS AP area 0000 and source ap.series / Food / Gasoline / HouseholdFuels files. Compiler code and its original bulk snapshot are absent. Observations end July 2026. Source inconsistencies and category errors are documented, not overwritten.

## Official sources added for production

`data/raw/2026-10-19/manifest.json` contains 695 entries with exact source URL, bytes, content type, actual UTC retrieval timestamp, kind and SHA-256. This manifest is the reproducible file-level source registry.

- Census ACS: 2015–2017 yearly sequence lookups, three relevant sequence archives per geography and geography CSVs; 2018/2019 prototype table files; 2021–2024 table files. Four table metadata files per standard survey year preserve actual variable definitions.
- Official Census state reference is included in the snapshot and config/state_reference.txt. Sequence source FIPS and geography names are validated against it.
- BLS CPI: food, rent and all-items API responses split into 2015–2024 and 2025–2026 requests. Returned footnotes are preserved. All selected series are U.S. city average / NSA.
- EIA: published monthly U.S. regular/all-formulations gasoline HTML, January 2015–September 2026. No EIA API key required for this official download route.

Existing cached files are verified, and a changed URL or hash causes failure. New resources are validated before atomic placement; the collector honors rate-limit responses and resumes cached downloads. No API keys were registered or committed.

## Separate feasibility evidence

`data/reference/` retains the BLS egg spot-check and initial probes, including the Census Missing Key HTML page and unparsed EIA XLS. Those probes are not concatenated into production observations. Production acquisition resolved Census access using official Summary Files. No Zillow/CE values were merged. Source/API errors are never treated as observations.

## Publication and reuse

See DATA_LICENSES.md for source notices and dependency licenses. Original code/documentation use MIT. No publisher endorses this analysis. The public companion packages only derived public-source results and static assets, with no user-entered simulator data, credentials or private financial records. The complete pipeline and retained public source snapshots are in the GitHub repository. No scheduled refresh or LinkedIn post was performed.
