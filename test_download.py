# test_download.py

from src.data_collector import download_multiple_stocks
from src.data_cleaner import clean_multiple_stocks
from src.indicators import add_all_indicators

# ── Updated Stock List ───────────────────────────────────────
US_STOCKS     = ['AAPL', 'MSFT', 'TSLA']
INDIAN_STOCKS = ['RELIANCE.NS', 'TCS.NS', '^NSEI']
ALL_TICKERS   = US_STOCKS + INDIAN_STOCKS

START_DATE = '2020-01-01'
END_DATE   = '2024-01-01'

# ── Download ─────────────────────────────────────────────────
print("Downloading US Stocks...")
print("Downloading Indian Stocks...")
data = download_multiple_stocks(ALL_TICKERS, START_DATE, END_DATE)

# ── Clean ────────────────────────────────────────────────────
cleaned_data = clean_multiple_stocks(data)

# ── Add Indicators ───────────────────────────────────────────
enriched_data = {}
for ticker in ALL_TICKERS:
    enriched_data[ticker] = add_all_indicators(
        cleaned_data[ticker],
        ticker
    )

# ── Quick Check ──────────────────────────────────────────────
print("\n" + "="*50)
print("DOWNLOAD SUMMARY")
print("="*50)
for ticker in ALL_TICKERS:
    df = enriched_data[ticker]
    print(f"{ticker:15} : {len(df)} rows, {len(df.columns)} columns")

print("\nAll data ready!")