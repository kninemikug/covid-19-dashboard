import kagglehub
import os
import pandas as pd

def inspect():
    # 1. OWID Dataset
    print("\n" + "="*50)
    print("DATASET 1: georgesaavedra/covid19-dataset (OWID)")
    print("="*50)
    path1 = kagglehub.dataset_download("georgesaavedra/covid19-dataset")
    file1 = os.path.join(path1, "owid-covid-data.csv")
    df1 = pd.read_csv(file1)
    print(f"File: {file1}")
    print(f"Shape: {df1.shape}")
    print("\nColumns:")
    print(df1.columns.tolist())
    print("\nHead(3):")
    print(df1.head(3))
    print("\nInfo:")
    print(df1.info())

    # 2. Daily Updates
    print("\n" + "="*50)
    print("DATASET 2: joebeachcapital/coronavirus-covid-19-cases-daily-updates")
    print("="*50)
    path2 = kagglehub.dataset_download("joebeachcapital/coronavirus-covid-19-cases-daily-updates")
    # Let's inspect 'covid_daily_full.csv' as it seems most comprehensive
    file2 = os.path.join(path2, "covid_daily_full.csv")
    df2 = pd.read_csv(file2)
    print(f"File: {file2}")
    print(f"Shape: {df2.shape}")
    print("\nColumns:")
    print(df2.columns.tolist())
    print("\nHead(3):")
    print(df2.head(3))
    print("\nInfo:")
    print(df2.info())

    # 3. Vaccination Progress
    print("\n" + "="*50)
    print("DATASET 3: gpreda/covid-world-vaccination-progress")
    print("="*50)
    path3 = kagglehub.dataset_download("gpreda/covid-world-vaccination-progress")
    # Inspect 'country_vaccinations.csv'
    file3 = os.path.join(path3, "country_vaccinations.csv")
    df3 = pd.read_csv(file3)
    print(f"File: {file3}")
    print(f"Shape: {df3.shape}")
    print("\nColumns:")
    print(df3.columns.tolist())
    print("\nHead(3):")
    print(df3.head(3))
    print("\nInfo:")
    print(df3.info())

if __name__ == "__main__":
    inspect()
