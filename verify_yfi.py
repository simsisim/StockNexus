import sys
import os
import json

# Add current directory to path so we can import src
sys.path.append(os.getcwd())

from src.yfi.client import fetch_all_timeframes
from src.yfi.analysis import analyze_ticker
from src.yfi.storage import save_dataframes, save_analysis
from src.config import OUTPUT_DIR

def test_yfi_enhancements():
    ticker = "NVDA"
    print(f"Testing for {ticker}...")
    
    # 1. Fetch
    daily, weekly, monthly = fetch_all_timeframes(ticker)
    if daily.empty or weekly.empty or monthly.empty:
        print("Failed to fetch data.")
        return False
    print("Data fetched successfully.")
    
    # 2. Analyze
    daily, weekly, monthly, analysis = analyze_ticker(ticker, daily, weekly, monthly)
    
    # Check EMAs in dataframe
    if 'EMA_50' not in daily.columns:
        print("EMA_50 missing in daily data.")
        return False
    print("Analysis complete.")
    
    # 3. Save
    save_dataframes(ticker, daily, weekly, monthly)
    save_analysis(ticker, analysis)
    
    # 4. Verify Files
    ticker_dir = os.path.join(OUTPUT_DIR, ticker)
    files = ["data_daily.csv", "data_weekly.csv", "data_monthly.csv", "analysis.json"]
    for f in files:
        if not os.path.exists(os.path.join(ticker_dir, f)):
            print(f"Missing file: {f}")
            return False
            
    # 5. Verify JSON Content
    with open(os.path.join(ticker_dir, "analysis.json"), "r") as f:
        data = json.load(f)
        if "daily" not in data or "EMA_50" not in data["daily"]:
             print("Invalid analysis.json content.")
             return False
             
    print("Verification Successful!")
    return True

if __name__ == "__main__":
    if test_yfi_enhancements():
        print("SUCCESS")
    else:
        print("FAILURE")
