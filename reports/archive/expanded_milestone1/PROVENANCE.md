# Provenance and retrieval record

- Retrieved: October 19, 2026 (America/Los_Angeles).
- [Kaggle dataset](https://www.kaggle.com/datasets/harshitsama/us-grocery-and-gas-prices-2015-2026), owner Harshit Kumar (harshitsama), version 2, updated September 6, 2026, 16:50:39 UTC per saved API metadata.
- Dataset license displayed by Kaggle: CC0: Public Domain. Preserve attribution and compiler README; BLS does not endorse this project. No separate project code license has been selected.
- Version 2 notes: wide file corrected to share the 74-item universe of long/summary. Audit confirms this alignment.
- Download endpoint: https://www.kaggle.com/api/v1/datasets/download/harshitsama/us-grocery-and-gas-prices-2015-2026
- Metadata endpoints: `/api/v1/datasets/view/harshitsama/us-grocery-and-gas-prices-2015-2026` and `/api/v1/datasets/list/harshitsama/us-grocery-and-gas-prices-2015-2026`.
- Original zip, extracted files and API metadata preserved under data/raw/. SHA-256 hashes of extracted files are in reports/audit_metrics.json. No raw files modified.
- Compiler reports BLS ap.series, ap.data.3.Food, ap.data.2.Gasoline, ap.data.1.HouseholdFuels, area_code 0000. Original compiler code and BLS extraction vintage not supplied.
- Primary methodology consulted: https://www.bls.gov/cpi/factsheets/average-prices.htm and https://download.bls.gov/pub/time.series/ap/ap.txt .
- Reference-only spot-check: https://api.bls.gov/publicAPI/v2/timeseries/data/APU0000708111?startyear=2025&endyear=2026 . Saved separately under data/reference/bls_eggs_2025_2026.json; no reference prices merged into Kaggle data.

Raw metadata may reflect transient download/view counters; those fields are not analytical inputs. Re-downloads can change if a newer dataset version is published; use the preserved snapshot and hashes for this audit.

## Expanded source feasibility probes — October 19, 2026

- Original Kaggle snapshot and its compiler attribution/license remain unchanged.
- Limited BLS CPI responses (food at home, rent and all items, 2015–2024), EIA monthly HTML/XLS and ACS group metadata were acquired as separate reference evidence. Exact successful probe URLs, status codes and hashes are recorded in `data/reference/feasibility/retrieval_manifest.json`; offline hashes and coverage are in `reports/source_feasibility_metrics.json`.
- A separate trial 2024 ACS state data query returned an HTML Missing Key page; it is saved as `acs2024_missing_key.html`, not disguised as JSON or counted as data. A 2025 metadata probe returned HTTP 404. No ACS numeric state panel is present.
- Census release schedule HTML is preserved; its planned October 29 release has not occurred as of the retrieval date.
- EIA XLS was retrieved from `https://www.eia.gov/dnav/pet/hist_xls/EMM_EPMR_PTE_NUS_DPGm.xls`. It was not parsed because the runtime lacks xlrd; the published HTML data table was independently parsed with pandas/lxml instead.
- The trial key-page query was `https://api.census.gov/data/2024/acs/acs1?get=NAME,B19013_001E,B19013_001M,B25064_001E,B25064_001M,B25106_024E,B25106_024M&for=state:*`. B25106_024 was an exploratory candidate and is not selected; B25070 is the documented final burden candidate.
- CE/Zillow documentation was reviewed through web access; no exact CE baseline cells or Zillow numerical file were selected. A direct CE report HTML fetch failed and is logged as a failed probe; it is not evidence of numerical data availability.
- Source-specific reuse/access decisions are in SOURCE_REGISTRY.md. No production pipeline, integrated marts, scheduled refresh or public deployment was created.
