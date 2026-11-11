Did your paycheck keep up with the cost of American essentials?

That question led me to build the American Affordability Index—a project combining income, rent, grocery, and gasoline data into an interactive dashboard.

I’ve now refreshed its item-price analysis with a newer Kaggle compilation of BLS retail prices:
• 74 national price series
• 8,989 usable observations through September 2026
• 120 additional observations, with every overlapping historical price checked against the original dataset

One finding from the separate annual model: rent accounts for about 74% of the modeled increase in a fixed essentials budget from 2015 to 2024.

The technical work spans Python, pandas, SQL/DuckDB, data validation, visualization, and a browser dashboard with an assumption-based budget simulator.

The update also reinforced a useful lesson: a newer upload isn’t automatically better data. I checked coverage, missing prices, stable series IDs, and historical agreement before using it.

A key distinction: the item prices reach September 2026, while the income-based affordability index ends in 2024. The budget is illustrative, and national averages don’t describe every household’s experience.

Explore the dashboard:
https://amanubhi.github.io/american-affordability-index/

Code, methodology, and validation:
https://github.com/amanubhi/american-affordability-index

Which expense has changed your budget the most: housing, groceries, or transportation?

#DataAnalytics #Python #SQL #DataVisualization
