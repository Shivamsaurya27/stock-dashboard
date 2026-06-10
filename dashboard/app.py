# ============================================================
# dashboard/app.py
# Purpose : Stock Market Analytics Dashboard
# Theme   : Dark + Colored Accents
# Author  : Shivam
# ============================================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data_collector import download_multiple_stocks
from src.data_cleaner import clean_multiple_stocks
from src.indicators import add_all_indicators

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title            = "Stock Analytics",
    page_icon             = "📈",
    layout                = "wide",
    initial_sidebar_state = "collapsed"
)

# ============================================================
# LOAD CSS
# ============================================================

def load_css():
    css_path = os.path.join(os.path.dirname(__file__), 'style.css')
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# ============================================================
# HIDE SIDEBAR COMPLETELY
# ============================================================

st.markdown("""
    <style>
        [data-testid="stSidebar"]               { display: none !important; }
        [data-testid="stSidebarCollapsedControl"]{ display: none !important; }
        [data-testid="collapsedControl"]         { display: none !important; }
    </style>
""", unsafe_allow_html=True)

# ============================================================
# COLOR PALETTE
# ============================================================

STOCK_COLORS = {
    'AAPL'        : '#60a5fa',
    'MSFT'        : '#a78bfa',
    'TSLA'        : '#f87171',
    'RELIANCE.NS' : '#34d399',
    'TCS.NS'      : '#fbbf24',
    '^NSEI'       : '#fb923c',
}

def make_theme(height=420):
    return dict(
        height        = height,
        paper_bgcolor = '#0d0d0d',
        plot_bgcolor  = '#0d0d0d',
        font          = dict(
            family = 'Space Grotesk, sans-serif',
            color  = '#666666',
            size   = 11
        ),
        xaxis = dict(
            gridcolor = '#161616',
            linecolor = '#222222',
            tickcolor = '#222222',
            tickfont  = dict(color='#555555', size=10),
            showgrid  = True,
            zeroline  = False,
        ),
        yaxis = dict(
            gridcolor = '#161616',
            linecolor = '#222222',
            tickcolor = '#222222',
            tickfont  = dict(color='#555555', size=10),
            showgrid  = True,
            zeroline  = False,
        ),
        legend = dict(
            bgcolor     = '#0d0d0d',
            bordercolor = '#1e1e1e',
            borderwidth = 1,
            font        = dict(color='#888888', size=11)
        ),
        hoverlabel = dict(
            bgcolor     = '#1a1a1a',
            bordercolor = '#333333',
            font        = dict(
                color  = '#ffffff',
                family = 'Space Grotesk',
                size   = 12
            )
        ),
        margin = dict(l=8, r=8, t=16, b=8),
    )

# ============================================================
# CONSTANTS
# ============================================================

US_STOCKS     = ['AAPL', 'MSFT', 'TSLA']
INDIAN_STOCKS = ['RELIANCE.NS', 'TCS.NS', '^NSEI']
ALL_TICKERS   = US_STOCKS + INDIAN_STOCKS
START_DATE    = '2020-01-01'
END_DATE      = '2024-01-01'

TICKER_NAMES = {
    'AAPL'        : 'Apple',
    'MSFT'        : 'Microsoft',
    'TSLA'        : 'Tesla',
    'RELIANCE.NS' : 'Reliance',
    'TCS.NS'      : 'TCS',
    '^NSEI'       : 'Nifty 50'
}

# ============================================================
# DATA LOADING
# ============================================================

@st.cache_data
def load_all_data():
    data     = download_multiple_stocks(ALL_TICKERS, START_DATE, END_DATE)
    cleaned  = clean_multiple_stocks(data)
    enriched = {}
    for ticker in ALL_TICKERS:
        enriched[ticker] = add_all_indicators(cleaned[ticker], ticker)
    return enriched

# ============================================================
# HELPER
# ============================================================

def section_label(left, right):
    st.markdown(f"""
        <p style='
            font-size     : 10px;
            letter-spacing: 3px;
            color         : #3a3a3a;
            text-transform: uppercase;
            margin        : 28px 0 10px 0;
            font-weight   : 500;
        '>{left} &nbsp;<span style='color:#222222'>·</span>&nbsp; {right}</p>
    """, unsafe_allow_html=True)

# ============================================================
# LOAD DATA
# ============================================================

with st.spinner("Fetching market data..."):
    data = load_all_data()

# ============================================================
# HEADER
# ============================================================

col_logo, col_title = st.columns([0.5, 11])

with col_logo:
    st.markdown("""
        <div style='
            width          : 48px;
            height         : 48px;
            background     : linear-gradient(135deg, #1a1a1a 0%, #222222 100%);
            border-radius  : 12px;
            border         : 1px solid #2a2a2a;
            display        : flex;
            align-items    : center;
            justify-content: center;
            margin-top     : 6px;
            font-size      : 24px;
        '>▲</div>
    """, unsafe_allow_html=True)

with col_title:
    st.markdown("""
        <div style='padding: 2px 0 0 4px'>
            <span style='
                font-size     : 10px;
                letter-spacing: 4px;
                color         : #333333;
                text-transform: uppercase;
                font-weight   : 500;
            '>Market Intelligence</span>
            <div style='
                font-size     : 1.9rem;
                color         : #ffffff;
                font-weight   : 700;
                letter-spacing: -1px;
                line-height   : 1.2;
                margin-top    : 2px;
            '>Stock Analytics
                <span style='color:#2a2a2a'>Dashboard</span>
            </div>
            <div style='
                font-size     : 12px;
                color         : #333333;
                margin-top    : 4px;
                letter-spacing: 0.5px;
            '>
                <span style='color:#60a5fa'>●</span> Apple &nbsp;
                <span style='color:#a78bfa'>●</span> Microsoft &nbsp;
                <span style='color:#f87171'>●</span> Tesla &nbsp;
                <span style='color:#34d399'>●</span> Reliance &nbsp;
                <span style='color:#fbbf24'>●</span> TCS &nbsp;
                <span style='color:#fb923c'>●</span> Nifty 50
            </div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
st.markdown("<hr style='border-color:#1a1a1a; margin:0'>", unsafe_allow_html=True)

# ============================================================
# CONTROLS BAR — Always Visible at Top
# ============================================================

st.markdown("""
    <div style='
        background    : #111111;
        border        : 1px solid #1e1e1e;
        border-radius : 12px;
        padding       : 16px 20px;
        margin        : 16px 0;
    '>
        <span style='
            font-size     : 10px;
            letter-spacing: 3px;
            color         : #333333;
            text-transform: uppercase;
        '>Dashboard Controls</span>
    </div>
""", unsafe_allow_html=True)

# Controls in one clean row
ctrl1, ctrl2, ctrl3 = st.columns([2, 3, 3])

with ctrl1:
    st.markdown("""
        <p style='font-size:11px; color:#444444;
        margin-bottom:6px; letter-spacing:1px'>
        SELECT STOCK</p>
    """, unsafe_allow_html=True)
    selected_ticker = st.selectbox(
        "stock",
        options     = ALL_TICKERS,
        format_func = lambda x: f"{TICKER_NAMES[x]}  ({x})",
        label_visibility = "collapsed"
    )

with ctrl2:
    st.markdown("""
        <p style='font-size:11px; color:#444444;
        margin-bottom:6px; letter-spacing:1px'>
        MOVING AVERAGES</p>
    """, unsafe_allow_html=True)
    ma_options = st.multiselect(
        "ma",
        options  = ['SMA_20', 'SMA_50', 'SMA_200'],
        default  = ['SMA_20', 'SMA_50'],
        label_visibility = "collapsed"
    )

with ctrl3:
    # Live returns for all stocks
    st.markdown("""
        <p style='font-size:11px; color:#444444;
        margin-bottom:6px; letter-spacing:1px'>
        TOTAL RETURNS</p>
    """, unsafe_allow_html=True)
    ret_cols = st.columns(6)
    for i, ticker in enumerate(ALL_TICKERS):
        c   = STOCK_COLORS[ticker]
        ret = round(data[ticker]['Cumulative_Return_Pct'].iloc[-1], 1)
        sign = "+" if ret > 0 else ""
        ret_cols[i].markdown(f"""
            <div style='text-align:center'>
                <div style='
                    font-size  : 9px;
                    color      : #444444;
                    letter-spacing: 1px;
                '>{TICKER_NAMES[ticker].upper()}</div>
                <div style='
                    font-size  : 13px;
                    color      : {c};
                    font-weight: 600;
                    margin-top : 2px;
                '>{sign}{ret}%</div>
            </div>
        """, unsafe_allow_html=True)

st.markdown("<hr style='border-color:#1a1a1a; margin:8px 0 0 0'>", unsafe_allow_html=True)

# ============================================================
# SELECTED STOCK
# ============================================================

df    = data[selected_ticker]
name  = TICKER_NAMES[selected_ticker]
color = STOCK_COLORS[selected_ticker]

# ============================================================
# SECTION 1 — METRICS
# ============================================================

section_label(name, "Key Metrics")

total_return = df['Cumulative_Return_Pct'].iloc[-1]
annual_vol   = df['Daily_Return'].std() * np.sqrt(252) * 100
best_day     = df['Daily_Return'].max() * 100
worst_day    = df['Daily_Return'].min() * 100
start_price  = df['Adj Close'].iloc[0]
end_price    = df['Adj Close'].iloc[-1]

c1,c2,c3,c4,c5 = st.columns(5)
c1.metric("Total Return",      f"{total_return:.1f}%", f"{total_return:.1f}%")
c2.metric("Annual Volatility", f"{annual_vol:.1f}%")
c3.metric("Best Single Day",   f"+{best_day:.2f}%",    f"{best_day:.2f}%")
c4.metric("Worst Single Day",  f"{worst_day:.2f}%",    f"{worst_day:.2f}%")
c5.metric("End Price",         f"{end_price:.2f}",     f"{end_price-start_price:.2f}")

# ============================================================
# SECTION 2 — PRICE CHART
# ============================================================

section_label(name, "Price History & Moving Averages")

fig_price = go.Figure()

fig_price.add_trace(go.Scatter(
    x         = df.index,
    y         = df['Adj Close'],
    fill      = 'tozeroy',
    fillcolor = f"rgba({int(color[1:3],16)},{int(color[3:5],16)},{int(color[5:7],16)},0.05)",
    line      = dict(color=color, width=2),
    name      = 'Price',
    hovertemplate = "<b>%{x|%d %b %Y}</b><br>Price: %{y:.2f}<extra></extra>"
))

ma_styles = {
    'SMA_20'  : ('#ffffff', 'dot',   1.0, 'SMA 20'),
    'SMA_50'  : ('#888888', 'dash',  1.0, 'SMA 50'),
    'SMA_200' : ('#555555', 'solid', 1.5, 'SMA 200'),
}

for ma in ma_options:
    if ma in df.columns:
        c, dash, w, label = ma_styles[ma]
        fig_price.add_trace(go.Scatter(
            x    = df.index,
            y    = df[ma],
            name = label,
            line = dict(color=c, width=w, dash=dash),
            hovertemplate = f"<b>%{{x|%d %b %Y}}</b><br>{label}: %{{y:.2f}}<extra></extra>"
        ))

theme = make_theme(440)
fig_price.update_layout(hovermode="x unified", **theme)
st.plotly_chart(fig_price, use_container_width=True)

# ============================================================
# SECTION 3 — RETURNS
# ============================================================

section_label(name, "Daily Returns")

col1, col2 = st.columns([3, 2])

with col1:
    pos_color = f"rgba({int(color[1:3],16)},{int(color[3:5],16)},{int(color[5:7],16)},0.8)"
    neg_color = "rgba(248, 113, 113, 0.75)"

    fig_ret = go.Figure()
    fig_ret.add_trace(go.Bar(
        x = df.index,
        y = df['Daily_Return'] * 100,
        marker_color = np.where(
            df['Daily_Return'] >= 0,
            pos_color,
            neg_color
        ),
        name = 'Daily Return',
        hovertemplate = "<b>%{x|%d %b %Y}</b><br>Return: %{y:.2f}%<extra></extra>"
    ))
    theme_ret = make_theme(340)
    theme_ret['yaxis']['title'] = dict(
        text="Return (%)", font=dict(color='#444444'))
    fig_ret.update_layout(showlegend=False, **theme_ret)
    st.plotly_chart(fig_ret, use_container_width=True)

with col2:
    fig_hist = go.Figure()
    fig_hist.add_trace(go.Histogram(
        x      = df['Daily_Return'] * 100,
        nbinsx = 60,
        marker = dict(
            color = f"rgba({int(color[1:3],16)},{int(color[3:5],16)},{int(color[5:7],16)},0.4)",
            line  = dict(
                color = f"rgba({int(color[1:3],16)},{int(color[3:5],16)},{int(color[5:7],16)},0.8)",
                width = 0.5
            )
        ),
        name = 'Distribution'
    ))
    fig_hist.add_vline(
        x          = 0,
        line_dash  = "dash",
        line_color = "#333333",
        line_width = 1.5
    )
    theme_hist = make_theme(340)
    theme_hist['xaxis']['title'] = dict(
        text="Daily Return (%)", font=dict(color='#444444'))
    theme_hist['yaxis']['title'] = dict(
        text="Frequency", font=dict(color='#444444'))
    fig_hist.update_layout(showlegend=False, **theme_hist)
    st.plotly_chart(fig_hist, use_container_width=True)

# ============================================================
# SECTION 4 — CUMULATIVE RETURNS
# ============================================================

section_label("All Stocks", "Cumulative Returns")

fig_cum = go.Figure()

for ticker in ALL_TICKERS:
    df_t = data[ticker]
    c    = STOCK_COLORS[ticker]
    fig_cum.add_trace(go.Scatter(
        x    = df_t.index,
        y    = df_t['Cumulative_Return_Pct'],
        name = TICKER_NAMES[ticker],
        line = dict(color=c, width=1.8),
        hovertemplate = f"<b>{TICKER_NAMES[ticker]}</b><br>%{{x|%d %b %Y}}<br>Return: %{{y:.1f}}%<extra></extra>"
    ))

theme_cum = make_theme(440)
theme_cum['yaxis']['title'] = dict(
    text="Cumulative Return (%)", font=dict(color='#444444'))
fig_cum.update_layout(hovermode="x unified", **theme_cum)
fig_cum.update_layout(legend=dict(orientation="h", y=1.08, x=0))
st.plotly_chart(fig_cum, use_container_width=True)

# ============================================================
# SECTION 5 — VOLATILITY
# ============================================================

section_label(name, "Rolling Volatility")

fig_vol = go.Figure()

r = int(color[1:3], 16)
g = int(color[3:5], 16)
b = int(color[5:7], 16)

fig_vol.add_trace(go.Scatter(
    x         = df.index,
    y         = df['Volatility_21d'] * 100,
    name      = '21-day',
    fill      = 'tozeroy',
    fillcolor = f'rgba({r},{g},{b},0.08)',
    line      = dict(color=color, width=1.5),
    hovertemplate = "<b>%{x|%d %b %Y}</b><br>21d Vol: %{y:.1f}%<extra></extra>"
))

fig_vol.add_trace(go.Scatter(
    x    = df.index,
    y    = df['Volatility_63d'] * 100,
    name = '63-day',
    line = dict(color='#444444', width=1.5, dash='dot'),
    hovertemplate = "<b>%{x|%d %b %Y}</b><br>63d Vol: %{y:.1f}%<extra></extra>"
))

theme_vol = make_theme(360)
theme_vol['yaxis']['title'] = dict(
    text="Annualized Volatility (%)", font=dict(color='#444444'))
fig_vol.update_layout(hovermode="x unified", **theme_vol)
st.plotly_chart(fig_vol, use_container_width=True)

# ============================================================
# SECTION 6 — CORRELATION + RISK VS RETURN
# ============================================================

section_label("All Stocks", "Correlation & Risk vs Return")

col1, col2 = st.columns([1, 1])

with col1:
    returns_df = pd.DataFrame({
        TICKER_NAMES[t]: data[t]['Daily_Return']
        for t in ALL_TICKERS
    })
    corr = returns_df.corr().round(2)

    fig_corr = go.Figure(data=go.Heatmap(
        z            = corr.values,
        x            = corr.columns.tolist(),
        y            = corr.index.tolist(),
        colorscale   = [
            [0.0, '#0d0d0d'],
            [0.3, '#1a1a2e'],
            [0.5, '#16213e'],
            [0.7, '#1e3a5f'],
            [1.0, '#60a5fa'],
        ],
        zmin         = -1,
        zmax         =  1,
        text         = corr.values,
        texttemplate = "%{text}",
        textfont     = dict(size=11, color='#cccccc'),
        showscale    = True,
        colorbar     = dict(
            tickfont    = dict(color='#555555', size=10),
            bgcolor     = '#0d0d0d',
            bordercolor = '#1e1e1e'
        )
    ))
    theme_corr = make_theme(380)
    fig_corr.update_layout(**theme_corr)
    st.plotly_chart(fig_corr, use_container_width=True)

with col2:
    fig_rr = go.Figure()

    for ticker in ALL_TICKERS:
        df_t  = data[ticker]
        c     = STOCK_COLORS[ticker]
        risk  = df_t['Daily_Return'].std() * np.sqrt(252) * 100
        ret   = df_t['Cumulative_Return_Pct'].iloc[-1]
        nname = TICKER_NAMES[ticker]

        fig_rr.add_trace(go.Scatter(
            x    = [risk],
            y    = [ret],
            mode = 'markers+text',
            marker = dict(
                size   = 16,
                color  = c,
                line   = dict(color='#0d0d0d', width=2),
                symbol = 'circle'
            ),
            text          = [nname],
            textposition  = 'top center',
            textfont      = dict(size=10, color=c),
            name          = nname,
            showlegend    = False,
            hovertemplate = f"<b>{nname}</b><br>Risk: %{{x:.1f}}%<br>Return: %{{y:.1f}}%<extra></extra>"
        ))

    theme_rr = make_theme(380)
    theme_rr['xaxis']['title'] = dict(
        text="Risk — Annual Volatility (%)", font=dict(color='#444444'))
    theme_rr['yaxis']['title'] = dict(
        text="Total Return (%)", font=dict(color='#444444'))
    fig_rr.update_layout(**theme_rr)
    st.plotly_chart(fig_rr, use_container_width=True)

# ============================================================
# SECTION 7 — DATA TABLE
# ============================================================

section_label(name, "Data Table")

rows = st.slider("Rows to display", 5, 50, 10)
display_cols = [
    'Open', 'High', 'Low', 'Close', 'Adj Close',
    'Daily_Return', 'SMA_20', 'SMA_50', 'Volatility_21d'
]
st.dataframe(
    df[display_cols].tail(rows).round(3),
    use_container_width=True
)

# ============================================================
# FOOTER
# ============================================================

st.markdown("""
    <div style='
        margin-top     : 56px;
        padding        : 20px 0;
        border-top     : 1px solid #161616;
        display        : flex;
        justify-content: space-between;
        align-items    : center;
    '>
        <span style='font-size:11px; color:#2a2a2a; letter-spacing:2px'>
            📈 STOCK ANALYTICS
        </span>
        <span style='font-size:10px; color:#222222; letter-spacing:1px'>
            BUILT BY SHIVAM &nbsp;·&nbsp;
            PYTHON / PANDAS / PLOTLY / STREAMLIT &nbsp;·&nbsp;
            DATA: YAHOO FINANCE
        </span>
        <span style='font-size:11px; color:#2a2a2a; letter-spacing:2px'>
            2020 – 2024
        </span>
    </div>
""", unsafe_allow_html=True)