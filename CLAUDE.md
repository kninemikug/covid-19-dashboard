# COVID-19 Dashboard - 개발 가이드

## 🎯 프로젝트 개요
Streamlit 기반 COVID-19 데이터 분석 대시보드 (팀 협업 프로젝트)

## 🌿 Git 브랜치 전략
- **main**: 안정 버전 (배포용)
- **kook**: 미국(USA) 데이터 분석 모듈 개발
- **[팀원명]**: 각자 담당 국가 개발

## 📝 커밋 컨벤션
```
feat: 새로운 기능 추가
fix: 버그 수정
docs: 문서 수정
style: 코드 포맷팅
refactor: 코드 리팩토링
test: 테스트 추가/수정
chore: 기타 작업
```

**예시:**
```bash
git commit -m "feat: 미국 데이터 분석 모듈 구현"
git commit -m "fix: 날짜 정렬 오류 수정"
```

## 👥 팀원별 담당 국가
- **kook**: United States (미국)
- **[팀원1]**: [국가명]
- **[팀원2]**: [국가명]

## 🚀 작업 흐름
1. 본인 브랜치 생성: `git checkout -b [이름]`
2. 국가 모듈 작성: `modules/countries/[국가명].py`
3. UI 등록: `modules/ui.py`의 `COUNTRY_MODULES`에 추가
4. 커밋 및 푸시
5. Pull Request 생성 (main으로)

## 📦 개발 환경 설정
```bash
# 가상환경 생성
python -m venv venv
source venv/bin/activate  # Mac/Linux
# venv\Scripts\activate  # Windows

# 패키지 설치
pip install -r requirements.txt

# 데이터 다운로드 확인
python modules/data_loader.py

# 앱 실행
streamlit run app.py
```

## 🔧 국가 모듈 개발 가이드
### 표준 인터페이스
```python
def process(df):
    country_name = "국가명"  # location 컬럼과 일치해야 함

    # 데이터 필터링 및 전처리
    country_df = df[df['location'] == country_name].copy()

    # 메트릭 계산
    latest_row = country_df.iloc[-1]
    metrics = {
        "total_cases": latest_row.get('total_cases', 0),
        "total_deaths": latest_row.get('total_deaths', 0),
        "people_fully_vaccinated": latest_row.get('people_fully_vaccinated', 0),
        "new_cases": latest_row.get('new_cases', 0)
    }

    # 반환 (형식 고정)
    return {
        "country_name": country_name,
        "country_df": country_df,
        "metrics": metrics
    }
```

## 📊 사용 가능한 주요 컬럼
- `location`: 국가/지역명
- `date`: 날짜
- `total_cases`, `new_cases`: 확진자 수
- `total_deaths`, `new_deaths`: 사망자 수
- `total_vaccinations`, `people_fully_vaccinated`: 백신 접종
- `new_cases_smoothed`: 7일 평균 신규 확진자
- `vaccine`: 백신 제조사

## 🌍 주요 국가명 (location 값)
- 한국: `South Korea`
- 미국: `United States`
- 일본: `Japan`
- 중국: `China`
- 영국: `United Kingdom`
- 프랑스: `France`
- 독일: `Germany`
- 이탈리아: `Italy`

## ⚠️ 주의사항
1. **반환 형식 준수**: `process(df)` 함수는 반드시 표준 Dict 형식 반환
2. **날짜 정렬**: 시각화를 위해 `country_df.sort_values('date')` 필수
3. **빈 데이터 처리**: 데이터가 없으면 `return None`
4. **컬럼 확인**: `latest_row.get('컬럼명', 기본값)` 사용 (안전)

## 🐛 트러블슈팅
### 데이터가 다운로드되지 않아요
- Kaggle API 인증 설정 확인 (`~/.kaggle/kaggle.json`)
- 인터넷 연결 확인
- `python modules/data_loader.py` 실행 후 에러 로그 확인

### 국가 데이터가 비어있어요
- `location` 값이 정확한지 확인
- 데이터셋에 해당 국가가 포함되어 있는지 확인
- 대소문자, 띄어쓰기 정확히 일치해야 함

### 시각화가 안 나와요
- `country_df`가 비어있지 않은지 확인
- 날짜 컬럼이 정렬되어 있는지 확인
- 필수 컬럼(`new_cases_smoothed`, `people_fully_vaccinated`)이 있는지 확인
