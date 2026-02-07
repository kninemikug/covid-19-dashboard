
import pandas as pd
import kagglehub
import os
import sys

sys.path.append('.')
from modules.countries import europe

def debug_europe_deep():
    path = "/Users/user/.cache/kagglehub/datasets/joebeachcapital/coronavirus-covid-19-cases-daily-updates/versions/747/covid_daily_full.csv"
    if not os.path.exists(path):
        print("Data not found.")
        return

    df = pd.read_csv(path)
    df['date'] = pd.to_datetime(df['date'])
    
    print("Processing with europe.py...")
    result = europe.process(df)
    europe_df = result['country_df']
    
    # Check aggregation
    agg_df = europe_df.groupby('date')[['total_cases', 'total_deaths']].sum().reset_index()
    agg_df['cfr'] = (agg_df['total_deaths'] / agg_df['total_cases'] * 100).fillna(0)
    
    high_cfr = agg_df[agg_df['cfr'] > 100]
    
    if not high_cfr.empty:
        print(f"Still found {len(high_cfr)} days with CFR > 100%!")
        print(high_cfr.head())
        
        # Pick the first problematic date
        problem_date = high_cfr.iloc[0]['date']
        print(f"\nDeep dive into {problem_date}:")
        
        day_data = europe_df[europe_df['date'] == problem_date]
        
        print(f"{'Country':<15} {'Cases':<10} {'Deaths':<10} {'CFR':<10}")
        print("-" * 50)
        for _, row in day_data.iterrows():
            c = row['total_cases']
            d = row['total_deaths']
            ratio = (d/c*100) if c > 0 else 0
            if d > c:
                print(f"{row['location']:<15} {c:<10} {d:<10} {ratio:.1f}%  <-- ANOMALY")
            elif d > 0 and c == 0:
                print(f"{row['location']:<15} {c:<10} {d:<10} INF%     <-- ANOMALY")
                
    else:
        print("No aggregated CFR > 100% found.")

if __name__ == "__main__":
    debug_europe_deep()
