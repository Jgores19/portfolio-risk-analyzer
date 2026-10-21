"""Pure portfolio analytics; daily close-to-close arithmetic returns."""
import numpy as np
import pandas as pd

DAYS_PER_YEAR = 252


def normalize_weights(amounts):
    values = np.asarray(amounts, dtype=float)
    if values.ndim != 1 or len(values) < 3 or not np.isfinite(values).all() or (values < 0).any() or values.sum() <= 0:
        raise ValueError('Enter at least three nonnegative allocations with a positive total.')
    return values / values.sum()


def analyze(prices: pd.DataFrame, tickers: list[str], weights, benchmark: str, risk_free_rate: float = 0.03):
    """Assumes end-of-day daily rebalancing to constant portfolio weights."""
    cols = list(dict.fromkeys(tickers + [benchmark]))
    if len(set(tickers)) < 3 or any(t not in prices.columns for t in cols):
        raise ValueError('Three distinct securities and a benchmark with price data are required.')
    p = prices[cols].apply(pd.to_numeric, errors='coerce').replace([np.inf, -np.inf], np.nan).dropna()
    if len(p) < 30 or (p <= 0).any().any():
        raise ValueError('Not enough overlapping valid prices (minimum 30 trading days).')
    w = normalize_weights(weights)
    r = p.pct_change().dropna()
    portfolio_r = r[tickers].dot(w)
    benchmark_r = r[benchmark]
    portfolio_growth = pd.concat([pd.Series([1.0], index=[p.index[0]]), (1 + portfolio_r).cumprod()])
    benchmark_growth = pd.concat([pd.Series([1.0], index=[p.index[0]]), (1 + benchmark_r).cumprod()])
    growth = pd.DataFrame({'Portfolio': portfolio_growth, benchmark: benchmark_growth})
    drawdown = growth.div(growth.cummax()).sub(1)

    def metrics(ret, growth_col):
        n = len(ret)
        vol = float(ret.std(ddof=1) * np.sqrt(DAYS_PER_YEAR))
        annual_return = float(growth_col.iloc[-1] ** (DAYS_PER_YEAR / n) - 1)
        sharpe = (float(ret.mean()) * DAYS_PER_YEAR - risk_free_rate) / vol if vol > 0 else float('nan')
        # Downside deviation for Sortino ratio: considers only downside volatility (returns < 0)
        neg_returns = np.minimum(ret, 0.0)
        downside_dev = float(np.sqrt(np.mean(neg_returns ** 2)) * np.sqrt(DAYS_PER_YEAR))
        sortino = (float(ret.mean()) * DAYS_PER_YEAR - risk_free_rate) / downside_dev if downside_dev > 0 else float('nan')
        # Historical Daily Value at Risk at 95% confidence (5th percentile of daily returns)
        var_95 = float(np.percentile(ret, 5))
        return {
            'Total return': float(growth_col.iloc[-1] - 1),
            'Annualized return': annual_return,
            'Annualized volatility': vol,
            'Sharpe ratio': float(sharpe),
            'Sortino ratio': float(sortino),
            'Maximum drawdown': float((growth_col / growth_col.cummax() - 1).min()),
            'Daily VaR (95%)': var_95,
        }

    port_metrics = metrics(portfolio_r, growth['Portfolio'])
    bench_metrics = metrics(benchmark_r, growth[benchmark])

    # Portfolio Beta and Jensen's Alpha relative to Benchmark
    bench_var = float(benchmark_r.var(ddof=1))
    cov_pb = float(portfolio_r.cov(benchmark_r))
    beta = (cov_pb / bench_var) if bench_var > 0 else float('nan')
    if np.isfinite(beta) and np.isfinite(port_metrics['Annualized return']) and np.isfinite(bench_metrics['Annualized return']):
        alpha = (port_metrics['Annualized return'] - risk_free_rate) - beta * (bench_metrics['Annualized return'] - risk_free_rate)
    else:
        alpha = float('nan')

    return {
        'prices': p, 'returns': r, 'portfolio_daily_returns': portfolio_r,
        'growth': growth, 'drawdown': drawdown,
        'portfolio': port_metrics,
        'benchmark': bench_metrics,
        'beta': float(beta),
        'alpha': float(alpha),
        'weights': pd.Series(w, index=tickers),
        'correlations': r[tickers].corr(),
        'start': p.index[0], 'end': p.index[-1], 'observations': len(r),
    }
