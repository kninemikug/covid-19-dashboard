import pandas as pd
from modules.wave_analysis import detect_waves, analyze_vaccination_impact
from modules.common_visualizations import (
    create_dual_axis_timeseries,
    create_vaccination_progress,
    create_reproduction_rate_chart,
    create_case_fatality_rate_chart,
    create_wave_detection_chart,
    create_wave_comparison_chart,
    create_vaccination_impact_chart,
    create_cases_deaths_decoupling_chart
)

def process(df):
    """
    South Korea COVID-19 Analysis Pipeline.
    """
    country_name = "South Korea"
    
    # --- 1. Custom Preprocessing Logic ---
    # Filter by country
    country_df = df[df['location'] == country_name].copy()
    
    if country_df.empty:
        return None
        
    # Sort data
    country_df = country_df.sort_values('date').reset_index(drop=True)

    # --- 1-1. Handle Missing Values ---
    # 누적 데이터: 결측치는 이전 값으로 채움 (ffill), 시작점은 0
    for col in ['total_cases', 'total_deaths', 'people_fully_vaccinated']:
        if col in country_df.columns:
            country_df[col] = country_df[col].ffill().fillna(0)
            
    # 일별 데이터: 결측치는 앞뒤 값으로 보간
    for col in ['new_cases_smoothed', 'new_deaths_smoothed']:
        if col in country_df.columns:
            country_df[col] = country_df[col].ffill().bfill().fillna(0)
            
    # 재생산지수 보간
    if 'reproduction_rate' in country_df.columns:
        country_df['reproduction_rate'] = country_df['reproduction_rate'].interpolate(method='linear')
    
    # --- 2. Wave Analysis (Shared Logic) ---
    waves_df = detect_waves(country_df)
    vacc_stats = analyze_vaccination_impact(country_df)
    
    # Calculate Custom Metrics
    latest_row = country_df.iloc[-1]
    
    total_cases = latest_row.get('total_cases', 0)
    total_deaths = latest_row.get('total_deaths', 0)
    
    # Population handling with fallback
    pop_val = latest_row.get('population')
    if pd.isna(pop_val) or pop_val == 0:
        population = 51780579.0  # Fallback: South Korea Population (~2020)
    else:
        population = pop_val
        
    vaccinated = latest_row.get('people_fully_vaccinated', 0)
    
    metrics = {
        "total_cases": total_cases,
        "total_deaths": total_deaths,
        "people_fully_vaccinated": vaccinated,
        "new_cases": latest_row.get('new_cases', 0),
        "case_fatality_rate": round((total_deaths / total_cases * 100), 2) if total_cases > 0 else 0,
        "vaccination_rate": round((vaccinated / population * 100), 2) if population > 0 else 0,
        "population": population,
        "total_waves_detected": len(waves_df)
    }
    
    # --- 3. Generate Visualizations (Localized) ---
    visualizations = {}
    
    try:
        # Standard Charts
        visualizations['dual_axis_timeseries'] = create_dual_axis_timeseries(country_df, country_name)
        visualizations['vaccination_progress'] = create_vaccination_progress(country_df, country_name)
        
        if 'reproduction_rate' in country_df.columns:
            visualizations['reproduction_rate'] = create_reproduction_rate_chart(country_df, country_name)
        
        visualizations['case_fatality_rate'] = create_case_fatality_rate_chart(country_df, country_name)
        
        # Wave Analysis Charts
        if not waves_df.empty:
            visualizations['wave_detection'] = create_wave_detection_chart(country_df, waves_df, country_name)
            visualizations['wave_comparison'] = create_wave_comparison_chart(waves_df, country_name)
            
        if vacc_stats:
            visualizations['vaccination_impact'] = create_vaccination_impact_chart(vacc_stats, country_name)
            visualizations['cases_deaths_decoupling'] = create_cases_deaths_decoupling_chart(
                country_df, vacc_stats['vacc_start_date'], country_name
            )
            
    except Exception as e:
        print(f"South Korea visualization error: {e}")
    
    # --- 4. Return Standardized Output ---
    return {
        "country_name": country_name,
        "country_df": country_df,
        "metrics": metrics,
        "visualizations": visualizations
    }
