import sys
import os
import streamlit as st
from unittest.mock import MagicMock

# Mock streamlit functions to avoid runtime errors
st.container = MagicMock()
st.columns = MagicMock(return_value=[MagicMock(), MagicMock(), MagicMock()])
st.markdown = MagicMock()
st.write = MagicMock()
st.caption = MagicMock()

# Add current directory to path
sys.path.append(os.getcwd())

from src.ui import render_ema_analysis

def test_render_ema_analysis():
    print("Testing render_ema_analysis...")
    
    analysis = {
        "daily": {
            "EMA_9": {"value": 100, "pct_diff": 0.5, "status": "Above"},
            "EMA_21": {"value": 95, "pct_diff": 5.0, "status": "Above"},
            "EMA_50": {"value": 110, "pct_diff": -10.0, "status": "Below"}
        },
        "weekly": {},
        "monthly": {}
    }
    
    try:
        render_ema_analysis(analysis)
        print("Function executed successfully.")
        return True
    except Exception as e:
        print(f"Function failed with error: {e}")
        return False

if __name__ == "__main__":
    if test_render_ema_analysis():
        print("SUCCESS")
    else:
        print("FAILURE")
