"""
Europe COVID-19 Analysis Module

유럽 다국가 COVID-19 데이터 분석 및 시각화.
다른 국가 모듈과 동일한 인터페이스를 제공합니다.
"""
import pandas as pd
from .europe_visualizations import (
    create_multi_country_trend,
    create_multi_country_reproduction_rate,
    create_multi_country_cfr_trend,
    create_europe_deaths_trend,
    create_vaccination_comparison,
    create_europe_summary_dashboard,
    create_deaths_bubble_chart
)
from modules.common_visualizations import create_dual_axis_timeseries

# 분석 대상 유럽 국가 목록
EUROPE_COUNTRIES = [
    'Germany', 'France', 'Italy', 'Spain', 'Poland', 'Romania', 'Netherlands',
    'Belgium', 'Sweden', 'Austria', 'Switzerland', 'Greece', 'Portugal',
    'Czechia', 'Hungary', 'Norway', 'Denmark', 'Finland', 'Ireland', 'Slovakia',
    'Bulgaria', 'Croatia', 'Slovenia', 'Lithuania', 'Latvia', 'Estonia'
]


def process(df):
    """
    유럽 COVID-19 데이터 전처리 및 분석 파이프라인.

    다른 국가 모듈과 동일한 반환 형식:
    - country_name: str
    - country_df: DataFrame
    - metrics: dict
    - visualizations: dict
    """
    region_name = "Europe"

    # ==========================================================
    # 1. 데이터 필터링 (유럽 국가들)
    # ==========================================================
    europe_df = df[df['location'].isin(EUROPE_COUNTRIES)].copy()

    if europe_df.empty:
        return None

    europe_df = europe_df.sort_values(['location', 'date']).reset_index(drop=True)

    # ==========================================================
    # 2. 결측치 처리
    # ==========================================================
    for col in ['new_cases_smoothed', 'new_deaths_smoothed', 'total_cases', 'total_deaths']:
        if col in europe_df.columns:
            europe_df[col] = europe_df.groupby('location')[col].transform(
                lambda x: x.ffill().fillna(0)
            )

    for col in ['people_fully_vaccinated', 'total_vaccinations']:
        if col in europe_df.columns:
            europe_df[col] = europe_df.groupby('location')[col].transform(
                lambda x: x.ffill()
            )

    # ==========================================================
    # 3. 메트릭 계산 (유럽 전체 집계)
    # ==========================================================
    # 각 국가별 최신 데이터
    latest_data = europe_df.groupby('location').apply(
        lambda x: x.loc[x['date'].idxmax()]
    ).reset_index(drop=True)

    total_cases = float(latest_data['total_cases'].sum())
    total_deaths = float(latest_data['total_deaths'].sum())
    total_vaccinated = float(latest_data['people_fully_vaccinated'].sum())
    total_population = float(latest_data['population'].sum())

    # 가장 최근 일별 확진자 합계
    latest_date = europe_df['date'].max()
    latest_daily = europe_df[europe_df['date'] == latest_date]
    new_cases = float(latest_daily['new_cases'].sum()) if 'new_cases' in latest_daily.columns else 0

    # 파생 지표
    cfr = (total_deaths / total_cases * 100) if total_cases > 0 else 0
    vacc_rate = (total_vaccinated / total_population * 100) if total_population > 0 else 0
    
    # Rt 평균 (유럽 전체)
    avg_rt = latest_data['reproduction_rate'].mean() if 'reproduction_rate' in latest_data.columns else 0

    metrics = {
        # 기본 메트릭 (UI 호환)
        "total_cases": total_cases,
        "total_deaths": total_deaths,
        "people_fully_vaccinated": total_vaccinated,
        "new_cases": new_cases,

        # 파생 메트릭
        "case_fatality_rate": round(cfr, 2),
        "vaccination_rate": round(vacc_rate, 2),
        "reproduction_rate": round(avg_rt, 2), # 추가
        "countries_count": len(EUROPE_COUNTRIES),
        "total_population": total_population,
    }

    # ==========================================================
    # 4. 시각화 생성
    # ==========================================================
    visualizations = {}

    try:
        # 유럽 전체 집계 데이터 생성 (dual_axis용)
        europe_agg = europe_df.groupby('date').agg({
            'new_cases_smoothed': 'sum',
            'new_deaths_smoothed': 'sum'
        }).reset_index()
        
        # 공통 시각화 (USA 스타일) - 유럽 전체 집계
        visualizations['dual_axis_timeseries'] = create_dual_axis_timeseries(europe_agg, region_name)
        
        # 유럽 고유 시각화 (국가별 비교)
        visualizations['multi_country_trend'] = create_multi_country_trend(europe_df)
        visualizations['multi_country_rt'] = create_multi_country_reproduction_rate(europe_df) # 추가
        visualizations['multi_country_cfr'] = create_multi_country_cfr_trend(europe_df) # 추가
        visualizations['europe_deaths_trend'] = create_europe_deaths_trend(europe_df) # 사망자 추이 추가
        visualizations['vaccination_progress'] = create_vaccination_comparison(europe_df)
        visualizations['summary_dashboard'] = create_europe_summary_dashboard(europe_df)
        visualizations['deaths_bubble'] = create_deaths_bubble_chart(europe_df)

    except Exception as e:
        print(f"Europe visualization error: {e}")

    # ==========================================================
    # 반환 (표준 형식)
    # ==========================================================
    return {
        "country_name": region_name,
        "country_df": europe_df,
        "metrics": metrics,
        "visualizations": visualizations,
    }
