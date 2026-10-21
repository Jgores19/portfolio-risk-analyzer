Investment Portfolio Risk Analyzer (Project 2)
For this project, I built an Investment Portfolio Risk Analyzer using Python and Streamlit. I wanted to create something that could show how different stock choices and investment amounts affect a portfolio's performance and risk. The app also compares the portfolio with a market benchmark so users can see the differences.
What the app does
- Allows users to select at least three stocks or ETFs and enter investment amounts or percentage weights.
- Calculates portfolio returns, annualized volatility, Sharpe ratio, maximum drawdown, and other risk measures.
- Compares the portfolio with SPY (the default benchmark), VTI, QQQ, or another available security.
- Shows charts for portfolio allocation, growth compared with the benchmark, drawdowns, daily returns, and stock correlations.
- Lets users change their investments and assumed risk-free rate, and download price and return data as CSV files.
- Gives error messages for invalid inputs, unavailable stocks, or API problems instead of crashing.
Stock market data
The app uses the Alpha Vantage API to get actual historical daily stock prices. It calls the TIME_SERIES_DAILY endpoint with outputsize=compact, which generally returns up to 100 recent daily closing prices. Users enter their own free API key in the dashboard. The app caches downloaded prices for an hour to limit repeated requests.

Alpha Vantage limits requests on free accounts, so the app may need to wait if the daily limit is reached. The prices are not live quotes. The data also uses unadjusted closing prices, which means it does not properly account for dividends or stock splits.

I also included an Illustrative demo dataset so someone can try the app without an API key. This data is simulated and is not actual stock performance.
- Alpha Vantage API documentation
- Get a free API key
How to run the app
You need Python 3.10 or newer. Download the repository and open its folder in Antigravity, VS Code, or a terminal. Run these commands in Windows PowerShell:
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m streamlit run app.py
On Mac or Linux, create the environment with python3 -m venv .venv and activate it with source .venv/bin/activate before installing the requirements and starting Streamlit.

The terminal will display a local address, usually http://localhost:8501. Open it in your browser, select at least three stocks, enter the investment amounts, and click Analyze portfolio. To use real data, select Alpha Vantage API in the sidebar and enter your API key. You can also select the demo dataset to test the app without a key.
Financial calculations
The app lines up available prices by date before calculating the returns. It does not fill in missing prices. The main calculations are:
- Daily stock return: Today's closing price divided by yesterday's closing price, minus one.
- Portfolio return: Each stock's daily return is multiplied by its portfolio weight and added together. The model assumes the target weights are reset each trading day.
- Total return: Compounds the daily portfolio returns over the period.
- Annualized return: Converts the compounded return to a yearly rate using 252 trading days.
- Annualized volatility: Standard deviation of daily returns multiplied by the square root of 252.
- Sharpe ratio: Annualized average return minus the selected risk-free rate, divided by annualized volatility.
- Maximum drawdown: The biggest percentage decline from an earlier portfolio high.
I included a few additional measures. The Sortino ratio focuses on downside volatility, while Value at Risk (95%) uses the fifth percentile of daily returns to estimate a one-day loss threshold. Beta measures how sensitive the portfolio is to the benchmark, and Jensen's alpha compares the portfolio's return with a return based on that beta. The app also calculates concentration from squared portfolio weights and correlation between the stocks' daily returns.
Example portfolio
I tested the app with the following investments:
Stock	Amount	Weight
AAPL	$4,000	40%
MSFT	$3,500	35%
NVDA	$2,500	25%


I used SPY as the benchmark. In one API test using prices through October 20, 2026, the dashboard showed 11.90% total return for the portfolio compared with 1.66% for SPY. However, the portfolio also had more volatility (21.40% compared with 12.40%) and a larger maximum drawdown. This helped show that a higher historical return can come with more risk.

Those results apply only to the dates analyzed. They are not a prediction of future performance.
Testing
Google Antigravity reviewed the app and ran the automated tests. It reported 16 tests passed, including tests for portfolio calculations, input validation, risk measures, demo data, and API response handling. To run the tests again, enter:
python -m pytest -v
I also opened the Streamlit dashboard with AAPL, MSFT, and NVDA, looked through the calculations and charts, and switched from the demo dataset to actual historical prices from Alpha Vantage. The app displayed 99 aligned trading days and compared my portfolio against SPY. I also checked the investment inputs and benchmark comparison. The automated API tests use controlled responses; the live dashboard test is separate evidence that the actual API connection worked.
Screenshots
I captured two screenshots of the dashboard using real Alpha Vantage data. The first shows the portfolio overview and growth chart, and the second shows the drawdown chart and comparison with SPY. I saved these for the Screenshots/ folder on GitHub. The screenshots identify Alpha Vantage API as the data source rather than the demo dataset.
How I used AI tools
I used ChatGPT to help make the first version of this project and organize the files. After that, I opened the project in Google Antigravity and asked its coding agent to review and improve the app. Antigravity found and fixed an error that could crash the risk comparison table. It also added more ways to measure risk, including Beta, Jensen's Alpha, the Sortino ratio, and Value at Risk. The agent improved the comparison with SPY, added support for custom stock tickers, improved API error messages, and expanded the tests from 5 to 16.

I then opened the dashboard, tried the portfolio inputs, and connected it to Alpha Vantage to see real historical prices. Working through this showed me how an AI coding tool can help find errors, add features, and test a finance application. More details about the agent's changes are in AI_AGENT_LOG.md.
Limitations
- The free API provides a limited amount of historical data, and the dashboard does not provide real-time prices.
- Prices are unadjusted for dividends and stock splits, so some performance results may be distorted.
- The model assumes daily rebalancing and does not include transaction costs, taxes, or slippage.
- The results depend on the dates selected, and past performance does not guarantee future returns.
- The demo dataset is simulated. The app is for education and does not place trades or give personalized financial advice.
Main project files
File or folder	Purpose
app.py	Streamlit dashboard
analytics.py	Portfolio return and risk calculations
data.py	Alpha Vantage connection and demo data
requirements.txt	Python packages needed to run the app
tests/test_analytics.py	Financial calculation tests
tests/test_data.py	Data handling tests
Screenshots/	Images of the running application
AI_AGENT_LOG.md	Notes about AI tool use
AGENT_PROMPT.md	Development prompt
DEMO_SCRIPT.md	Short presentation guide


To reproduce the project, download the repository, install the dependencies, and run app.py using the instructions above. Do not upload your API key, .env or .venv files, or Python cache folders to GitHub.
