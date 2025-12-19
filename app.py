import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import bcrypt
from github import Github
import os
import json

# --- Configuration ---
DEFAULT_TICKER = "MU"
CSV_FILE = "user_data.csv"
JSON_FILE = "ticker_data.json"
REPO_NAME = "StockNexus"

# --- Authentication ---
# Load users from secrets
USERS = st.secrets["passwords"]

def check_password():
    """Returns `True` if the user had the correct password."""
    def password_entered():
        if st.session_state["username"] in USERS and st.session_state["password"]:
            stored_hash = USERS[st.session_state["username"]]
            if isinstance(stored_hash, str):
                stored_hash = stored_hash.encode('utf-8')
            if bcrypt.checkpw(st.session_state["password"].encode(), stored_hash):
                st.session_state["password_correct"] = True
                del st.session_state["password"]
                del st.session_state["username"]
            else:
                st.session_state["password_correct"] = False
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.text_input("Username", key="username")
        st.text_input("Password", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        st.text_input("Username", key="username")
        st.text_input("Password", type="password", on_change=password_entered, key="password")
        st.error("😕 User not known or password incorrect")
        return False
    else:
        return True

# --- Data Persistence ---
def load_data():
    """Loads the JSON data from local file."""
    try:
        with open(JSON_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_json_to_github(new_data):
    """Saves the updated JSON to GitHub."""
    token = st.secrets.get("GITHUB_TOKEN")
    if not token:
        st.error("GITHUB_TOKEN not found.")
        return False
    try:
        g = Github(token)
        user = g.get_user()
        repo = user.get_repo(REPO_NAME)
        contents = repo.get_contents(JSON_FILE)
        new_content = json.dumps(new_data, indent=2)
        repo.update_file(contents.path, "Update ticker_data.json via Streamlit", new_content, contents.sha)
        return True
    except Exception as e:
        st.error(f"Error saving to GitHub: {e}")
        return False

# --- Main App ---
st.set_page_config(page_title="StockNexus", layout="wide", page_icon="📈")

# Sidebar
ticker = st.sidebar.text_input("Ticker Symbol", value=DEFAULT_TICKER).upper()
data = load_data()

# --- Public View: Analysis Dashboard ---
st.title(f"Analysis: {ticker}")

if ticker in data:
    t_data = data[ticker]
    
    # Layout: 3 Columns (Left Info, Center Chart/News, Right Metrics)
    col1, col2, col3 = st.columns([1, 1.5, 1])
    
    # --- Column 1: Segments & Customers ---
    with col1:
        st.subheader(t_data.get("company_name", ticker))
        
        # Segment 1
        with st.container(border=True):
            s1 = t_data.get("segments", {}).get("top_left", {})
            st.markdown(f"**{s1.get('title', 'Segment 1')}**")
            st.caption(s1.get("content", ""))
            
        # Segment 2
        with st.container(border=True):
            s2 = t_data.get("segments", {}).get("mid_left", {})
            st.markdown(f"**{s2.get('title', 'Segment 2')}**")
            st.caption(s2.get("content", ""))
            
        # Product Mix
        with st.container(border=True):
            st.markdown("**Product Mix**")
            st.write(t_data.get("product_mix", ""))
            
        # Main Customers
        with st.container(border=True):
            st.markdown("**Main Customers**")
            c_cols = st.columns(2)
            cust = t_data.get("main_customers", {})
            with c_cols[0]:
                st.markdown(f"<u>{cust.get('col1', {}).get('title', '')}</u>", unsafe_allow_html=True)
                for c in cust.get('col1', {}).get('names', []):
                    st.text(c)
            with c_cols[1]:
                st.markdown(f"<u>{cust.get('col2', {}).get('title', '')}</u>", unsafe_allow_html=True)
                for c in cust.get('col2', {}).get('names', []):
                    st.text(c)

    # --- Column 2: Chart & News ---
    with col2:
        # Price Chart
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period="1y")
            if not hist.empty:
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=hist.index, y=hist['Close'], mode='lines', name='Close'))
                fig.update_layout(height=300, margin=dict(l=0, r=0, t=0, b=0))
                st.plotly_chart(fig, use_container_width=True)
        except:
            st.error("Chart unavailable")
            
        # News
        with st.container(border=True):
            st.markdown("**Main Customer News**")
            st.write(t_data.get("news", {}).get("main_customer_news", ""))
            
        with st.container(border=True):
            st.markdown("**Other News**")
            for n in t_data.get("news", {}).get("other_news", []):
                st.markdown(f"- {n}")

    # --- Column 3: Metrics & AI Stats ---
    with col3:
        metrics = t_data.get("metrics", {})
        
        with st.container(border=True):
            st.markdown("**Rank Info**")
            st.write(metrics.get("rank_info", ""))
            
        with st.container(border=True):
            st.markdown("**Earnings / Sales Trend**")
            st.write(metrics.get("earnings_trend", ""))
            
        with st.container(border=True):
            st.markdown("**Revisions**")
            for r in metrics.get("revisions", []):
                st.markdown(f"- {r}")
                
        with st.container(border=True):
            st.markdown("**Valuation**")
            st.write(metrics.get("valuation", ""))
            
        # AI Stats
        with st.container(border=True):
            ai = t_data.get("ai_stats", {})
            st.markdown(f"**Megatrend:** {ai.get('megatrend', '')}")
            st.markdown(f"**Moat:** {ai.get('moat', '')}")
            st.markdown(f"**Bottleneck:** {ai.get('bottleneck', '')}")
            st.markdown(f"**Exposure:** {ai.get('exposure', '')}")

else:
    st.info(f"No analysis data found for {ticker}. Login to create it.")
    # Fallback to just chart
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="1y")
        st.line_chart(hist['Close'])
    except:
        pass

# --- Admin Area ---
st.divider()
with st.expander("🔒 Admin: Edit Analysis"):
    if check_password():
        st.success(f"Editing {ticker}")
        
        # Load existing or template
        if ticker in data:
            edit_data = data[ticker]
        else:
            edit_data = {
                "company_name": "", "segments": {"top_left": {}, "mid_left": {}},
                "product_mix": "", "main_customers": {"col1": {"names": []}, "col2": {"names": []}},
                "news": {"other_news": []}, "metrics": {"revisions": []}, "ai_stats": {}
            }
            
        with st.form("edit_form"):
            edit_data["company_name"] = st.text_input("Company Name", edit_data.get("company_name", ""))
            
            c1, c2 = st.columns(2)
            with c1:
                st.subheader("Left Column")
                edit_data["segments"]["top_left"]["title"] = st.text_input("Seg 1 Title", edit_data["segments"]["top_left"].get("title", ""))
                edit_data["segments"]["top_left"]["content"] = st.text_area("Seg 1 Content", edit_data["segments"]["top_left"].get("content", ""))
                edit_data["segments"]["mid_left"]["title"] = st.text_input("Seg 2 Title", edit_data["segments"]["mid_left"].get("title", ""))
                edit_data["segments"]["mid_left"]["content"] = st.text_area("Seg 2 Content", edit_data["segments"]["mid_left"].get("content", ""))
                edit_data["product_mix"] = st.text_area("Product Mix", edit_data.get("product_mix", ""))
                
            with c2:
                st.subheader("Right Column")
                edit_data["metrics"]["rank_info"] = st.text_input("Rank Info", edit_data["metrics"].get("rank_info", ""))
                edit_data["metrics"]["earnings_trend"] = st.text_input("Earnings Trend", edit_data["metrics"].get("earnings_trend", ""))
                edit_data["metrics"]["valuation"] = st.text_input("Valuation", edit_data["metrics"].get("valuation", ""))
                
                st.markdown("---")
                st.caption("AI Stats")
                edit_data["ai_stats"]["megatrend"] = st.text_input("Megatrend", edit_data["ai_stats"].get("megatrend", ""))
                edit_data["ai_stats"]["moat"] = st.text_input("Moat", edit_data["ai_stats"].get("moat", ""))
                edit_data["ai_stats"]["bottleneck"] = st.text_input("Bottleneck", edit_data["ai_stats"].get("bottleneck", ""))
                edit_data["ai_stats"]["exposure"] = st.text_input("Exposure", edit_data["ai_stats"].get("exposure", ""))

            st.subheader("Customers & News")
            # Simplified for form: Comma separated lists
            cust_col1 = st.text_area("Customers Col 1 (comma sep)", ", ".join(edit_data["main_customers"]["col1"].get("names", [])))
            edit_data["main_customers"]["col1"]["names"] = [x.strip() for x in cust_col1.split(",") if x.strip()]
            edit_data["main_customers"]["col1"]["title"] = st.text_input("Cust Col 1 Title", edit_data["main_customers"]["col1"].get("title", "HBM"))

            cust_col2 = st.text_area("Customers Col 2 (comma sep)", ", ".join(edit_data["main_customers"]["col2"].get("names", [])))
            edit_data["main_customers"]["col2"]["names"] = [x.strip() for x in cust_col2.split(",") if x.strip()]
            edit_data["main_customers"]["col2"]["title"] = st.text_input("Cust Col 2 Title", edit_data["main_customers"]["col2"].get("title", "DRAM"))

            edit_data["news"]["main_customer_news"] = st.text_area("Main News", edit_data["news"].get("main_customer_news", ""))
            
            other_news = st.text_area("Other News (one per line)", "\n".join(edit_data["news"].get("other_news", [])))
            edit_data["news"]["other_news"] = [x.strip() for x in other_news.split("\n") if x.strip()]
            
            revisions = st.text_area("Revisions (one per line)", "\n".join(edit_data["metrics"].get("revisions", [])))
            edit_data["metrics"]["revisions"] = [x.strip() for x in revisions.split("\n") if x.strip()]

            if st.form_submit_button("Save Analysis"):
                data[ticker] = edit_data
                if save_json_to_github(data):
                    st.success("Saved to GitHub!")
                    # Update local file too
                    with open(JSON_FILE, "w") as f:
                        json.dump(data, f, indent=2)
                    st.rerun()
