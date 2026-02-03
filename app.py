import streamlit as st
from modules import ui

def main():
    st.set_page_config(page_title="Covid-19 Dashboard", layout="wide")
    
    st.title("Corona-19 Live Dashboard")
    
    # Placeholder for UI
    ui.render_header()
    
    st.write("Welcome to the Covid-19 Dashboard.")

if __name__ == "__main__":
    main()
