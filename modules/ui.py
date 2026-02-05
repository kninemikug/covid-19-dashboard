import streamlit as st
import pandas as pd
import importlib
import plotly.express as px

# Register available country modules here
# Key: Display Name, Value: Module Name (filename in modules/countries without .py)
COUNTRY_MODULES = {
    "South Korea": "south_korea",
    "United States": "usa",
    "Japan" : "japan"
}

def render_header(df):
    """
    Render the dashboard header with global statistics.
    """
    st.header("Global Status")
    
    if df.empty:
        st.warning("No data available.")
        return

    # Get the latest date
    latest_date = df['date'].max()
    
    # Filter data for the latest date and world aggregate if available, or sum up countries
    world_data = df[(df['location'] == 'World') & (df['date'] == latest_date)]
    
    if not world_data.empty:
        total_cases_val = world_data['total_cases'].values[0]
        total_deaths_val = world_data['total_deaths'].values[0]
        total_vaccinations_val = world_data['total_vaccinations'].values[0]

        total_cases = int(total_cases_val) if pd.notna(total_cases_val) else 0
        total_deaths = int(total_deaths_val) if pd.notna(total_deaths_val) else 0
        total_vaccinations = total_vaccinations_val if pd.notna(total_vaccinations_val) else 0
    else:
        total_cases = 0
        total_deaths = 0
        total_vaccinations = 0

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Cases", f"{total_cases:,}")
    col2.metric("Total Deaths", f"{total_deaths:,}")
    col3.metric("Total Vaccinations", f"{total_vaccinations:,.0f}" if pd.notna(total_vaccinations) else "N/A")

    st.caption(f"Last Updated: {latest_date.date()}")
    
    st.markdown("---")
    
    # --- Sidebar & Navigation ---
    st.sidebar.title("Navigation")
    
    # Mode Selection
    mode = st.sidebar.radio("Go to", ["Global Overview", "Country Analysis"])
    
    if mode == "Country Analysis":
        st.sidebar.subheader("Select Country")
        selected_country = st.sidebar.selectbox("Choose a country module:", list(COUNTRY_MODULES.keys()))
        
        if selected_country:
            module_name = COUNTRY_MODULES[selected_country]
            try:
                # Dynamic Import
                module = importlib.import_module(f"modules.countries.{module_name}")
                
                # Retrieve processed data from module
                data = module.process(df)
                
                if data:
                    render_country_dashboard(data)
                else:
                    st.warning(f"No data returned for {selected_country}")
                    
            except AttributeError:
                 st.error(f"Module {module_name} does not have a 'process(df)' function.")
            except Exception as e:
                st.error(f"Failed to load module for {selected_country}: {e}")
    else:
        st.info("Select 'Country Analysis' in the sidebar to view detailed reports by country.")

def render_country_dashboard(data):
    """
    Centralized function to render visualization for any country.
    Args:
        data (dict): Dictionary containing 'country_name', 'country_df', 'metrics', and 'visualizations'.
    """
    country_name = data.get('country_name', 'Unknown')
    country_df = data.get('country_df')
    metrics = data.get('metrics')
    visualizations = data.get('visualizations', {})

    st.markdown(f"## 🏳️ {country_name} Analysis")

    # 1. Metrics Row
    if metrics:
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Cases", f"{metrics['total_cases']:,.0f}")
        col2.metric("Total Deaths", f"{metrics['total_deaths']:,.0f}")
        col3.metric("Fully Vaccinated", f"{metrics['people_fully_vaccinated']:,.0f}")
        col4.metric("New Cases", f"{metrics['new_cases']:,.0f}")

    # 2. Daily Cases Trend (with USA enhancement)
    st.write("### 📈 Daily Cases vs Deaths")
    if 'dual_axis_timeseries' in visualizations:
        st.plotly_chart(visualizations['dual_axis_timeseries'], use_container_width=True)
    elif not country_df.empty:
        # Fallback to basic chart
        fig = px.line(
            country_df,
            x='date',
            y='new_cases_smoothed',
            title=f'Daily New Cases (Smoothed) in {country_name}',
            labels={'new_cases_smoothed': 'New Cases (7-day Avg)', 'date': 'Date'}
        )
        st.plotly_chart(fig, use_container_width=True)

    # 3. Vaccination Progress (with USA enhancement)
    st.write("### 💉 Vaccination Progress")
    if 'vaccination_progress' in visualizations:
        st.plotly_chart(visualizations['vaccination_progress'], use_container_width=True)
    elif not country_df.empty and 'people_fully_vaccinated' in country_df.columns:
        # Fallback to basic chart
        fig2 = px.area(
            country_df,
            x='date',
            y='people_fully_vaccinated',
            title=f'Cumulative Fully Vaccinated People in {country_name}',
            labels={'people_fully_vaccinated': 'People Vaccinated', 'date': 'Date'}
        )
        st.plotly_chart(fig2, use_container_width=True)

    # === USA-Specific Advanced Visualizations ===
    if country_name == "United States" and visualizations:

        # 4. Reproduction Rate (Rt)
        if 'reproduction_rate' in visualizations:
            st.write("### 🦠 Reproduction Rate (Rt)")
            st.plotly_chart(visualizations['reproduction_rate'], use_container_width=True)

        # 5. Vaccine by Manufacturer
        if 'vaccine_manufacturer' in visualizations and visualizations['vaccine_manufacturer']:
            st.write("### 💊 Vaccinations by Manufacturer")
            st.plotly_chart(visualizations['vaccine_manufacturer'], use_container_width=True)

        # 6. Case Fatality Rate Trend
        if 'case_fatality_rate' in visualizations:
            st.write("### 📊 Case Fatality Rate Trend")
            st.plotly_chart(visualizations['case_fatality_rate'], use_container_width=True)

        # 7. Comprehensive Dashboard (4-Panel)
        if 'comprehensive_dashboard' in visualizations:
            st.write("### 📉 Comprehensive COVID-19 Dashboard")
            st.plotly_chart(visualizations['comprehensive_dashboard'], use_container_width=True)

    # === Japan-Specific Advanced Visualizations ===
    if country_name == "Japan" and visualizations:

        # 4. Wave Detection (파동 감지)
        if 'wave_detection' in visualizations:
            st.write("### 🌊 Wave Detection (파동 감지)")
            st.plotly_chart(visualizations['wave_detection'], use_container_width=True)

        # 5. Wave Comparison (파동별 비교)
        if 'wave_comparison' in visualizations:
            st.write("### 📊 Wave Comparison (파동별 비교)")
            st.plotly_chart(visualizations['wave_comparison'], use_container_width=True)

        # 6. Vaccination Impact (백신 전/후 비교)
        if 'vaccination_impact' in visualizations:
            st.write("### 💉 Vaccination Impact (백신 접종 전/후 비교)")
            st.plotly_chart(visualizations['vaccination_impact'], use_container_width=True)

        # 7. Cases-Deaths Decoupling (확진-사망 디커플링)
        if 'cases_deaths_decoupling' in visualizations:
            st.write("### 📉 Cases-Deaths Decoupling (확진-사망 디커플링)")
            st.plotly_chart(visualizations['cases_deaths_decoupling'], use_container_width=True)
