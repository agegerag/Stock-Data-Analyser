# Stock Data Analyser

A Python application for fetching, storing, and analysing historical stock price data, with a clean web dashboard built in Streamlit.

> **Live demo:** *(deploy to [Streamlit Cloud](https://streamlit.io/cloud) for free and paste your link here)*

## Overview

This tool pulls real-time and historical stock data from Yahoo Finance via the `yfinance` API and stores it locally in a SQLite database. Users can track multiple stocks, view moving average analysis, and compare portfolio performance through an interactive browser-based dashboard.

Built with Streamlit and Plotly.

## Features

- **Live data ingestion** fetches OHLCV data from Yahoo Finance and falls back to deterministic sample data if the API is unavailable
- **Persistent local storage** saves all price history to a SQLite database that survives between sessions
- **Technical analysis** computes 20-day and 50-day moving averages using Pandas
- **Interactive candlestick charts** with OHLC, MA overlays, and volume bars via Plotly
- **Portfolio comparison** normalised multi-stock performance chart (base = 100)
- **Period performance table** showing start/end price, % change, high and low per stock
- **Full CRUD** to add, update, and remove tracked stocks from the sidebar

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.10+ |
| Web UI | Streamlit |
| Charts | Plotly |
| Data | Pandas |
| Storage | SQLite (via `sqlite3`) |
| Data Source | yfinance (Yahoo Finance API) |

## Getting Started

### 1. Clone the repo
```bash
git clone https://github.com/YOUR_USERNAME/stock-data-analyser.git
cd stock-data-analyser
```

### 2. Install dependencies
```bash
pip install streamlit plotly pandas yfinance
```

### 3. Run the web app
```bash
streamlit run app.py
```

## Project Structure

```
stock-data-analyser/
├── app.py                # Streamlit web dashboard
└── README.md
```

## How It Works

1. **Fetch** - enter a ticker (e.g. `AAPL`) and select a period (1m / 3m / 6m / 1y); the app calls the yfinance API and stores results in SQLite
2. **Analyse** - the dashboard computes MA20/MA50, period high/low, and percentage change from stored data
3. **Compare** - the comparison tab normalises all tracked stocks to a base of 100 for fair performance comparison
4. **Fallback** - if live data is unavailable, the app generates consistent sample data using a seeded random number generator so it remains fully functional offline

## Screenshots

*(Add screenshots here once deployed)*

## Author

**Thabang Kgosiemang**

