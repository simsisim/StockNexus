import requests
import re
import streamlit as st

@st.cache_data(ttl=3600) # Cache for 1 hour
def scrape_zacks_data(ticker):
    """Scrapes Zacks Rank, Style Scores, and Industry Rank."""
    url = f"https://www.zacks.com/stock/quote/{ticker}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    info = []
    try:
        r = requests.get(url, headers=headers, timeout=5)
        if r.status_code != 200:
            return None
            
        text = r.text
        
        # 1. Zacks Rank
        rank_match = re.search(r'<p class="rank_view">\s*([0-9]-[a-zA-Z ]+)', text)
        if rank_match:
            info.append(f"Zacks Rank: {rank_match.group(1).strip()}")
            
        # 2. Style Scores
        if "Style Scores" in text:
            scores = []
            for style in ["Value", "Growth", "Momentum"]:
                m = re.search(r'>([A-F])</span>&nbsp;' + style, text)
                if m:
                    scores.append(f"{style}: {m.group(1)}")
            if scores:
                info.append(" | ".join(scores))
                
        # 3. Industry Rank
        ind_match = re.search(r'class="status">\s*(Top [0-9]+% \([0-9]+ out of [0-9]+\))', text)
        if ind_match:
            info.append(f"Ind: {ind_match.group(1)}")
            
        return "\n".join(info)
    except Exception as e:
        print(f"Scrape error: {e}")
        return None
