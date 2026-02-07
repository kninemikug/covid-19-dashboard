"""
Common Visualizations Module

공통 시각화 함수 (모든 국가에서 사용)
USA 스타일의 프로페셔널한 차트 형식을 기반으로 하며, 모든 텍스트는 **한국어**로 제공됩니다.
"""

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

# ============================================================
# Common Styling
# ============================================================
CHART_THEME = {
    "template": "plotly_white",
    "height": 500,
    "font": {"family": "AppleGothic, Malgun Gothic, sans-serif", "size": 12}, # 한글 폰트 우선
    "title_font": {"size": 18, "color": "#2c3e50"},
    "hovermode": "x unified"
}

COLORS = {
    "cases": "#E84855",        # Red equivalent
    "deaths": "#2D3047",       # Dark
    "vaccinations": "#1B998B", # Green/Teal
    "rt": "#9b59b6",           # Purple
    "pre_vacc": "#E84855",
    "post_vacc": "#1B998B",
}

# 파동 배경색 (반투명 파스텔)
WAVE_COLORS = [
    "rgba(255,179,186,0.25)",
    "rgba(186,225,255,0.25)",
    "rgba(186,255,201,0.25)",
    "rgba(255,255,186,0.25)",
    "rgba(232,186,255,0.25)",
    "rgba(255,217,186,0.25)",
    "rgba(186,255,238,0.25)",
    "rgba(255,201,222,0.25)",
]

# 파동 바 색상
WAVE_BAR_COLORS = [
    "#E84855", "#3185FC", "#2ECC71", "#F9C22E",
    "#9B59B6", "#FF6B35", "#1B998B", "#D81E5B",
]


# ============================================================
# Chart 1: Dual Y-Axis Timeseries (확진자 vs 사망자)
# ============================================================
def create_dual_axis_timeseries(country_df, country_name):
    """
    확진자와 사망자를 이중 Y축 차트로 표시 (한글화).
    좌측 Y축: 일일 확진자 (7일 평균, 빨강)
    우측 Y축: 일일 사망자 (7일 평균, 짙은 남색)
    """
    fig = go.Figure()

    # Cases (Left Y-axis)
    fig.add_trace(go.Scatter(
        x=country_df['date'],
        y=country_df['new_cases_smoothed'],
        name='일일 확진자 (7일 평균)',
        line=dict(color=COLORS['cases'], width=2),
        fill='tozeroy',
        fillcolor='rgba(232, 72, 85, 0.2)',
        yaxis='y',
        hovertemplate='<b>확진자:</b> %{y:,.0f}명<extra></extra>'
    ))

    # Deaths (Right Y-axis)
    fig.add_trace(go.Scatter(
        x=country_df['date'],
        y=country_df['new_deaths_smoothed'],
        name='일일 사망자 (7일 평균)',
        line=dict(color=COLORS['deaths'], width=2, dash='dash'),
        yaxis='y2',
        hovertemplate='<b>사망자:</b> %{y:,.0f}명<extra></extra>'
    ))

    # Layout
    fig.update_layout(
        title=f'{country_name} - 일일 확진자 및 사망자 추이',
        yaxis=dict(
            title='일일 확진자 수',
            tickfont=dict(color=COLORS['cases']),
            side='left'
        ),
        yaxis2=dict(
            title='일일 사망자 수',
            tickfont=dict(color=COLORS['deaths']),
            overlaying='y',
            side='right'
        ),
        **CHART_THEME,

        # Range Selector (기간 선택)
        xaxis=dict(
            rangeslider=dict(visible=True),
            rangeselector=dict(
                buttons=list([
                    dict(count=1, label='1개월', step='month', stepmode='backward'),
                    dict(count=3, label='3개월', step='month', stepmode='backward'),
                    dict(count=6, label='6개월', step='month', stepmode='backward'),
                    dict(step='all', label='전체')
                ]),
                bgcolor='rgba(255, 255, 255, 0.8)',
            ),
            type='date'
        )
    )

    return fig


# ============================================================
# Chart 2: Vaccination Progress (백신 접종 진행률)
# ============================================================
def create_vaccination_progress(country_df, country_name):
    """
    백신 완전 접종자 수 누적 추이 영역 차트 (한글화).
    """
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=country_df['date'],
        y=country_df['people_fully_vaccinated'],
        name='완전 접종자',
        line=dict(color=COLORS['vaccinations'], width=2),
        fill='tozeroy',
        fillcolor='rgba(27, 153, 139, 0.3)',
        hovertemplate='<b>날짜:</b> %{x|%Y-%m-%d}<br>' +
                      '<b>접종완료:</b> %{y:,.0f}명<extra></extra>'
    ))

    fig.update_layout(
        title=f'{country_name} - 백신 접종 진행 현황',
        xaxis_title='날짜',
        yaxis_title='누적 완전 접종자 수 (명)',
        yaxis=dict(tickformat=','),
        xaxis=dict(
            rangeslider=dict(visible=True),
            type='date'
        ),
        **CHART_THEME
    )

    return fig


# ============================================================
# Chart 3: Reproduction Rate (감염재생산지수 Rt)
# ============================================================
def create_reproduction_rate_chart(country_df, country_name):
    """
    감염재생산지수(Rt) 추이 및 기준선(1.0) 표시 (한글화).
    """
    fig = go.Figure()

    # Rt line
    fig.add_trace(go.Scatter(
        x=country_df['date'],
        y=country_df['reproduction_rate'],
        name='감염재생산지수 (Rt)',
        line=dict(color=COLORS['rt'], width=2),
        fill='tozeroy',
        fillcolor='rgba(155, 89, 182, 0.2)',
        hovertemplate='<b>Rt:</b> %{y:.2f}<extra></extra>'
    ))

    # Rt=1.0 critical line
    fig.add_hline(
        y=1.0,
        line_dash='dash',
        line_color='red',
        line_width=2,
        annotation_text='Rt = 1.0 (유행 확산 기준)',
        annotation_position='bottom right',
        annotation=dict(
            font=dict(size=12, color='red'),
            bgcolor='rgba(255, 255, 255, 0.8)'
        )
    )

    fig.update_layout(
        title=f'{country_name} - 감염재생산지수 (Rt) 추이',
        xaxis_title='날짜',
        yaxis_title='Rt 값',
        xaxis=dict(
            rangeslider=dict(visible=True),
            type='date'
        ),
        **CHART_THEME
    )

    return fig


# ============================================================
# Chart 4: Case Fatality Rate (치명률 CFR)
# ============================================================
def create_case_fatality_rate_chart(country_df, country_name):
    """
    치명률(CFR) 추이 차트 (한글화).
    확진자가 적은 초기 구간(50명 미만)의 노이즈는 0 처리됨.
    """
    country_df_copy = country_df.copy()
    
    # 노이즈 제거된 CFR 계산
    country_df_copy['cfr'] = 0.0
    mask = country_df_copy['total_cases'] > 50
    country_df_copy.loc[mask, 'cfr'] = (
        country_df_copy.loc[mask, 'total_deaths'] / country_df_copy.loc[mask, 'total_cases'] * 100
    ).fillna(0)

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=country_df_copy['date'],
        y=country_df_copy['cfr'],
        name='치명률 (%)',
        line=dict(color='#e67e22', width=2),
        fill='tozeroy',
        fillcolor='rgba(230, 126, 34, 0.2)',
        hovertemplate='<b>날짜:</b> %{x|%Y-%m-%d}<br>' +
                      '<b>치명률:</b> %{y:.2f}%<extra></extra>'
    ))

    fig.update_layout(
        title=f'{country_name} - 치명률 (CFR) 추이',
        xaxis_title='날짜',
        yaxis_title='치명률 (%)',
        yaxis=dict(ticksuffix='%'),
        xaxis=dict(
            rangeslider=dict(visible=True),
            type='date'
        ),
        **CHART_THEME
    )

    return fig


# ============================================================
# Chart 5: Wave Detection Timeline (파동 감지 타임라인 - 신규)
# ============================================================
def create_wave_detection_chart(country_df, waves_df, country_name):
    """
    일별 확진자 추이 위에 감지된 파동 구간을 색상 영역으로 표시 (한글화).
    """
    fig = go.Figure()

    # 일별 확진자 라인
    fig.add_trace(go.Scatter(
        x=country_df['date'],
        y=country_df['new_cases_smoothed'],
        name='일일 확진자 (7일 평균)',
        line=dict(color=COLORS['cases'], width=2),
        hovertemplate='<b>날짜:</b> %{x|%Y-%m-%d}<br>'
                      '<b>확진자:</b> %{y:,.0f}명<extra></extra>'
    ))

    # 각 파동 구간 배경 + 피크 어노테이션
    for _, wave in waves_df.iterrows():
        idx = int(wave['wave_number']) - 1
        bg_color = WAVE_COLORS[idx % len(WAVE_COLORS)]
        bar_color = WAVE_BAR_COLORS[idx % len(WAVE_BAR_COLORS)]

        fig.add_vrect(
            x0=str(wave['start_date']), x1=str(wave['end_date']),
            fillcolor=bg_color,
            layer="below", line_width=0,
        )

        fig.add_trace(go.Scatter(
            x=[wave['peak_date']],
            y=[wave['peak_daily_cases']],
            mode='markers+text',
            marker=dict(size=10, color=bar_color, symbol='diamond'),
            text=[f"{int(wave['wave_number'])}차 유행"],
            textposition='top center',
            textfont=dict(size=11, color=bar_color, weight="bold"),
            showlegend=False,
            hovertemplate=(
                f"<b>{int(wave['wave_number'])}차 대유행</b><br>"
                f"정점: %{{y:,.0f}}명<br>"
                f"지속기간: {int(wave['duration_days'])}일<extra></extra>"
            )
        ))

    fig.update_layout(
        title=f'{country_name} - COVID-19 확산 파동(Wave) 감지',
        xaxis_title='날짜',
        yaxis_title='일일 확진자 (7일 평균)',
        yaxis=dict(tickformat=','),
        xaxis=dict(
            rangeslider=dict(visible=True),
            rangeselector=dict(
                buttons=list([
                    dict(count=6, label='6개월', step='month', stepmode='backward'),
                    dict(count=1, label='1년', step='year', stepmode='backward'),
                    dict(step='all', label='전체')
                ]),
                bgcolor='rgba(255,255,255,0.8)',
            ),
            type='date'
        ),
        **CHART_THEME
    )

    return fig


# ============================================================
# Chart 6: Wave Comparison (파동별 비교 분석 - 신규)
# ============================================================
def create_wave_comparison_chart(waves_df, country_name):
    """
    파동별 핵심 지표(피크 확진자, 총 사망자)를 비교하는 막대 차트 (한글화).
    """
    wave_labels = [f"{int(w)}차" for w in waves_df['wave_number']]
    n_waves = len(waves_df)
    colors = [WAVE_BAR_COLORS[i % len(WAVE_BAR_COLORS)] for i in range(n_waves)]

    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=('유행 차수별 피크 확진자 수', '유행 차수별 총 사망자 수'),
        vertical_spacing=0.15
    )

    # 상단: 피크 확진자
    fig.add_trace(go.Bar(
        x=wave_labels,
        y=waves_df['peak_daily_cases'],
        marker_color=colors,
        text=[f"{v:,.0f}" for v in waves_df['peak_daily_cases']],
        textposition='outside',
        name='피크 확진자',
        showlegend=False,
        hovertemplate='<b>%{x}</b><br>정점: %{y:,.0f}명<extra></extra>'
    ), row=1, col=1)

    # 하단: 총 사망자 + 지속 일수
    death_texts = [
        f"{int(d):,}명 ({int(dur)}일)"
        for d, dur in zip(waves_df['total_deaths'], waves_df['duration_days'])
    ]
    fig.add_trace(go.Bar(
        x=wave_labels,
        y=waves_df['total_deaths'],
        marker_color=colors,
        text=death_texts,
        textposition='outside',
        name='사망자',
        showlegend=False,
        hovertemplate='<b>%{x}</b><br>사망자: %{y:,.0f}명<extra></extra>'
    ), row=2, col=1)

    # 파동 기간 표시
    period_annotations = []
    for i, (_, wave) in enumerate(waves_df.iterrows()):
        start_str = wave['start_date'].strftime('%y.%m')
        end_str = wave['end_date'].strftime('%y.%m')
        period_annotations.append(dict(
            x=wave_labels[i], y=-0.05,
            xref='x2', yref='paper',
            text=f"{start_str}~{end_str}",
            showarrow=False,
            font=dict(size=9, color='gray')
        ))

    fig.update_layout(
        title=f'{country_name} - 유행 파동(Wave)별 규모 비교',
        height=600,
        template='plotly_white',
        annotations=period_annotations,
        font={"family": "AppleGothic, Malgun Gothic, sans-serif", "size": 12},
        title_font={"size": 18, "color": "#2c3e50"},
    )

    fig.update_yaxes(tickformat=',', row=1, col=1)
    fig.update_yaxes(tickformat=',', row=2, col=1)

    return fig


# ============================================================
# Chart 7: Vaccination Impact (백신 접종 효과 분석 - 신규)
# ============================================================
def create_vaccination_impact_chart(vacc_stats, country_name):
    """
    백신 접종 전/후 핵심 지표 변화 비교 (한글화).
    """
    pre = vacc_stats['pre_vaccination']
    post = vacc_stats['post_vaccination']

    metrics = ['치명률(CFR) (%)', '일평균 사망자 (명)', '일평균 확진자 (명)']
    pre_vals = [pre['cfr'], pre['avg_daily_deaths'], pre['avg_daily_cases']]
    post_vals = [post['cfr'], post['avg_daily_deaths'], post['avg_daily_cases']]

    fig = make_subplots(
        rows=1, cols=3,
        subplot_titles=metrics,
        horizontal_spacing=0.12
    )

    for i, (metric, pv, av) in enumerate(zip(metrics, pre_vals, post_vals)):
        col = i + 1
        change_pct = ((av - pv) / pv * 100) if pv > 0 else 0

        # Bar Chart
        fig.add_trace(go.Bar(
            x=['접종 전', '접종 후'],
            y=[pv, av],
            marker_color=[COLORS['pre_vacc'], COLORS['post_vacc']],
            text=[f"{pv:,.1f}", f"{av:,.1f}"],
            textposition='outside',
            showlegend=False,
            hovertemplate=f'<b>{metric}</b><br>%{{x}}: %{{y:,.2f}}<extra></extra>'
        ), row=1, col=col)

        # Arrow Annotation
        arrow = "↓" if change_pct < 0 else "↑"
        color = "#1B998B" if change_pct < 0 else "#E84855"
        fig.add_annotation(
            x=0.5, y=max(pv, av) * 1.3,
            xref=f'x{col}', yref=f'y{col}',
            text=f"{arrow} {abs(change_pct):.1f}%",
            showarrow=False,
            font=dict(size=14, color=color, family="Arial Black")
        )

    vacc_date_str = vacc_stats['vacc_start_date'].strftime('%Y-%m-%d')

    fig.update_layout(
        title=f'{country_name} - 백신 접종 전/후 지표 변화 (기준일: {vacc_date_str})',
        height=450,
        template='plotly_white',
        font={"family": "AppleGothic, Malgun Gothic, sans-serif", "size": 12},
        title_font={"size": 16, "color": "#2c3e50"},
    )

    return fig


# ============================================================
# Chart 8: Cases-Deaths Decoupling (디커플링 분석 - 신규)
# ============================================================
def create_cases_deaths_decoupling_chart(country_df, vacc_start_date, country_name):
    """
    확진자-사망자 간 디커플링(괴리) 현상 시각화 (한글화).
    """
    fig = go.Figure()

    date_min_str = str(country_df['date'].min())
    date_max_str = str(country_df['date'].max())
    vacc_str = str(vacc_start_date)

    # 접종 전/후 배경
    fig.add_vrect(
        x0=date_min_str, x1=vacc_str,
        fillcolor="rgba(232,72,85,0.07)", layer="below", line_width=0,
        annotation_text="백신 접종 전", annotation_position="top left",
        annotation=dict(font=dict(size=11, color=COLORS['pre_vacc']))
    )
    fig.add_vrect(
        x0=vacc_str, x1=date_max_str,
        fillcolor="rgba(27,153,139,0.07)", layer="below", line_width=0,
        annotation_text="백신 접종 후", annotation_position="top left",
        annotation=dict(font=dict(size=11, color=COLORS['post_vacc']))
    )

    # 확진자 (좌축)
    fig.add_trace(go.Scatter(
        x=country_df['date'],
        y=country_df['new_cases_smoothed'],
        name='신규 확진자',
        line=dict(color=COLORS['cases'], width=2),
        fill='tozeroy',
        fillcolor='rgba(232,72,85,0.15)',
        yaxis='y',
        hovertemplate='<b>확진자:</b> %{y:,.0f}명<extra></extra>'
    ))

    # 사망자 (우축)
    fig.add_trace(go.Scatter(
        x=country_df['date'],
        y=country_df['new_deaths_smoothed'],
        name='신규 사망자',
        line=dict(color=COLORS['deaths'], width=2, dash='dash'),
        yaxis='y2',
        hovertemplate='<b>사망자:</b> %{y:,.0f}명<extra></extra>'
    ))

    # 접종 시작 수직선
    fig.add_shape(
        type='line',
        x0=vacc_str, x1=vacc_str,
        y0=0, y1=1,
        yref='paper',
        line=dict(dash='dot', color='#1B998B', width=2),
    )
    fig.add_annotation(
        x=vacc_str, y=1.05, yref='paper',
        text=f"접종 본격화 ({vacc_start_date.strftime('%Y-%m-%d')})",
        showarrow=False,
        font=dict(size=11, color='#1B998B'),
        bgcolor='rgba(255,255,255,0.8)',
    )

    fig.update_layout(
        title=f'{country_name} - 확진자 vs 사망자 탈동조화(Decoupling) 분석',
        yaxis=dict(
            title=dict(text='일일 확진자 수', font=dict(color=COLORS['cases'])),
            tickfont=dict(color=COLORS['cases']),
            tickformat=',',
            side='left'
        ),
        yaxis2=dict(
            title=dict(text='일일 사망자 수', font=dict(color=COLORS['deaths'])),
            tickfont=dict(color=COLORS['deaths']),
            tickformat=',',
            overlaying='y',
            side='right'
        ),
        xaxis=dict(
            rangeslider=dict(visible=True),
            rangeselector=dict(
                buttons=list([
                    dict(count=6, label='6개월', step='month', stepmode='backward'),
                    dict(count=1, label='1년', step='year', stepmode='backward'),
                    dict(step='all', label='전체')
                ]),
                bgcolor='rgba(255,255,255,0.8)',
            ),
            type='date'
        ),
        **CHART_THEME
    )

    return fig
