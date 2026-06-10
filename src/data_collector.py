# ============================================================
# src/data_collector.py
# Purpose : Download and load stock data from Yahoo Finance
# Author  : Shivam
# ============================================================

import yfinance as yf
import pandas as pd
import os

SAVE_DIR = 'data/raw'


def download_stock_data(ticker, start_date, end_date, save=True):
    """
    Downloads historical OHLCV data for one stock from Yahoo Finance.

    Inputs:
        ticker     (str)  : Stock symbol e.g. 'AAPL', 'RELIANCE.NS'
        start_date (str)  : 'YYYY-MM-DD' format
        end_date   (str)  : 'YYYY-MM-DD' format
        save       (bool) : Save as CSV? Default is True

    Output:
        df (DataFrame) : Table of stock data OR None if failed
    """

    print(f"\nDownloading: {ticker}...")

    try:
        df = yf.download(
            ticker,
            start=start_date,
            end=end_date,
            progress=False
        )
    except Exception as e:
        print(f"ERROR downloading {ticker}: {e}")
        return None

    # ── Validate Download ────────────────────────────────────
    if df.empty:
        print(f"WARNING: No data found for '{ticker}'.")
        print("Check if ticker symbol is correct.")
        return None

    # ── Flatten MultiIndex Columns ───────────────────────────
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
        # newer yfinance returns ('Close','AAPL') style columns
        # this flattens them to just 'Close'

    # ── Select Available Columns ─────────────────────────────
    available = [c for c in ['Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']
                 if c in df.columns]
    df = df[available]

    # ── Handle Missing Adj Close ─────────────────────────────
    if 'Adj Close' not in df.columns and 'Close' in df.columns:
        df['Adj Close'] = df['Close']
        # New yfinance already adjusts Close for splits/dividends
        # We create Adj Close as a copy for consistency

    # ── Reorder Columns ──────────────────────────────────────
    df = df[['Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']]

    # ── Round Price Columns ──────────────────────────────────
    price_cols = ['Open', 'High', 'Low', 'Close', 'Adj Close']
    df[price_cols] = df[price_cols].round(2)

    # ── Save to CSV ──────────────────────────────────────────
    if save:
        os.makedirs(SAVE_DIR, exist_ok=True)
        filepath = f"{SAVE_DIR}/{ticker}_{start_date}_{end_date}.csv"
        df.to_csv(filepath)
        print(f"Saved to: {filepath}")

    print(f"Downloaded {len(df)} rows for {ticker}")
    return df


def download_multiple_stocks(tickers, start_date, end_date):
    """
    Downloads data for a list of stocks.

    Inputs:
        tickers    (list) : e.g. ['AAPL', 'MSFT', 'GOOGL']
        start_date (str)  : 'YYYY-MM-DD'
        end_date   (str)  : 'YYYY-MM-DD'

    Output:
        data_dict (dict) : {'AAPL': DataFrame, 'MSFT': DataFrame ...}
    """

    data_dict = {}

    for ticker in tickers:
        df = download_stock_data(ticker, start_date, end_date)
        if df is not None:
            data_dict[ticker] = df

    print(f"\n{'='*40}")
    print(f"Download Complete!")
    print(f"Successful : {len(data_dict)} stocks")
    print(f"Failed     : {len(tickers) - len(data_dict)} stocks")
    print(f"{'='*40}")

    return data_dict


def load_stock_data(ticker, start_date, end_date):
    """
    Loads from CSV if exists, otherwise downloads.

    Inputs:
        ticker     (str) : Stock symbol
        start_date (str) : 'YYYY-MM-DD'
        end_date   (str) : 'YYYY-MM-DD'

    Output:
        df (DataFrame) : Stock data
    """

    filepath = f"{SAVE_DIR}/{ticker}_{start_date}_{end_date}.csv"

    if os.path.exists(filepath):
        print(f"Loading {ticker} from saved CSV...")
        df = pd.read_csv(
            filepath,
            index_col='Date',
            parse_dates=True
        )
        return df
    else:
        print(f"CSV not found. Downloading {ticker}...")
        return download_stock_data(ticker, start_date, end_date, save=True)