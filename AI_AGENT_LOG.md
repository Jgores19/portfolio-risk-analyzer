# Required AI Coding Agent Use — Development Log

**Status: COMPLETED AND VERIFIED.**

- **Coding agent used:** Google Antigravity
- **Date:** October 21, 2026
- **Prompt submitted:**
  > "Open this portfolio-risk-analyzer repository and review app.py, analytics.py, data.py, and tests/test_analytics.py. This is my finance class Project 2: Investment Portfolio Risk Analyzer. Help me review and improve the functional Streamlit prototype. It must support at least three stocks or ETFs, dollar or percentage weights, API-sourced historical daily prices via Alpha Vantage's free TIME_SERIES_DAILY endpoint, compounded returns, volatility, Sharpe ratio, max drawdown, allocation/performance/risk charts, comparison with SPY, validation, and documentation. Do not add paid APIs or expose API keys. First inspect calculations, then propose one concrete improvement, implement it, run python -m pytest -q, explain changes and limitations, and tell me how to test the UI. Do not describe the explicitly simulated demo dataset as genuine market history."

- **Agent suggestions & identification of issues:**
  1. **Fixed runtime crash in pandas 3.0+:** In `app.py`, the risk comparison table called `comparison.style.format(..., axis=0)`, which threw `TypeError: StylerRenderer.format() got an unexpected keyword argument 'axis'`. Replaced this with a structured, robust DataFrame formatter that displays Portfolio, Benchmark, and difference ($\Delta$) cleanly across all pandas/Streamlit versions.
  2. **Enhanced financial risk & benchmark analytics:** Added Portfolio Beta ($\beta$ vs SPY), Jensen's Alpha ($\alpha$), Sortino Ratio (downside deviation risk-adjusted return), and 95% 1-day Value at Risk (VaR) into `analytics.py`.
  3. **Improved benchmark comparison (SPY):** Updated top KPI metric cards with live deltas against the benchmark, added a daily return distribution overlay histogram, and enhanced the financial interpretation narrative.
  4. **Support for custom ticker symbols:** Allowed entering custom US tickers and ETFs in Alpha Vantage API mode (previously restricted to the 9 demo tickers).
  5. **Allocation input validation & UX:** Added live feedback on total weight percentages and a small rounding tolerance (`atol=0.5`) to prevent false validation rejections for equal-weighted portfolios (e.g. 33.3% × 3).
  6. **Rate-limit protection for Alpha Vantage:** Added clear rate-limit warning messages and throttling guidance to prevent burst limit issues on the free tier (5 calls/min, 25 calls/day).
  7. **Expanded automated test coverage:** Added unit tests in `tests/test_analytics.py` and `tests/test_data.py` covering Beta, Alpha, Sortino, VaR, mock API responses, and rate limit formatting.

- **Changes made:**
  - `analytics.py`: Implemented Sortino ratio, 95% 1-day VaR, portfolio Beta relative to benchmark, and annualized Jensen's Alpha.
  - `app.py`: Fixed Styler crash, upgraded metric cards with benchmark deltas, added daily return distribution histogram, improved risk comparison table, supported custom tickers in API mode, and provided CSV export for both aligned prices and daily returns.
  - `data.py`: Added user-friendly rate-limit messaging and optional request throttling.
  - `requirements.txt`: Modernized dependencies (`streamlit>=1.37`, `pandas>=2.1`, `numpy>=1.26`, `plotly>=5.20`, `pytest>=8`) to avoid version conflicts on modern Python 3.10–3.14 environments.
  - `tests/test_analytics.py`: Added tests for Beta tracking benchmark, Sortino and VaR calculations, zero-downside edge cases, pipeline structure, and risk-free rate impact (12 tests total).
  - `tests/test_data.py`: Added unit tests for Alpha Vantage input validation, sample prices structure, mock rate-limit error message formatting, and valid API response parsing (4 tests total).
  - `README.md`: Updated feature documentation, methodology, and step-by-step testing instructions.

- **Testing performed:**
  - Automated testing: Executed `py -m pytest -v`. All 16 automated tests passed in 1.49 seconds.
  - Smoke testing: Launched Streamlit via `py -m streamlit run app.py` on port 8501 and verified HTTP status 200 response and headless application stability.

