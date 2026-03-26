"""
Stock Data Analyser — Streamlit Web App
Wraps the original CLI stock_analyser.py logic into a clean dashboard UI.
"""

import sqlite3
import random
from datetime import datetime, timedelta

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# ─────────────────────────────────────────────────────────────────────────────
# Page config
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Stock Analyser",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:wght@300;400;600&display=swap');

    html, body, [class*="css"] { font-family: 'IBM Plex Sans', sans-serif; }
    .stApp { background-color: #0d1117; color: #e6edf3; }
    h1, h2, h3 { font-family: 'IBM Plex Mono', monospace !important; }

    .metric-card {
        background: #161b22;
        border: 1px solid #30363d;
        border-radius: 8px;
        padding: 16px 20px;
        text-align: center;
    }
    .metric-label {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 11px;
        color: #8b949e;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        margin-bottom: 6px;
    }
    .metric-value {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 22px;
        font-weight: 600;
        color: #e6edf3;
    }
    .metric-value.positive { color: #3fb950; }
    .metric-value.negative { color: #f85149; }

    .stButton > button {
        background: #238636; color: white; border: none;
        border-radius: 6px; font-family: 'IBM Plex Mono', monospace;
        font-size: 13px; padding: 8px 20px;
    }
    .stButton > button:hover { background: #2ea043; }

    footer { visibility: hidden; }
    #MainMenu { visibility: hidden; }
    header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# DB helpers
# ─────────────────────────────────────────────────────────────────────────────
DB_PATH = "stocks.db"
SEED_PRICES = {
    "AAPL": 170.0, "MSFT": 370.0, "GOOGL": 140.0,
    "AMZN": 178.0, "TSLA": 250.0, "NVDA": 800.0,
}


def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS stock_prices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticker TEXT NOT NULL, date TEXT NOT NULL,
            open REAL, high REAL, low REAL, close REAL, volume INTEGER,
            UNIQUE(ticker, date)
        )
    """)
    conn.commit(); conn.close()


def _generate_sample_data(ticker, days=180):
    random.seed(hash(ticker) % 10000)
    base = SEED_PRICES.get(ticker, 100.0)
    rows, price = [], base
    start = datetime.today() - timedelta(days=days)
    for i in range(days):
        date = start + timedelta(days=i)
        if date.weekday() >= 5:
            continue
        change = price * random.uniform(-0.025, 0.027)
        price = max(price + change, 1.0)
        rows.append((
            date.strftime("%Y-%m-%d"),
            round(price * random.uniform(0.995, 1.005), 4),
            round(price * random.uniform(1.000, 1.020), 4),
            round(price * random.uniform(0.980, 1.000), 4),
            round(price, 4),
            random.randint(20_000_000, 80_000_000)
        ))
    return rows


def fetch_and_store(ticker, period="6mo"):
    rows, source = None, "sample"
    try:
        import yfinance as yf
        df = yf.Ticker(ticker).history(period=period)
        if not df.empty:
            rows = [(
                date.strftime("%Y-%m-%d"),
                round(row["Open"], 4), round(row["High"], 4),
                round(row["Low"], 4), round(row["Close"], 4),
                int(row["Volume"])
            ) for date, row in df.iterrows()]
            source = "live"
    except Exception:
        pass
    if not rows:
        days_map = {"1mo": 30, "3mo": 90, "6mo": 180, "1y": 365}
        rows = _generate_sample_data(ticker, days=days_map.get(period, 180))
    conn = sqlite3.connect(DB_PATH)
    conn.execute("DELETE FROM stock_prices WHERE ticker = ?", (ticker,))
    conn.executemany(
        "INSERT OR IGNORE INTO stock_prices (ticker,date,open,high,low,close,volume) VALUES (?,?,?,?,?,?,?)",
        [(ticker, *r) for r in rows]
    )
    conn.commit(); conn.close()
    return len(rows), source


def get_tracked_tickers():
    conn = sqlite3.connect(DB_PATH)
    t = [r[0] for r in conn.execute(
        "SELECT DISTINCT ticker FROM stock_prices ORDER BY ticker"
    ).fetchall()]
    conn.close()
    return t


def load_data(ticker):
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(
        "SELECT date,open,high,low,close,volume FROM stock_prices WHERE ticker=? ORDER BY date ASC",
        conn, params=(ticker,)
    )
    conn.close()
    df["date"] = pd.to_datetime(df["date"])
    df.set_index("date", inplace=True)
    return df


def remove_ticker(ticker):
    conn = sqlite3.connect(DB_PATH)
    conn.execute("DELETE FROM stock_prices WHERE ticker=?", (ticker,))
    conn.commit(); conn.close()


# ─────────────────────────────────────────────────────────────────────────────
# Chart builders
# ─────────────────────────────────────────────────────────────────────────────
BG = "#0d1117"
GRID = "#21262d"


def candlestick_chart(ticker, df):
    df = df.copy()
    df["MA_20"] = df["close"].rolling(20).mean()
    df["MA_50"] = df["close"].rolling(50).mean()

    fig = go.Figure()
    fig.add_trace(go.Candlestick(
        x=df.index, open=df["open"], high=df["high"],
        low=df["low"], close=df["close"], name="OHLC",
        increasing_line_color="#3fb950", decreasing_line_color="#f85149",
        increasing_fillcolor="#3fb950",  decreasing_fillcolor="#f85149",
    ))
    if not df["MA_20"].isna().all():
        fig.add_trace(go.Scatter(x=df.index, y=df["MA_20"], name="MA 20",
            line=dict(color="#58a6ff", width=1.5, dash="dot")))
    if not df["MA_50"].isna().all():
        fig.add_trace(go.Scatter(x=df.index, y=df["MA_50"], name="MA 50",
            line=dict(color="#f0883e", width=1.5, dash="dot")))

    fig.update_layout(
        title=f"{ticker} — Price (OHLC + Moving Averages)",
        template="plotly_dark", paper_bgcolor=BG, plot_bgcolor=BG,
        xaxis=dict(gridcolor=GRID, rangeslider_visible=False),
        yaxis=dict(gridcolor=GRID, title="Price (USD)"),
        legend=dict(bgcolor="#161b22", bordercolor="#30363d", borderwidth=1),
        height=480, margin=dict(l=10, r=10, t=50, b=10),
    )
    return fig


def volume_chart(ticker, df):
    colors = ["#3fb950" if c >= o else "#f85149"
              for c, o in zip(df["close"], df["open"])]
    fig = go.Figure()
    fig.add_trace(go.Bar(x=df.index, y=df["volume"],
                         marker_color=colors, name="Volume"))
    fig.update_layout(
        title=f"{ticker} — Volume",
        template="plotly_dark", paper_bgcolor=BG, plot_bgcolor=BG,
        xaxis=dict(gridcolor=GRID),
        yaxis=dict(gridcolor=GRID, title="Volume"),
        height=220, margin=dict(l=10, r=10, t=50, b=10),
        showlegend=False,
    )
    return fig


def comparison_chart(tickers):
    COLORS = ["#58a6ff", "#3fb950", "#f85149", "#f0883e", "#bc8cff", "#39d353"]
    fig = go.Figure()
    for i, ticker in enumerate(tickers):
        df = load_data(ticker)
        if df.empty:
            continue
        norm = (df["close"] / df["close"].iloc[0]) * 100
        fig.add_trace(go.Scatter(
            x=norm.index, y=norm, name=ticker,
            line=dict(color=COLORS[i % len(COLORS)], width=2),
        ))
    fig.add_hline(y=100, line_dash="dash", line_color="#8b949e", opacity=0.5)
    fig.update_layout(
        title="Portfolio Comparison (Normalised to 100)",
        template="plotly_dark", paper_bgcolor=BG, plot_bgcolor=BG,
        xaxis=dict(gridcolor=GRID),
        yaxis=dict(gridcolor=GRID, title="Normalised Price (Base = 100)"),
        legend=dict(bgcolor="#161b22", bordercolor="#30363d", borderwidth=1),
        height=500, margin=dict(l=10, r=10, t=50, b=10),
    )
    return fig


# ─────────────────────────────────────────────────────────────────────────────
# Summary stats
# ─────────────────────────────────────────────────────────────────────────────
def render_metrics(ticker, df):
    df = df.copy()
    df["MA_20"] = df["close"].rolling(20).mean()
    df["MA_50"] = df["close"].rolling(50).mean()

    latest     = df["close"].iloc[-1]
    first      = df["close"].iloc[0]
    pct        = ((latest - first) / first) * 100
    high       = df["close"].max()
    low        = df["close"].min()
    ma20       = df["MA_20"].iloc[-1]
    ma50       = df["MA_50"].iloc[-1]
    avg_vol    = int(df["volume"].mean())

    pos = "positive" if pct >= 0 else "negative"
    sign = "+" if pct >= 0 else ""

    cols = st.columns(6)
    metrics = [
        ("Current Price",  f"${latest:,.2f}",          ""),
        ("Period Change",  f"{sign}{pct:.2f}%",         pos),
        ("Period High",    f"${high:,.2f}",              ""),
        ("Period Low",     f"${low:,.2f}",               ""),
        ("20-Day MA",      f"${ma20:,.2f}" if not pd.isna(ma20) else "N/A", ""),
        ("50-Day MA",      f"${ma50:,.2f}" if not pd.isna(ma50) else "N/A", ""),
    ]
    for col, (label, value, css_class) in zip(cols, metrics):
        with col:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">{label}</div>
                <div class="metric-value {css_class}">{value}</div>
            </div>
            """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# App
# ─────────────────────────────────────────────────────────────────────────────
init_db()

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📈 Stock Analyser")
    st.markdown("---")

    st.markdown("### Add / Update Stock")
    new_ticker = st.text_input("Ticker Symbol", placeholder="e.g. AAPL, TSLA, NVDA").upper().strip()
    period = st.selectbox("Period", ["1mo", "3mo", "6mo", "1y"], index=2)

    if st.button("Fetch Data", use_container_width=True):
        if new_ticker:
            with st.spinner(f"Fetching {new_ticker}..."):
                n, source = fetch_and_store(new_ticker, period)
            label = "live" if source == "live" else "sample"
            st.success(f"✓ {new_ticker}: {n} days ({label} data)")
            st.rerun()
        else:
            st.warning("Enter a ticker symbol first.")

    st.markdown("---")
    st.markdown("### Tracked Stocks")
    tickers = get_tracked_tickers()
    if tickers:
        for t in tickers:
            col1, col2 = st.columns([3, 1])
            col1.markdown(f"**{t}**")
            if col2.button("✕", key=f"del_{t}"):
                remove_ticker(t)
                st.rerun()
    else:
        st.caption("No stocks tracked yet. Add one above.")

    st.markdown("---")
    st.caption("Data via yfinance · Falls back to sample data if unavailable.")

# ── Main ──────────────────────────────────────────────────────────────────────
st.markdown("# Stock Data Analyser")

tickers = get_tracked_tickers()

if not tickers:
    st.info("👈 Add a stock in the sidebar to get started.")
    st.stop()

tab1, tab2 = st.tabs(["📊  Individual Analysis", "⚖️  Portfolio Comparison"])

# ── Tab 1: Individual ────────────────────────────────────────────────────────
with tab1:
    selected = st.selectbox("Select Stock", tickers)
    df = load_data(selected)

    if df.empty:
        st.warning(f"No data for {selected}.")
    else:
        st.markdown("#### Summary Statistics")
        render_metrics(selected, df)
        st.markdown("<div style='margin-top:24px'></div>", unsafe_allow_html=True)

        st.plotly_chart(candlestick_chart(selected, df), use_container_width=True)
        st.plotly_chart(volume_chart(selected, df), use_container_width=True)

        with st.expander("📋 Raw Data Table"):
            show = df.copy().reset_index()
            show.columns = [c.title() for c in show.columns]
            show["Date"] = show["Date"].dt.strftime("%Y-%m-%d")
            st.dataframe(show, use_container_width=True, hide_index=True)

# ── Tab 2: Comparison ────────────────────────────────────────────────────────
with tab2:
    if len(tickers) < 2:
        st.info("Add at least 2 stocks to compare.")
    else:
        selected_compare = st.multiselect(
            "Select stocks to compare", tickers, default=tickers[:min(4, len(tickers))]
        )
        if len(selected_compare) >= 2:
            st.plotly_chart(comparison_chart(selected_compare), use_container_width=True)

            st.markdown("#### Period Performance")
            perf_data = []
            for t in selected_compare:
                d = load_data(t)
                if not d.empty:
                    pct = ((d["close"].iloc[-1] - d["close"].iloc[0]) / d["close"].iloc[0]) * 100
                    perf_data.append({
                        "Ticker": t,
                        "Start Price": f"${d['close'].iloc[0]:,.2f}",
                        "End Price":   f"${d['close'].iloc[-1]:,.2f}",
                        "Change":      f"{'+' if pct>=0 else ''}{pct:.2f}%",
                        "High":        f"${d['close'].max():,.2f}",
                        "Low":         f"${d['close'].min():,.2f}",
                    })
            st.dataframe(pd.DataFrame(perf_data), use_container_width=True, hide_index=True)
        else:
            st.info("Select at least 2 stocks.")
