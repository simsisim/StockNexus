import os

# --- Configuration ---
DEFAULT_TICKER = "MU"
REPO_NAME = "StockNexus"

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
SRC_DIR = os.path.join(BASE_DIR, "src")

# Files
CSV_FILE = os.path.join(BASE_DIR, "user_data.csv") # Keep user_data in root or move to data? Plan said data/ticker_data.json, let's keep user_data in root for now as it wasn't explicitly moved in plan, but ticker_data was.
JSON_FILE = os.path.join(DATA_DIR, "ticker_data.json")

# Ensure directories exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)
