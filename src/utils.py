def fmt_num(n):
    """Formats a number to a readable string with suffixes (T, B, M)."""
    if n is None: return "N/A"
    if n >= 1e12: return f"{n/1e12:.2f} T"
    if n >= 1e9: return f"{n/1e9:.2f} B"
    if n >= 1e6: return f"{n/1e6:.2f} M"
    return f"{n:,.2f}"

def fmt_range(low, high):
    """Formats a range of two numbers."""
    if low is None or high is None: return "N/A"
    return f"{low:,.2f} - {high:,.2f}"
