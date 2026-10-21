# Investment Portfolio Risk Analyzer (Project 2)

A Python/Streamlit financial technology prototype that helps investors understand how asset allocation changes portfolio performance, volatility, concentration and downside risk. Users choose **three or more stocks/ETFs**, enter dollar allocations or percentage weights, and compare a weighted portfolio to a market ETF benchmark.

## Features and assignment mapping

- **Securities and allocation:** choose three or more securities; enter dollars or weights; edit allocations interactively; support for custom ticker symbols in API mode.
- **Portfolio returns:** calculates historical daily portfolio returns, cumulative compounded returns, and annualized compounded return (CAGR).
- **Risk measures:** annualized volatility, annualized-mean Sharpe ratio, Sortino ratio (downside deviation), maximum drawdown, and 95% 1-day Value at Risk (VaR).
- **Benchmark comparison (SPY):** benchmark delta indicators on all primary metric cards, portfolio Beta ($\beta$), and annualized Jensen's Alpha ($\alpha$) relative to the S&P 500.
- **Visualizations:** allocation doughnut chart; portfolio vs benchmark growth of $10,000; drawdown time series; daily returns distribution histogram; correlation heatmap.
- **Benchmark:** choose SPY (default), VTI, QQQ, or another listed ETF/stock for comparison.
- **External financial API:** Alpha Vantage `TIME_SERIES_DAILY` for actual historical daily closing prices using your **own free API key** with clear rate-limit handling.
- **Offline demonstration:** deterministic simulated prices, **not real historical prices**, for running without an API key.
- **Error handling:** invalid allocations, missing or short history, invalid tickers, API outages and rate limits produce clear, non-crashing messages.
- **Downloads:** export both the aligned historical closing-price table and daily returns as CSV.

## Install and run (Windows PowerShell)

1. Download/extract the project folder, open PowerShell or a VS Code terminal inside `portfolio-risk-analyzer`.
2. Ensure Python 3.10 or newer is installed. Create a virtual environment:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

3. Launch:

```powershell
python -m streamlit run app.py
```

4. Open the local Streamlit URL printed by the command (usually `http://localhost:8501`). Choose the **Illustrative demo dataset**, keep the default AAPL / MSFT / NVDA weights, and press **Analyze portfolio**. Try adjusting your investments, benchmark, and risk-free rate.
5. For real API data, obtain a free key at [Alpha Vantage](https://www.alphavantage.co/support/#api-key), choose **Alpha Vantage API** in the sidebar, and paste your key in the password field (it is not stored in GitHub). Then analyze.

**Mac/Linux:** Replace the activation command with `source .venv/bin/activate` and use `python3` if necessary.

> This environment-free ZIP ships source and tests, not installed Python packages. Installation is required. It is not hosted or deployed automatically.

## API details, eligibility and limits

Alpha Vantage API endpoint: `https://www.alphavantage.co/query` using `function=TIME_SERIES_DAILY`, `symbol`, `outputsize=compact`, `apikey`. The API returns **up to the latest 100 daily prices** in the free compact output, so the live analysis typically covers only about five months. Our fetch function calls the external API for each selected ticker/benchmark; it does not use mock data when API mode is selected. Responses are cached for one hour. Each unique uncached symbol consumes a request. Check limits before switching symbols repeatedly; Alpha Vantage publicly lists a standard free quota of 25 requests/day, subject to changes. No paid subscription is required for the basic endpoint.

Source: [Alpha Vantage API documentation](https://www.alphavantage.co/documentation/#daily) and [Alpha Vantage support](https://www.alphavantage.co/support/).

The other included source, `data.sample_prices()`, generates a seeded (2026) **hypothetical** set of 252 business-day prices across nine named tickers for demonstration; its values are not security quotes and MUST NOT be portrayed as real market performance. The application labels this mode prominently.

## Financial methodology

Let `w_i` be the entered allocations divided by their sum, `P_i,t` the daily closing price, and `r_i,t = P_i,t / P_i,t-1 - 1` the simple daily security return.

1. **Daily portfolio return:** `r_p,t = sum_i(w_i * r_i,t)`; fixed target weights are reset *daily*, simulating daily rebalancing.
2. **Cumulative portfolio growth:** `V_t = $10,000 × product_(s<=t)(1 + r_p,s)`; total return = `V_final / V_start - 1`.
3. **Annualized compounded return:** `(V_final/V_start)^(252 / N) - 1` for `N` daily return observations.
4. **Annualized volatility:** `sample_std(daily_returns) × sqrt(252)`.
5. **Sharpe ratio:** `(arithmetic_mean(daily_returns) × 252 - annual_risk_free_rate) / annualized_volatility`. With zero volatility, the Sharpe ratio is reported as unavailable.
6. **Sortino ratio:** `(arithmetic_mean(daily_returns) × 252 - annual_risk_free_rate) / downside_deviation`, where downside deviation is `sqrt(mean(min(r_t, 0)^2)) * sqrt(252)`.
7. **Maximum drawdown:** minimum of `(V_t / max_(s<=t) V_s - 1)`.
8. **Value at Risk (VaR 95%):** 5th percentile of daily portfolio returns.
9. **Portfolio Beta:** `Cov(r_portfolio, r_benchmark) / Var(r_benchmark)`. Measures systematic risk relative to SPY.
10. **Jensen's Alpha:** `(annualized_return_p - risk_free_rate) - Beta * (annualized_return_benchmark - risk_free_rate)`.
11. **Concentration:** the displayed Herfindahl index is `sum_i(w_i^2)`; higher values mean higher concentration.
12. **Correlation:** Pearson correlations calculated using aligned daily simple returns.

Dates are aligned by **intersection** before calculating returns. No forward filling is used. The comparison uses the same dates and return-calculation method. The benchmark can also be part of the portfolio (e.g., holding SPY and comparing against SPY); this is allowed but may make the portfolios more similar.

## Example portfolio and interpretation

Start with **AAPL $4,000 (40%) + MSFT $3,500 (35%) + NVDA $2,500 (25%)** and benchmark **SPY**. The dashboard reports portfolio vs. benchmark historical return and volatility, Sharpe ratio, deepest drawdown, and concentration. Adjust NVDA or any other stock weight to examine how historical exposure changes risk. If the portfolio's volatility is higher than SPY's, it experienced more day-to-day fluctuation in the observed period. A more negative drawdown means it experienced a deeper loss from an earlier peak. Results depend on the historical window and do not justify a forecast.

## Testing

```powershell
py -m pytest -v
```

Included tests verify allocation normalization, invalid input rejection, zero-volatility Sharpe behavior, compounding and drawdown correctness, repeatable demo data, Beta/Alpha tracking vs benchmark, Sortino ratio, 95% VaR, API rate-limit formatting, and price response parsing. All 16 automated tests pass.

Suggested manual test cases:

1. Demo mode: AAPL/MSFT/NVDA, 40/35/25 and SPY: charts and measures appear.
2. Change the allocations to 20/30/50, confirm chart labels update.
3. Change to percentage weights totaling 99: validation message, no crash.
4. Choose only two stocks: validation message, no crash.
5. Real mode with no key, invalid ticker or quota exhausted: readable error message, no fabricated quotes.
6. Real mode with valid key: confirms date range and 30+ overlapping trading days; investigate differences with an independent source.

## Screenshots (required for GitHub submission)

**Two screenshots must be captured after you run the application locally.** Add files to `screenshots/`:

- `screenshots/01-portfolio-overview.png`: demo mode after clicking **Analyze portfolio**, showing allocations and growth chart.
- `screenshots/02-risk-comparison.png`: risk metrics, drawdown chart and interpretation, ideally after changing weights or benchmark.

You can use Windows **Win + Shift + S** and save the screenshots to this folder. Do not present screenshots from simulated prices as actual historical data. The `screenshots/` directory includes a checklist file; screenshots cannot be honestly included until the app has actually run.

## AI development process

The project was created with OpenAI's assistance to plan functions, produce Streamlit UI and financial analytics, build API handling, and add validation and unit tests. This conversation is ChatGPT-assisted work and **does not itself establish use of the required standalone coding agent**. Before submitting, open the repository in **OpenAI Codex** (or Claude Code / Google Antigravity) and use the supplied `AGENT_PROMPT.md`, inspect suggested revisions, run the tests, and record the real agent interaction and changes in `AI_AGENT_LOG.md`. Do not claim agent use unless completed.

## Limitations

- The real-data provider's free compact endpoint returns a limited window (~100 sessions) and has a request quota; the dashboard is not real-time.
- The API sends **unadjusted close prices**, not adjusted/total-return prices. Splits and dividends can distort computed performance and risk, including misleading extreme drawdowns. This is a **prototype**, not an appropriate basis for trading decisions. An adjusted-price source would improve the model.
- Demo prices are synthetic, not historical evidence.
- Portfolio weights are assumed rebalanced every day, rather than buy-and-hold; no transaction costs, slippage, taxes, deposits, withdrawals, borrowing, or short selling.
- Sharpe ratios and annualization are sensitive to the period sampled; historical values are not predictions.
- All correlation and risk calculations are backward-looking; diversification may fail in stressed markets.
- No trade placement, accounts, or personalized financial advice.

## Files

- `app.py` — interactive Streamlit dashboard
- `analytics.py` — return and risk calculation functions
- `data.py` — external API and sample dataset generator
- `tests/test_analytics.py` — automated unit tests
- `requirements.txt` — dependencies
- `AGENT_PROMPT.md` — prompt for required AI coding agent
- `AI_AGENT_LOG.md` — log template for authentic development evidence
- `DEMO_SCRIPT.md` — short presentation script
- `screenshots/README.md` — required screenshot checklist

## GitHub upload

Create an empty **public** GitHub repository called `portfolio-risk-analyzer`, then from this folder run:

```powershell
git init
git add .
git commit -m "Build Project 2 portfolio risk dashboard"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/portfolio-risk-analyzer.git
git push -u origin main
```

Replace `YOUR_USERNAME` and follow GitHub's authentication prompt. If a repository already exists, use its real remote URL. **Never commit an API key.** After adding the two real screenshots and authentic agent notes, run:

```powershell
git add screenshots AI_AGENT_LOG.md
git commit -m "Add tested app screenshots and AI agent development notes"
git push
```

Submit the **actual GitHub repository URL** along with a short in-person or screen-recorded working demo.
