import requests
import re

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

def check_url(url):
    print(f"Fetching {url}...")
    try:
        r = requests.get(url, headers=headers, timeout=10)
        
        # Look for class="rank_view"
        print("--- Searching for 'rank_view' ---")
        matches = [m.start() for m in re.finditer("rank_view", r.text)]
        for m in matches:
            print(r.text[m-50:m+100])
            
        # Look for "1-Strong Buy" etc
        print("--- Searching for Rank Values ---")
        ranks = ["1-Strong Buy", "2-Buy", "3-Hold", "4-Sell", "5-Strong Sell"]
        for rank in ranks:
            if rank in r.text:
                print(f"FOUND: {rank}")
                idx = r.text.find(rank)
                print(r.text[idx-50:idx+50])

    except Exception as e:
        print(f"Error: {e}")

check_url("https://www.zacks.com/stock/quote/MU")
