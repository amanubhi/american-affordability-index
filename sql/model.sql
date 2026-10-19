-- All facts preserve their true geography and grain. No national price/state joins.
CREATE TABLE dim_geography AS SELECT * FROM read_parquet('data/processed/geographies.parquet');
CREATE TABLE dim_calendar AS
SELECT d::DATE AS date, year(d)::INTEGER AS year, month(d)::INTEGER AS month
FROM generate_series(DATE '2015-01-01', DATE '2026-12-01', INTERVAL '1 month') t(d);
CREATE TABLE dim_category AS SELECT * FROM (VALUES
 ('rent','Rent of primary residence','index (1982–84=100)'),
 ('food','Food at home','index (1982–84=100)'),
 ('gasoline','Regular gasoline','USD/US gallon'),
 ('all_items','CPI-U all items','index (1982–84=100)')) t(category,label,unit);
CREATE TABLE fact_price AS SELECT * FROM read_parquet('data/processed/monthly_prices.parquet');
CREATE TABLE fact_acs AS SELECT * FROM read_parquet('data/processed/acs_observations.parquet');
CREATE TABLE fact_item_price AS SELECT * FROM read_parquet('data/processed/item_prices.parquet');
CREATE TABLE model_budget AS SELECT * FROM budget_input;

CREATE TABLE mart_annual_price AS
WITH grouped AS (
 SELECT year(date)::INTEGER AS year, category, count(value) observed_months,
        avg(value) observed_mean, min(value) min_value, max(value) max_value
 FROM fact_price GROUP BY ALL
), complete AS (
 SELECT *, CASE WHEN observed_months=12 THEN observed_mean END annual_price
 FROM grouped
)
SELECT a.*, b.annual_price baseline_2015,
 100*a.annual_price/b.annual_price index_2015
FROM complete a JOIN complete b ON a.category=b.category AND b.year=2015;

CREATE TABLE mart_housing AS
WITH a AS (
 SELECT year,geography_id,
 max(CASE WHEN variable='B19013_001E' THEN estimate END) household_income,
 max(CASE WHEN variable='B19013_001E' THEN moe_90 END) household_income_moe,
 max(CASE WHEN variable='B25119_003E' THEN estimate END) renter_income,
 max(CASE WHEN variable='B25119_003E' THEN moe_90 END) renter_income_moe,
 max(CASE WHEN variable='B25064_001E' THEN estimate END) monthly_gross_rent,
 max(CASE WHEN variable='B25064_001E' THEN moe_90 END) gross_rent_moe,
 max(CASE WHEN variable='B25070_001E' THEN estimate END) cash_rent_units,
 max(CASE WHEN variable='B25070_011E' THEN estimate END) not_computed_units,
 sum(CASE WHEN variable IN ('B25070_007E','B25070_008E','B25070_009E','B25070_010E') THEN estimate END) burdened_units,
 count(CASE WHEN variable IN ('B25070_007E','B25070_008E','B25070_009E','B25070_010E') THEN estimate END) burden_band_count
 FROM fact_acs GROUP BY ALL
)
SELECT a.*,g.name,g.abbreviation,g.geography_type,
 12*monthly_gross_rent/nullif(household_income,0) all_household_rent_proxy,
 12*monthly_gross_rent/nullif(renter_income,0) renter_rent_proxy,
 CASE WHEN burden_band_count=4 THEN burdened_units/nullif(cash_rent_units-not_computed_units,0) END burden_share,
 not_computed_units/nullif(cash_rent_units,0) not_computed_share
FROM a JOIN dim_geography g USING(geography_id);

CREATE TABLE mart_components AS
SELECT p.year,p.category,p.annual_price,p.observed_months,
 b.baseline_annual_usd, p.annual_price/p.baseline_2015 price_relative,
 b.baseline_annual_usd*p.annual_price/p.baseline_2015 modeled_annual_usd,
 b.baseline_annual_usd*(p.annual_price/p.baseline_2015-1) contribution_usd
FROM mart_annual_price p JOIN model_budget b USING(category);

CREATE TABLE mart_national AS
WITH cost AS (
 SELECT year, CASE WHEN count(modeled_annual_usd)=3 THEN sum(modeled_annual_usd) END modeled_annual_cost,
 sum(baseline_annual_usd) baseline_annual_cost
 FROM mart_components GROUP BY year
), base_income AS (
 SELECT renter_income,household_income FROM mart_housing WHERE geography_id='US' AND year=2015
)
SELECT c.*, h.renter_income,h.household_income,h.renter_income_moe,
 100*modeled_annual_cost/baseline_annual_cost essential_cost_index,
 100*h.renter_income/b.renter_income renter_income_index,
 100*h.household_income/b.household_income household_income_index,
 100*(h.renter_income/b.renter_income)/(modeled_annual_cost/baseline_annual_cost) affordability_index,
 b.renter_income*modeled_annual_cost/baseline_annual_cost restore_income,
 baseline_annual_cost*h.renter_income/b.renter_income restore_cost,
 'US' geography_id
FROM cost c CROSS JOIN base_income b
LEFT JOIN mart_housing h ON h.year=c.year AND h.geography_id='US';

CREATE TABLE mart_state_housing AS
WITH ranked AS (
 SELECT *,rank() OVER(PARTITION BY year ORDER BY renter_rent_proxy) renter_proxy_rank
 FROM mart_housing WHERE geography_type='state'
)
SELECT * FROM ranked;

-- Calendar grid prevents LAG/rolling windows from treating gaps as adjacent months.
CREATE TABLE mart_monthly_price AS
WITH grid AS (
 SELECT c.date,c.year,c.month,k.category,p.value,p.unit,p.source
 FROM dim_calendar c CROSS JOIN dim_category k
 LEFT JOIN fact_price p ON p.date=c.date AND p.category=k.category
), lagged AS (
 SELECT *,lag(value) OVER(PARTITION BY category ORDER BY date) previous_value,
 avg(value) OVER(PARTITION BY category ORDER BY date ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) avg3,
 count(value) OVER(PARTITION BY category ORDER BY date ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) n3,
 avg(value) OVER(PARTITION BY category ORDER BY date ROWS BETWEEN 11 PRECEDING AND CURRENT ROW) avg12,
 count(value) OVER(PARTITION BY category ORDER BY date ROWS BETWEEN 11 PRECEDING AND CURRENT ROW) n12
 FROM grid
)
SELECT *,100*(value/nullif(previous_value,0)-1) monthly_change_pct,
 CASE WHEN n3=3 THEN avg3 END rolling_3mo,
 CASE WHEN n12=12 THEN avg12 END rolling_12mo
FROM lagged;
