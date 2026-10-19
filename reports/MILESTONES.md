# Milestone acceptance record

The user authorized work through Milestone 8. The original milestone gate is superseded. Historical acceptance criteria remain in archive/expanded_milestone1/MILESTONES.md.

| Milestone | Result | Evidence and limits |
|---|---|---|
| 1. Discovery/feasibility | Complete | Original Kaggle audit plus official-source feasibility, source definitions, access/license review and two-product design. |
| 2. Ingestion/raw storage | Complete | 695 checksummed resources; keyless official Census Summary File route; two source formats; immutable cache, response validation, bounded retry/rate-limit handling and resumable downloads. |
| 3. Cleaning/validation | Complete | 7,488 ACS records, published MOEs and raw symbols preserved; official FIPS; 468 burden-universe reconciliations; source labels retained; missing-month/complete-basket rules enforced. |
| 4. SQL model | Complete | DuckDB facts/dimensions; national and state marts; 14 named analytical result sets; no national-price fan-out to states; independent formula and total reconciliation. |
| 5. Core analysis | Complete | Six questions answered with actual evidence; weight/relationship sensitivity, item volatility, calendar-safe rolling measures and transparent scenarios. Unsupported causal, welfare and forecast conclusions excluded. |
| 6. Dashboard | Complete with verification limit | Four-page Streamlit app plus browser-only public companion and simulator. All pages pass AppTest and browser-simulator arithmetic cases pass. Live browser visual/map QA was declined. |
| 7. Testing/deployment | Release prepared and publication tracked | 24 Python tests, six JS cases, offline build and GitHub Actions workflow. See DEPLOYMENT.md for actual remote status. Browser visual QA remains unverified; no scheduled refresh. |
| 8. Storytelling | Complete | Executive case study, two-page PDF brief, six-page LinkedIn carousel, concise post draft, executed notebook and interview walkthrough/five questions. No LinkedIn post sent. |

## Decisions made during implementation

- Preserved the current workspace rather than renaming the user's folder. Remote portfolio name is american-affordability-index.
- Replaced the initial manual geography lookup with Census's official reference after validation caught a mismatch; added explicit 52-geography/FIPS checks and source/national anchors.
- Preserved a 2020 ACS gap and October 2025 CPI gaps. The annual endpoint is 2024, not 2026.
- Used illustrative weights rather than implying unverified CE representativeness.
- Kept state housing/income independent of national-only grocery/fuel prices.
- Used Sites for the public browser-only companion, since it cannot host a Python Streamlit server. The tested Streamlit application is included for local or separate Community Cloud deployment.
- Reported modeled affordability improvement despite the original cost-squeeze framing. The findings do not generalize to all expenses, income groups or households.
