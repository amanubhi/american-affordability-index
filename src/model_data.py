"""Build DuckDB model from validated Parquet and export readable analytical results."""
import json
import re
import duckdb
import pandas as pd
from common import ROOT,PROCESSED,REPORTS


def main():
    budget=json.loads((ROOT/'config/budget.json').read_text())
    budget_input=pd.DataFrame([{'category':k,'baseline_annual_usd':v} for k,v in budget['annual_baseline_usd'].items()])
    path=ROOT/'data/warehouse/affordability.duckdb';path.parent.mkdir(exist_ok=True)
    # All paths in SQL are repository-relative. The pipeline runs from this root.
    connection=duckdb.connect(str(path))
    connection.execute('SET threads=1')
    existing=connection.sql('SHOW TABLES').fetchall()
    for (name,) in existing:connection.execute(f'DROP TABLE "{name}"')
    connection.register('budget_input',budget_input)
    connection.execute((ROOT/'sql/model.sql').read_text())
    result_dir=REPORTS/'sql_results';result_dir.mkdir(exist_ok=True)
    query_text=(ROOT/'sql/analytical_queries.sql').read_text()
    parts=re.split(r'-- query: (\w+)\n',query_text)
    for i in range(1,len(parts),2):
        name,query=parts[i:i+2];frame=connection.execute(query).df()
        frame.to_csv(result_dir/f'{name}.csv',index=False)
    for table in ['mart_national','mart_components','mart_state_housing','mart_housing','mart_annual_price','mart_monthly_price']:
        frame=connection.sql(f'SELECT * FROM {table}').df()
        ordering=[k for k in ['year','geography_id','category','date'] if k in frame.columns]
        if ordering:frame=frame.sort_values(ordering).reset_index(drop=True)
        frame.to_parquet(PROCESSED/f'{table}.parquet',index=False)
        frame.to_csv(PROCESSED/f'{table}.csv',index=False)
    counts={n:connection.sql(f'SELECT count(*) FROM {n}').fetchone()[0] for (n,) in connection.sql('SHOW TABLES').fetchall()}
    connection.close();print(json.dumps(counts,indent=2))


if __name__=='__main__':main()
