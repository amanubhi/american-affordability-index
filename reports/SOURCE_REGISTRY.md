# Production source registry

Frozen snapshot: **October 19, 2026**. Feasibility notes are preserved in archive/expanded_milestone1/. They are superseded by the completed ingestion and validation described here.

| Selected source | Exact inputs | Verified scope | Access and reuse |
|---|---|---|---|
| Census ACS 1-year | B19013, B25064, B25070, B25119 | 2015–2019 and 2021–2024; 50 states, DC and nation; 7,488 estimate/MOE records | Official public Summary Files, no API key. Public federal statistics with attribution. |
| Census geography | geo/docs/reference/state.txt and source sequence geography records | 50 states + DC reference; territories excluded from model | Official reference bytes preserved; matches checked. |
| BLS CPI-U NSA | CUUR0000SAF11 food at home; CUUR0000SEHA rent; CUUR0000SA0 all items | Monthly January 2015–September 2026; 141 calendar records per series, with October 2025 missing in each | Public API, 10-year request chunks. Public-domain information, credit BLS. |
| EIA regular gasoline | EMM_EPMR_PTE_NUS_DPG, regular/all formulations | 141 complete monthly U.S. values, January 2015–September 2026 | Published monthly HTML table. Public federal statistics, credit EIA and preserve notices. |
| Kaggle/BLS average prices | harshitsama/us-grocery-and-gas-prices-2015-2026, version 2 | 8,869 observations, 74 national items, January 2015–July 2026 | Original zip/CSVs/metadata retained unchanged. Kaggle labels compilation CC0. |

**Not selected:** CE weights, Zillow asking rents and unidentified Kaggle search results. The primary budget is explicitly illustrative. No unverified supplementary prices or assumed quantities enter the national model. The separate six-item basket uses documented illustrative quantities.

## Source locations and references

- [ACS Summary File guide](https://www.census.gov/programs-surveys/acs/data/summary-file.html). 2015–2017 use sequence files with each year's lookup offsets and geography LOGRECNO. 2018/2019 use the official prototype table format; 2021–2024 use table-based files. Actual headers differ and are normalized explicitly.
- [Census state reference](https://www2.census.gov/geo/docs/reference/state.txt).
- [BLS API specification](https://www.bls.gov/developers/api_signature_v2.htm).
- [EIA monthly series](https://www.eia.gov/dnav/pet/hist/LeafHandler.ashx?n=PET&s=EMM_EPMR_PTE_NUS_DPG&f=M).
- [Kaggle compilation](https://www.kaggle.com/datasets/harshitsama/us-grocery-and-gas-prices-2015-2026).
- [2025 ACS release schedule](https://www.census.gov/programs-surveys/acs/news/data-releases/2025/release-schedule.html): scheduled October 29, 2026, after this snapshot.
- [2020 experimental ACS FAQ](https://www.census.gov/programs-surveys/acs/data/experimental-data/faq.html): do not substitute experimental values into standard-year comparisons.

## Evidence and refresh rules

`data/raw/2026-10-19/manifest.json` records 695 resources, URLs, retrieval timestamps, byte sizes, content types and SHA-256 hashes. Original Kaggle manifest information remains in `data/raw/dataset_metadata.json` and `reports/audit_metrics.json`. Source snapshots total 66,692,256 bytes excluding the separate original Kaggle archive and feasibility probes.

The data API's key requirement is resolved by the documented public-download route, not by treating the HTML error page as data. No credentials are needed for reproduction from frozen files. Collecting a new vintage uses `ingest_data.py --snapshot YYYY-MM-DD`, followed by an explicitly reviewed update to SNAPSHOT in common.py and a complete rebuild/validation. Existing files are never overwritten silently; changed URLs or hashes fail.

No automatic refresh is scheduled. Source definitions, source vintage and current data availability must be reviewed before extending 2025/2026 affordability results. See DATA_LICENSES.md for reuse notices.
