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
    USA COVID-19 Analysis Pipeline.
    Includes Wave Detection and Vaccination Impact Analysis (Localized).
    """
    country_name = "United States"
    
    # ==========================================================
    # 1. Custom Preprocessing Logic
    # ==========================================================
    # Filter by country
    country_df = df[df['location'] == country_name].copy()
    
    if country_df.empty:
        return None
        
    # Sort data
    country_df = country_df.sort_values('date').reset_index(drop=True)

    # ==========================================================
    # 2. Missing Values Handling
    # ==========================================================
    # 누적 데이터: 결측치는 0으로 채움 (bfill 사용 시 과거 데이터 왜곡 방지)
    for col in ['total_cases', 'total_deaths']:
        if col in country_df.columns:
             country_df[col] = country_df[col].ffill().fillna(0)
             
    # 백신 데이터: forward fill only
    for col in ['people_fully_vaccinated', 'total_vaccinations', 'total_boosters']:
        if col in country_df.columns:
            country_df[col] = country_df[col].ffill()
            
    # 일별 데이터: 결측치는 앞뒤 값으로 보간
    for col in ['new_cases_smoothed', 'new_deaths_smoothed']:
        if col in country_df.columns:
            country_df[col] = country_df[col].ffill().bfill().fillna(0)
            
    # 재생산지수 보간
    if 'reproduction_rate' in country_df.columns:
        country_df['reproduction_rate'] = country_df['reproduction_rate'].interpolate(method='linear')

    # ==========================================================
    # 3. Wave Analysis (Shared Logic)
    # ==========================================================
    waves_df = detect_waves(country_df)
    vacc_stats = analyze_vaccination_impact(country_df)

    # ==========================================================
    # 4. Advanced Metrics Calculation
    # ==========================================================
    latest_row = country_df.iloc[-1]
    
    # Calculate CFR
    total_cases = float(latest_row.get('total_cases', 0))
    total_deaths = float(latest_row.get('total_deaths', 0))
    cfr = (total_deaths / total_cases * 100) if total_cases > 0 else 0
    
    # Calculate Vaccination Rate
    population = float(latest_row.get('population', 0))
    vaccinated = float(latest_row.get('people_fully_vaccinated', 0)) if pd.notna(latest_row.get('people_fully_vaccinated')) else 0
    vacc_rate = (vaccinated / population * 100) if population > 0 else 0
    
    # Calculate Peak Dates
    peak_cases_date = country_df.loc[country_df['new_cases_smoothed'].idxmax(), 'date'] if not country_df.empty else None
    peak_deaths_date = country_df.loc[country_df['new_deaths_smoothed'].idxmax(), 'date'] if not country_df.empty else None
    
    metrics = {
        # === Basic Metrics (UI Compatible) ===
        "total_cases": total_cases,
        "total_deaths": total_deaths,
        "people_fully_vaccinated": vaccinated,
        "new_cases": float(latest_row.get('new_cases', 0)),

        # === Advanced Metrics ===
        "case_fatality_rate": round(cfr, 2),
        "vaccination_rate": round(vacc_rate, 2),
        "total_waves_detected": len(waves_df),
        "current_reproduction_rate": float(latest_row.get('reproduction_rate', 0)) if pd.notna(latest_row.get('reproduction_rate')) else 0,
        "stringency_index": float(latest_row.get('stringency_index', 0)) if pd.notna(latest_row.get('stringency_index')) else 0,
        "peak_cases_date": str(peak_cases_date.date()) if peak_cases_date is not None else "N/A",
        "peak_deaths_date": str(peak_deaths_date.date()) if peak_deaths_date is not None else "N/A",
        "total_boosters": float(latest_row.get('total_boosters', 0)) if pd.notna(latest_row.get('total_boosters')) else 0,
        "population": population,
    }

    # ============================================================
    # 5. Visualization Generation (Localized)
    # ============================================================
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
        print(f"USA visualization error: {e}")

    # ============================================================
    # 6. Return Standardized Output
    # ============================================================
    return {
        "country_name": country_name,
        "country_df": country_df,
        "metrics": metrics,
        "visualizations": visualizations
    }
