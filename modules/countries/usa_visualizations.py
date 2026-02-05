"""
USA-specific COVID-19 Visualizations Module

Professional Plotly charts for United States data analysis:
- Dual Y-axis timeseries (cases vs deaths)
- Vaccination progress tracking
- Vaccine manufacturer comparison
- Reproduction rate (Rt) monitoring
- Comprehensive 4-panel dashboard
- Case fatality rate trends
"""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd

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
    "cases": "#3498db",        # Blue
    "deaths": "#e74c3c",       # Red
    "vaccinations": "#2ecc71", # Green
    "rt": "#9b59b6",           # Purple
    "pfizer": "#1e90ff",
    "moderna": "#ff6347",
    "jj": "#32cd32"
}


# ============================================================
# Chart 1: Dual Y-Axis Timeseries (Cases vs Deaths)
# ============================================================
def create_dual_axis_timeseries(country_df, country_name):
    """
    Display cases and deaths on separate Y-axes.

    Left Y-axis: new_cases_smoothed (blue)
    Right Y-axis: new_deaths_smoothed (red)

    Features:
    - Range selector (1M, 3M, 6M, All)
    - Fill area under lines
    - Unified hover tooltip
    """
    fig = go.Figure()

    # Cases (Left Y-axis)
    fig.add_trace(go.Scatter(
        x=country_df['date'],
        y=country_df['new_cases_smoothed'],
        name='New Cases (7-day Avg)',
        line=dict(color=COLORS['cases'], width=2),
        fill='tozeroy',
        fillcolor='rgba(52, 152, 219, 0.2)',
        yaxis='y',
        hovertemplate='<b>Cases:</b> %{y:,.0f}<extra></extra>'
    ))

    # Deaths (Right Y-axis)
    fig.add_trace(go.Scatter(
        x=country_df['date'],
        y=country_df['new_deaths_smoothed'],
        name='New Deaths (7-day Avg)',
        line=dict(color=COLORS['deaths'], width=2, dash='dash'),
        yaxis='y2',
        hovertemplate='<b>Deaths:</b> %{y:,.0f}<extra></extra>'
    ))

    # Layout
    fig.update_layout(
        title=f'{country_name} - Daily Cases vs Deaths',
        yaxis=dict(
            title='New Cases',
            titlefont=dict(color=COLORS['cases']),
            tickfont=dict(color=COLORS['cases']),
            side='left'
        ),
        yaxis2=dict(
            title='New Deaths',
            titlefont=dict(color=COLORS['deaths']),
            tickfont=dict(color=COLORS['deaths']),
            overlaying='y',
            side='right'
        ),
        **CHART_THEME,

        # Range Selector
        xaxis=dict(
            rangeselector=dict(
                buttons=list([
                    dict(count=1, label='1M', step='month', stepmode='backward'),
                    dict(count=3, label='3M', step='month', stepmode='backward'),
                    dict(count=6, label='6M', step='month', stepmode='backward'),
                    dict(step='all', label='All')
                ]),
                bgcolor='rgba(255, 255, 255, 0.8)',
                activecolor='rgba(52, 152, 219, 0.3)'
            ),
            rangeslider=dict(visible=False),
            type='date'
        )
    )

    return fig


# ============================================================
# Chart 2: Vaccination Progress (Area Chart)
# ============================================================
def create_vaccination_progress(country_df, country_name):
    """
    Cumulative vaccination progress over time.

    Shows people_fully_vaccinated as an area chart with:
    - Smooth green gradient
    - Custom hover tooltip
    - Clean formatting
    """
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=country_df['date'],
        y=country_df['people_fully_vaccinated'],
        name='Fully Vaccinated',
        line=dict(color=COLORS['vaccinations'], width=2),
        fill='tozeroy',
        fillcolor='rgba(46, 204, 113, 0.3)',
        hovertemplate='<b>Date:</b> %{x|%Y-%m-%d}<br>' +
                      '<b>Vaccinated:</b> %{y:,.0f}<extra></extra>'
    ))

    fig.update_layout(
        title=f'{country_name} - Vaccination Progress',
        xaxis_title='Date',
        yaxis_title='People Fully Vaccinated',
        yaxis=dict(tickformat=','),
        **CHART_THEME
    )

    return fig


# ============================================================
# Chart 3: Vaccine Manufacturer Comparison (Bar Chart)
# ============================================================
def create_vaccine_manufacturer_comparison(vaccine_data):
    """
    Compare total vaccinations by manufacturer.

    Args:
        vaccine_data: List of dicts with 'vaccine' and 'total' keys

    Returns:
        Plotly bar chart or None if no data
    """
    if not vaccine_data or len(vaccine_data) == 0:
        return None

    df = pd.DataFrame(vaccine_data)

    fig = px.bar(
        df,
        x='vaccine',
        y='total',
        color='vaccine',
        title='Vaccinations by Manufacturer',
        labels={'total': 'Total Vaccinations', 'vaccine': 'Manufacturer'},
        text='total',
        color_discrete_sequence=[COLORS['pfizer'], COLORS['moderna'], COLORS['jj']]
    )

    fig.update_traces(
        texttemplate='%{text:,.0f}',
        textposition='outside'
    )

    fig.update_layout(
        **CHART_THEME,
        showlegend=False,
        xaxis_tickangle=-45
    )

    return fig


# ============================================================
# Chart 4: Reproduction Rate (Rt) Tracking
# ============================================================
def create_reproduction_rate_chart(country_df, country_name):
    """
    Track Rt value with critical threshold line.

    Features:
    - Rt=1.0 baseline (red dashed line)
    - Purple area fill
    - Clear threshold annotations
    """
    fig = go.Figure()

    # Rt line
    fig.add_trace(go.Scatter(
        x=country_df['date'],
        y=country_df['reproduction_rate'],
        name='Reproduction Rate (Rt)',
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
        annotation_text='Rt = 1.0 (Critical Threshold)',
        annotation_position='bottom right',
        annotation=dict(
            font=dict(size=12, color='red'),
            bgcolor='rgba(255, 255, 255, 0.8)'
        )
    )

    fig.update_layout(
        title=f'{country_name} - Reproduction Rate (Rt)',
        xaxis_title='Date',
        yaxis_title='Rt Value',
        **CHART_THEME
    )

    return fig


# ============================================================
# Chart 5: Comprehensive 4-Panel Dashboard (Subplots)
# ============================================================
def create_comprehensive_dashboard(country_df, country_name):
    """
    4-panel comprehensive COVID-19 dashboard.

    Panels:
    1. Top-Left: Daily new cases
    2. Top-Right: Daily new deaths
    3. Bottom-Left: Vaccination progress
    4. Bottom-Right: Reproduction rate (Rt)

    All panels share X-axis (date) for easy comparison.
    """
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            'Daily New Cases',
            'Daily New Deaths',
            'Vaccination Progress',
            'Reproduction Rate (Rt)'
        ),
        specs=[
            [{"type": "scatter"}, {"type": "scatter"}],
            [{"type": "scatter"}, {"type": "scatter"}]
        ],
        vertical_spacing=0.12,
        horizontal_spacing=0.10
    )

    # Panel 1: Cases
    fig.add_trace(
        go.Scatter(
            x=country_df['date'],
            y=country_df['new_cases_smoothed'],
            name='New Cases',
            line=dict(color=COLORS['cases'], width=2),
            fill='tozeroy',
            fillcolor='rgba(52, 152, 219, 0.2)',
            showlegend=True
        ),
        row=1, col=1
    )

    # Panel 2: Deaths
    fig.add_trace(
        go.Scatter(
            x=country_df['date'],
            y=country_df['new_deaths_smoothed'],
            name='New Deaths',
            line=dict(color=COLORS['deaths'], width=2),
            fill='tozeroy',
            fillcolor='rgba(231, 76, 60, 0.2)',
            showlegend=True
        ),
        row=1, col=2
    )

    # Panel 3: Vaccinations
    fig.add_trace(
        go.Scatter(
            x=country_df['date'],
            y=country_df['people_fully_vaccinated'],
            name='Vaccinated',
            line=dict(color=COLORS['vaccinations'], width=2),
            fill='tozeroy',
            fillcolor='rgba(46, 204, 113, 0.2)',
            showlegend=True
        ),
        row=2, col=1
    )

    # Panel 4: Rt
    fig.add_trace(
        go.Scatter(
            x=country_df['date'],
            y=country_df['reproduction_rate'],
            name='Rt',
            line=dict(color=COLORS['rt'], width=2),
            showlegend=True
        ),
        row=2, col=2
    )

    # Rt=1 baseline on Panel 4
    fig.add_hline(
        y=1.0,
        line_dash='dash',
        line_color='red',
        line_width=1,
        row=2, col=2
    )

    # Update axes
    fig.update_xaxes(title_text='Date', row=2, col=1)
    fig.update_xaxes(title_text='Date', row=2, col=2)
    fig.update_yaxes(title_text='Cases', row=1, col=1)
    fig.update_yaxes(title_text='Deaths', row=1, col=2)
    fig.update_yaxes(title_text='People', row=2, col=1)
    fig.update_yaxes(title_text='Rt', row=2, col=2)

    fig.update_layout(
        title_text=f'{country_name} - Comprehensive COVID-19 Dashboard',
        height=800,
        template='plotly_white',
        showlegend=True,
        hovermode='x unified'
    )

    return fig


# ============================================================
# Chart 6: Case Fatality Rate Trend
# ============================================================
def create_case_fatality_rate_chart(country_df, country_name):
    """
    Case fatality rate (CFR) over time.

    CFR = (total_deaths / total_cases) * 100

    Shows trend in orange area chart with:
    - Percentage formatting
    - Clean hover tooltip
    """
    # Calculate CFR
    country_df_copy = country_df.copy()
    country_df_copy['cfr'] = (
        country_df_copy['total_deaths'] / country_df_copy['total_cases'] * 100
    ).fillna(0)

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=country_df_copy['date'],
        y=country_df_copy['cfr'],
        name='Case Fatality Rate (%)',
        line=dict(color='#e67e22', width=2),
        fill='tozeroy',
        fillcolor='rgba(230, 126, 34, 0.2)',
        hovertemplate='<b>Date:</b> %{x|%Y-%m-%d}<br>' +
                      '<b>CFR:</b> %{y:.2f}%<extra></extra>'
    ))

    fig.update_layout(
        title=f'{country_name} - Case Fatality Rate Trend',
        xaxis_title='Date',
        yaxis_title='CFR (%)',
        yaxis=dict(ticksuffix='%'),
        **CHART_THEME
    )

    return fig
