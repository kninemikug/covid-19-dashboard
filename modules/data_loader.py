import pandas as pd
import kagglehub
import os

# Kaggle Dataset Handles (username/dataset-slug)
DATASET_HANDLES = [
    "georgesaavedra/covid19-dataset",
    "joebeachcapital/coronavirus-covid-19-cases-daily-updates",
    "gpreda/covid-world-vaccination-progress"
]

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
        
        # --- 2. Load Secondary Dataset (OWID) ---
        # Used for supplementary info (e.g. early spread data not in main)
        owid_path = os.path.join(dataset_paths["georgesaavedra/covid19-dataset"], "owid-covid-data.csv")
        print(f"Loading secondary dataset (OWID) from {owid_path}...")
        df_owid = pd.read_csv(owid_path)
        df_owid['date'] = pd.to_datetime(df_owid['date'])
        
        # --- 3. Load Vaccination Manufacturer Data ---
        vacc_path = os.path.join(dataset_paths["gpreda/covid-world-vaccination-progress"], "country_vaccinations_by_manufacturer.csv")
        print(f"Loading vaccination data from {vacc_path}...")
        df_vacc = pd.read_csv(vacc_path)
        df_vacc['date'] = pd.to_datetime(df_vacc['date'])
        
        # --- 4. Merge Datasets ---
        print("Merging datasets...")
        
        # Merge 1: Main + OWID (Left Join)
        # Suffix '_owid' for overlapping columns to distinguish source
        merged_step1 = pd.merge(
            df_main, 
            df_owid, 
            how='left', 
            on=['location', 'date'],
            suffixes=('', '_owid')
        )
        
        # Merge 2: Result + Vaccination Manufacturer (Left Join)
        merged_df = pd.merge(
            merged_step1, 
            df_vacc, 
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

