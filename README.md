# 📈 Stock Data Analyser

A Python application for fetching, storing, and analysing historical stock price data — with a clean web dashboard built in Streamlit.

> **Live demo:** *(deploy to [Streamlit Cloud](https://streamlit.io/cloud) for free and paste your link here)*

---

## Overview

This tool pulls real-time and historical stock data from Yahoo Finance via the `yfinance` API and stores it locally in a SQLite database. Users can track multiple stocks, view moving average analysis, and compare portfolio performance — all through an interactive browser-based dashboard.

The project started as a command-line tool (`stock_analyser.py`) and was extended into a full web application (`app.py`) using Streamlit and Plotly.

---

## Features

- **Live data ingestion** — fetches OHLCV data from Yahoo Finance; falls back to deterministic sample data if the API is unavailable
- **Persistent local storage** — all price history saved to a SQLite database; data survives between sessions
- **Technical analysis** — 20-day and 50-day moving averages calculated with Pandas
- **Interactive candlestick charts** — OHLC + MA overlays + volume bars via Plotly
- **Portfolio comparison** — normalised multi-stock performance chart (base = 100)
- **Period performance table** — start/end price, % change, high/low per stock
- **Full CRUD** — add, update, and remove tracked stocks from the sidebar

---

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.10+ |
| Web UI | Streamlit |
| Charts | Plotly |
| Data | Pandas |
| Storage | SQLite (via `sqlite3`) |
| Data Source | yfinance (Yahoo Finance API) |
| CLI Version | Matplotlib |

---

## Getting Started

### 1. Clone the repo
```bash
git clone https://github.com/YOUR_USERNAME/stock-analyser.git
cd stock-analyser
```

### 2. Install dependencies
```bash
pip install streamlit plotly pandas yfinance
```

### 3. Run the web app
```bash
streamlit run app.py
```

Or run the original CLI version:
```bash
python stock_analyser.py
```

---

## Project Structure

```
stock-analyser/
├── app.py                # Streamlit web dashboard
├── stock_analyser.py     # Original CLI application
├── stocks.db             # SQLite database (auto-created on first run)
└── README.md
```

---

## Screenshots

> *(Add screenshots here once deployed — sidebar + candlestick chart + comparison tab)*

---

## How It Works

1. **Fetch** — enter a ticker (e.g. `AAPL`) and select a period (1m / 3m / 6m / 1y); the app calls the yfinance API and stores results in SQLite
2. **Analyse** — the dashboard computes MA20/MA50, period high/low, and % change from stored data
3. **Compare** — the comparison tab normalises all tracked stocks to a base of 100 for fair performance comparison
4. **Fallback** — if live data is unavailable (no internet, rate-limited), the app generates consistent sample data using a seeded random number generator so the app remains fully functional

---

## CLI Version

The original `stock_analyser.py` is a standalone terminal application with a numbered menu:

```
==================================================
   STOCK DATA ANALYSER
==================================================
  [1] Add / update a stock
  [2] View summary for a stock
  [3] Generate chart for a stock
  [4] Compare all tracked stocks
  [5] Remove a stock
  [6] Exit
```

Charts are saved as `.png` files using Matplotlib.

---

## Author

**Thabang Aubrey Kgosiemang**
BSc Computer Science & Informatics — University of Johannesburg
[kgosiemangt07@gmail.com](mailto:kgosiemangt07@gmail.com)
