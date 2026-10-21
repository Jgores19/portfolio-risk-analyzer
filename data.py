"""Alpha Vantage TIME_SERIES_DAILY (free compact series) and reproducible demonstration data."""
from datetime import datetime
import time
import numpy as np
import pandas as pd
import requests

API_URL = 'https://www.alphavantage.co/query'
DEMO_TICKERS = ['AAPL', 'MSFT', 'NVDA', 'SPY', 'VTI', 'QQQ', 'GOOGL', 'AMZN', 'JPM']


class DataSourceError(ValueError):
    pass


def fetch_daily_close(ticker: str, api_key: str) -> pd.Series:
    ticker = ticker.strip().upper()
    if not ticker or not api_key.strip():
        raise DataSourceError('A ticker and Alpha Vantage API key are required.')
    try:
        response = requests.get(API_URL, params={
            'function': 'TIME_SERIES_DAILY', 'symbol': ticker,
            'outputsize': 'compact', 'apikey': api_key.strip(),
        }, timeout=20)
        response.raise_for_status()
        payload = response.json()
    except (requests.RequestException, ValueError) as exc:
        raise DataSourceError(f'Could not retrieve {ticker}: {exc}') from exc
    daily = payload.get('Time Series (Daily)')
    if not isinstance(daily, dict) or not daily:
        raw_msg = payload.get('Note') or payload.get('Information') or payload.get('Error Message') or 'No daily data returned.'
        if 'frequency' in raw_msg.lower() or 'premium' in raw_msg.lower() or '25 requests' in raw_msg.lower():
            msg = f"{raw_msg} [Free rate limit reached: max 5 calls/min and 25 calls/day. Please wait ~60s or switch to Illustrative demo dataset.]"
        else:
            msg = raw_msg
        raise DataSourceError(f'{ticker}: {msg}')
    try:
        s = pd.Series({pd.Timestamp(date): float(row['4. close']) for date, row in daily.items()}, name=ticker).sort_index()
    except (TypeError, ValueError, KeyError) as exc:
        raise DataSourceError(f'Unexpected price response for {ticker}.') from exc
    if (s <= 0).any() or len(s) < 30:
        raise DataSourceError(f'{ticker} returned too few valid positive closing prices (minimum 30 trading days).')
    return s


def fetch_portfolio(tickers: list[str], api_key: str, delay_seconds: float = 0.5) -> pd.DataFrame:
    # All symbols fetched separately; API quotas apply.
    unique = list(dict.fromkeys(tickers))
    series = []
    for i, t in enumerate(unique):
        if i > 0 and delay_seconds > 0:
            time.sleep(delay_seconds)
        series.append(fetch_daily_close(t, api_key))
    return pd.concat(series, axis=1)


def sample_prices() -> pd.DataFrame:
    """Fixed-seed illustrative simulated data. Not historical prices or market observations."""
    rng = np.random.default_rng(2026)
    dates = pd.bdate_range('2025-10-01', periods=252)
    market = rng.normal(0.00035, 0.010, len(dates))
    specs = {
        'AAPL': (0.0003, 0.80, 0.009, 180),
        'MSFT': (0.00045, 0.88, 0.008, 425),
        'NVDA': (0.0008, 1.35, 0.019, 110),
        'SPY': (0.0001, 1.00, 0.001, 550),
        'VTI': (0.0001, 0.99, 0.002, 290),
        'QQQ': (0.0003, 1.16, 0.005, 480),
        'GOOGL': (0.0003, 1.05, 0.010, 175),
        'AMZN': (0.0005, 1.11, 0.012, 200),
        'JPM': (0.0002, 0.72, 0.010, 210),
    }
    out = {}
    for ticker, (drift, beta, noise, start) in specs.items():
        returns = drift + beta * market + rng.normal(0, noise, len(dates))
        out[ticker] = start * np.cumprod(1 + returns)
    return pd.DataFrame(out, index=dates)
