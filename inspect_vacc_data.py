
import pandas as pd
import kagglehub
import os
import sys

print(f"Python: {sys.executable}")

def check_vaccination_data():
    try:
        path = kagglehub.dataset_download("gpreda/covid-world-vaccination-progress")
        file_path = os.path.join(path, "country_vaccinations.csv")
        
        print(f"Loading {file_path}...")
        df = pd.read_csv(file_path)
        
        # Check S.Korea
        korea = df[df['country'].isin(['South Korea', 'Korea, South'])]
        print(f"South Korea rows: {len(korea)}")
        if not korea.empty:
            print(f"Country name used: {korea['country'].unique()}")
            print(korea[['date', 'people_fully_vaccinated']].tail())
            print(f"Nulls: {korea['people_fully_vaccinated'].isna().sum()} / {len(korea)}")
        else:
            print("South Korea not found in vaccination data.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_vaccination_data()
