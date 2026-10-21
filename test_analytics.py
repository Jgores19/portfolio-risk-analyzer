import numpy as np
import pandas as pd
import pytest
from analytics import analyze, normalize_weights
from data import sample_prices


def test_weights_normalization():
    assert np.allclose(normalize_weights([4000, 3500, 2500]), [.4, .35, .25])


def test_reject_bad_weights():
    with pytest.raises(ValueError):
        normalize_weights([-1, 2, 3])


def test_zero_volatility_has_undefined_sharpe():
    dates = pd.bdate_range('2026-01-01', periods=40)
    p = pd.DataFrame({t: np.full(40, 100.0) for t in ['A', 'B', 'C', 'SPY']}, index=dates)
    x = analyze(p, ['A', 'B', 'C'], [1, 1, 1], 'SPY')
    assert x['portfolio']['Total return'] == 0
    assert np.isnan(x['portfolio']['Sharpe ratio'])
    assert x['portfolio']['Maximum drawdown'] == 0


def test_compounding_and_drawdown():
    dates = pd.bdate_range('2026-01-01', periods=40)
    arr = np.array([100.0] * 20 + [80.0] * 20)
    p = pd.DataFrame({t: arr for t in ['A', 'B', 'C', 'SPY']}, index=dates)
    x = analyze(p, ['A', 'B', 'C'], [2, 3, 5], 'SPY')
    assert x['portfolio']['Total return'] == pytest.approx(-0.20)
    assert x['portfolio']['Maximum drawdown'] == pytest.approx(-0.20)


def test_sample_deterministic():
    assert sample_prices().equals(sample_prices())
    assert len(sample_prices()) == 252


def test_beta_and_alpha_when_tracking_benchmark():
    dates = pd.bdate_range('2026-01-01', periods=50)
    # Generate mock benchmark with slight random movement
    rng = np.random.default_rng(42)
    daily_returns = rng.normal(0.0005, 0.01, 50)
    prices = 100 * np.cumprod(1 + daily_returns)
    p = pd.DataFrame({'A': prices, 'B': prices, 'C': prices, 'SPY': prices}, index=dates)
    x = analyze(p, ['A', 'B', 'C'], [0.4, 0.35, 0.25], 'SPY', risk_free_rate=0.03)
    assert x['beta'] == pytest.approx(1.0, abs=1e-6)
    assert x['alpha'] == pytest.approx(0.0, abs=1e-6)


def test_sortino_and_var():
    p = sample_prices()
    res = analyze(p, ['AAPL', 'MSFT', 'NVDA'], [40, 35, 25], 'SPY')
    port = res['portfolio']
    assert np.isfinite(port['Sortino ratio'])
    assert np.isfinite(port['Daily VaR (95%)'])
    assert port['Daily VaR (95%)'] < 0  # 5th percentile is negative in normal market distributions


def test_zero_downside_sortino():
    dates = pd.bdate_range('2026-01-01', periods=40)
    # Strictly increasing prices -> no negative returns
    arr = np.linspace(100.0, 150.0, 40)
    p = pd.DataFrame({t: arr for t in ['A', 'B', 'C', 'SPY']}, index=dates)
    x = analyze(p, ['A', 'B', 'C'], [1, 1, 1], 'SPY')
    assert np.isnan(x['portfolio']['Sortino ratio'])


def test_reject_fewer_than_three_securities():
    p = sample_prices()
    with pytest.raises(ValueError):
        analyze(p, ['AAPL', 'MSFT'], [50, 50], 'SPY')


def test_full_pipeline_output_structure():
    p = sample_prices()
    res = analyze(p, ['AAPL', 'MSFT', 'NVDA'], [40, 35, 25], 'SPY', 0.03)
    expected_top_keys = {
        'prices', 'returns', 'portfolio_daily_returns', 'growth',
        'drawdown', 'portfolio', 'benchmark', 'beta', 'alpha',
        'weights', 'correlations', 'start', 'end', 'observations'
    }
    assert expected_top_keys.issubset(res.keys())
    expected_metric_keys = {
        'Total return', 'Annualized return', 'Annualized volatility',
        'Sharpe ratio', 'Sortino ratio', 'Maximum drawdown', 'Daily VaR (95%)'
    }
    assert expected_metric_keys == set(res['portfolio'].keys())
    assert expected_metric_keys == set(res['benchmark'].keys())
    assert len(res['weights']) == 3
    assert np.isclose(res['weights'].sum(), 1.0)


def test_risk_free_rate_impact():
    p = sample_prices()
    res_low_rf = analyze(p, ['AAPL', 'MSFT', 'NVDA'], [40, 35, 25], 'SPY', risk_free_rate=0.01)
    res_high_rf = analyze(p, ['AAPL', 'MSFT', 'NVDA'], [40, 35, 25], 'SPY', risk_free_rate=0.05)
    # Higher risk-free rate must reduce Sharpe ratio
    assert res_low_rf['portfolio']['Sharpe ratio'] > res_high_rf['portfolio']['Sharpe ratio']
    # Higher risk-free rate must reduce Sortino ratio
    assert res_low_rf['portfolio']['Sortino ratio'] > res_high_rf['portfolio']['Sortino ratio']


def test_too_few_trading_days_rejected():
    dates = pd.bdate_range('2026-01-01', periods=20)
    p = pd.DataFrame({t: np.linspace(100, 110, 20) for t in ['A', 'B', 'C', 'SPY']}, index=dates)
    with pytest.raises(ValueError, match='minimum 30 trading days'):
        analyze(p, ['A', 'B', 'C'], [1, 1, 1], 'SPY')


