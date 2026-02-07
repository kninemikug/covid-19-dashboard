
import pandas as pd
import numpy as np
import kagglehub
import os

# Mocking the data loading part or loading directly if possible
# To save time, I will use the code from data_loader logic roughly or just load from cache if I know the path.
# However, using the actual modules is better to reproduce exact behavior.

import sys
sys.path.append('.')
from modules.countries import europe

def load_data():
    print("Loading data...")
    # Direct path from previous logs to avoid downloading again if possible, or use standard loader
    # /Users/user/.cache/kagglehub/datasets/joebeachcapital/coronavirus-covid-19-cases-daily-updates/versions/747/covid_daily_full.csv
    
    # We need to replicate the data loading and merging 
    # But for europe.py, it mainly needs 'location', 'date', 'total_cases', 'total_deaths', 'new_cases_smoothed', 'new_deaths_smoothed', 'people_fully_vaccinated', 'total_vaccinations', 'population'
    
    # Let's try to load the main dataset only first as it contains cases/deaths
    main_df_path = "/Users/user/.cache/kagglehub/datasets/joebeachcapital/coronavirus-covid-19-cases-daily-updates/versions/747/covid_daily_full.csv"
    
    if not os.path.exists(main_df_path):
        print("Cached file not found, downloading...")
        path = kagglehub.dataset_download("joebeachcapital/coronavirus-covid-19-cases-daily-updates")
        main_df_path = f"{path}/covid_daily_full.csv"
        
    df = pd.read_csv(main_df_path)
    # Convert date
    df['date'] = pd.to_datetime(df['date'])
    return df

def debug_europe():
    df = load_data()
    print(f"Data loaded. Shape: {df.shape}")
    
    # Process using Europe module
    print("Processing with europe.py...")
    result = europe.process(df)
    
    if result is None:
        print("Europe process returned None")
        return

    europe_df = result['country_df']
    print(f"Europe DF shape: {europe_df.shape}")
    
    # Replicate the aggregation logic in comparison_visualizations.py
    print("Aggregating for CFR...")
    agg_df = europe_df.groupby('date')[['total_cases', 'total_deaths']].sum().reset_index()
    agg_df['cfr'] = (agg_df['total_deaths'] / agg_df['total_cases'] * 100).fillna(0)
    
    # Check for anomalous CFR
    high_cfr = agg_df[agg_df['cfr'] > 100]
    if not high_cfr.empty:
        print(f"Found {len(high_cfr)} days with CFR > 100%!")
        print(high_cfr.head(10))
        print("Max CFR:", agg_df['cfr'].max())
        
        # Investigate the peak date
        max_idx = agg_df['cfr'].idxmax()
        peak_date = agg_df.loc[max_idx, 'date']
        print(f"Peak CFR Date: {peak_date}")
        print("Aggregated data at peak:", agg_df.loc[max_idx])
        
        # Check individual countries on that date
        print("Individual countries on peak date:")
        peak_data = europe_df[europe_df['date'] == peak_date][['location', 'total_cases', 'total_deaths']]
        peak_data['country_cfr'] = (peak_data['total_deaths'] / peak_data['total_cases'] * 100)
        print(peak_data.sort_values('country_cfr', ascending=False))
        
    else:
        print("No CFR > 100% found in aggregated data.")
        print("Max CFR:", agg_df['cfr'].max())

if __name__ == "__main__":
    debug_europe()
