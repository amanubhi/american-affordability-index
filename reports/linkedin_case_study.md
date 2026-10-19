# LinkedIn case study — ready-to-post draft

U.S. renter median income rose 51.8% from 2015 to 2024. My illustrative budget of rent, groceries and gasoline rose 40.6%.

That produces an affordability index of 108.0, with 2015 set to 100.

I built the American Affordability Index to investigate whether income kept pace with selected essentials, using official Census, BLS and EIA data. Python handles ingestion and validation; DuckDB SQL builds the analytical model; an interactive dashboard exposes the assumptions.

Three verified findings:

• Modeled purchasing power improved 8.0% under the primary fixed budget, despite higher prices.
• Rent contributed $5,623 of the $7,554 annual modeled cost increase (74.4%).
• Gasoline and grocery monthly price changes had a Pearson correlation of -0.073 across 138 valid month pairs. Their level correlation told a different story.

The practical value is transparent budget stress testing and state housing screening. The model uses illustrative weights and aggregate renter income. It excludes taxes and major expenses, so it cannot establish that every household became better off. Standard ACS data also leave a 2020 gap.

The dashboard lets users replace assumptions and inspect a separate state housing comparison.

Which omitted expense would most change the affordability picture for the households you work with?

Dashboard: https://american-affordability-index.sunlittuna11.chatgpt.site
Code and methodology: https://github.com/amanubhi/american-affordability-index

#DataAnalytics #SQL #Python #BusinessIntelligence

---
Prepared as a draft. No LinkedIn account was accessed and no post was sent. Share the carousel PDF alongside the post after reviewing its scope disclosures.
