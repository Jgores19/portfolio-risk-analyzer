import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
from data import DataSourceError, fetch_daily_close, sample_prices, DEMO_TICKERS


def test_fetch_daily_close_requires_ticker_and_key():
    with pytest.raises(DataSourceError, match='ticker and Alpha Vantage API key are required'):
        fetch_daily_close('', '')

    with pytest.raises(DataSourceError, match='ticker and Alpha Vantage API key are required'):
        fetch_daily_close('AAPL', '   ')


def test_sample_prices_structure():
    df = sample_prices()
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 252
    for t in DEMO_TICKERS:
        assert t in df.columns
    # Check all prices are strictly positive and finite
    assert (df > 0).all().all()
    assert not df.isna().any().any()


@patch('requests.get')
def test_fetch_daily_close_rate_limit_formatting(mock_get):
    mock_resp = MagicMock()
    mock_resp.json.return_value = {
        'Note': 'Thank you for using Alpha Vantage! Our standard API call frequency is 5 calls per minute and 25 calls per day.'
    }
    mock_resp.raise_for_status = MagicMock()
    mock_get.return_value = mock_resp

    with pytest.raises(DataSourceError) as exc_info:
        fetch_daily_close('AAPL', 'dummy_key')

    assert 'Free rate limit reached' in str(exc_info.value)
    assert 'max 5 calls/min' in str(exc_info.value)


@patch('requests.get')
def test_fetch_daily_close_valid_mock(mock_get):
    mock_resp = MagicMock()
    # Mock 35 days of daily prices with real dates
    dates = pd.bdate_range('2026-01-01', periods=35).strftime('%Y-%m-%d')
    time_series = {d: {'4. close': str(100.0 + i)} for i, d in enumerate(dates)}
    mock_resp.json.return_value = {'Time Series (Daily)': time_series}
    mock_resp.raise_for_status = MagicMock()
    mock_get.return_value = mock_resp

    s = fetch_daily_close('AAPL', 'dummy_key')
    assert isinstance(s, pd.Series)
    assert len(s) == 35
    assert s.name == 'AAPL'
    assert s.iloc[0] == 100.0
