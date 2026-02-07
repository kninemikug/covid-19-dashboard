
import pandas as pd
import sys
import os

# 아나콘다 환경의 Pandas 사용 확인
print(f"Python Executable: {sys.executable}")

try:
    # 데이터 경로 (app.py 로그 기반)
    # Main dataset
    MAIN_DATA = "/Users/user/.cache/kagglehub/datasets/joebeachcapital/coronavirus-covid-19-cases-daily-updates/versions/747/covid_daily_full.csv"
    # Secondary (OWID)
    OWID_DATA = "/Users/user/.cache/kagglehub/datasets/georgesaavedra/covid19-dataset/versions/6/owid-covid-data.csv"
    
    print("Loading datasets...")
    df_main = pd.read_csv(MAIN_DATA)
    df_owid = pd.read_csv(OWID_DATA)
    
    # 한국 데이터 확인
    print("\n[Main Dataset] South Korea check:")
    korea_main = df_main[df_main['location'].isin(['South Korea', 'Korea, South'])]
    print(f"Rows: {len(korea_main)}")
    if not korea_main.empty:
        print(f"Sample columns: {list(korea_main.columns)[:10]}")
        
    print("\n[OWID Dataset] South Korea check:")
    korea_owid = df_owid[df_owid['location'].isin(['South Korea', 'Korea, South'])]
    print(f"Rows: {len(korea_owid)}")
    if not korea_owid.empty:
        print(f"Columns containing 'vaccin': {[c for c in korea_owid.columns if 'vaccin' in c]}")
        print(f"Nulls in people_fully_vaccinated: {korea_owid['people_fully_vaccinated'].isna().sum()} / {len(korea_owid)}")

except Exception as e:
    print(f"Error: {e}")
