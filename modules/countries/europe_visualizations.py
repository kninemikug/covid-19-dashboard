"""
Europe-specific COVID-19 Visualizations Module

Plotly charts for European region analysis:
- Multi-country comparison (다국가 비교)
- Vaccination vs CFR scatter (백신 접종률 vs 치명률)
- Total deaths bubble chart (사망률 버블 차트)
"""
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

# 유럽 국가 목록 (주요 국가)
EUROPE_COUNTRIES = [
    'Germany', 'France', 'Italy', 'Spain', 'Poland', 'Romania', 'Netherlands',
    'Belgium', 'Sweden', 'Austria', 'Switzerland', 'Greece', 'Portugal',
    'Czechia', 'Hungary', 'Norway', 'Denmark', 'Finland', 'Ireland', 'Slovakia'
]

# 색상 팔레트
COLOR_PALETTE = px.colors.qualitative.Set2


# ============================================================
# Chart 1: Multi-Country Cases & Deaths Trend (다국가 확진/사망 추이)
# ============================================================
def create_multi_country_trend(europe_df, countries=None):
    """
    유럽 국가들의 일별 확진자를 개별 라인으로 비교하는 차트 (USA 스타일).
    """
    if countries is None:
        countries = EUROPE_COUNTRIES
    
    df = europe_df[europe_df['location'].isin(countries)].copy()
    
    if df.empty:
        return None
    
    fig = go.Figure()
    
    for i, country in enumerate(df['location'].unique()):
        country_data = df[df['location'] == country]
        color = COLOR_PALETTE[i % len(COLOR_PALETTE)]
        
        fig.add_trace(go.Scatter(
            x=country_data['date'],
            y=country_data['new_cases_smoothed'],
            name=country,
            line=dict(color=color, width=1.5),
            hovertemplate=f'<b>{country}</b><br>확진자: %{{y:,.0f}}명<extra></extra>'
        ))
    
    fig.update_layout(
        title='📈 유럽 국가별 일별 확진자 추이 (7일 평균)',
        xaxis_title='날짜',
        yaxis_title='신규 확진자 (7일 평균)',
        template='plotly_white',
        hovermode='x unified',
        height=500,
        xaxis=dict(
            rangeslider=dict(visible=True),
            rangeselector=dict(
                buttons=[
                    dict(count=1, label='1개월', step='month', stepmode='backward'),
                    dict(count=3, label='3개월', step='month', stepmode='backward'),
                    dict(count=6, label='6개월', step='month', stepmode='backward'),
                    dict(step='all', label='전체')
                ]
            ),
            type='date'
        ),
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='center',
            x=0.5,
            font=dict(size=9)
        )
    )
    
    return fig


def create_multi_country_reproduction_rate(europe_df, countries=None):
    """
    유럽 국가들의 재생산지수(Rt) 추이 비교 차트.
    Rt=1.0 기준선 포함.
    """
    if countries is None:
        countries = EUROPE_COUNTRIES
    
    df = europe_df[europe_df['location'].isin(countries)].copy()
    
    if df.empty:
        return None
    
    fig = go.Figure()
    
    for i, country in enumerate(df['location'].unique()):
        country_data = df[df['location'] == country]
        # Rt 데이터가 없으면 스킵
        if 'reproduction_rate' not in country_data.columns:
            continue
            
        color = COLOR_PALETTE[i % len(COLOR_PALETTE)]
        
        fig.add_trace(go.Scatter(
            x=country_data['date'],
            y=country_data['reproduction_rate'],
            name=country,
            line=dict(color=color, width=1.5),
            hovertemplate=f'<b>{country}</b><br>Rt: %{{y:.2f}}<extra></extra>'
        ))
    
    # Rt=1.0 기준선
    fig.add_hline(y=1.0, line_dash="dash", line_color="red", opacity=0.7, annotation_text="Rt=1.0 (위험 기준)")
    
    fig.update_layout(
        title='📊 유럽 국가별 감염재생산지수(Rt) 추이',
        xaxis_title='날짜',
        yaxis_title='감염재생산지수 (Rt)',
        yaxis=dict(range=[0, 3]),
        template='plotly_white',
        xaxis=dict(
            rangeslider=dict(visible=True),
            type='date'
        ),
        hovermode='x unified',
        height=500,
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='center',
            x=0.5,
            font=dict(size=9)
        )
    )
    
    return fig


def create_multi_country_cfr_trend(europe_df, countries=None):
    """
    유럽 국가들의 치명률(CFR) 추이 비교 차트.
    """
    if countries is None:
        countries = EUROPE_COUNTRIES
    
    df = europe_df[europe_df['location'].isin(countries)].copy()
    
    if df.empty:
        return None
    
    fig = go.Figure()
    
    for i, country in enumerate(df['location'].unique()):
        country_data = df[df['location'] == country]
        # 필수 데이터 확인
        if 'total_cases' not in country_data.columns or 'total_deaths' not in country_data.columns:
            continue
            
        color = COLOR_PALETTE[i % len(COLOR_PALETTE)]
        
        # CFR 계산
        temp_df = country_data.sort_values('date').copy()
        temp_df['cfr'] = 0.0
        mask = temp_df['total_cases'] > 50
        
        temp_df.loc[mask, 'cfr'] = (temp_df.loc[mask, 'total_deaths'] / temp_df.loc[mask, 'total_cases'] * 100).fillna(0)
        
        fig.add_trace(go.Scatter(
            x=temp_df['date'],
            y=temp_df['cfr'],
            name=country,
            line=dict(color=color, width=1.5),
            hovertemplate=f'<b>{country}</b><br>치명률: %{{y:.2f}}%<extra></extra>'
        ))
    
    fig.update_layout(
        title='⚠️ 유럽 국가별 치명률(CFR) 추이',
        xaxis_title='날짜',
        yaxis_title='치명률 (%)',
        yaxis=dict(ticksuffix='%'),
        template='plotly_white',
        xaxis=dict(
            rangeslider=dict(visible=True),
            type='date'
        ),
        hovermode='x unified',
        height=500,
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='center',
            x=0.5,
            font=dict(size=9)
        )
    )
    
    return fig


def create_europe_deaths_trend(europe_df, countries=None):
    """
    유럽 국가들의 일별 사망자를 개별 라인으로 비교하는 차트.
    """
    if countries is None:
        countries = EUROPE_COUNTRIES
    
    df = europe_df[europe_df['location'].isin(countries)].copy()
    
    if df.empty:
        return None
    
    fig = go.Figure()
    
    for i, country in enumerate(df['location'].unique()):
        country_data = df[df['location'] == country]
        color = COLOR_PALETTE[i % len(COLOR_PALETTE)]
        
        fig.add_trace(go.Scatter(
            x=country_data['date'],
            y=country_data['new_deaths_smoothed'],
            name=country,
            line=dict(color=color, width=1.5),
            hovertemplate=f'<b>{country}</b><br>사망자: %{{y:,.0f}}명<extra></extra>'
        ))
    
    fig.update_layout(
        title='📉 유럽 국가별 일별 사망자 추이 (7일 평균)',
        xaxis_title='날짜',
        yaxis_title='신규 사망자 (7일 평균)',
        template='plotly_white',
        hovermode='x unified',
        height=500,
        xaxis=dict(
            rangeslider=dict(visible=True),
            rangeselector=dict(
                buttons=[
                    dict(count=1, label='1개월', step='month', stepmode='backward'),
                    dict(count=3, label='3개월', step='month', stepmode='backward'),
                    dict(count=6, label='6개월', step='month', stepmode='backward'),
                    dict(step='all', label='전체')
                ]
            ),
            type='date'
        ),
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='center',
            x=0.5,
            font=dict(size=9)
        )
    )
    
    return fig


# ============================================================
# Chart 2: Vaccination Rate Comparison (백신 접종률 비교)
# ============================================================
def create_vaccination_comparison(europe_df, countries=None):
    """
    유럽 국가들의 백신 접종률을 막대 차트로 비교.
    """
    if countries is None:
        countries = EUROPE_COUNTRIES[:10]
    
    df = europe_df[europe_df['location'].isin(countries)].copy()
    
    if df.empty:
        return None
    
    # 각 국가별 최신 데이터
    latest_data = df.groupby('location').apply(
        lambda x: x.loc[x['date'].idxmax()]
    ).reset_index(drop=True)
    
    # 접종률 계산
    latest_data['vaccination_rate'] = (
        latest_data['people_fully_vaccinated'] / latest_data['population'] * 100
    ).fillna(0)
    
    latest_data = latest_data.sort_values('vaccination_rate', ascending=True)
    
    fig = px.bar(
        latest_data,
        x='vaccination_rate',
        y='location',
        orientation='h',
        title='유럽 주요 국가 백신 접종 완료율 (%)',
        labels={
            'vaccination_rate': '접종 완료율 (%)',
            'location': '국가'
        },
        color='vaccination_rate',
        color_continuous_scale='Greens'
    )
    
    fig.update_layout(
        template='plotly_white',
        showlegend=False,
        coloraxis_showscale=False
    )
    
    return fig


# ============================================================
# Chart 3: COVID-19 Summary Dashboard (종합 대시보드)
# ============================================================
def create_europe_summary_dashboard(europe_df, countries=None):
    """
    유럽 국가들의 COVID-19 주요 지표를 종합 비교하는 2x2 서브플롯.
    
    1. 총 확진자 수
    2. 총 사망자 수  
    3. 백신 접종률
    4. 치명률(CFR)
    """
    if countries is None:
        countries = ['Germany', 'France', 'Italy', 'Spain', 'Poland', 
                     'Romania', 'Netherlands', 'Belgium']
    
    df = europe_df[europe_df['location'].isin(countries)].copy()
    
    if df.empty:
        return None
    
    # 각 국가별 최신 데이터
    latest_data = df.groupby('location').apply(
        lambda x: x.loc[x['date'].idxmax()]
    ).reset_index(drop=True)
    
    # 파생 지표 계산
    latest_data['vaccination_rate'] = (
        latest_data['people_fully_vaccinated'] / latest_data['population'] * 100
    ).fillna(0)
    
    latest_data['cfr'] = (
        latest_data['total_deaths'] / latest_data['total_cases'] * 100
    ).fillna(0)
    
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            '총 확진자 수', '총 사망자 수',
            '백신 접종 완료율 (%)', '치명률 (CFR, %)'
        ),
        vertical_spacing=0.15,
        horizontal_spacing=0.1
    )
    
    # 총 확진자 수
    sorted_cases = latest_data.sort_values('total_cases', ascending=True)
    fig.add_trace(
        go.Bar(
            x=sorted_cases['total_cases'],
            y=sorted_cases['location'],
            orientation='h',
            marker_color='#3498db',
            name='확진자'
        ),
        row=1, col=1
    )
    
    # 총 사망자 수
    sorted_deaths = latest_data.sort_values('total_deaths', ascending=True)
    fig.add_trace(
        go.Bar(
            x=sorted_deaths['total_deaths'],
            y=sorted_deaths['location'],
            orientation='h',
            marker_color='#e74c3c',
            name='사망자'
        ),
        row=1, col=2
    )
    
    # 백신 접종률
    sorted_vacc = latest_data.sort_values('vaccination_rate', ascending=True)
    fig.add_trace(
        go.Bar(
            x=sorted_vacc['vaccination_rate'],
            y=sorted_vacc['location'],
            orientation='h',
            marker_color='#2ecc71',
            name='접종률'
        ),
        row=2, col=1
    )
    
    # 치명률
    sorted_cfr = latest_data.sort_values('cfr', ascending=True)
    fig.add_trace(
        go.Bar(
            x=sorted_cfr['cfr'],
            y=sorted_cfr['location'],
            orientation='h',
            marker_color='#9b59b6',
            name='치명률'
        ),
        row=2, col=2
    )
    
    fig.update_layout(
        title='유럽 주요 국가 COVID-19 종합 비교',
        height=700,
        showlegend=False,
        template='plotly_white'
    )
    
    return fig


# ============================================================
# Chart 4: Deaths per Million Bubble Chart (백만명당 사망자 버블 차트)
# ============================================================
def create_deaths_bubble_chart(europe_df, countries=None):
    """
    백신 접종률 vs 백만명당 사망자 버블 차트.
    버블 크기는 인구, 색상은 사망률.
    """
    if countries is None:
        countries = EUROPE_COUNTRIES
    
    df = europe_df[europe_df['location'].isin(countries)].copy()
    
    if df.empty:
        return None
    
    # 각 국가별 최신 데이터
    latest_data = df.groupby('location').apply(
        lambda x: x.loc[x['date'].idxmax()]
    ).reset_index(drop=True)
    
    # 필터링: 인구 100만 이상
    latest_data = latest_data[latest_data['population'] > 1_000_000].copy()
    
    if latest_data.empty:
        return None
    
    # 파생 지표 계산
    latest_data['vaccination_rate'] = (
        latest_data['people_fully_vaccinated'] / latest_data['population'] * 100
    ).fillna(0)
    
    # total_deaths_per_million이 없으면 계산
    if 'total_deaths_per_million' not in latest_data.columns:
        latest_data['total_deaths_per_million'] = (
            latest_data['total_deaths'] / latest_data['population'] * 1_000_000
        ).fillna(0)
    
    latest_data['population_millions'] = latest_data['population'] / 1_000_000
    
    fig = px.scatter(
        latest_data,
        x='vaccination_rate',
        y='total_deaths_per_million',
        size='population_millions',
        color='total_deaths_per_million',
        hover_name='location',
        hover_data={
            'vaccination_rate': ':.1f',
            'total_deaths_per_million': ':.1f',
            'population_millions': ':.1f'
        },
        color_continuous_scale='Reds',
        size_max=50,
        title='유럽 국가별 백신 접종률 vs 백만명당 사망자<br><sub>버블 크기 = 인구 | 색상 = 사망률</sub>',
        labels={
            'vaccination_rate': '백신 접종률 (%)',
            'total_deaths_per_million': '백만명당 사망자',
            'population_millions': '인구 (백만)'
        }
    )
    
    fig.update_layout(
        template='plotly_white',
        hovermode='closest'
    )
    
    fig.update_traces(
        marker=dict(
            line=dict(width=1, color='white')
        )
    )
    
    return fig
