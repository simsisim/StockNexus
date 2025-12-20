import pandas as pd

def calculate_emas(df, spans):
    """Calculates EMAs for the given spans and adds them to the dataframe."""
    if df.empty:
        return df
    
    df = df.copy()
    for span in spans:
        df[f'EMA_{span}'] = df['Close'].ewm(span=span, adjust=False).mean()
    return df

def calculate_diffs(df, spans):
    """Calculates % difference from Close to EMAs for the latest date."""
    if df.empty:
        return {}
    
    latest = df.iloc[-1]
    close = latest['Close']
    diffs = {}
    
    for span in spans:
        ema_val = latest.get(f'EMA_{span}')
        if pd.notna(ema_val) and ema_val != 0:
            # Calculate percentage difference: (Close - EMA) / EMA * 100
            # Or (Close - EMA) / Close * 100? Usually it's relative to EMA or Price.
            # The image shows "Above 0.25%", which implies (Price - EMA) / EMA or similar.
            # Let's use (Price - EMA) / EMA * 100 to show how much above/below the EMA the price is.
            pct_diff = ((close - ema_val) / ema_val) * 100
            diffs[f'EMA_{span}'] = {
                "value": ema_val,
                "pct_diff": pct_diff,
                "status": "Above" if pct_diff > 0 else "Below"
            }
            
    return diffs

def analyze_ticker(ticker, daily_df, weekly_df, monthly_df):
    """Orchestrates analysis for all timeframes."""
    
    # Define spans
    daily_spans = [9, 21, 50]
    weekly_spans = [9, 21, 50]
    monthly_spans = [9, 21]
    
    # Calculate EMAs
    daily_df = calculate_emas(daily_df, daily_spans)
    weekly_df = calculate_emas(weekly_df, weekly_spans)
    monthly_df = calculate_emas(monthly_df, monthly_spans)
    
    # Calculate Diffs
    daily_diffs = calculate_diffs(daily_df, daily_spans)
    weekly_diffs = calculate_diffs(weekly_df, weekly_spans)
    monthly_diffs = calculate_diffs(monthly_df, monthly_spans)
    
    analysis = {
        "daily": daily_diffs,
        "weekly": weekly_diffs,
        "monthly": monthly_diffs
    }
    
    return daily_df, weekly_df, monthly_df, analysis
