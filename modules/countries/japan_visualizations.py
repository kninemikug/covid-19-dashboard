"""
Japan-specific COVID-19 Visualizations Module

Plotly charts for Japan data analysis:
- Wave detection timeline (파동 감지 타임라인)
- Wave comparison bar chart (파동별 비교)
- Pre/Post vaccination impact (백신 전/후 비교)
- Cases-Deaths decoupling analysis (확진-사망 디커플링)
"""

import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ============================================================
# Common Styling
# ============================================================
CHART_THEME = {
    "template": "plotly_white",
    "height": 500,
    "font": {"family": "Arial, sans-serif", "size": 12},
    "title_font": {"size": 18, "color": "#2c3e50"},
    "hovermode": "x unified"
}

COLORS = {
    "cases": "#E84855",
    "deaths": "#2D3047",
    "vaccinations": "#1B998B",
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
# Chart 1: Wave Detection Timeline (파동 감지 타임라인)
# ============================================================
def create_wave_detection_chart(country_df, waves_df, country_name):
    """
    일별 확진자 추이 위에 감지된 파동 구간을 색상 영역으로 표시.
    각 파동의 피크 지점에 마커와 어노테이션 추가.
    """
    fig = go.Figure()

    # 일별 확진자 라인
    fig.add_trace(go.Scatter(
        x=country_df['date'],
        y=country_df['new_cases_smoothed'],
        name='Daily Cases (7-day Avg)',
        line=dict(color=COLORS['cases'], width=2),
        hovertemplate='<b>Date:</b> %{x|%Y-%m-%d}<br>'
                      '<b>Cases:</b> %{y:,.0f}<extra></extra>'
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
            text=[f"Wave {int(wave['wave_number'])}"],
            textposition='top center',
            textfont=dict(size=10, color=bar_color),
            showlegend=False,
            hovertemplate=(
                f"<b>Wave {int(wave['wave_number'])}</b><br>"
                f"Peak: %{{y:,.0f}}<br>"
                f"Duration: {int(wave['duration_days'])}days<extra></extra>"
            )
        ))

    fig.update_layout(
        title=f'{country_name} - COVID-19 Wave Detection (파동 감지)',
        xaxis_title='Date',
        yaxis_title='New Cases (7-day Avg)',
        yaxis=dict(tickformat=','),
        xaxis=dict(
            rangeselector=dict(
                buttons=list([
                    dict(count=3, label='3M', step='month', stepmode='backward'),
                    dict(count=6, label='6M', step='month', stepmode='backward'),
                    dict(count=1, label='1Y', step='year', stepmode='backward'),
                    dict(step='all', label='All')
                ]),
                bgcolor='rgba(255,255,255,0.8)',
            ),
            type='date'
        ),
        **CHART_THEME
    )

    return fig


# ============================================================
# Chart 2: Wave Comparison (파동별 비교 분석)
# ============================================================
def create_wave_comparison_chart(waves_df, country_name):
    """
    파동별 핵심 지표를 2행 서브플롯 막대 차트로 비교.
    Top: 피크 일일 확진자 수
    Bottom: 총 사망자 수 (+ 지속 일수 텍스트)
    """
    wave_labels = [f"W{int(w)}" for w in waves_df['wave_number']]
    n_waves = len(waves_df)
    colors = [WAVE_BAR_COLORS[i % len(WAVE_BAR_COLORS)] for i in range(n_waves)]

    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=('Peak Daily Cases (피크 일일 확진)', 'Total Deaths (총 사망자)'),
        vertical_spacing=0.15
    )

    # 상단: 피크 확진자
    fig.add_trace(go.Bar(
        x=wave_labels,
        y=waves_df['peak_daily_cases'],
        marker_color=colors,
        text=[f"{v:,.0f}" for v in waves_df['peak_daily_cases']],
        textposition='outside',
        name='Peak Cases',
        showlegend=False,
        hovertemplate='<b>%{x}</b><br>Peak: %{y:,.0f}<extra></extra>'
    ), row=1, col=1)

    # 하단: 총 사망자 + 지속 일수
    death_texts = [
        f"{int(d):,} ({int(dur)}days)"
        for d, dur in zip(waves_df['total_deaths'], waves_df['duration_days'])
    ]
    fig.add_trace(go.Bar(
        x=wave_labels,
        y=waves_df['total_deaths'],
        marker_color=colors,
        text=death_texts,
        textposition='outside',
        name='Deaths',
        showlegend=False,
        hovertemplate='<b>%{x}</b><br>Deaths: %{y:,.0f}<extra></extra>'
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
        title=f'{country_name} - Wave Comparison (파동별 비교)',
        height=600,
        template='plotly_white',
        annotations=period_annotations,
        font={"family": "Arial, sans-serif", "size": 12},
        title_font={"size": 18, "color": "#2c3e50"},
    )

    fig.update_yaxes(tickformat=',', row=1, col=1)
    fig.update_yaxes(tickformat=',', row=2, col=1)

    return fig


# ============================================================
# Chart 3: Pre/Post Vaccination Impact (백신 전/후 비교)
# ============================================================
def create_vaccination_impact_chart(vacc_stats, country_name):
    """
    백신 접종 전/후 핵심 지표를 그룹 막대 차트로 비교.
    비교 지표: CFR(%), 일평균 사망자, 일평균 확진자
    변화율(%) 어노테이션 포함.
    """
    pre = vacc_stats['pre_vaccination']
    post = vacc_stats['post_vaccination']

    metrics = ['CFR (%)', 'Avg Daily Deaths', 'Avg Daily Cases']
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

        fig.add_trace(go.Bar(
            x=['Pre-Vacc', 'Post-Vacc'],
            y=[pv, av],
            marker_color=[COLORS['pre_vacc'], COLORS['post_vacc']],
            text=[f"{pv:,.1f}", f"{av:,.1f}"],
            textposition='outside',
            showlegend=False,
            hovertemplate=f'<b>{metric}</b><br>%{{x}}: %{{y:,.2f}}<extra></extra>'
        ), row=1, col=col)

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
        title=f'{country_name} - Vaccination Impact (백신 전/후 비교, 기준: {vacc_date_str})',
        height=450,
        template='plotly_white',
        font={"family": "Arial, sans-serif", "size": 12},
        title_font={"size": 16, "color": "#2c3e50"},
    )

    return fig


# ============================================================
# Chart 4: Cases-Deaths Decoupling (확진-사망 디커플링)
# ============================================================
def create_cases_deaths_decoupling_chart(country_df, vacc_start_date, country_name):
    """
    백신 접종 이후 확진자-사망자 간 디커플링 현상을 시각화.
    좌 Y축: 확진자, 우 Y축: 사망자, 백신 접종 시작일 수직선.
    접종 전/후 배경색으로 구간 구분.
    """
    fig = go.Figure()

    # Timestamp → 문자열 변환 (plotly vrect/vline 호환)
    date_min_str = str(country_df['date'].min())
    date_max_str = str(country_df['date'].max())
    vacc_str = str(vacc_start_date)

    # 접종 전/후 배경
    fig.add_vrect(
        x0=date_min_str, x1=vacc_str,
        fillcolor="rgba(232,72,85,0.07)", layer="below", line_width=0,
        annotation_text="Pre-Vaccination", annotation_position="top left",
        annotation=dict(font=dict(size=11, color=COLORS['pre_vacc']))
    )
    fig.add_vrect(
        x0=vacc_str, x1=date_max_str,
        fillcolor="rgba(27,153,139,0.07)", layer="below", line_width=0,
        annotation_text="Post-Vaccination", annotation_position="top left",
        annotation=dict(font=dict(size=11, color=COLORS['post_vacc']))
    )

    # 확진자 (좌축)
    fig.add_trace(go.Scatter(
        x=country_df['date'],
        y=country_df['new_cases_smoothed'],
        name='New Cases (7-day Avg)',
        line=dict(color=COLORS['cases'], width=2),
        fill='tozeroy',
        fillcolor='rgba(232,72,85,0.15)',
        yaxis='y',
        hovertemplate='<b>Cases:</b> %{y:,.0f}<extra></extra>'
    ))

    # 사망자 (우축)
    fig.add_trace(go.Scatter(
        x=country_df['date'],
        y=country_df['new_deaths_smoothed'],
        name='New Deaths (7-day Avg)',
        line=dict(color=COLORS['deaths'], width=2, dash='dash'),
        yaxis='y2',
        hovertemplate='<b>Deaths:</b> %{y:,.0f}<extra></extra>'
    ))

    # 접종 시작 수직선 (add_shape + add_annotation 분리)
    fig.add_shape(
        type='line',
        x0=vacc_str, x1=vacc_str,
        y0=0, y1=1,
        yref='paper',
        line=dict(dash='dot', color='#1B998B', width=2),
    )
    fig.add_annotation(
        x=vacc_str, y=1.05, yref='paper',
        text=f"Vaccination Start ({vacc_start_date.strftime('%Y-%m-%d')})",
        showarrow=False,
        font=dict(size=11, color='#1B998B'),
        bgcolor='rgba(255,255,255,0.8)',
    )

    fig.update_layout(
        title=f'{country_name} - Cases vs Deaths Decoupling (확진-사망 디커플링)',
        yaxis=dict(
            title=dict(text='New Cases', font=dict(color=COLORS['cases'])),
            tickfont=dict(color=COLORS['cases']),
            tickformat=',',
            side='left'
        ),
        yaxis2=dict(
            title=dict(text='New Deaths', font=dict(color=COLORS['deaths'])),
            tickfont=dict(color=COLORS['deaths']),
            tickformat=',',
            overlaying='y',
            side='right'
        ),
        xaxis=dict(
            rangeselector=dict(
                buttons=list([
                    dict(count=6, label='6M', step='month', stepmode='backward'),
                    dict(count=1, label='1Y', step='year', stepmode='backward'),
                    dict(step='all', label='All')
                ]),
                bgcolor='rgba(255,255,255,0.8)',
            ),
            type='date'
        ),
        **CHART_THEME
    )

    return fig
