# Delivery milestones and acceptance criteria

Milestone 1 has been expanded to match the new blueprint. Existing Kaggle audit is retained. Work remains gated before Milestone 2.

| Milestone | Deliverable | Acceptance criteria |
|---|---|---|
| 1. Discovery and feasibility | Source registry, saved probes, revised scope and metric contracts | Separate verified values from metadata/candidates; document actual endpoints, access/license conditions, ACS 2020 gap and incompatible populations; recommend feasible national/state products. Complete as feasibility work; ACS value quality and CE baseline remain explicit dependencies. |
| 2. Ingestion and raw storage | Configured Python collectors and immutable source manifests | Census key available securely or official downloadable alternative verified; response/schema checks; pagination/time-range chunking, bounded retries; snapshot hashes/vintages; reproducible collection of all agreed years/geographies; no raw overwrites. |
| 3. Cleaning and validation | pandas/Parquet outputs with meaningful checks | Geography/series/date keys unique; Census sentinels/annotations preserved as missing, not negative money; all intermediate-year schemas checked; coverage/MOEs audited; population, housing/utility definition, baseline weights and annual completeness rules documented; stop on unresolved incompatibility. |
| 4. SQL model | DuckDB facts, dimensions and separate national/state marts | Declare grain and join cardinalities; no national-price geographic fan-out; reconcile source counts/totals; independent reproduction of baseline and derived formulas; no missing or duplicated joins silently accepted. |
| 5. Core analysis | Evidence addressing six questions | Reproduce metrics in SQL/Python; retain unanswered gaps; quantify sensitivity, uncertainty and valid sample counts; contributions reconcile; causal/forecast claims absent unless separately justified. |
| 6. Streamlit dashboard | Four-page working application | Every metric labeled by dates/geography/population; clear model assumptions and missingness; simulator inputs separate from observations; valid ranges, baseline identity and scenario calculations checked; accessible charts and methodology links. |
| 7. Testing and deployment | Reproducible repository, CI and public dashboard | Clean-environment build; meaningful data/model/simulator tests; secrets excluded; source/asset reuse cleared; deployment target agreed and public content reviewed; scheduled ingestion only if authorized, never fabricated fresh data. |
| 8. Storytelling | Executive case study, GitHub narrative, LinkedIn carousel, interview guide | All claims trace to verified outputs and source vintages; describe limitations and decision value; distinguish evidence from implications; public posting requires explicit authorization. |

A four-to-six-week schedule is a planning estimate. ACS access, source compatibility and baseline-budget choices can change effort. No background automation has been scheduled.
