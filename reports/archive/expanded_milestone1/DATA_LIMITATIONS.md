# Data limitations

1. **Scope:** selected U.S. city average price estimates, January 2015–July 2026, monthly and not seasonally adjusted per compiler documentation. No state, city, store, brand, SKU, household, income, quantity, or expenditure observations. No regional inequality or actual household spending claims are supported.
2. **Average price is not pure inflation:** BLS cautions that sample rotation, quality and product mix can affect changes. A fixed-quantity basket built from these estimates is an illustrative priced basket, not an official cost-of-living index or observed spending. Food prices exclude sales tax; fuel/utility prices include relevant taxes per BLS methodology.
3. **Coverage:** 1,417 absent cells on the full grid; 455 internal gaps. Missing does not mean zero. Only three series are complete over the full window. Late starts and different end dates prevent naive rankings and balanced basket totals. Do not carry forward silently or sum an incomplete basket.
4. **Category integrity:** coffee is labeled Beef. Potato chips are grouped under Vegetables. Review all groupings, retain original labels, and document a project taxonomy before category results. Raw prices with different units must never be averaged into a category price.
5. **Overlaps:** broad meat aggregates overlap individual meat items; gasoline all-types overlaps grades. A basket must select mutually exclusive items and one gasoline definition. Utilities, diesel, alcohol can be excluded from the core groceries/regular-gasoline scope.
6. **Summary integrity:** source is_current is not proof of discontinuation. Actual endpoints include 2017 and 2026, contradicting the README's 2019–2022 description. First/last 12 available observations are not necessarily 12 contiguous months; 12-month means mitigate seasonality only with comparable coverage. Source README and API description also give inconsistent CPI comparison figures (about 35% vs 38.7%); neither is adopted.
7. **Provenance:** Kaggle compilation of BLS AP files; no compiler source code or original BLS bulk snapshot is included. One series was checked directly, not every value. BLS footnotes are absent from Kaggle. Do not generalize the spot-check into full verification.
8. **Freshness:** latest included reference month is July 2026 (date label July 1). It is not a full-year 2026 result. BLS eggs have August/September observations as of retrieval; they remain separate reference evidence and are not appended.
9. **Statistical inference:** trending levels can produce spurious correlations. Use consecutive monthly changes, lag sensitivity, seasonal/trend checks and shock-period comparisons later. Correlation does not establish gasoline causing grocery changes. No household weights or official sampling errors are provided.
10. **Scenarios:** quantities must be explicit illustrative assumptions unless representative consumption evidence is obtained. Scenario ranges are assumptions, not confidence intervals or validated forecasts.

## Supplementary sources only if required

- [BLS AP methodology](https://www.bls.gov/cpi/factsheets/average-prices.htm): essential interpretation and series/unit checks. Used for this audit.
- [BLS public API](https://www.bls.gov/developers/): targeted missing-month and provenance checks. One egg series response is preserved separately in `data/reference/`.
- [BLS CPI](https://www.bls.gov/cpi/): needed only for a separately sourced real-price sensitivity analysis; not yet downloaded.
- [BLS Consumer Expenditure Surveys](https://www.bls.gov/cex/): potential expenditure weights; aggregate spending does not directly supply exact quantities for these AP items. Not yet downloaded.
- [EIA gasoline data](https://www.eia.gov/petroleum/gasdiesel/): only if a distinct regional gasoline extension is approved. It cannot create regional grocery coverage.

## Expanded affordability scope — October 19 revision

The source proposals above were for the original grocery/gas project. The revised scope selects official CPI, EIA and ACS conditionally as core sources; see SOURCE_REGISTRY.md for current status.

- ACS state data values have not been retrieved or validated. Metadata availability is not proof of complete, comparable state/year data. The current data endpoint requires an API key.
- Standard ACS 1-year 2020 is absent; Census advises against direct comparisons of its experimental estimates to standard years. The annual panel must display a gap. ACS five-year estimates are overlapping survey windows, not replacements for single-year points.
- As of October 19, 2026, 2025 ACS tables are scheduled for October 29. A complete 2026 affordability panel is unavailable; 2024 is the provisional common endpoint.
- ACS income is not individual wages. Renter versus all-household populations differ. Changes in aggregate medians do not track the same households, establish causation, or describe every income group.
- Gross rent, CPI rent, and asking rents measure different concepts; their trends cannot be silently spliced. Gross rent already includes relevant utilities. Choose a consistent housing definition and avoid utility double counting.
- ACS MOEs, annotations, suppression/sentinel values and denominator exclusions must survive transformations. Ranks of close estimates may be statistically indistinguishable.
- A CE-weighted index combined with ACS median income remains a modeled ratio across different statistical populations. CE consumer-unit mean expenditure weights do not supply an observed median-household budget or a complete item quantity list.
- The branded index covers selected essentials only. Healthcare, childcare, insurance, taxes, debt, savings and other costs remain outside the initial model; before-tax income is not disposable purchasing power.
- National EIA/BLS estimates cannot establish state grocery/fuel differences. State dashboard rankings measure housing/income only.
- Zillow current file coverage and reuse terms remain unverified; no Zillow data should be treated as selected or publishable yet. Unidentified Kaggle discovery links are not verified data sources.
