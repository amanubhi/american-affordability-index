-- Named sections are executed separately and exported to reports/sql_results/.
-- query: annual_prices
SELECT year,category,observed_months,annual_price,index_2015
FROM mart_annual_price ORDER BY category,year;

-- query: yoy_changes
WITH lagged AS (
 SELECT *,lag(annual_price) OVER(PARTITION BY category ORDER BY year) AS previous_annual,
 lag(year) OVER(PARTITION BY category ORDER BY year) prior_year
 FROM mart_annual_price
)
SELECT year,category,CASE WHEN year-prior_year=1 THEN 100*(annual_price/previous_annual-1) END yoy_pct
FROM lagged ORDER BY category,year;

-- query: cumulative_changes
SELECT year,category,100*(annual_price/baseline_2015-1) cumulative_pct
FROM mart_annual_price ORDER BY category,year;

-- query: highest_lowest_periods
WITH ranked AS (
 SELECT category,date,value,unit,
 rank() OVER(PARTITION BY category ORDER BY value DESC) high_rank,
 rank() OVER(PARTITION BY category ORDER BY value) low_rank
 FROM fact_price WHERE value IS NOT NULL
)
SELECT * FROM ranked WHERE high_rank=1 OR low_rank=1 ORDER BY category,date;

-- query: item_rankings
WITH annual AS (
 SELECT series_id,item,category,unit,year(date) AS year,count(price) n,avg(price) price
 FROM fact_item_price GROUP BY ALL
), changes AS (
 SELECT c.series_id,c.item,c.category,c.unit,b.price baseline_2015,c.price endpoint_2024,
 100*(c.price/b.price-1) cumulative_pct
 FROM annual c JOIN annual b USING(series_id)
 WHERE b.year=2015 AND c.year=2024 AND b.n=12 AND c.n=12
)
SELECT *,rank() OVER(ORDER BY cumulative_pct DESC) price_change_rank FROM changes ORDER BY price_change_rank,item;

-- query: category_rankings
-- Median of item percentage changes, explicitly unweighted and selection-dependent.
WITH annual AS (
 SELECT series_id,category,year(date) AS year,count(price) n,avg(price) price
 FROM fact_item_price GROUP BY ALL
), changes AS (
 SELECT c.category,100*(c.price/b.price-1) pct
 FROM annual c JOIN annual b USING(series_id)
 WHERE b.year=2015 AND c.year=2024 AND b.n=12 AND c.n=12 AND c.category!='Energy'
)
SELECT category,count(*) eligible_items,median(pct) median_item_change_pct
FROM changes GROUP BY category ORDER BY median_item_change_pct DESC;

-- query: monthly_volatility
SELECT category,year,count(monthly_change_pct) valid_changes,stddev_samp(monthly_change_pct) change_stddev_pp
FROM mart_monthly_price WHERE monthly_change_pct IS NOT NULL GROUP BY ALL ORDER BY category,year;

-- query: rolling_prices
SELECT date,category,unit,value,rolling_3mo,rolling_12mo FROM mart_monthly_price WHERE value IS NOT NULL ORDER BY category,date;

-- query: largest_shocks
SELECT date,category,monthly_change_pct,rank() OVER(PARTITION BY category ORDER BY abs(monthly_change_pct) DESC) shock_rank
FROM mart_monthly_price WHERE monthly_change_pct IS NOT NULL QUALIFY shock_rank<=5 ORDER BY category,shock_rank;

-- query: basket_contributions
SELECT year,category,baseline_annual_usd,modeled_annual_usd,contribution_usd FROM mart_components ORDER BY year,category;

-- query: gas_grocery_relationship
SELECT count(*) valid_pairs,corr(g.monthly_change_pct,f.monthly_change_pct) pearson_changes
FROM mart_monthly_price g JOIN mart_monthly_price f USING(date)
WHERE g.category='gasoline' AND f.category='food' AND g.monthly_change_pct IS NOT NULL AND f.monthly_change_pct IS NOT NULL;

-- query: lead_changes
SELECT date,category,monthly_change_pct,lead(monthly_change_pct,1) OVER(PARTITION BY category ORDER BY date) following_calendar_month_change
FROM mart_monthly_price ORDER BY category,date;

-- query: state_housing_rankings
SELECT year,name,abbreviation,renter_rent_proxy,all_household_rent_proxy,burden_share,renter_proxy_rank,
 monthly_gross_rent,gross_rent_moe,renter_income,renter_income_moe
FROM mart_state_housing ORDER BY year,renter_proxy_rank;

-- query: item_volatility
WITH lagged AS (
 SELECT *,lag(price) OVER(PARTITION BY series_id ORDER BY date) previous_price,
 lag(date) OVER(PARTITION BY series_id ORDER BY date) previous_date
 FROM fact_item_price
), changes AS (
 SELECT *,CASE WHEN date_diff('month',previous_date,date)=1 THEN 100*(price/previous_price-1) END change_pct
 FROM lagged
)
SELECT series_id,item,category,count(change_pct) valid_changes,
 stddev_samp(change_pct) monthly_change_stddev_pp,max(abs(change_pct)) largest_abs_monthly_change_pct
FROM changes GROUP BY ALL HAVING count(change_pct)>=60 ORDER BY monthly_change_stddev_pp DESC;
