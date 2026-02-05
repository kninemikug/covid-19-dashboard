import pandas as pd
from .usa_visualizations import (
    create_dual_axis_timeseries,
    create_vaccination_progress,
    create_vaccine_manufacturer_comparison,
    create_reproduction_rate_chart,
    create_comprehensive_dashboard,
    create_case_fatality_rate_chart
)

def process(df):
    """
    Process COVID-19 data for United States.

    Returns comprehensive metrics and preprocessed data including:
    - 20+ advanced metrics (CFR, vaccination rate, Rt, etc.)
    - Vaccine manufacturer breakdown
    - Trend analysis (7-day changes)
    - Population demographics
    """
    country_name = "United States"

    # ============================================================
    # 1. Data Filtering and Sorting
    # ============================================================
    country_df = df[df['location'] == country_name].copy()

    if country_df.empty:
        return None

    country_df = country_df.sort_values('date').reset_index(drop=True)

    # ============================================================
    # 2. Missing Value Handling
    # ============================================================
    # Time-series interpolation for cases and deaths
    country_df['new_cases_smoothed'] = country_df['new_cases_smoothed'].fillna(method='ffill').fillna(method='bfill')
    country_df['new_deaths_smoothed'] = country_df['new_deaths_smoothed'].fillna(method='ffill').fillna(method='bfill')
    country_df['total_cases'] = country_df['total_cases'].fillna(method='ffill').fillna(method='bfill')
    country_df['total_deaths'] = country_df['total_deaths'].fillna(method='ffill').fillna(method='bfill')

    # Cumulative data (forward fill only)
    country_df['people_fully_vaccinated'] = country_df['people_fully_vaccinated'].fillna(method='ffill')
    country_df['total_vaccinations'] = country_df['total_vaccinations'].fillna(method='ffill')
    country_df['total_boosters'] = country_df['total_boosters'].fillna(method='ffill')

    # Reproduction rate (linear interpolation)
    country_df['reproduction_rate'] = country_df['reproduction_rate'].interpolate(method='linear')

    # Policy stringency index
    country_df['stringency_index'] = country_df['stringency_index'].fillna(method='ffill')

    # ============================================================
    # 3. Derived Metrics Calculation
    # ============================================================
    latest_row = country_df.iloc[-1]

    # Case Fatality Rate (CFR)
    total_cases_val = latest_row.get('total_cases', 0)
    total_deaths_val = latest_row.get('total_deaths', 0)
    cfr = (total_deaths_val / total_cases_val * 100) if total_cases_val > 0 else 0

    # Vaccination Rate
    population_val = latest_row.get('population', 0)
    people_fully_vacc_val = latest_row.get('people_fully_vaccinated', 0)
    vacc_rate = (people_fully_vacc_val / population_val * 100) if population_val > 0 else 0

    # Peak Dates
    peak_cases_idx = country_df['new_cases_smoothed'].idxmax()
    peak_deaths_idx = country_df['new_deaths_smoothed'].idxmax()
    peak_cases_date = country_df.loc[peak_cases_idx, 'date'] if pd.notna(peak_cases_idx) else None
    peak_deaths_date = country_df.loc[peak_deaths_idx, 'date'] if pd.notna(peak_deaths_idx) else None

    # 7-Day Change
    if len(country_df) >= 14:
        recent_7d = country_df['new_cases_smoothed'].iloc[-7:].sum()
        previous_7d = country_df['new_cases_smoothed'].iloc[-14:-7].sum()
        cases_7d_change = recent_7d - previous_7d
    else:
        cases_7d_change = 0

    # Monthly Average (last month)
    try:
        country_df_indexed = country_df.set_index('date')
        monthly_avg = country_df_indexed['new_cases_smoothed'].resample('M').mean()
        monthly_avg_cases = monthly_avg.iloc[-1] if len(monthly_avg) > 0 else 0
    except:
        monthly_avg_cases = 0

    # ============================================================
    # 4. Vaccine Manufacturer Data Extraction
    # ============================================================
    vaccine_manufacturers = []

    if 'vaccine' in country_df.columns:
        vaccine_df = country_df[country_df['vaccine'].notna()].copy()

        if not vaccine_df.empty:
            for manufacturer in vaccine_df['vaccine'].unique():
                mfr_data = vaccine_df[vaccine_df['vaccine'] == manufacturer]

                if not mfr_data.empty:
                    latest_vacc = mfr_data.iloc[-1]

                    vaccine_manufacturers.append({
                        "vaccine": manufacturer,
                        "total": float(latest_vacc.get('total_vaccinations', 0)),
                        "date": str(latest_vacc['date'].date()) if pd.notna(latest_vacc.get('date')) else ""
                    })

    # ============================================================
    # 5. Metrics Dictionary Construction
    # ============================================================
    metrics = {
        # === Basic Metrics (UI Compatible) ===
        "total_cases": float(latest_row.get('total_cases', 0)),
        "total_deaths": float(latest_row.get('total_deaths', 0)),
        "people_fully_vaccinated": float(latest_row.get('people_fully_vaccinated', 0)),
        "new_cases": float(latest_row.get('new_cases', 0)),

        # === Advanced Metrics ===
        "case_fatality_rate": round(cfr, 2),
        "vaccination_rate": round(vacc_rate, 2),
        "current_reproduction_rate": float(latest_row.get('reproduction_rate', 0)) if pd.notna(latest_row.get('reproduction_rate')) else 0,
        "stringency_index": float(latest_row.get('stringency_index', 0)) if pd.notna(latest_row.get('stringency_index')) else 0,
        "peak_cases_date": str(peak_cases_date.date()) if peak_cases_date is not None else "N/A",
        "peak_deaths_date": str(peak_deaths_date.date()) if peak_deaths_date is not None else "N/A",
        "total_boosters": float(latest_row.get('total_boosters', 0)) if pd.notna(latest_row.get('total_boosters')) else 0,

        # === Vaccine Manufacturer Breakdown ===
        "vaccine_by_manufacturer": vaccine_manufacturers,

        # === Trend Analysis ===
        "new_cases_7d_change": float(cases_7d_change),
        "monthly_avg_cases": float(monthly_avg_cases),

        # === Population Demographics ===
        "population": float(latest_row.get('population', 0)),
        "median_age": float(latest_row.get('median_age', 0)) if pd.notna(latest_row.get('median_age')) else 0,
        "hospital_beds_per_thousand": float(latest_row.get('hospital_beds_per_thousand', 0)) if pd.notna(latest_row.get('hospital_beds_per_thousand')) else 0
    }

    # ============================================================
    # 6. Visualization Generation
    # ============================================================
    visualizations = {}

    try:
        visualizations['dual_axis_timeseries'] = create_dual_axis_timeseries(country_df, country_name)
        visualizations['vaccination_progress'] = create_vaccination_progress(country_df, country_name)
        visualizations['vaccine_manufacturer'] = create_vaccine_manufacturer_comparison(vaccine_manufacturers)
        visualizations['reproduction_rate'] = create_reproduction_rate_chart(country_df, country_name)
        visualizations['comprehensive_dashboard'] = create_comprehensive_dashboard(country_df, country_name)
        visualizations['case_fatality_rate'] = create_case_fatality_rate_chart(country_df, country_name)
    except Exception as e:
        print(f"Visualization generation error: {e}")
        visualizations = {}

    # ============================================================
    # 7. Return Standardized Output
    # ============================================================
    return {
        "country_name": country_name,
        "country_df": country_df,
        "metrics": metrics,
        "visualizations": visualizations
    }
