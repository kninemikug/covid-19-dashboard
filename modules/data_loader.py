import pandas as pd
import kagglehub
import streamlit as st
import os

# Kaggle Dataset Handles (username/dataset-slug)
DATASET_HANDLES = [
    "georgesaavedra/covid19-dataset",
    "joebeachcapital/coronavirus-covid-19-cases-daily-updates",
    "gpreda/covid-world-vaccination-progress"
]


@st.cache_data(ttl=3600)  # 1시간 캐시
def download_datasets():
    """
    Download datasets from Kaggle using kagglehub.
    Returns:
        dict: A dictionary mapping dataset handle to its local path.
    """
    dataset_paths = {}
    print("Downloading datasets with kagglehub...")
    
    for handle in DATASET_HANDLES:
        try:
            # kagglehub downloads to a cache directory by default and returns the path
            path = kagglehub.dataset_download(handle)
            print(f"Downloaded {handle} to: {path}")
            dataset_paths[handle] = path
        except Exception as e:
            print(f"Error downloading {handle}: {e}")
            
    return dataset_paths


@st.cache_data(ttl=3600)  # 1시간 캐시
def load_data():
    """
    Load, merge, and preprocess data from downloaded datasets.
    Returns:
        pd.DataFrame: Merged and preprocessed data.
    """
    # 1. Download Data and get paths
    dataset_paths = download_datasets()
    
    merged_df = pd.DataFrame()

    try:
        # --- 1. Load Main Dataset (Daily Updates) ---
        daily_path = os.path.join(dataset_paths["joebeachcapital/coronavirus-covid-19-cases-daily-updates"], "covid_daily_full.csv")
        print(f"Loading main dataset from {daily_path}...")
        df_main = pd.read_csv(daily_path)
        df_main['date'] = pd.to_datetime(df_main['date'])
        
        # --- Standardize Country Names for Consistency ---
        # Main dataset (JHU style) uses 'Korea, South', 'US'
        # Secondary dataset (OWID) uses 'South Korea', 'United States'
        name_mapping = {
            'Korea, South': 'South Korea',
            'US': 'United States'
        }
        df_main['location'] = df_main['location'].replace(name_mapping)
        
        # --- 2. Load Secondary Dataset (OWID) ---
        # Used for supplementary info (e.g. early spread data not in main)
        owid_path = os.path.join(dataset_paths["georgesaavedra/covid19-dataset"], "owid-covid-data.csv")
        print(f"Loading secondary dataset (OWID) from {owid_path}...")
        df_owid = pd.read_csv(owid_path)
        df_owid['date'] = pd.to_datetime(df_owid['date'])
        
        # --- 3. Load Vaccination Data (General + Manufacturer) ---
        # 3-1. General Vaccination Progress (More complete than OWID for some countries)
        vacc_prog_path = os.path.join(dataset_paths["gpreda/covid-world-vaccination-progress"], "country_vaccinations.csv")
        print(f"Loading vaccination progress data from {vacc_prog_path}...")
        df_vacc_prog = pd.read_csv(vacc_prog_path)
        df_vacc_prog['date'] = pd.to_datetime(df_vacc_prog['date'])
        df_vacc_prog.rename(columns={'country': 'location'}, inplace=True) # Rename for merge

        # 3-2. Manufacturer Data
        vacc_mfg_path = os.path.join(dataset_paths["gpreda/covid-world-vaccination-progress"], "country_vaccinations_by_manufacturer.csv")
        print(f"Loading vaccination manufacturer data from {vacc_mfg_path}...")
        df_vacc_mfg = pd.read_csv(vacc_mfg_path)
        df_vacc_mfg['date'] = pd.to_datetime(df_vacc_mfg['date'])
        
        # --- 4. Merge Datasets ---
        print("Merging datasets...")
        
        # Merge 1: Main + OWID (Left Join)
        merged_step1 = pd.merge(
            df_main, 
            df_owid, 
            how='left', 
            on=['location', 'date'],
            suffixes=('', '_owid')
        )
        
        # Merge 2: Result + Vaccination Progress (Left Join)
        # Use this to fill missing values from OWID
        merged_step2 = pd.merge(
            merged_step1,
            df_vacc_prog[['location', 'date', 'people_fully_vaccinated', 'total_vaccinations']],
            how='left',
            on=['location', 'date'],
            suffixes=('', '_vax_prog')
        )
        
        # Fill missing values: Main/OWID -> Vaccination Progress
        for col in ['people_fully_vaccinated', 'total_vaccinations']:
            vax_col = f"{col}_vax_prog"
            if vax_col in merged_step2.columns:
                merged_step2[col] = merged_step2[col].fillna(merged_step2[vax_col])
                merged_step2.drop(columns=[vax_col], inplace=True)

        # Merge 3: Result + Vaccination Manufacturer (Left Join)
        merged_df = pd.merge(
            merged_step2, 
            df_vacc_mfg, 
            how='left', 
            on=['location', 'date'],
            suffixes=('', '_vacc_manufacturer')
        )
        
        # Handle duplicate ISO codes if necessary (Optional cleanup)
        if 'iso_code_owid' in merged_df.columns:
            merged_df.drop(columns=['iso_code_owid'], inplace=True)

        print(f"Data joined successfully. Shape: {merged_df.shape}")
        return merged_df

    except Exception as e:
        print(f"Error processing data: {e}")
        # Return whatever we managed to load, or empty if critical failure
        if not merged_df.empty:
            return merged_df
        return pd.DataFrame()

if __name__ == "__main__":
    data = load_data()
    print(data.head())
    print(data.info())
    print(data.columns.tolist())

