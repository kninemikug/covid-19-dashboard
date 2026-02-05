import pandas as pd
import streamlit as st

def get_country_list(df):
    """
    Get a sorted list of unique countries from the dataframe.
    Exclude 'World' and other aggregates.
    """
    if df.empty:
        return []
    
    # Filter out continental/world aggregates if 'location' is used directly
    # 'owid-covid-data' often includes 'World', 'Europe', etc.
    # It's better to filter by 'continent' being not null usually, 
    # but 'covid_daily_full' might act differently.
    # Let's trust 'location' column first.
    
    countries = df['location'].unique().tolist()
    
    # Standard cleanup for known aggregates
    aggregates = ['World', 'Africa', 'Asia', 'Europe', 'European Union', 
                  'North America', 'Oceania', 'South America', 'High income', 
                  'Upper middle income', 'Lower middle income', 'Low income']
    
    cleaned_list = [c for c in countries if c not in aggregates]
    cleaned_list.sort()
    
    return cleaned_list

@st.cache_data
def filter_data_by_country(df, country):
    """
    Filter dataframe by location (country).
    """
    if df.empty or not country:
        return pd.DataFrame()
    
    return df[df['location'] == country].copy()

def get_latest_metrics(country_df):
    """
    Get the latest key metrics (Cases, Deaths, Vaxx) for a specific country data.
    """
    if country_df.empty:
        return None
    
    # Sort by date just in case
    country_df = country_df.sort_values(by='date')
    latest_row = country_df.iloc[-1]
    
    metrics = {
        "date": latest_row['date'],
        "total_cases": latest_row.get('total_cases', 0),
        "total_deaths": latest_row.get('total_deaths', 0),
        "people_fully_vaccinated": latest_row.get('people_fully_vaccinated', 0),
        "total_vaccinations": latest_row.get('total_vaccinations', 0),
        "new_cases": latest_row.get('new_cases', 0),
        "new_deaths": latest_row.get('new_deaths', 0)
    }
    
    return metrics
