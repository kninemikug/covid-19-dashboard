"""
Multi-Country Comparison Visualizations Module

국가별 비교 차트 (USA 스타일 dual-axis)
"""

import plotly.graph_objects as go
import pandas as pd

# 스타일 설정
CHART_THEME = {
    "template": "plotly_white",
    "height": 500,
    "hovermode": "x unified"
}

COLORS = {
    "South Korea": "#3498db",
    "United States": "#e74c3c", 
    "Japan": "#9b59b6",
    "Europe": "#2ecc71"
}


def create_dual_axis_comparison(all_country_data, show_europe_countries=False):
    """
    모든 국가의 일별 확진자를 비교 (유럽은 집계).
    """
    fig = go.Figure()
    
    for module_name, data in all_country_data.items():
        if data is None:
            continue
        
        display_name = data.get('country_name', module_name)
        country_df = data.get('country_df')
        
        if country_df is None or country_df.empty:
            continue
        
        # 유럽: 날짜별 집계
        if display_name == "Europe" and 'location' in country_df.columns:
            country_df = country_df.groupby('date').agg({
                'new_cases_smoothed': 'sum'
            }).reset_index()
        
        if 'new_cases_smoothed' not in country_df.columns:
            continue
        
        color = COLORS.get(display_name, '#888888')
        
        fig.add_trace(go.Scatter(
            x=country_df['date'],
            y=country_df['new_cases_smoothed'],
            name=display_name,
            line=dict(color=color, width=2),
            fill='tozeroy',
            fillcolor=f'rgba{tuple(list(int(color.lstrip("#")[i:i+2], 16) for i in (0, 2, 4)) + [0.1])}',
            hovertemplate=f'<b>{display_name}</b><br>확진자: %{{y:,.0f}}명<extra></extra>'
        ))
    
    fig.update_layout(
        title='📈 국가별 일일 신규 확진자 비교 (7일 평균)',
        xaxis_title='날짜',
        yaxis_title='신규 확진자 (명)',
        **CHART_THEME,
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
        legend=dict(orientation='h', y=1.02, x=0.5, xanchor='center')
    )
    
    return fig


def create_deaths_comparison(all_country_data, show_europe_countries=False):
    """
    모든 국가의 일별 사망자를 비교.
    """
    fig = go.Figure()
    
    for module_name, data in all_country_data.items():
        if data is None:
            continue
        
        display_name = data.get('country_name', module_name)
        country_df = data.get('country_df')
        
        if country_df is None or country_df.empty:
            continue
        
        # 유럽: 날짜별 집계
        if display_name == "Europe" and 'location' in country_df.columns:
            country_df = country_df.groupby('date').agg({
                'new_deaths_smoothed': 'sum'
            }).reset_index()
        
        if 'new_deaths_smoothed' not in country_df.columns:
            continue
        
        color = COLORS.get(display_name, '#888888')
        
        fig.add_trace(go.Scatter(
            x=country_df['date'],
            y=country_df['new_deaths_smoothed'],
            name=display_name,
            line=dict(color=color, width=2),
            fill='tozeroy',
            fillcolor=f'rgba{tuple(list(int(color.lstrip("#")[i:i+2], 16) for i in (0, 2, 4)) + [0.1])}',
            hovertemplate=f'<b>{display_name}</b><br>사망자: %{{y:,.0f}}명<extra></extra>'
        ))
    
    fig.update_layout(
        title='📉 국가별 일일 사망자 비교 (7일 평균)',
        xaxis_title='날짜',
        yaxis_title='사망자 (명)',
        **CHART_THEME,
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
        legend=dict(orientation='h', y=1.02, x=0.5, xanchor='center')
    )
    
    return fig


def create_vaccination_comparison(all_country_data):
    """백신 접종률 비교."""
    data_list = []
    
    for module_name, data in all_country_data.items():
        if data is None:
            continue
        display_name = data.get('country_name', module_name)
        metrics = data.get('metrics', {})
        vacc_rate = metrics.get('vaccination_rate', 0)
        data_list.append({'country': display_name, 'rate': vacc_rate})
    
    if not data_list:
        return None
    
    df = pd.DataFrame(data_list).sort_values('rate', ascending=True)
    colors = [COLORS.get(c, '#888') for c in df['country']]
    
    fig = go.Figure(go.Bar(
        x=df['rate'], y=df['country'], orientation='h',
        marker=dict(color=colors),
        text=df['rate'].apply(lambda x: f'{x:.1f}%'),
        textposition='outside'
    ))
    
    fig.update_layout(title='💉 백신 접종 완료율 (%)', height=300, template='plotly_white')
    return fig


def create_cfr_comparison(all_country_data):
    """치명률 비교."""
    data_list = []
    
    for module_name, data in all_country_data.items():
        if data is None:
            continue
        display_name = data.get('country_name', module_name)
        metrics = data.get('metrics', {})
        cfr = metrics.get('case_fatality_rate', 0)
        data_list.append({'country': display_name, 'cfr': cfr})
    
    if not data_list:
        return None
    
    df = pd.DataFrame(data_list).sort_values('cfr', ascending=True)
    colors = [COLORS.get(c, '#888') for c in df['country']]
    
    fig = go.Figure(go.Bar(
        x=df['cfr'], y=df['country'], orientation='h',
        marker=dict(color=colors),
        text=df['cfr'].apply(lambda x: f'{x:.2f}%'),
        textposition='outside'
    ))
    
    fig.update_layout(title='⚠️ 치명률 (CFR, %)', height=300, template='plotly_white')
    return fig


def create_total_cases_comparison(all_country_data):
    """총 확진자 비교."""
    data_list = []
    
    for module_name, data in all_country_data.items():
        if data is None:
            continue
        display_name = data.get('country_name', module_name)
        metrics = data.get('metrics', {})
        total = metrics.get('total_cases', 0)
        data_list.append({'country': display_name, 'total': total})
    
    if not data_list:
        return None
    
    df = pd.DataFrame(data_list).sort_values('total', ascending=True)
    colors = [COLORS.get(c, '#888') for c in df['country']]
    
    fig = go.Figure(go.Bar(
        x=df['total'], y=df['country'], orientation='h',
        marker=dict(color=colors),
        text=df['total'].apply(lambda x: f'{x/1e6:.1f}M'),
        textposition='outside'
    ))
    
    
    fig.update_layout(title='🦠 누적 확진자 수', height=300, template='plotly_white')
    return fig


def create_vaccination_timeline(all_country_data):
    """
    모든 국가의 백신 접종률 추이를 시계열 라인 차트로 비교 (Overlaid Line Chart).
    유럽의 경우 개별 국가 데이터를 빈틈없이 메워서(ffill) 합산 처리.
    """
    fig = go.Figure()
    
    for module_name, data in all_country_data.items():
        if data is None:
            continue
        
        display_name = data.get('country_name', module_name)
        country_df = data.get('country_df')
        metrics = data.get('metrics', {})
        population = metrics.get('total_population') or metrics.get('population')
        
        if country_df is None or country_df.empty or not population:
            continue
            
        # 유럽 처리: 모든 국가의 데이터를 채워서 합산
        if display_name == "Europe" and 'location' in country_df.columns:
            try:
                # 1. 피벗 테이블 생성 (날짜 x 국가)
                # 중복 날짜/국가 조합이 있을 경우 max 값 사용 (누적 데이터이므로)
                pivot = country_df.pivot_table(
                    index='date', 
                    columns='location', 
                    values='people_fully_vaccinated', 
                    aggfunc='max'
                )
                
                # 2. 전체 날짜 범위로 리인덱싱 (빈 날짜 생성)
                all_dates = pd.date_range(start=pivot.index.min(), end=pivot.index.max())
                pivot = pivot.reindex(all_dates)
                
                # 3. 결측치 처리: ffill로 누적값 유지, 앞부분은 0으로 채움
                pivot = pivot.ffill().fillna(0)
                
                # 4. 일별 합계 계산
                total_vaccinated = pivot.sum(axis=1)
                
                # 5. 접종률 계산
                y_data = (total_vaccinated / population) * 100
                x_data = total_vaccinated.index
                
            except Exception as e:
                print(f"Europe vaccination aggregation error: {e}")
                continue
            
        else:
            # 단일 국가
            if 'people_fully_vaccinated' not in country_df.columns:
                continue
                
            # 안전장치: 시각화 직전 한번 더 결측치 처리 (South Korea 등 데이터 끊김 방지)
            df_temp = country_df.sort_values('date').copy()
            # 누적 데이터이므로 ffill 후 0으로 채움
            vax_series = df_temp['people_fully_vaccinated'].ffill().fillna(0)
            
            x_data = df_temp['date']
            y_data = (vax_series / population) * 100
        
        # 100% 넘는 경우 클리핑 (인구 통계 오차 등)
        y_data = y_data.clip(upper=100)
        
        color = COLORS.get(display_name, '#888888')
        
        # Hex to RGBA for fill
        if color.startswith('#'):
            hex_c = color.lstrip('#')
            fill_color = f"rgba({int(hex_c[0:2], 16)}, {int(hex_c[2:4], 16)}, {int(hex_c[4:6], 16)}, 0.1)"
        else:
            fill_color = color # 이미 rgba 형식이거나 이름인 경우 그대로 사용
            
        fig.add_trace(go.Scatter(
            x=x_data,
            y=y_data,
            name=display_name,
            line=dict(color=color, width=2),
            fill='tozeroy',
            fillcolor=fill_color,
            hovertemplate=f'<b>{display_name}</b><br>접종률: %{{y:.1f}}%<extra></extra>'
        ))
        
    fig.update_layout(
        title='💉 국가별 백신 접종 완료율 추이',
        xaxis_title='날짜',
        yaxis_title='접종 완료율 (%)',
        yaxis=dict(range=[0, 105]), # 100% 살짝 위까지 여유
        **CHART_THEME,
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
        legend=dict(orientation='h', y=1.02, x=0.5, xanchor='center')
    )
    
    return fig


def create_reproduction_rate_comparison(all_country_data):
    """
    모든 국가의 재생산지수(Rt) 추이를 시계열 라인 차트로 비교.
    Rt=1.0 기준선을 표시하여 확산/진정 국면 파악 용이.
    유럽의 경우 국가별 평균 Rt를 사용.
    """
    fig = go.Figure()
    
    for module_name, data in all_country_data.items():
        if data is None:
            continue
        
        display_name = data.get('country_name', module_name)
        country_df = data.get('country_df')
        
        if country_df is None or country_df.empty:
            continue
            
        color = COLORS.get(display_name, '#888888')
        
        # 유럽 처리: 모든 국가의 Rt 평균 계산
        if display_name == "Europe" and 'location' in country_df.columns:
            try:
                pivot = country_df.pivot_table(
                    index='date', 
                    columns='location', 
                    values='reproduction_rate', 
                    aggfunc='mean'
                )
                # 날짜 리인덱싱 및 보간
                all_dates = pd.date_range(start=pivot.index.min(), end=pivot.index.max())
                pivot = pivot.reindex(all_dates).interpolate(method='linear')
                
                # 일별 평균 Rt
                y_data = pivot.mean(axis=1)
                x_data = y_data.index
            except Exception as e:
                print(f"Europe Rt aggregation error: {e}")
                continue
        else:
            # 단일 국가
            if 'reproduction_rate' not in country_df.columns:
                continue
            
            # 안전장치: 보간
            df_temp = country_df.sort_values('date').copy()
            df_temp['reproduction_rate'] = df_temp['reproduction_rate'].interpolate(method='linear')
            
            x_data = df_temp['date']
            y_data = df_temp['reproduction_rate']
            
        fig.add_trace(go.Scatter(
            x=x_data,
            y=y_data,
            name=display_name,
            line=dict(color=color, width=1.5),
            hovertemplate=f'<b>{display_name}</b><br>Rt: %{{y:.2f}}<extra></extra>'
        ))
        
    # Rt=1.0 기준선
    fig.add_hline(y=1.0, line_dash="dash", line_color="red", opacity=0.7, annotation_text="Rt=1.0 (위험 기준)", annotation_position="bottom right")

    fig.update_layout(
        title='🦠 국가별 감염재생산지수 (Rt) 비교',
        xaxis_title='날짜',
        yaxis_title='감염재생산지수 (Rt)',
        yaxis=dict(range=[0, 3]), # Rt는 보통 0~3 사이
        **CHART_THEME,
        xaxis=dict(
            rangeslider=dict(visible=True),
            type='date'
        ),
        legend=dict(orientation='h', y=1.02, x=0.5, xanchor='center')
    )
    
    return fig


def create_cfr_timeline(all_country_data):
    """
    모든 국가의 치명률(CFR) 추이를 시계열 라인 차트로 비교.
    """
    fig = go.Figure()
    
    for module_name, data in all_country_data.items():
        if data is None:
            continue
        
        display_name = data.get('country_name', module_name)
        country_df = data.get('country_df')
        
        if country_df is None or country_df.empty:
            continue
            
        color = COLORS.get(display_name, '#888888')
        
        # 유럽 처리: 일별 합계로 CFR 재계산
        if display_name == "Europe" and 'location' in country_df.columns:
            try:
                # 날짜별 합계 계산
                agg_df = country_df.groupby('date')[['total_cases', 'total_deaths']].sum().reset_index()
                
                # 노이즈 제거: 확진자 수가 너무 적을 때는 CFR 계산 제외 (예: 50명 미만)
                mask = agg_df['total_cases'] > 50
                agg_df.loc[~mask, 'cfr'] = 0
                agg_df.loc[mask, 'cfr'] = (agg_df.loc[mask, 'total_deaths'] / agg_df.loc[mask, 'total_cases'] * 100).fillna(0)
                
                x_data = agg_df['date']
                y_data = agg_df['cfr']
            except Exception as e:
                print(f"Europe CFR aggregation error: {e}")
                continue
        else:
            # 단일 국가
            if 'total_cases' not in country_df.columns or 'total_deaths' not in country_df.columns:
                continue
            
            # CFR 계산
            df_temp = country_df.sort_values('date').copy()
            
            # 노이즈 제거
            df_temp['cfr'] = 0.0
            mask = df_temp['total_cases'] > 50
            df_temp.loc[mask, 'cfr'] = (df_temp.loc[mask, 'total_deaths'] / df_temp.loc[mask, 'total_cases'] * 100).fillna(0)
            
            x_data = df_temp['date']
            y_data = df_temp['cfr']
            
        fig.add_trace(go.Scatter(
            x=x_data,
            y=y_data,
            name=display_name,
            line=dict(color=color, width=1.5),
            hovertemplate=f'<b>{display_name}</b><br>치명률: %{{y:.2f}}%<extra></extra>'
        ))
        
    fig.update_layout(
        title='⚠️ 국가별 치명률 (CFR) 추이 비교',
        xaxis_title='날짜',
        yaxis_title='치명률 (%)',
        yaxis=dict(ticksuffix='%'),
        **CHART_THEME,
        xaxis=dict(
            rangeslider=dict(visible=True),
            type='date'
        ),
        legend=dict(orientation='h', y=1.02, x=0.5, xanchor='center')
    )
    

    return fig


def create_global_deaths_bubble_chart(all_country_data):
    """
    전 세계 국가별 백신 접종률 vs 백만명당 사망자 버블 차트.
    유럽의 경우 개별 국가로 분해하여 표시 (De-aggregation).
    """
    import plotly.express as px
    
    # 데이터 수집
    data_points = []
    
    for module_name, data in all_country_data.items():
        if data is None:
            continue
        
        display_name = data.get('country_name', module_name)
        country_df = data.get('country_df')
        metrics = data.get('metrics', {})
        
        if country_df is None or country_df.empty:
            continue
            
        # 모든 국가/지역을 동일하게 처리 (Aggregation)
        # metrics에서 이미 집계된 값을 가져옴
        population = metrics.get('total_population') or metrics.get('population')
        total_deaths = metrics.get('total_deaths')
        people_fully_vaccinated = metrics.get('people_fully_vaccinated')
        
        # 값이 없는 경우 latest_row에서 fallback (안전장치)
        if not population or not total_deaths:
            latest_row = country_df.iloc[-1]
            if not population:
                population = latest_row.get('population', 0)
            if not total_deaths:
                total_deaths = latest_row.get('total_deaths', 0)
            if not people_fully_vaccinated:
                 people_fully_vaccinated = latest_row.get('people_fully_vaccinated', 0)
        
        if population < 1: 
            continue

        data_points.append({
            'location': display_name,
            'population': population,
            'total_deaths': total_deaths,
            'people_fully_vaccinated': people_fully_vaccinated,
            'region': display_name # 색상/그룹용
        })
    
    if not data_points:
        return None
        
    df = pd.DataFrame(data_points)
    
    # 파생 지표 계산
    df['vaccination_rate'] = (df['people_fully_vaccinated'] / df['population'] * 100).fillna(0)
    df['deaths_per_million'] = (df['total_deaths'] / df['population'] * 1_000_000).fillna(0)
    df['population_millions'] = df['population'] / 1_000_000
    
    # 버블 차트 생성
    fig = px.scatter(
        df,
        x='vaccination_rate',
        y='deaths_per_million',
        size='population_millions',
        color='deaths_per_million', # 색상은 사망률로 통일 (유럽 스타일)
        hover_name='location',
        hover_data={
            'vaccination_rate': ':.1f',
            'deaths_per_million': ':.1f',
            'population_millions': ':.1f'
        },
        color_continuous_scale='Reds',
        size_max=50,
        title='전 세계 백신 접종률 vs 백만명당 사망자<br><sub>버블 크기 = 인구 | 색상 = 사망률</sub>',
        labels={
            'vaccination_rate': '백신 접종률 (%)',
            'deaths_per_million': '백만명당 사망자',
            'population_millions': '인구 (백만)'
        }
    )
    
    fig.update_layout(
        template='plotly_white',
        hovermode='closest',
        height=600,
        xaxis=dict(range=[0, 105])
    )
    
    fig.update_traces(
        marker=dict(
            line=dict(width=1, color='white')
        )
    )
    
    return fig
