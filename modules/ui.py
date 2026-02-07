import streamlit as st
import pandas as pd
import importlib
import plotly.express as px
from modules.comparison_visualizations import (
    create_dual_axis_comparison,
    create_deaths_comparison,
    create_vaccination_comparison,
    create_vaccination_timeline,
    create_reproduction_rate_comparison,
    create_cfr_comparison,
    create_cfr_timeline,
    create_total_cases_comparison,
    create_global_deaths_bubble_chart
)

# Register available country modules here
# Key: Display Name, Value: Module Name (filename in modules/countries without .py)
COUNTRY_MODULES = {
    "South Korea": "south_korea",
    "United States": "usa",
    "Japan": "japan",
    "Europe": "europe"
}


@st.cache_resource(show_spinner=False)
def get_all_country_data(_df):
    """
    모든 국가 데이터를 한 번에 처리하여 메모리에 캐시.
    @st.cache_resource는 객체를 직렬화하지 않고 그대로 저장하므로
    Plotly 차트 객체도 빠르게 반환됨.
    """
    results = {}
    
    for display_name, module_name in COUNTRY_MODULES.items():
        try:
            module = importlib.import_module(f"modules.countries.{module_name}")
            importlib.reload(module) # Force reload to reflect code changes
            results[module_name] = module.process(_df)
        except Exception as e:
            print(f"Failed to load {display_name}: {e}")
            results[module_name] = None
    
    return results


def prewarm_country_cache(df):
    """
    앱 시작 시 모든 국가 데이터 캐시 워밍.
    """
    with st.spinner("🔄 모든 국가 데이터를 로딩 중입니다..."):
        get_all_country_data(df)
    st.success("✅ 데이터 로딩 완료!")


def render_header(df):
    """
    Render the dashboard header with global statistics.
    """
    # --- Sidebar & Navigation ---
    st.sidebar.title("메뉴 (Navigation)")
    
    # Mode Selection - 2 options (Global Overview removed)
    mode = st.sidebar.radio("이동", ["국가별 비교 분석", "국가별 상세 리포트"])
    
    # 캐시된 데이터 가져오기
    all_data = get_all_country_data(df)
    
    if mode == "국가별 비교 분석":
        render_comparison_dashboard(all_data)
    
    elif mode == "국가별 상세 리포트":
        # 탭 방식으로 국가 선택
        country_names = list(COUNTRY_MODULES.keys())
        tabs = st.tabs(country_names)
        
        for tab, country_name in zip(tabs, country_names):
            with tab:
                module_name = COUNTRY_MODULES[country_name]
                data = all_data.get(module_name)
                
                if data:
                    render_country_dashboard(data)
                else:
                    st.warning(f"{country_name}에 대한 데이터가 없습니다.")


def render_comparison_dashboard(all_data):
    """
    모든 국가의 데이터를 비교하는 대시보드 렌더링.
    """
    st.header("📊 국가별 비교 분석 (Comparison Dashboard)")
    st.markdown("주요 국가들의 COVID-19 핵심 지표를 비교합니다.")
    
    # Row 1: Cases and Deaths comparison (full width)
    st.subheader("일일 확진자 및 사망자 추이")
    
    cases_fig = create_dual_axis_comparison(all_data)
    if cases_fig:
        st.plotly_chart(cases_fig, use_container_width=True)
    
    deaths_fig = create_deaths_comparison(all_data)
    if deaths_fig:
        st.plotly_chart(deaths_fig, use_container_width=True)
    
    st.markdown("---")
    
    # Row 2: Vaccination Timeline (Overlay chart)
    st.subheader("백신 접종 진행 현황")
    vacc_timeline_fig = create_vaccination_timeline(all_data)
    if vacc_timeline_fig:
        st.plotly_chart(vacc_timeline_fig, use_container_width=True)
    
    # Row 3: Reproduction Rate Comparison
    st.subheader("감염재생산지수 (Rt) 비교")
    rt_comparison_fig = create_reproduction_rate_comparison(all_data)
    if rt_comparison_fig:
        st.plotly_chart(rt_comparison_fig, use_container_width=True)

    # Row 4: CFR Trend Comparison (New)
    st.subheader("치명률 (CFR) 추이 비교")
    cfr_timeline_fig = create_cfr_timeline(all_data)
    if cfr_timeline_fig:
        st.plotly_chart(cfr_timeline_fig, use_container_width=True)
    
    st.markdown("---")
    
    # Row 5: Bar chart comparisons (2 columns)
    st.subheader("주요 통계 순위")
    
    col1, col2 = st.columns(2)
    
    with col1:
        vacc_fig = create_vaccination_comparison(all_data)
        if vacc_fig:
            st.plotly_chart(vacc_fig, use_container_width=True)
        
        cases_total_fig = create_total_cases_comparison(all_data)
        if cases_total_fig:
            st.plotly_chart(cases_total_fig, use_container_width=True)
    
    with col2:
        cfr_fig = create_cfr_comparison(all_data)
        if cfr_fig:
            st.plotly_chart(cfr_fig, use_container_width=True)


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

    st.markdown(f"## 🏳️ {country_name} 상세 분석")

    # 1. Metrics Row
    if metrics:
        col1, col2, col3 = st.columns(3)
        col1.metric("총 확진자", f"{metrics['total_cases']:,.0f}명")
        col2.metric("총 사망자", f"{metrics['total_deaths']:,.0f}명")
        col3.metric("백신 완전 접종", f"{metrics['people_fully_vaccinated']:,.0f}명")

    # 2. Daily Cases Trend (with USA enhancement)
    st.write("### 📈 일일 확진자 및 사망자 추이")
    if 'dual_axis_timeseries' in visualizations:
        st.plotly_chart(visualizations['dual_axis_timeseries'], use_container_width=True)
    elif not country_df.empty:
        # Fallback to basic chart
        fig = px.line(
            country_df,
            x='date',
            y='new_cases_smoothed',
            title=f'{country_name} 일일 신규 확진자 (7일 평균)',
            labels={'new_cases_smoothed': '신규 확진자 (7일 평균)', 'date': '날짜'}
        )
        st.plotly_chart(fig, use_container_width=True)

    # 3. Vaccination Progress (with USA enhancement)
    st.write("### 💉 백신 접종 진행 현황")
    if 'vaccination_progress' in visualizations:
        st.plotly_chart(visualizations['vaccination_progress'], use_container_width=True)
    elif not country_df.empty and 'people_fully_vaccinated' in country_df.columns:
        # Fallback to basic chart
        fig2 = px.area(
            country_df,
            x='date',
            y='people_fully_vaccinated',
            title=f'{country_name} 누적 백신 완전 접종자 수',
            labels={'people_fully_vaccinated': '접종 완료자 수', 'date': '날짜'}
        )
        st.plotly_chart(fig2, use_container_width=True)

    # === Common Advanced Visualizations (All Countries) ===
    # 4. Reproduction Rate (Rt)
    if 'reproduction_rate' in visualizations:
        st.write("### 🦠 감염재생산지수 (Rt)")
        st.plotly_chart(visualizations['reproduction_rate'], use_container_width=True)

    # 5. Case Fatality Rate Trend
    if 'case_fatality_rate' in visualizations:
        st.write("### 📊 치명률 (CFR) 추이")
        st.plotly_chart(visualizations['case_fatality_rate'], use_container_width=True)

    # === USA-Specific Advanced Visualizations ===
    if country_name == "United States" and visualizations:
            
        # Wave Analysis (For USA as well now)
        if 'wave_detection' in visualizations:
            st.write("### 🌊 파동(Wave) 감지 분석")
            st.plotly_chart(visualizations['wave_detection'], use_container_width=True)
            
        if 'wave_comparison' in visualizations:
            st.write("### 📊 파동별 규모 비교")
            st.plotly_chart(visualizations['wave_comparison'], use_container_width=True)
            
        if 'vaccination_impact' in visualizations:
            st.write("### 💉 백신 접종 효과 분석")
            st.plotly_chart(visualizations['vaccination_impact'], use_container_width=True)

    # === Japan-Specific Advanced Visualizations ===
    if country_name == "Japan" and visualizations:

        # 4. Wave Detection (파동 감지)
        if 'wave_detection' in visualizations:
            st.write("### 🌊 파동(Wave) 감지 분석")
            st.plotly_chart(visualizations['wave_detection'], use_container_width=True)

        # 5. Wave Comparison (파동별 비교)
        if 'wave_comparison' in visualizations:
            st.write("### 📊 파동별 규모 비교")
            st.plotly_chart(visualizations['wave_comparison'], use_container_width=True)

        # 6. Vaccination Impact (백신 전/후 비교)
        if 'vaccination_impact' in visualizations:
            st.write("### 💉 백신 접종 효과 분석")
            st.plotly_chart(visualizations['vaccination_impact'], use_container_width=True)

        # 7. Cases-Deaths Decoupling (확진-사망 디커플링)
        if 'cases_deaths_decoupling' in visualizations:
            st.write("### 📉 확진-사망 디커플링 분석")
            st.plotly_chart(visualizations['cases_deaths_decoupling'], use_container_width=True)
            
    # === South Korea-Specific Advanced Visualizations (Added) ===
    if country_name == "South Korea" and visualizations:
        
        # Wave Analysis
        if 'wave_detection' in visualizations:
            st.write("### 🌊 파동(Wave) 감지 분석")
            st.plotly_chart(visualizations['wave_detection'], use_container_width=True)
            
        if 'wave_comparison' in visualizations:
            st.write("### 📊 파동별 규모 비교")
            st.plotly_chart(visualizations['wave_comparison'], use_container_width=True)
            
        if 'vaccination_impact' in visualizations:
            st.write("### 💉 백신 접종 효과 분석")
            st.plotly_chart(visualizations['vaccination_impact'], use_container_width=True)

    # === Europe-Specific Advanced Visualizations ===
    if country_name == "Europe" and visualizations:
        
        # 4. Multi-Country Trends (국가별 트렌드)
        st.write("### 📈 유럽 주요 국가별 트렌드")
        
        if 'multi_country_trend' in visualizations:
            st.plotly_chart(visualizations['multi_country_trend'], use_container_width=True)

        if 'multi_country_rt' in visualizations: # 추가된 차트
            st.plotly_chart(visualizations['multi_country_rt'], use_container_width=True)
            
        if 'europe_deaths_trend' in visualizations:
            st.plotly_chart(visualizations['europe_deaths_trend'], use_container_width=True)

        # 5. Summary Dashboard (종합 대시보드)
        if 'summary_dashboard' in visualizations:
            st.write("### 📊 종합 대시보드")
            st.plotly_chart(visualizations['summary_dashboard'], use_container_width=True)

        # 5. Deaths Bubble Chart (사망률 버블 차트)
        if 'deaths_bubble' in visualizations:
            st.write("### 🔴 백신 접종률 vs 백만명당 사망자")
            st.plotly_chart(visualizations['deaths_bubble'], use_container_width=True)
