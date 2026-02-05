# COVID-19 Dashboard

Streamlit 기반의 전 세계 코로나19(COVID-19) 현황 분석 대시보드 프로젝트입니다.
3개의 Kaggle 데이터셋을 결합하여 확진자, 사망자, 백신 접종 현황 등 포괄적인 데이터를 시각화합니다.

## 📂 데이터셋 구조 및 출처 (Data Sources & Structure)

이 프로젝트는 `kagglehub`를 사용하여 다음 3개의 데이터셋을 자동으로 다운로드하고 병합하여 사용합니다.

### 1. Main Dataset (일별 현황)
*   **출처**: [Coronavirus (COVID-19) Cases - Daily Updates](https://www.kaggle.com/datasets/joebeachcapital/coronavirus-covid-19-cases-daily-updates)
*   **역할**: 프로젝트의 **메인 데이터소스**입니다. 가장 방대한 기간(Time-series)의 확진자(`cases`), 사망자(`deaths`), 검사(`tests`) 데이터를 제공합니다.
*   **파일명**: `covid_daily_full.csv`

### 2. Secondary Dataset (보조 데이터)
*   **출처**: [COVID-19 Dataset (OWID)](https://www.kaggle.com/datasets/georgesaavedra/covid19-dataset)
*   **역할**: 메인 데이터에 없는 초기 확산 정보나 추가적인 인구 통계/경제 지표를 보완하기 위해 사용합니다.
*   **파일명**: `owid-covid-data.csv`
*   **병합 방식**: 메인 데이터에 `Left Join`으로 결합되며, 중복 컬럼은 `_owid` 접미사가 붙습니다.

### 3. Vaccination Details (백신 상세)
*   **출처**: [COVID-19 World Vaccination Progress](https://www.kaggle.com/datasets/gpreda/covid-world-vaccination-progress)
*   **역할**: 백신 종류(`vaccine`) 및 제조사별 접종 현황 등 상세 백신 정보를 제공합니다.
*   **파일명**: `country_vaccinations_by_manufacturer.csv`
*   **병합 방식**: `location`과 `date`를 기준으로 결합됩니다.

---

## 🛠 데이터 로드 방법 (How to Load Data)

데이터 다운로드 및 전처리 로직은 `modules/data_loader.py`에 구현되어 있습니다.
데이터셋 구조를 확인하거나 다운로드를 수행하려면 다음 명령어를 실행하세요.

### 데이터 준비 및 확인
```bash
python modules/data_loader.py
```
위 스크립트를 실행하면 `kagglehub`를 통해 데이터를 다운로드하고, 병합된 데이터의 정보(`info`, `head`)를 출력합니다.
앱 실행 전 데이터가 정상적으로 준비되었는지 확인할 때 사용합니다.

---

## 🚀 설치 및 실행 방법 (Installation & Usage)

### 1. 환경 설정
Python 3.8+ 환경을 권장합니다.
```bash
# 가상환경 생성 (선택)
python -m venv venv
source venv/bin/activate
```

### 2. 패키지 설치
`kagglehub`를 포함한 필수 패키지를 설치합니다.
```bash
pip install -r requirements.txt
```

### 3. 앱 실행
```bash
streamlit run app.py
```

---

## 👨‍💻 협업 가이드 (Contribution Guide)

팀원들은 각자 담당한 국가의 **데이터 전처리(Preprocessing)** 로직을 본인의 모듈 파일 내에서 자유롭게 구현하면 됩니다.
단, 시각화를 위해 결과값은 반드시 **정해진 Dict 형태**로 반환해야 합니다.

### 1. 모듈 파일 생성
`modules/countries/` 폴더 안에 국가명으로 파이썬 파일을 생성합니다. (예: `usa.py`)

**템플릿 코드** (복사해서 사용하세요):
```python
# modules/countries/your_country.py
import pandas as pd

def process(df):
    country_name = "United States"
    
    # ---------------------------------------------------------
    # [자유 구현 영역] 
    # Pandas를 사용하여 필터링, 컬럼 추가, 데이터 정제 등을 자유롭게 수행하세요.
    # ---------------------------------------------------------
    
    # 예시: 국가로 필터링
    country_df = df[df['location'] == country_name].copy()
    
    if country_df.empty:
        return None
    
    # 예시: 메트릭 계산 (가장 최신 데이터)
    latest_row = country_df.iloc[-1]
    metrics = {
        "total_cases": latest_row.get('total_cases', 0),
        "total_deaths": latest_row.get('total_deaths', 0),
        "people_fully_vaccinated": latest_row.get('people_fully_vaccinated', 0),
        "new_cases": latest_row.get('new_cases', 0)
    }
    
    # 날짜순 정렬 (시각화를 위해 필수)
    country_df = country_df.sort_values('date')

    # ---------------------------------------------------------
    # [반환 영역] 아래 키 값들은 변경하지 마세요.
    # ---------------------------------------------------------
    return {
        "country_name": country_name,
        "country_df": country_df,  # 시각화에 쓰일 DataFrame
        "metrics": metrics         # 상단 카드에 표시될 수치
    }
```

### 2. UI 등록
작성 완료 후 `modules/ui.py` 의 `COUNTRY_MODULES` 에 등록하면 됩니다.

```python
COUNTRY_MODULES = {
    "South Korea": "south_korea",
    "United States": "usa", 
}
```