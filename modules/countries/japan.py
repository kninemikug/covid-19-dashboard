import pandas as pd
from .japan_visualizations import (
    create_wave_detection_chart,
    create_wave_comparison_chart,
    create_vaccination_impact_chart,
    create_cases_deaths_decoupling_chart
)


# =============================================================
# 파동(Wave) 감지 알고리즘
# 사용 pandas 기법: rolling, diff, idxmin, idxmax, iloc, loc, Boolean indexing
# =============================================================
def _detect_waves(country_df):
    """
    COVID-19 확산 파동을 피크(peak) 기반으로 자동 감지한다.

    알고리즘:
    1. new_cases_smoothed에 21일 이동평균을 추가 적용 (rolling)
    2. 변화율(velocity)을 계산하여 양→음 전환점 = 피크 (diff)
    3. 30일 내 근접 피크를 병합하여 중복 제거
    4. 각 피크 사이의 최저점(trough)을 파동 경계로 설정 (idxmin)
    5. trough-to-trough 구간별 통계 집계
    """
    df = country_df[['date', 'new_cases_smoothed', 'new_cases', 'new_deaths']].copy()
    df = df.sort_values('date').reset_index(drop=True)

    # 21일 centered 이동평균으로 추가 평활화
    df['trend'] = (
        df['new_cases_smoothed']
        .rolling(21, center=True, min_periods=7)
        .mean()
        .fillna(0)
    )

    # 변화율 (velocity = 추세의 1차 미분)
    df['velocity'] = df['trend'].diff()

    # 최소 피크 기준 (일일 1,000명 이상만 유의미한 파동)
    min_peak = 1000

    # 피크 탐지: velocity가 양→음으로 전환 + trend > min_peak
    peak_indices = []
    for i in range(1, len(df) - 1):
        if (df.loc[i, 'trend'] > min_peak
                and df.loc[i - 1, 'velocity'] > 0
                and df.loc[i, 'velocity'] <= 0):
            peak_indices.append(i)

    # 30일 내 근접 피크 병합 (더 높은 피크만 유지)
    merged_peaks = []
    for p in peak_indices:
        if merged_peaks and (df.loc[p, 'date'] - df.loc[merged_peaks[-1], 'date']).days < 30:
            if df.loc[p, 'trend'] > df.loc[merged_peaks[-1], 'trend']:
                merged_peaks[-1] = p
        else:
            merged_peaks.append(p)

    # 각 피크 주변의 trough(최저점)를 경계로 파동 정의
    waves = []
    for wave_num, peak_idx in enumerate(merged_peaks):
        # 이전 trough (시작점)
        search_start = merged_peaks[wave_num - 1] if wave_num > 0 else 0
        start_idx = int(df.loc[search_start:peak_idx, 'trend'].idxmin())

        # 이후 trough (끝점)
        search_end = merged_peaks[wave_num + 1] if wave_num < len(merged_peaks) - 1 else len(df) - 1
        end_idx = int(df.loc[peak_idx:search_end, 'trend'].idxmin())

        wave_data = df.loc[start_idx:end_idx]
        duration = (df.loc[end_idx, 'date'] - df.loc[start_idx, 'date']).days

        if duration < 7:
            continue

        waves.append({
            'wave_number': wave_num + 1,
            'start_date': df.loc[start_idx, 'date'],
            'peak_date': df.loc[peak_idx, 'date'],
            'end_date': df.loc[end_idx, 'date'],
            'peak_daily_cases': float(wave_data['new_cases_smoothed'].max()),
            'total_cases': float(wave_data['new_cases'].sum()),
            'total_deaths': float(wave_data['new_deaths'].sum()),
            'duration_days': duration,
            'avg_daily_cases': float(wave_data['new_cases'].mean()),
        })

    return pd.DataFrame(waves)


# =============================================================
# 백신 접종 전/후 비교 분석
# 사용 pandas 기법: resample, groupby, agg, Boolean indexing, 파생 컬럼
# =============================================================
def _analyze_vaccination_impact(country_df):
    """
    백신 접종 본격화 시점을 기준으로 전/후 핵심 지표를 비교한다.

    기준 시점: people_fully_vaccinated가 전체 인구의 10%를 넘는 최초 날짜
    (소수 접종 시작이 아닌 "본격화" 시점을 기준으로 함)

    비교 지표:
    - CFR (치명률): total_deaths / total_cases * 100
    - 일평균 확진자 (new_cases_smoothed mean)
    - 일평균 사망자 (new_deaths_smoothed mean)
    - 월별 집계 (resample)
    """
    df = country_df.copy()

    # 인구 대비 접종률로 본격화 시점 판단
    population = df['population'].iloc[0]
    if population <= 0:
        return None

    # 접종률 파생 컬럼 생성
    df['vacc_rate'] = df['people_fully_vaccinated'] / population * 100

    # 10% 돌파 시점 탐색
    vacc_milestone = df[df['vacc_rate'] >= 10]
    if vacc_milestone.empty:
        # 10% 미달이면 최초 유효 접종 데이터 사용
        vacc_data = df[df['people_fully_vaccinated'].notna() & (df['people_fully_vaccinated'] > 0)]
        if vacc_data.empty:
            return None
        vacc_start_date = vacc_data['date'].iloc[0]
    else:
        vacc_start_date = vacc_milestone['date'].iloc[0]

    # 전/후 기간 분리
    pre_vacc = df[df['date'] < vacc_start_date].copy()
    post_vacc = df[df['date'] >= vacc_start_date].copy()

    if pre_vacc.empty or post_vacc.empty:
        return None

    # 월별 집계 (resample)
    pre_monthly = pre_vacc.set_index('date').resample('ME').agg({
        'new_cases': 'sum',
        'new_deaths': 'sum',
        'new_cases_smoothed': 'mean',
    })
    post_monthly = post_vacc.set_index('date').resample('ME').agg({
        'new_cases': 'sum',
        'new_deaths': 'sum',
        'new_cases_smoothed': 'mean',
    })

    # CFR 계산 (파생 지표)
    pre_total_cases = pre_vacc['new_cases'].sum()
    pre_total_deaths = pre_vacc['new_deaths'].sum()
    pre_cfr = (pre_total_deaths / pre_total_cases * 100) if pre_total_cases > 0 else 0

    post_total_cases = post_vacc['new_cases'].sum()
    post_total_deaths = post_vacc['new_deaths'].sum()
    post_cfr = (post_total_deaths / post_total_cases * 100) if post_total_cases > 0 else 0

    return {
        'vacc_start_date': vacc_start_date,
        'pre_vaccination': {
            'period': f"{pre_vacc['date'].min().date()} ~ {pre_vacc['date'].max().date()}",
            'total_cases': float(pre_total_cases),
            'total_deaths': float(pre_total_deaths),
            'cfr': round(pre_cfr, 2),
            'avg_daily_cases': float(pre_vacc['new_cases_smoothed'].mean()),
            'avg_daily_deaths': float(pre_vacc['new_deaths_smoothed'].mean()),
            'months': len(pre_monthly),
        },
        'post_vaccination': {
            'period': f"{post_vacc['date'].min().date()} ~ {post_vacc['date'].max().date()}",
            'total_cases': float(post_total_cases),
            'total_deaths': float(post_total_deaths),
            'cfr': round(post_cfr, 2),
            'avg_daily_cases': float(post_vacc['new_cases_smoothed'].mean()),
            'avg_daily_deaths': float(post_vacc['new_deaths_smoothed'].mean()),
            'months': len(post_monthly),
        },
        'monthly_pre': pre_monthly,
        'monthly_post': post_monthly,
    }


# =============================================================
# 메인 process 함수
# =============================================================
def process(df):
    """
    일본 COVID-19 데이터 전처리 및 분석 파이프라인.

    1단계: 데이터 필터링 & 정렬
    2단계: 결측치 처리 (fillna, interpolate)
    3단계: 파동(Wave) 감지
    4단계: 백신 접종 전/후 비교 분석
    5단계: 메트릭 계산 (기본 + 파생)
    6단계: 시각화 생성
    """
    country_name = "Japan"

    # ==========================================================
    # 1. 데이터 필터링 & 정렬
    # ==========================================================
    country_df = df[df['location'] == country_name].copy()

    if country_df.empty:
        return None

    country_df = country_df.sort_values('date').reset_index(drop=True)

    # ==========================================================
    # 2. 결측치 처리
    # ==========================================================
    # 시계열 데이터: forward fill → backward fill
    for col in ['new_cases_smoothed', 'new_deaths_smoothed', 'total_cases', 'total_deaths']:
        country_df[col] = country_df[col].ffill().bfill()

    # 누적 데이터: forward fill만 (미래값으로 채우지 않음)
    for col in ['people_fully_vaccinated', 'total_vaccinations', 'total_boosters']:
        country_df[col] = country_df[col].ffill()

    # 재생산지수: 선형 보간
    country_df['reproduction_rate'] = country_df['reproduction_rate'].interpolate(method='linear')

    # 정책 강도: forward fill
    country_df['stringency_index'] = country_df['stringency_index'].ffill()

    # 검사 양성률: forward fill
    country_df['positive_rate'] = country_df['positive_rate'].ffill()

    # ==========================================================
    # 3. 파동(Wave) 감지
    # ==========================================================
    waves_df = _detect_waves(country_df)

    # ==========================================================
    # 4. 백신 접종 전/후 비교 분석
    # ==========================================================
    vacc_stats = _analyze_vaccination_impact(country_df)

    # ==========================================================
    # 5. 메트릭 계산
    # ==========================================================
    latest_row = country_df.iloc[-1]

    # CFR (치명률) 파생 지표
    total_cases_val = float(latest_row.get('total_cases', 0))
    total_deaths_val = float(latest_row.get('total_deaths', 0))
    cfr = (total_deaths_val / total_cases_val * 100) if total_cases_val > 0 else 0

    # 백신 접종률 파생 지표
    population = float(latest_row.get('population', 0))
    fully_vacc = float(latest_row.get('people_fully_vaccinated', 0)) if pd.notna(latest_row.get('people_fully_vaccinated')) else 0
    vacc_rate = (fully_vacc / population * 100) if population > 0 else 0

    metrics = {
        # 기본 메트릭 (UI 호환 - 필수 4개)
        "total_cases": total_cases_val,
        "total_deaths": total_deaths_val,
        "people_fully_vaccinated": fully_vacc,
        "new_cases": float(latest_row.get('new_cases', 0)),

        # 파생 메트릭
        "case_fatality_rate": round(cfr, 2),
        "vaccination_rate": round(vacc_rate, 2),
        "total_waves_detected": len(waves_df),
        "population": population,
    }

    # ==========================================================
    # 6. 시각화 생성
    # ==========================================================
    visualizations = {}

    try:
        if not waves_df.empty:
            visualizations['wave_detection'] = create_wave_detection_chart(
                country_df, waves_df, country_name
            )
            visualizations['wave_comparison'] = create_wave_comparison_chart(
                waves_df, country_name
            )

        if vacc_stats:
            visualizations['vaccination_impact'] = create_vaccination_impact_chart(
                vacc_stats, country_name
            )
            visualizations['cases_deaths_decoupling'] = create_cases_deaths_decoupling_chart(
                country_df, vacc_stats['vacc_start_date'], country_name
            )
    except Exception as e:
        print(f"Japan visualization error: {e}")

    # ==========================================================
    # [반환 영역] 아래 키 값들은 변경하지 마세요.
    # ==========================================================
    return {
        "country_name": country_name,
        "country_df": country_df,
        "metrics": metrics,
        "visualizations": visualizations,
    }
