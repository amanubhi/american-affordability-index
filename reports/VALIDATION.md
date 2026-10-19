# Validation record — release v1

## Data and models

- 695 official-source resources in the production snapshot are verified against SHA-256, URL and source metadata; original Kaggle fingerprints are preserved separately.
- 7,488 ACS estimate/MOE records cover 52 geographies × nine standard survey years × 16 variables. No missing selected estimates or MOEs, duplicate keys or missing state/national rows.
- 468 Census burden universes reconcile exactly: all burden bands plus not-computed equal source totals.
- Published 2024 national income anchors ($81,604 all households; $54,446 renters) match the processed observations. National income uses the national record, not state averages.
- 564 national price records include three explicit October 2025 CPI gaps. No nonpositive numerical prices/indexes or duplicate series-month keys. 2015–2024 annual price groups each have all 12 valid months.
- Primary baseline index equals 100. SQL and Python affordability arithmetic agree; unrounded category contributions reconcile to total modeled change.
- Calendar gaps invalidate monthly changes/rolling measures. Missing items invalidate basket totals; no partial-cost sum is treated as a complete basket.
- Revised category labels retain original categories and units. Item basket source units match configuration before calculation.

## Executed checks

- `python src/run_pipeline.py --with-story`: regenerates processed data, database, named SQL results, analysis, charts, public companion and storytelling from frozen files.
- `python -m pytest -q`: **24 tests pass**, including all four Streamlit pages and a changed simulator input, invalid inputs, source sentinel handling, baseline/restore algebra, geography coverage and missingness rules.
- `node web/test_simulator.cjs`: **six arithmetic/validation cases pass** for the browser companion without browser/network access.
- The exploratory notebook executes all code cells successfully and retains outputs.
- Seven chart PNG/SVG/HTML sets were generated. Static chart inspection identified and corrected clipped category labels, unsorted annual points and an edge annotation.
- Executive brief: two pages. LinkedIn carousel: six pages. Both PDFs were rendered to PNG for inspection; overlapping content was corrected before release. PDF text/page-count checks pass.

## Verification boundary

The browser approval gate declined localhost preview access. No alternate browser surface or headless workaround was used. Streamlit AppTest verifies application rendering/state changes, not real-browser visual behavior. Responsive layout, interactive map display and downloadable-file UI behavior have not been visually verified in a live browser. This limitation is retained in the README and limitations document.

Sites native deployment status and GitHub Actions status are recorded in DEPLOYMENT.md after publication. A successful deployment is not a claim that browser visual QA occurred. The public Site is a browser-only companion exported from the same results; the Streamlit app remains separately runnable.
