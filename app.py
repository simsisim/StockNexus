import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import bcrypt
from github import Github
import os

# --- Configuration ---
# Default to AAPL if no input, but allow user to change it
DEFAULT_TICKER = "AAPL"
CSV_FILE = "user_data.csv"
REPO_NAME = "StockNexus" # This should match your GitHub repo name if possible, or be configurable

# --- Authentication ---
def check_password():
    """Returns `True` if the user had the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["password"]:
            # Compare the entered password with the stored hash
            # The hash below is for 'admin123' - REPLACE THIS IN PRODUCTION
            stored_hash = b'$2b$12$tnGA3Q3Kkh5Tn2/BNqtwY.E7GUrDwCrmXQeuKeNLe/S5D6SZVgOc6' 
            if bcrypt.checkpw(st.session_state["password"].encode(), stored_hash):
                st.session_state["password_correct"] = True
                del st.session_state["password"]  # Don't store the password
            else:
                st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First run, show input for password
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        return False
    elif not st.session_state["password_correct"]:
        # Password incorrect, show input again
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        st.error("😕 Password incorrect")
        return False
    else:
        # Password correct
        return True

# --- GitHub Persistence ---
def save_to_github(new_value):
    """Saves the updated CSV to GitHub."""
    token = st.secrets.get("GITHUB_TOKEN")
    if not token:
        st.error("GITHUB_TOKEN not found in secrets. Cannot save to GitHub.")
        return False

    try:
        g = Github(token)
        # You might need to adjust 'your_username/StockNexus' to the actual path
        # Assuming the repo is owned by the token owner
        user = g.get_user()
        repo = user.get_repo(REPO_NAME) 
        
        # Get the file to update
        contents = repo.get_contents(CSV_FILE)
        
        # Create the new content
        new_content = f"value\n{new_value}"
        
        # Update the file
        repo.update_file(contents.path, "Update user_data.csv via Streamlit", new_content, contents.sha)
        return True
    except Exception as e:
        st.error(f"Error saving to GitHub: {e}")
        return False

# --- Main App ---
st.set_page_config(page_title="StockNexus Dashboard", page_icon="📈")

st.title("📈 StockNexus Dashboard")

# Sidebar for Ticker Selection
ticker = st.sidebar.text_input("Ticker Symbol", value=DEFAULT_TICKER).upper()

# 1. Public View: Stock Chart
try:
    with st.spinner(f"Loading data for {ticker}..."):
        stock = yf.Ticker(ticker)
        hist = stock.history(period="1y")
        
        if not hist.empty:
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=hist.index, y=hist['Close'], mode='lines', name='Close Price'))
            fig.update_layout(title=f"{ticker} - 1 Year Price History", xaxis_title="Date", yaxis_title="Price (USD)")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning(f"No data found for {ticker}.")
except Exception as e:
    st.error(f"Error fetching data: {e}")

# 2. Public View: Display CSV Value
st.divider()
st.subheader("📌 Key Value")

# Load local CSV (Streamlit Cloud pulls this from repo on boot)
try:
    df = pd.read_csv(CSV_FILE)
    current_value = float(df['value'].iloc[0])
    st.metric(label="Current Value (from CSV)", value=current_value)
except Exception as e:
    st.error("Could not load local CSV. It might not exist yet.")
    current_value = 0.0

# 3. Admin View: Edit Value
st.divider()
st.subheader("🔒 Admin Area")

if check_password():
    st.success("Authenticated")
    
    new_val = st.number_input("Update Value", value=current_value)
    
    if st.button("Save to GitHub"):
        with st.spinner("Saving to GitHub..."):
            if save_to_github(new_val):
                st.success("✅ Saved! The app will update shortly (Streamlit Cloud usually auto-reloads on commit).")
                # We can also update the local file for immediate feedback, 
                # though it will be overwritten by the pull eventually.
                with open(CSV_FILE, "w") as f:
                    f.write(f"value\n{new_val}")
                st.rerun()
