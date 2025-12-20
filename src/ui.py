import streamlit as st
import pandas as pd
from .utils import fmt_num, fmt_range
from .market_data import get_stock_data, create_chart, save_stock_data, save_chart
from .scraper import scrape_zacks_data
from .data_manager import save_json_to_github, save_local_data
from .config import JSON_FILE
import json

def render_dashboard(ticker, data, live_zacks_info):
    """Renders the main dashboard."""
    
    # --- TOP ROW: Chart & Key Data ---
    top_c1, top_c2 = st.columns([2.5, 1])
    
    with top_c1:
        # Controls Row
        ctrl_c1, ctrl_c2 = st.columns([3, 1])
        with ctrl_c1:
            timeframe = st.pills("Timeframe", ["1M", "3M", "6M", "YTD", "1Y", "3Y", "5Y"], default="1Y", selection_mode="single", label_visibility="collapsed")
        with ctrl_c2:
            show_candles = st.toggle("Candlestick", value=False)
        
        period_map = {
            "1M": "1mo", "3M": "3mo", "6M": "6mo", "YTD": "ytd",
            "1Y": "1y", "3Y": "5y", "5Y": "5y"
        }
        yf_period = period_map.get(timeframe, "1y")

        stock, hist, analysis = get_stock_data(ticker, period=yf_period)

        if not hist.empty:
            # Filter for 3Y manually
            if timeframe == "3Y":
                cutoff = pd.Timestamp.now(tz=hist.index.tz) - pd.DateOffset(years=3)
                hist = hist[hist.index >= cutoff]
            
            # Save data and chart automatically on render
            save_stock_data(ticker, hist)
            
            fig = create_chart(ticker, hist, show_candles)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
                save_chart(ticker, fig)
            
            # Render EMA Analysis
            render_ema_analysis(analysis)

        else:
            if stock is None:
                 st.error("Ticker not found")
            else:
                 st.warning(f"No data found for {ticker}.")

    with top_c2:
        # Key Data
        with st.container(border=True):
            st.markdown("**Key Data**")
            if stock:
                try:
                    info = stock.info
                    col_a, col_b = st.columns(2)
                    
                    with col_a:
                        st.caption("Open")
                        st.write(f"{info.get('open', 'N/A')}")
                        st.caption("52-Wk Range")
                        st.write(fmt_range(info.get('fiftyTwoWeekLow'), info.get('fiftyTwoWeekHigh')))
                        st.caption("Market Cap")
                        st.write(fmt_num(info.get('marketCap')))
                        
                    with col_b:
                        st.caption("Day Range")
                        st.write(fmt_range(info.get('dayLow'), info.get('dayHigh')))
                        st.caption("Beta")
                        st.write(f"{info.get('beta', 'N/A')}")
                        st.caption("Dividend")
                        div = info.get('dividendRate')
                        yield_pct = info.get('dividendYield')
                        if div:
                            st.write(f"{div} ({yield_pct*100:.2f}%)")
                        else:
                            st.write("N/A")
                except:
                    st.error("Data unavailable")
            else:
                st.write("N/A")

    st.divider()

    # --- BOTTOM ROW: Analysis Columns ---
    if ticker in data:
        t_data = data[ticker]
        col1, col2, col3 = st.columns([1, 1, 1])
        
        # --- Column 1: Segments & Customers ---
        with col1:
            with st.container(border=True):
                s1 = t_data.get("segments", {}).get("top_left", {})
                st.markdown(f"**{s1.get('title', 'Segment 1')}**")
                st.caption(s1.get("content", ""))
                
            with st.container(border=True):
                s2 = t_data.get("segments", {}).get("mid_left", {})
                st.markdown(f"**{s2.get('title', 'Segment 2')}**")
                st.caption(s2.get("content", ""))
                
            with st.container(border=True):
                st.markdown("**Product Mix**")
                st.write(t_data.get("product_mix", ""))
                
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

        # --- Column 2: News ---
        with col2:
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
                if live_zacks_info:
                    st.write(live_zacks_info)
                    st.caption("✅ Live from Zacks")
                else:
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
                
            with st.container(border=True):
                ai = t_data.get("ai_stats", {})
                st.markdown(f"**Megatrend:** {ai.get('megatrend', '')}")
                st.markdown(f"**Moat:** {ai.get('moat', '')}")
                st.markdown(f"**Bottleneck:** {ai.get('bottleneck', '')}")
                st.markdown(f"**Exposure:** {ai.get('exposure', '')}")
    else:
        st.info(f"No analysis data found for {ticker}. Login to create it.")

def render_admin(ticker, data):
    """Renders the admin area."""
    st.divider()
    with st.expander("🔒 Admin: Edit Analysis"):
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
            
        # Auto-Fetch Button
        if st.button("✨ Auto-Fetch Zacks Data"):
            with st.spinner("Scraping Zacks..."):
                zacks_info = scrape_zacks_data(ticker)
                if zacks_info:
                    edit_data["metrics"]["rank_info"] = zacks_info
                    st.success("Fetched Zacks Rank!")
                else:
                    st.error("Could not fetch data. Check ticker or try again.")

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
                edit_data["metrics"]["rank_info"] = st.text_area("Rank Info", edit_data["metrics"].get("rank_info", ""))
                edit_data["metrics"]["earnings_trend"] = st.text_input("Earnings Trend", edit_data["metrics"].get("earnings_trend", ""))
                edit_data["metrics"]["valuation"] = st.text_input("Valuation", edit_data["metrics"].get("valuation", ""))
                
                st.markdown("---")
                st.caption("AI Stats")
                edit_data["ai_stats"]["megatrend"] = st.text_input("Megatrend", edit_data["ai_stats"].get("megatrend", ""))
                edit_data["ai_stats"]["moat"] = st.text_input("Moat", edit_data["ai_stats"].get("moat", ""))
                edit_data["ai_stats"]["bottleneck"] = st.text_input("Bottleneck", edit_data["ai_stats"].get("bottleneck", ""))
                edit_data["ai_stats"]["exposure"] = st.text_input("Exposure", edit_data["ai_stats"].get("exposure", ""))

            st.subheader("Customers & News")
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
                    save_local_data(data)
                    st.rerun()

def render_ema_analysis(analysis):
    """Renders the EMA analysis table."""
    if not analysis:
        return

    # Create a container for the analysis
    with st.container(border=True):
        cols = st.columns(3)
        timeframes = ["daily", "weekly", "monthly"]
        
        for i, tf in enumerate(timeframes):
            with cols[i]:
                st.markdown(f"<div style='text-align: center; font-weight: bold; margin-bottom: 10px;'>{tf.upper()}</div>", unsafe_allow_html=True)
                tf_data = analysis.get(tf, {})
                if not tf_data:
                    st.write("N/A")
                    continue
                
                # Sort EMAs by span (assuming keys are EMA_9, EMA_21, etc.)
                sorted_keys = sorted(tf_data.keys(), key=lambda x: int(x.split('_')[1]))
                
                # Create columns for each EMA within the timeframe column
                ema_cols = st.columns(len(sorted_keys))
                for j, key in enumerate(sorted_keys):
                    data = tf_data[key]
                    with ema_cols[j]:
                        st.markdown(f"<div style='text-align: center; font-size: 0.8em; color: gray;'>{key.replace('_', ' ')}</div>", unsafe_allow_html=True)
                        
                        pct = data['pct_diff']
                        # Determine colors based on status
                        if pct > 0:
                            bg_color = "rgba(33, 195, 84, 0.2)" # Green tint
                            border_color = "rgb(33, 195, 84)"
                            text_color = "rgb(33, 195, 84)"
                            status_text = "Above"
                        else:
                            bg_color = "rgba(255, 75, 75, 0.2)" # Red tint
                            border_color = "rgb(255, 75, 75)"
                            text_color = "rgb(255, 75, 75)"
                            status_text = "Below"
                            
                        st.markdown(
                            f"""
                            <div style="
                                background-color: {bg_color};
                                border: 1px solid {border_color};
                                border-radius: 4px;
                                padding: 4px 2px;
                                text-align: center;
                                color: {text_color};
                                font-size: 0.8em;
                                font-weight: bold;
                                margin-top: 5px;
                            ">
                                {status_text} {abs(pct):.2f}%
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
