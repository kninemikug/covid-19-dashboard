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
    Japan COVID-19 Analysis Pipeline.
    Refactored to use shared Wave Analysis and Common Visualizations modules.
    """
    country_name = "Japan"

    # ==========================================================
    # 1. Data Filtering & Sorting
    # ==========================================================
    country_df = df[df['location'] == country_name].copy()

    if country_df.empty:
        return None

    country_df = country_df.sort_values('date').reset_index(drop=True)

    # ==========================================================
    # 2. Missing Values Handling
    # ==========================================================
    # Time-series: forward fill -> backward fill
    for col in ['new_cases_smoothed', 'new_deaths_smoothed', 'total_cases', 'total_deaths']:
        country_df[col] = country_df[col].ffill().fillna(0)

    # Cumulative: forward fill only
    for col in ['people_fully_vaccinated', 'total_vaccinations', 'total_boosters']:
        country_df[col] = country_df[col].ffill()

    # Reproduction rate: linear interpolation
    country_df['reproduction_rate'] = country_df['reproduction_rate'].interpolate(method='linear')

    # Stringency index: forward fill
    country_df['stringency_index'] = country_df['stringency_index'].ffill()

    # Positive rate: forward fill
    country_df['positive_rate'] = country_df['positive_rate'].ffill()

    # ==========================================================
    # 3. Wave Analysis (Shared Logic)
    # ==========================================================
    waves_df = detect_waves(country_df)
    vacc_stats = analyze_vaccination_impact(country_df)

    # ==========================================================
    # 4. Metrics Calculation
    # ==========================================================
    latest_row = country_df.iloc[-1]

    # CFR (Case Fatality Rate)
    total_cases_val = float(latest_row.get('total_cases', 0))
    total_deaths_val = float(latest_row.get('total_deaths', 0))
    cfr = (total_deaths_val / total_cases_val * 100) if total_cases_val > 0 else 0

    # Vaccination Rate
    population = float(latest_row.get('population', 0))
    fully_vacc = float(latest_row.get('people_fully_vaccinated', 0)) if pd.notna(latest_row.get('people_fully_vaccinated')) else 0
    vacc_rate = (fully_vacc / population * 100) if population > 0 else 0

    metrics = {
        # Basic Metrics
        "total_cases": total_cases_val,
        "total_deaths": total_deaths_val,
        "people_fully_vaccinated": fully_vacc,
        "new_cases": float(latest_row.get('new_cases', 0)),

        # Derived Metrics
        "case_fatality_rate": round(cfr, 2),
        "vaccination_rate": round(vacc_rate, 2),
        "total_waves_detected": len(waves_df),
        "population": population,
    }

    # ==========================================================
    # 5. Visualization Generation (Localized)
    # ==========================================================
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
            visualizations['wave_detection'] = create_wave_detection_chart(
                country_df, waves_df, country_name
            )
            visualizations['wave_comparison'] = create_wave_comparison_chart(
                waves_df, country_name
            )

        if vacc_stats:
            visualizations['vaccination_impact'] = create_vaccination_impact_chart(
                vacc_stats, country_name
            )
            visualizations['cases_deaths_decoupling'] = create_cases_deaths_decoupling_chart(
                country_df, vacc_stats['vacc_start_date'], country_name
            )
    except Exception as e:
        print(f"Japan visualization error: {e}")

    # ==========================================================
    # [Return Area]
    # ==========================================================
    return {
        "country_name": country_name,
        "country_df": country_df,
        "metrics": metrics,
        "visualizations": visualizations,
    }
