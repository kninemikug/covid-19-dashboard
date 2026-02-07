
import pandas as pd
import streamlit as st
import sys
import os

# 모듈 경로 추가
sys.path.append(os.getcwd())

from modules.data_loader import load_data

def inspect_merged():
    print("Loading data via data_loader...")
    df = load_data()
    
    print("\n[Merged Data Inspection]")
    print(f"Total shape: {df.shape}")
    
    # Check South Korea
    korea = df[df['location'].isin(['South Korea', 'Korea, South'])]
    print(f"South Korea rows: {len(korea)}")
    
    if not korea.empty:
        print(f"Unique locations: {korea['location'].unique()}")
        
        # Check vaccination columns
        vax_cols = ['people_fully_vaccinated', 'total_vaccinations']
        print(f"Data in {vax_cols}:")
        print(korea[vax_cols].describe())
        
        # Check dates where vax data exists
        vax_data = korea[korea['people_fully_vaccinated'] > 0]
        if not vax_data.empty:
            print(f"First vaccination date: {vax_data['date'].min()}")
            print(f"Last vaccination date: {vax_data['date'].max()}")
            print(f"Max value: {vax_data['people_fully_vaccinated'].max()}")
        else:
            print("No vaccination data found (all 0 or NaN).")
            
    else:
        print("South Korea not found in merged dataframe.")

if __name__ == "__main__":
    inspect_merged()
