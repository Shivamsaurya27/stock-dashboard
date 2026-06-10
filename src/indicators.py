# ============================================================
# src/indicators.py
# Purpose : Calculate financial indicators and features
# Author  : Shivam
# ============================================================

import pandas as pd
import numpy as np


# ── FUNCTION 1: Daily Returns ────────────────────────────────
def calculate_returns(df):
    """
    Calculates simple and log daily returns.

    Input : df (DataFrame) — cleaned stock data
    Output: df (DataFrame) — with new return columns added
    """

    df = df.copy()

    # ── Simple Daily Return ──────────────────────────────────
    df['Daily_Return'] = df['Adj Close'].pct_change()
    # pct_change() = (current - previous) / previous
    # First row will be NaN — no previous price exists
    # This is correct and expected

    # ── Log Daily Return ─────────────────────────────────────
    df['Log_Return'] = np.log(df['Adj Close'] / df['Adj Close'].shift(1))
    # shift(1) moves the column down by 1 row
    # So each row gets divided by the previous row's value
    # np.log() applies natural logarithm
    # First row will be NaN — same reason as above

    # ── Cumulative Return ────────────────────────────────────
    df['Cumulative_Return'] = (1 + df['Daily_Return']).cumprod()
    # (1 + return) converts % to multiplier e.g. 5% → 1.05
    # .cumprod() multiplies all values progressively
    # e.g. 1.05 × 0.98 × 1.03 × ...
    # Result: if you invested ₹1, how much do you have now?
    # Value of 1.5 means 50% total gain since start

    # ── Cumulative Return Percentage ─────────────────────────
    df['Cumulative_Return_Pct'] = (df['Cumulative_Return'] - 1) * 100
    # Converts multiplier to percentage for readability
    # 1.5 → 50.0 (meaning +50%)

    return df


# ── FUNCTION 2: Moving Averages ──────────────────────────────
def calculate_moving_averages(df, windows=[20, 50, 200]):
    """
    Calculates Simple and Exponential Moving Averages.

    Input : df      (DataFrame) — stock data with Adj Close
            windows (list)      — list of periods e.g. [20, 50, 200]
    Output: df (DataFrame) — with MA columns added
    """

    df = df.copy()

    for window in windows:
        # Loop through each window size e.g. 20, 50, 200

        # ── Simple Moving Average ────────────────────────────
        df[f'SMA_{window}'] = df['Adj Close'].rolling(window=window).mean()
        # .rolling(window=N) creates a sliding window of N rows
        # .mean() calculates average within that window
        # First N-1 rows will be NaN — not enough data yet
        # e.g. SMA_20 needs 20 rows before first value appears

        # ── Exponential Moving Average ───────────────────────
        df[f'EMA_{window}'] = df['Adj Close'].ewm(
            span=window,
            adjust=False
        ).mean()
        # .ewm() = exponentially weighted moving average
        # span=N roughly equivalent to N-day window
        # adjust=False uses the standard EMA formula
        # EMA has values from row 1 — no NaN period

    return df


# ── FUNCTION 3: Volatility ───────────────────────────────────
def calculate_volatility(df, windows=[21, 63]):
    """
    Calculates rolling volatility (risk measure).

    Input : df      (DataFrame) — must have Daily_Return column
            windows (list)      — rolling periods
                                  21  = ~1 month
                                  63  = ~3 months
    Output: df (DataFrame) — with volatility columns added
    """

    df = df.copy()

    # ── Overall Volatility ───────────────────────────────────
    daily_vol = df['Daily_Return'].std()
    annual_vol = daily_vol * np.sqrt(252)
    # std() = standard deviation of all daily returns
    # Multiply by √252 to annualize
    # This is a single number for the entire period

    print(f"  Overall Daily Volatility  : {daily_vol:.4f} ({daily_vol*100:.2f}%)")
    print(f"  Overall Annual Volatility : {annual_vol:.4f} ({annual_vol*100:.2f}%)")

    # ── Rolling Volatility ───────────────────────────────────
    for window in windows:
        col_name = f'Volatility_{window}d'
        df[col_name] = df['Daily_Return'].rolling(window=window).std() * np.sqrt(252)
        # Rolling std over N days × √252 = annualized rolling volatility
        # This creates a new value for each day
        # Shows HOW volatility changed over time
        # High values = turbulent period, Low values = calm period

    return df


# ── FUNCTION 4: Daily Price Range ────────────────────────────
def calculate_daily_range(df):
    """
    Calculates daily price range and range percentage.

    Input : df (DataFrame) — stock data with High and Low
    Output: df (DataFrame) — with range columns added
    """

    df = df.copy()

    # ── Absolute Range ───────────────────────────────────────
    df['Daily_Range'] = df['High'] - df['Low']
    # Simple difference between highest and lowest price of the day
    # Higher range = more intraday volatility

    # ── Range as Percentage of Close ─────────────────────────
    df['Daily_Range_Pct'] = (df['Daily_Range'] / df['Close']) * 100
    # Normalizes range by price level
    # A ₹10 range on a ₹100 stock = 10% (significant)
    # A ₹10 range on a ₹1000 stock = 1% (less significant)

    return df


# ── FUNCTION 5: All Indicators Together ─────────────────────
def add_all_indicators(df, ticker=""):
    """
    Runs all indicator functions on a single DataFrame.
    This is the main function we call from outside.

    Input : df     (DataFrame) — cleaned stock data
            ticker (str)       — name for display
    Output: df (DataFrame) — enriched with all indicators
    """

    print(f"\nCalculating indicators for: {ticker}")

    df = calculate_returns(df)
    print(f"  Returns calculated ✓")

    df = calculate_moving_averages(df)
    print(f"  Moving averages calculated ✓")

    df = calculate_volatility(df)

    df = calculate_daily_range(df)
    print(f"  Daily range calculated ✓")

    print(f"  Total columns now: {len(df.columns)}")
    print(f"  Columns: {df.columns.tolist()}")

    return df


# ── FUNCTION 6: Summary Statistics ──────────────────────────
def get_summary_stats(df, ticker=""):
    """
    Returns key summary statistics for a stock.

    Input : df     (DataFrame) — enriched stock data
            ticker (str)       — stock name
    Output: stats (dict) — key metrics
    """

    stats = {
        'Ticker'              : ticker,
        'Total Trading Days'  : len(df),
        'Mean Daily Return'   : f"{df['Daily_Return'].mean()*100:.3f}%",
        'Std Daily Return'    : f"{df['Daily_Return'].std()*100:.3f}%",
        'Best Day'            : f"{df['Daily_Return'].max()*100:.2f}%",
        'Worst Day'           : f"{df['Daily_Return'].min()*100:.2f}%",
        'Annual Volatility'   : f"{df['Daily_Return'].std()*np.sqrt(252)*100:.2f}%",
        'Total Return'        : f"{df['Cumulative_Return_Pct'].iloc[-1]:.2f}%",
        'Starting Price'      : f"${df['Adj Close'].iloc[0]:.2f}",
        'Ending Price'        : f"${df['Adj Close'].iloc[-1]:.2f}",
    }

    return stats