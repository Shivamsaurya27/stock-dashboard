# ============================================================
# src/data_cleaner.py
# Purpose : Clean and validate downloaded stock data
# Author  : Shivam
# ============================================================

import pandas as pd
import numpy as np


def clean_stock_data(df, ticker=""):
    """
    Cleans and validates a single stock DataFrame.

    Inputs:
        df     (DataFrame) : Raw stock data from data_collector
        ticker (str)       : Stock name for display in messages

    Output:
        df (DataFrame) : Cleaned stock data
    """

    print(f"\nCleaning data for: {ticker}")
    print(f"Starting shape: {df.shape}")

    # ── Step 1: Copy to avoid modifying original ─────────────
    df = df.copy()
    # .copy() creates a new independent DataFrame
    # Without this, changes here would affect the original df
    # This is called "defensive copying" — best practice

    # ── Step 2: Ensure Index is DatetimeIndex ────────────────
    if not isinstance(df.index, pd.DatetimeIndex):
        df.index = pd.to_datetime(df.index)
    # pd.DatetimeIndex allows time-based operations
    # e.g. df['2020'], df.resample('M'), df.loc['2020-01']
    # If index is plain strings, these operations fail

    # ── Step 3: Sort by Date ─────────────────────────────────
    df = df.sort_index()
    # Ensures data is in chronological order
    # Downloaded data is usually sorted but never assume
    # Unsorted time series gives wrong returns and MAs

    # ── Step 4: Remove Duplicate Dates ──────────────────────
    duplicates = df.index.duplicated()
    # .duplicated() returns True for every duplicate row
    # First occurrence is kept (marked False)

    if duplicates.sum() > 0:
        print(f"  Removed {duplicates.sum()} duplicate rows")
        df = df[~duplicates]
        # ~ means NOT — keeps rows where duplicated is False
        # i.e. keeps only unique dates

    # ── Step 5: Handle Missing Values ───────────────────────
    missing_before = df.isnull().sum().sum()
    # .isnull() returns True for each NaN cell
    # .sum().sum() counts total NaN across all columns

    if missing_before > 0:
        print(f"  Missing values found: {missing_before}")

        # Forward fill first — use previous day's value
        df = df.ffill()
        # ffill = forward fill
        # e.g. if Monday is NaN, use Friday's value
        # Makes sense for prices — market was just closed

        # Backward fill for any remaining NaN at start
        df = df.bfill()
        # bfill = backward fill
        # Handles NaN at the very beginning of the data

        missing_after = df.isnull().sum().sum()
        print(f"  Missing values after fill: {missing_after}")

    # ── Step 6: Remove Zero or Negative Prices ──────────────
    price_cols = ['Open', 'High', 'Low', 'Close', 'Adj Close']
    price_cols = [c for c in price_cols if c in df.columns]
    # Only check columns that actually exist

    zero_mask = (df[price_cols] <= 0).any(axis=1)
    # <= 0 checks each price cell for zero or negative value
    # .any(axis=1) returns True if ANY price in that row is <=0
    # axis=1 means check across columns (row by row)

    if zero_mask.sum() > 0:
        print(f"  Removed {zero_mask.sum()} rows with zero/negative prices")
        df = df[~zero_mask]
        # Keep only rows where all prices are positive

    # ── Step 7: Remove Negative Volume ──────────────────────
    if 'Volume' in df.columns:
        neg_vol = df['Volume'] < 0
        if neg_vol.sum() > 0:
            print(f"  Removed {neg_vol.sum()} rows with negative volume")
            df = df[~neg_vol]

    # ── Step 8: Validate OHLC Logic ─────────────────────────
    # High must be >= Low always
    # High must be >= Open and Close
    # Low must be <= Open and Close

    if all(c in df.columns for c in ['Open', 'High', 'Low', 'Close']):
        invalid = (
            (df['High'] < df['Low']) |
            (df['High'] < df['Open']) |
            (df['High'] < df['Close']) |
            (df['Low'] > df['Open']) |
            (df['Low'] > df['Close'])
        )
        # | means OR — flag row if ANY condition is true
        # These are logical impossibilities in market data

        if invalid.sum() > 0:
            print(f"  WARNING: {invalid.sum()} rows with invalid OHLC values")
            df = df[~invalid]

    # ── Step 9: Detect Extreme Outliers ─────────────────────
    # Calculate daily returns temporarily to find extreme moves
    temp_returns = df['Close'].pct_change()
    # pct_change() calculates percentage change from previous row
    # e.g. (157.5 - 150) / 150 = 0.05 = 5%

    extreme = temp_returns.abs() > 0.5
    # Flag any single-day move greater than 50%
    # >50% daily move is almost certainly a data error
    # Real crashes like 2008 saw ~10-15% single day moves

    if extreme.sum() > 0:
        print(f"  WARNING: {extreme.sum()} extreme price movements detected (>50%)")
        print(f"  Dates: {df.index[extreme].tolist()}")
        # We warn but don't remove — could be real events
        # Data scientist should investigate manually

    # ── Step 10: Final Report ────────────────────────────────
    print(f"Final shape  : {df.shape}")
    print(f"Date range   : {df.index[0].date()} to {df.index[-1].date()}")
    print(f"Missing values: {df.isnull().sum().sum()}")
    print(f"Cleaning complete ✓")

    return df


def clean_multiple_stocks(data_dict):
    """
    Cleans data for all stocks in a dictionary.

    Inputs:
        data_dict (dict) : {'AAPL': DataFrame, 'MSFT': DataFrame ...}

    Output:
        cleaned_dict (dict) : Same structure with cleaned DataFrames
    """

    cleaned_dict = {}

    for ticker, df in data_dict.items():
        # .items() gives both key and value in each iteration
        # ticker = 'AAPL', df = its DataFrame

        cleaned_df = clean_stock_data(df, ticker)
        cleaned_dict[ticker] = cleaned_df

    print(f"\n{'='*40}")
    print(f"All {len(cleaned_dict)} stocks cleaned successfully")
    print(f"{'='*40}")

    return cleaned_dict


def get_cleaning_report(df, ticker=""):
    """
    Generates a detailed data quality report.

    Inputs:
        df     (DataFrame) : Stock DataFrame
        ticker (str)       : Stock name

    Output:
        report (dict) : Data quality metrics
    """

    report = {
        'ticker'        : ticker,
        'total_rows'    : len(df),
        'total_columns' : len(df.columns),
        'date_start'    : str(df.index[0].date()),
        'date_end'      : str(df.index[-1].date()),
        'missing_values': int(df.isnull().sum().sum()),
        'duplicate_rows': int(df.index.duplicated().sum()),
        'zero_prices'   : int((df[['Open','High','Low','Close']] <= 0).sum().sum()),
        'mean_volume'   : int(df['Volume'].mean()),
        'price_min'     : float(df['Close'].min()),
        'price_max'     : float(df['Close'].max()),
    }

    return report