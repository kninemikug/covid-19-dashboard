import streamlit as st
import pandas as pd
import importlib
import plotly.express as px

# Register available country modules here
# Key: Display Name, Value: Module Name (filename in modules/countries without .py)
COUNTRY_MODULES = {
    "South Korea": "south_korea",
    "United States": "usa"
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
        total_cases = int(world_data['total_cases'].values[0])
        total_deaths = int(world_data['total_deaths'].values[0])
        total_vaccinations = world_data['total_vaccinations'].values[0]
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
        data (dict): Dictionary containing 'country_name', 'country_df', and 'metrics'.
    """
    country_name = data.get('country_name', 'Unknown')
    country_df = data.get('country_df')
    metrics = data.get('metrics')
    
    st.markdown(f"## 🏳️ {country_name} Analysis")
    
    # 1. Metrics Row
    if metrics:
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Cases", f"{metrics['total_cases']:,.0f}")
        col2.metric("Total Deaths", f"{metrics['total_deaths']:,.0f}")
        col3.metric("Fully Vaccinated", f"{metrics['people_fully_vaccinated']:,.0f}")
        col4.metric("New Cases", f"{metrics['new_cases']:,.0f}")
    
    # 2. Daily Cases Chart
    st.write("### 📈 Daily Cases Trend")
    if not country_df.empty:
        fig = px.line(
            country_df, 
            x='date', 
            y='new_cases_smoothed', 
            title=f'Daily New Cases (Smoothed) in {country_name}',
            labels={'new_cases_smoothed': 'New Cases (7-day Avg)', 'date': 'Date'}
        )
        st.plotly_chart(fig, use_container_width=True)

    # 3. Vaccination Chart
    st.write("### 💉 Vaccination Progress")
    if not country_df.empty and 'people_fully_vaccinated' in country_df.columns:
        fig2 = px.area(
            country_df, 
            x='date', 
            y='people_fully_vaccinated', 
            title=f'Cumulative Fully Vaccinated People in {country_name}',
            labels={'people_fully_vaccinated': 'People Vaccinated', 'date': 'Date'}
        )
        st.plotly_chart(fig2, use_container_width=True)
