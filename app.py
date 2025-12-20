import streamlit as st
from src.config import DEFAULT_TICKER
from src.auth import check_password
from src.data_manager import load_data
from src.scraper import scrape_zacks_data
from src.ui import render_dashboard, render_admin

# --- Main App ---
st.set_page_config(page_title="StockNexus", layout="wide", page_icon="📈")

# Sidebar
ticker = st.sidebar.text_input("Ticker Symbol", value=DEFAULT_TICKER).upper()
data = load_data()

# --- Public View: Analysis Dashboard ---
# Determine title (Company Name if available, else Ticker)
if ticker in data:
    page_title = data[ticker].get("company_name", ticker)
else:
    page_title = f"Analysis: {ticker}"
    
st.title(page_title)

# Always try to scrape live data for the public view
with st.spinner("Fetching latest data..."):
    live_zacks_info = scrape_zacks_data(ticker)

render_dashboard(ticker, data, live_zacks_info)

# --- Admin Area ---
if check_password():
    render_admin(ticker, data)
