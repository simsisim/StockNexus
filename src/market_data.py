import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import os
from .config import OUTPUT_DIR
from .yfi.client import fetch_all_timeframes
from .yfi.analysis import analyze_ticker
from .yfi.storage import save_dataframes, save_analysis

def get_stock_data(ticker, period="1y"):
    """
    Fetches stock history and performs analysis.
    Returns the stock object (mocked or minimal) and the daily history for compatibility.
    """
    try:
        # 1. Fetch All Timeframes
        daily, weekly, monthly = fetch_all_timeframes(ticker)
        
        if daily.empty:
            return None, pd.DataFrame()

        # 2. Analyze
        daily, weekly, monthly, analysis = analyze_ticker(ticker, daily, weekly, monthly)
        
        # 3. Save
        save_dataframes(ticker, daily, weekly, monthly)
        save_analysis(ticker, analysis)
        
        # Return daily data for the chart, filtered to requested period if needed
        # Note: fetch_all_timeframes fetches 2y for daily. 
        # If period is "1y", we might want to slice it for the return value, 
        # but the UI handles slicing for the chart.
        # We need to return a "stock" object because UI expects it for info.
        # Let's re-instantiate yf.Ticker just for the info part or refactor UI.
        # For now, to minimize UI changes, let's just return yf.Ticker(ticker).
        import yfinance as yf
        stock = yf.Ticker(ticker)
        
        return stock, daily, analysis
        
    except Exception as e:
        st.error(f"Error fetching data for {ticker}: {e}")
        return None, pd.DataFrame(), {}

def save_stock_data(ticker, hist):
    """Deprecated: Logic moved to src/yfi/storage.py. Kept for compatibility if needed."""
    pass 

def create_chart(ticker, hist, show_candles=False):
    """Creates a Plotly chart for the stock history."""
    if hist.empty:
        return None

    fig = go.Figure()
    if show_candles:
        fig.add_trace(go.Candlestick(x=hist.index,
                        open=hist['Open'],
                        high=hist['High'],
                        low=hist['Low'],
                        close=hist['Close'],
                        name='OHLC'))
        fig.update_layout(xaxis_rangeslider_visible=False)
    else:
        fig.add_trace(go.Scatter(x=hist.index, y=hist['Close'], mode='lines', name='Close'))
    
    # Add EMAs to chart if they exist
    colors = {'EMA_9': 'blue', 'EMA_21': 'orange', 'EMA_50': 'red'}
    for col, color in colors.items():
        if col in hist.columns:
            fig.add_trace(go.Scatter(x=hist.index, y=hist[col], mode='lines', name=col, line=dict(color=color, width=1)))

    fig.update_layout(
        height=400, 
        margin=dict(l=0, r=0, t=10, b=0),
        xaxis_title=None,
        yaxis_title=None
    )
    return fig

def save_chart(ticker, fig):
    """Saves the chart to HTML in output directory."""
    if not fig:
        return

    ticker_dir = os.path.join(OUTPUT_DIR, ticker)
    os.makedirs(ticker_dir, exist_ok=True)
    
    file_path = os.path.join(ticker_dir, "chart.html")
    fig.write_html(file_path)

