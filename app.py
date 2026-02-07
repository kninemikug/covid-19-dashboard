import streamlit as st
from modules import ui
from modules.data_loader import load_data

def main():
    st.set_page_config(page_title="Covid-19 Dashboard", layout="wide")

    st.title("Corona-19 Live Dashboard")

    # Load data (캐시됨)
    df = load_data()

    # 앱 시작 시 모든 국가 데이터 미리 캐싱 (한 번만 실행)
    if "cache_warmed" not in st.session_state:
        ui.prewarm_country_cache(df)
        st.session_state.cache_warmed = True

    # Render UI with data
    ui.render_header(df)

if __name__ == "__main__":
    main()
