import streamlit as st
from modules import ui
from modules.data_loader import load_data

def main():
    st.set_page_config(page_title="Covid-19 Dashboard", layout="wide")

    st.title("Corona-19 Live Dashboard")

    # Load data
    df = load_data()

    # Render UI with data
    ui.render_header(df)

if __name__ == "__main__":
    main()
