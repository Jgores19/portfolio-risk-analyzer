# 2–3 Minute Live Demonstration Script

**Introduction (20 seconds):** This application addresses a common investment mistake: concentrating too much money in a few investments without understanding downside risk. My Streamlit dashboard lets users compare a portfolio against a market benchmark.

**Inputs (30 seconds):** I select AAPL, MSFT, and NVDA and allocate $4,000, $3,500 and $2,500, or 40%, 35% and 25%. I choose SPY as my benchmark and 3% as the assumed risk-free rate. The demo mode uses **simulated values**, clearly identified as hypothetical. Alternatively, with a free Alpha Vantage key I can fetch recent actual **unadjusted** daily closing prices.

**Analysis (55 seconds):** When I click Analyze portfolio, the allocation chart shows my weight in each stock. The performance chart compares the compounded growth of $10,000 invested in my portfolio and in SPY. Annualized volatility measures fluctuations, the Sharpe ratio shows historical average excess return per unit of volatility, and maximum drawdown shows the largest observed peak-to-trough loss. The correlation chart helps explain diversification. I can change weights and recalculate.

**Evaluation (30 seconds):** The app handles fewer than three stocks, invalid weights, missing API keys and unavailable price data. Daily prices are aligned. Limitations include the free API's short history, unadjusted prices, past-performance uncertainty and unrealistic daily rebalancing. This helps compare risk, not predict outcomes or recommend trades.

**Closing (20 seconds):** My repository includes the source code, dependencies, test cases, README, screenshots taken while the app runs, and my record of how I used a required coding agent.
