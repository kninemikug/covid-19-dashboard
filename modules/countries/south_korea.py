import pandas as pd

def process(df):
    """
    Process data for South Korea.
    Team members can customize preprocessing logic here freely.
    """
    country_name = "South Korea"
    
    # --- 1. Custom Preprocessing Logic (Free to customize) ---
    # Filter by country
    country_df = df[df['location'] == country_name].copy()
    
    if country_df.empty:
        return None
        
    # Sort data
    country_df = country_df.sort_values('date')
    
    # Calculate Custom Metrics
    latest_row = country_df.iloc[-1]
    
    metrics = {
        "total_cases": latest_row.get('total_cases', 0),
        "total_deaths": latest_row.get('total_deaths', 0),
        "people_fully_vaccinated": latest_row.get('people_fully_vaccinated', 0),
        "new_cases": latest_row.get('new_cases', 0)
    }
    
    # --- 2. Return Standardized Output ---
    return {
        "country_name": country_name,
        "country_df": country_df,
        "metrics": metrics
    }
