"""Streamlit educational investment portfolio risk dashboard."""
import os
import time
import numpy as np
import pandas as pd
import requests
import plotly.express as px
import streamlit as st

from analytics import analyze
from data import DataSourceError, DEMO_TICKERS, fetch_daily_close, sample_prices

st.set_page_config(page_title='Portfolio Risk Analyzer', page_icon='📈', layout='wide')
st.title('📈 Investment Portfolio Risk Analyzer')
st.caption('Project 2 · Applied Finance & FinTech · Educational Prototype')

with st.sidebar:
    st.header('Portfolio Setup')
    mode = st.radio(
        'Price Data Source',
        ['Illustrative demo dataset', 'Alpha Vantage API (historical daily closes)'],
        help='Use the demo dataset for offline testing without an API key, or Alpha Vantage for real market history.'
    )

    available_tickers = list(DEMO_TICKERS)
    custom_tickers = []
    if mode.startswith('Alpha'):
        custom_input = st.text_input(
            'Add custom tickers (comma-separated)',
            value='',
            help='Enter additional US tickers or ETFs (e.g. TSLA, META, AMD).'
        )
        if custom_input.strip():
            custom_tickers = [t.strip().upper() for t in custom_input.split(',') if t.strip()]
            for ct in custom_tickers:
                if ct not in available_tickers:
                    available_tickers.append(ct)

    universe = st.multiselect(
        'Choose at least 3 stocks / ETFs',
        available_tickers,
        default=['AAPL', 'MSFT', 'NVDA']
    )

    benchmark_options = [t for t in available_tickers if t in ['SPY', 'QQQ', 'VTI'] or t not in universe]
    if 'SPY' not in benchmark_options:
        benchmark_options.insert(0, 'SPY')
    default_bench_idx = benchmark_options.index('SPY') if 'SPY' in benchmark_options else 0
    benchmark = st.selectbox('Market benchmark', benchmark_options, index=default_bench_idx)

    entry = st.radio('Allocation input', ['Investment amounts ($)', 'Portfolio weights (%)'])
    allocations = []
    default_dollars = {'AAPL': 4000.0, 'MSFT': 3500.0, 'NVDA': 2500.0}
    default_pcts = {'AAPL': 40.0, 'MSFT': 35.0, 'NVDA': 25.0}

    for ticker in universe:
        if entry.startswith('Investment'):
            val = float(default_dollars.get(ticker, 1000.0))
            allocations.append(st.number_input(f'{ticker} ($)', min_value=0.0, value=val, step=100.0, key=f'amt-{ticker}'))
        else:
            val = float(default_pcts.get(ticker, round(100.0 / len(universe), 2) if universe else 10.0))
            allocations.append(st.number_input(f'{ticker} weight (%)', min_value=0.0, value=val, step=1.0, key=f'pct-{ticker}'))

    if entry.startswith('Portfolio') and universe:
        current_sum = sum(allocations)
        if np.isclose(current_sum, 100.0, atol=0.5):
            st.caption(f'✅ Total weight: **{current_sum:.1f}%**')
        else:
            st.warning(f'⚠️ Total weight is currently **{current_sum:.1f}%** (must equal 100%).')

    rf = st.number_input('Assumed annual risk-free rate (%)', min_value=0.0, max_value=50.0, value=3.0, step=0.25)
    key = ''
    if mode.startswith('Alpha'):
        key = st.text_input(
            'Alpha Vantage API key',
            type='password',
            value=os.environ.get('ALPHAVANTAGE_API_KEY', ''),
            help='Obtain a free key at alphavantage.co. Keys are not stored.'
        )

    run = st.button('Analyze portfolio', type='primary', use_container_width=True)

@st.cache_data(ttl=3600, show_spinner=False)
def cached_quote(ticker: str, api_key: str):
    return fetch_daily_close(ticker, api_key)

if mode.startswith('Illustrative'):
    st.warning('⚠️ **DEMO MODE**: Prices are simulated, not actual stock-market data. Switch to Alpha Vantage for real external API data.')
else:
    st.info('ℹ️ **LIVE API MODE**: Alpha Vantage free daily endpoint returns up to 100 recent observations. Data are unadjusted closing prices, not total returns; excludes dividends, splits and transaction costs.')

if not run:
    st.info('👈 Select at least three securities, enter allocations in the sidebar, and click **Analyze portfolio**. Default demonstration portfolio is 40% AAPL, 35% MSFT, and 25% NVDA, compared with SPY.')
    st.stop()

if len(universe) < 3:
    st.error('❌ Please select at least three distinct stocks or ETFs.')
    st.stop()
if sum(allocations) <= 0:
    st.error('❌ Total allocation must be positive.')
    st.stop()
if entry.startswith('Portfolio') and not np.isclose(sum(allocations), 100, atol=0.5):
    st.error(f'❌ Portfolio weights must add up to 100% (current total: {sum(allocations):.2f}%).')
    st.stop()

try:
    if mode.startswith('Alpha'):
        if not key.strip():
            st.error('❌ Please enter an Alpha Vantage API key to retrieve live historical market data.')
            st.stop()
        tickers_to_fetch = list(dict.fromkeys(universe + [benchmark]))
        series_list = []
        progress_bar = st.progress(0, text='Connecting to Alpha Vantage API...')
        for i, t in enumerate(tickers_to_fetch):
            progress_bar.progress(i / len(tickers_to_fetch), text=f'Retrieving {t} ({i+1}/{len(tickers_to_fetch)}) from Alpha Vantage...')
            series_list.append(cached_quote(t, key))
            if i < len(tickers_to_fetch) - 1:
                time.sleep(1.2)  # Respect free-tier rate limits (max 5 calls/min)
        progress_bar.progress(1.0, text='Data retrieval complete!')
        time.sleep(0.3)
        progress_bar.empty()
        prices = pd.concat(series_list, axis=1)
    else:
        prices = sample_prices()

    result = analyze(prices, universe, allocations, benchmark, rf / 100)
except (DataSourceError, ValueError, KeyError, requests.exceptions.RequestException) as exc:
    st.error(f'Analysis unavailable: {exc}')
    st.info('Troubleshooting: verify ticker symbols, ensure your free Alpha Vantage key is valid and within its quota (5 calls/min, 25 calls/day), or switch to the Illustrative demo dataset.')
    st.stop()

portfolio, bench = result['portfolio'], result['benchmark']
st.success(f"Analyzed **{result['observations']}** aligned trading days | Date range: **{result['start']:%Y-%m-%d}** to **{result['end']:%Y-%m-%d}** | Data source: **{'Simulated Demo Data' if mode.startswith('Illustrative') else 'Alpha Vantage API (TIME_SERIES_DAILY)'}**")

# Top KPI Metric Cards (comparing Portfolio to Benchmark)
col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    delta_tot = portfolio['Total return'] - bench['Total return']
    st.metric('Total Return', f"{portfolio['Total return']:.2%}", delta=f"{delta_tot:+.2%} vs {benchmark}")
with col2:
    delta_ann = portfolio['Annualized return'] - bench['Annualized return']
    st.metric('Annualized Return', f"{portfolio['Annualized return']:.2%}", delta=f"{delta_ann:+.2%} vs {benchmark}")
with col3:
    delta_vol = portfolio['Annualized volatility'] - bench['Annualized volatility']
    # For volatility, lower is safer/preferred, so inverse coloring can be helpful
    st.metric('Annualized Volatility', f"{portfolio['Annualized volatility']:.2%}", delta=f"{delta_vol:+.2%} vs {benchmark}", delta_color='inverse')
with col4:
    delta_sharpe = portfolio['Sharpe ratio'] - bench['Sharpe ratio']
    st.metric('Sharpe Ratio', f"{portfolio['Sharpe ratio']:.2f}" if np.isfinite(portfolio['Sharpe ratio']) else 'N/A',
              delta=f"{delta_sharpe:+.2f} vs {benchmark}" if np.isfinite(delta_sharpe) else None)
with col5:
    delta_dd = portfolio['Maximum drawdown'] - bench['Maximum drawdown']
    st.metric('Max Drawdown', f"{portfolio['Maximum drawdown']:.2%}", delta=f"{delta_dd:+.2%} vs {benchmark}")

# Additional Risk Factor Metrics (Sortino, Beta, Alpha, VaR)
mcol1, mcol2, mcol3, mcol4 = st.columns(4)
with mcol1:
    st.metric(f'Beta (vs {benchmark})', f"{result['beta']:.2f}" if np.isfinite(result['beta']) else 'N/A',
              help='Systematic risk sensitivity relative to the market benchmark. Beta > 1 means more volatile than benchmark.')
with mcol2:
    st.metric(f"Jensen's Alpha (vs {benchmark})", f"{result['alpha']:+.2%}" if np.isfinite(result['alpha']) else 'N/A',
              help='Annualized excess return generated above CAPM expectations given the portfolio beta.')
with mcol3:
    st.metric('Sortino Ratio', f"{portfolio['Sortino ratio']:.2f}" if np.isfinite(portfolio['Sortino ratio']) else 'N/A',
              help='Excess return divided by downside deviation. Unlike Sharpe, it only penalizes harmful downside volatility.')
with mcol4:
    st.metric('Daily VaR (95%)', f"{portfolio['Daily VaR (95%)']:.2%}",
              help='Historical 1-day Value at Risk at 95% confidence level (5th percentile of daily returns).')

st.divider()

# Charts Section 1: Allocation & Performance Growth
left, right = st.columns([1, 1.6])
with left:
    st.subheader('Portfolio Allocation')
    weights = result['weights']
    fig_alloc = px.pie(
        names=weights.index,
        values=weights.values,
        hole=0.52,
        title='Target Weight Distribution',
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    fig_alloc.update_traces(textposition='inside', textinfo='label+percent')
    st.plotly_chart(fig_alloc, use_container_width=True)
    alloc_display = pd.DataFrame({
        'Security': weights.index,
        'Target Weight': (weights * 100).round(2).astype(str) + '%',
        'Effective Allocation': [f"${w * 10000:,.2f} per $10k" for w in weights.values]
    })
    st.dataframe(alloc_display, hide_index=True, use_container_width=True)

with right:
    st.subheader(f'Growth of $10,000 Investment vs {benchmark}')
    growth = result['growth'] * 10000
    fig_growth = px.line(
        growth,
        x=growth.index,
        y=growth.columns,
        labels={'value': 'Portfolio Value ($)', 'index': 'Date', 'variable': 'Strategy'}
    )
    fig_growth.update_layout(yaxis_tickprefix='$', yaxis_tickformat=',.0f', hovermode='x unified')
    st.plotly_chart(fig_growth, use_container_width=True)

# Charts Section 2: Drawdown & Comprehensive Risk Comparison Table
left, right = st.columns([1.2, 1])
with left:
    st.subheader('Drawdown Over Time')
    dd = result['drawdown'] * 100
    fig_dd = px.line(
        dd,
        x=dd.index,
        y=dd.columns,
        labels={'value': 'Drawdown (%)', 'index': 'Date', 'variable': 'Strategy'}
    )
    fig_dd.update_layout(yaxis_ticksuffix='%', hovermode='x unified')
    st.plotly_chart(fig_dd, use_container_width=True)

with right:
    st.subheader('Risk & Performance Comparison')
    def format_row(val, is_pct=False, decimals=2):
        if val is None or not np.isfinite(val):
            return 'N/A'
        if is_pct:
            return f"{val:.{decimals}%}"
        return f"{val:.{decimals}f}"

    comp_rows = [
        ('Total Return', format_row(portfolio['Total return'], True), format_row(bench['Total return'], True), f"{portfolio['Total return'] - bench['Total return']:+.2%}"),
        ('Annualized Return (CAGR)', format_row(portfolio['Annualized return'], True), format_row(bench['Annualized return'], True), f"{portfolio['Annualized return'] - bench['Annualized return']:+.2%}"),
        ('Annualized Volatility (σ)', format_row(portfolio['Annualized volatility'], True), format_row(bench['Annualized volatility'], True), f"{portfolio['Annualized volatility'] - bench['Annualized volatility']:+.2%}"),
        ('Sharpe Ratio (Rf=' + f"{rf:.1f}%)", format_row(portfolio['Sharpe ratio']), format_row(bench['Sharpe ratio']), f"{portfolio['Sharpe ratio'] - bench['Sharpe ratio']:+.2f}" if np.isfinite(portfolio['Sharpe ratio'] - bench['Sharpe ratio']) else '-'),
        ('Sortino Ratio', format_row(portfolio['Sortino ratio']), format_row(bench['Sortino ratio']), f"{portfolio['Sortino ratio'] - bench['Sortino ratio']:+.2f}" if np.isfinite(portfolio['Sortino ratio'] - bench['Sortino ratio']) else '-'),
        ('Maximum Drawdown', format_row(portfolio['Maximum drawdown'], True), format_row(bench['Maximum drawdown'], True), f"{portfolio['Maximum drawdown'] - bench['Maximum drawdown']:+.2%}"),
        ('Daily VaR (95%)', format_row(portfolio['Daily VaR (95%)'], True), format_row(bench['Daily VaR (95%)'], True), f"{portfolio['Daily VaR (95%)'] - bench['Daily VaR (95%)']:+.2%}"),
        (f'Beta (vs {benchmark})', format_row(result['beta']), '1.00', f"{result['beta'] - 1.0:+.2f}" if np.isfinite(result['beta']) else '-'),
        (f"Jensen's Alpha", format_row(result['alpha'], True), '0.00%', f"{result['alpha']:+.2%}" if np.isfinite(result['alpha']) else '-')
    ]
    comparison_df = pd.DataFrame(comp_rows, columns=['Metric', 'Portfolio', benchmark, 'Difference (Δ)'])
    st.dataframe(comparison_df, hide_index=True, use_container_width=True)

st.divider()

# Charts Section 3: Return Distribution & Correlation Matrix
col_hist, col_corr = st.columns(2)
with col_hist:
    st.subheader('Daily Returns Distribution')
    daily_rets = pd.DataFrame({
        'Portfolio': result['portfolio_daily_returns'] * 100,
        benchmark: result['returns'][benchmark] * 100
    })
    fig_hist = px.histogram(
        daily_rets,
        barmode='overlay',
        nbins=40,
        labels={'value': 'Daily Return (%)', 'variable': 'Strategy'},
        color_discrete_sequence=['#636EFA', '#EF553B']
    )
    fig_hist.update_layout(xaxis_ticksuffix='%', bargap=0.05)
    st.plotly_chart(fig_hist, use_container_width=True)

with col_corr:
    st.subheader('Asset Correlation Matrix')
    fig_corr = px.imshow(
        result['correlations'],
        text_auto='.2f',
        zmin=-1,
        zmax=1,
        color_continuous_scale='RdBu_r'
    )
    st.plotly_chart(fig_corr, use_container_width=True)

# Interpretation Section
st.subheader('Financial Analysis & Interpretation')
rel_ret = portfolio['Total return'] - bench['Total return']
concentration = float((weights ** 2).sum())
hhi_desc = 'Low concentration (well-diversified)' if concentration < 0.25 else ('Moderate concentration' if concentration < 0.40 else 'High concentration')

interpretation_text = (
    f"1. **Performance vs Benchmark:** The portfolio achieved a cumulative total return of **{portfolio['Total return']:.2%}** "
    f"compared to **{bench['Total return']:.2%}** for **{benchmark}**, representing a **{abs(rel_ret):.2%} "
    f"{'outperformance' if rel_ret >= 0 else 'underperformance'}** over the {result['observations']} trading sessions.\n\n"
    f"2. **Risk & Volatility:** The portfolio annualized volatility was **{portfolio['Annualized volatility']:.2%}** "
    f"(vs. **{bench['Annualized volatility']:.2%}** for {benchmark}). "
    f"Its Beta of **{result['beta']:.2f}** indicates that the portfolio has **{abs(result['beta'] - 1.0):.1%} "
    f"{'more' if result['beta'] > 1 else 'less'} systematic sensitivity** than the broad market benchmark.\n\n"
    f"3. **Downside Exposure:** The maximum peak-to-trough drawdown was **{portfolio['Maximum drawdown']:.2%}** "
    f"(vs. **{bench['Maximum drawdown']:.2%}** for {benchmark}). The 95% 1-day Value at Risk (VaR) indicates that on 95% of days, "
    f"daily losses did not exceed **{abs(portfolio['Daily VaR (95%)']):.2%}**.\n\n"
    f"4. **Risk-Adjusted Efficiency:** The portfolio achieved a Sharpe ratio of **{portfolio['Sharpe ratio']:.2f}** "
    f"and a Sortino ratio of **{portfolio['Sortino ratio']:.2f}**, reflecting excess returns earned per unit of total risk and downside deviation, respectively.\n\n"
    f"5. **Portfolio Concentration:** The largest single holding is **{weights.idxmax()}** at **{weights.max():.1%}**. "
    f"The portfolio's Herfindahl-Hirschman Index (HHI) is **{concentration:.3f}**, indicating **{hhi_desc}**."
)
st.markdown(interpretation_text)

st.caption(
    'Assumptions & Limitations: Daily rebalancing to target weights; long-only fractional shares; zero transaction fees, slippage, and taxes; '
    'API historical closing prices are unadjusted for dividends and stock splits. Past performance does not guarantee future results. '
    'Educational prototype for FIN 471; not investment advice.'
)

# Export Data Section
st.divider()
exp_col1, exp_col2 = st.columns(2)
with exp_col1:
    st.download_button(
        '📥 Download Aligned Prices (CSV)',
        data=result['prices'].to_csv().encode('utf-8'),
        file_name='aligned_prices.csv',
        mime='text/csv',
        use_container_width=True
    )
with exp_col2:
    st.download_button(
        '📥 Download Daily Returns (CSV)',
        data=result['returns'].to_csv().encode('utf-8'),
        file_name='daily_returns.csv',
        mime='text/csv',
        use_container_width=True
    )
