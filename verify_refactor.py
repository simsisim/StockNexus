import sys
import os

# Add current directory to path so we can import src
sys.path.append(os.getcwd())

from src.market_data import get_stock_data, save_stock_data, create_chart, save_chart
from src.config import OUTPUT_DIR

def test_market_data():
    ticker = "AAPL"
    print(f"Testing for {ticker}...")
    
    # 1. Fetch Data
    stock, hist = get_stock_data(ticker, period="1mo")
    if hist.empty:
        print("Failed to fetch data.")
        return False
    print("Data fetched successfully.")
    
    # 2. Save Data
    save_stock_data(ticker, hist)
    expected_csv = os.path.join(OUTPUT_DIR, ticker, "data.csv")
    if os.path.exists(expected_csv):
        print(f"Data saved to {expected_csv}")
    else:
        print(f"Failed to save data to {expected_csv}")
        return False

    # 3. Create & Save Chart
    fig = create_chart(ticker, hist)
    save_chart(ticker, fig)
    expected_html = os.path.join(OUTPUT_DIR, ticker, "chart.html")
    if os.path.exists(expected_html):
        print(f"Chart saved to {expected_html}")
    else:
        print(f"Failed to save chart to {expected_html}")
        return False
        
    return True

if __name__ == "__main__":
    if test_market_data():
        print("Verification Successful!")
    else:
        print("Verification Failed!")
