import os
import json
from ..config import OUTPUT_DIR

def save_dataframes(ticker, daily_df, weekly_df, monthly_df):
    """Saves Daily, Weekly, and Monthly dataframes to CSV."""
    ticker_dir = os.path.join(OUTPUT_DIR, ticker)
    os.makedirs(ticker_dir, exist_ok=True)
    
    if not daily_df.empty:
        daily_df.to_csv(os.path.join(ticker_dir, "data_daily.csv"))
        
    if not weekly_df.empty:
        weekly_df.to_csv(os.path.join(ticker_dir, "data_weekly.csv"))
        
    if not monthly_df.empty:
        monthly_df.to_csv(os.path.join(ticker_dir, "data_monthly.csv"))

def save_analysis(ticker, analysis):
    """Saves analysis results to JSON."""
    ticker_dir = os.path.join(OUTPUT_DIR, ticker)
    os.makedirs(ticker_dir, exist_ok=True)
    
    with open(os.path.join(ticker_dir, "analysis.json"), "w") as f:
        json.dump(analysis, f, indent=2)
