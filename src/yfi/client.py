import yfinance as yf
import pandas as pd
import streamlit as st

def fetch_data(ticker, period="2y", interval="1d"):
    """Fetches stock history from yfinance."""
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period=period, interval=interval)
        return hist
    except Exception as e:
        print(f"Error fetching data for {ticker} ({interval}): {e}")
        return pd.DataFrame()

def fetch_all_timeframes(ticker):
    """Fetches Daily, Weekly, and Monthly data."""
    # Daily: 2 years to get enough data for 50 EMA
    daily = fetch_data(ticker, period="2y", interval="1d")
    
    # Weekly: 5 years
    weekly = fetch_data(ticker, period="5y", interval="1wk")
    
    # Monthly: Max to ensure enough data points
    monthly = fetch_data(ticker, period="max", interval="1mo")
    
    return daily, weekly, monthly
