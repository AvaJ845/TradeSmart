import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
from datetime import datetime, timedelta

from utils.data_fetcher import get_stock_data
from utils.backtest import simulate_paper_trade
from utils.visualization import plot_portfolio_performance

def paper_trading_module():
    """
    Paper Trading module for simulating strategies without risking real money
    """
    st.markdown('<p class="main-header">Paper Trading Simulator</p>', unsafe_allow_html=True)
    
    st.markdown("""
    Test trading strategies without risking real capital. This simulator allows you to
    backtest strategies on historical data and track hypothetical performance.
    """)
    
    # Create tabs for different paper trading sections
    tab1, tab2, tab3 = st.tabs(["Strategy Backtesting", "Manual Trading Simulator", "Paper Portfolio"])
    
    with tab1:
        st.markdown("### Strategy Backtesting")
        
        # Input parameters
        col1, col2, col3 = st.columns(3)
        
        with col1:
            ticker = st.text_input("Enter Ticker Symbol", "AAPL", key="backtest_ticker")
        
        with col2:
            strategy = st.selectbox(
                "Select Trading Strategy",
                options=["Technical Indicators", "Moving Average Crossover", "RSI Strategy", "MACD Strategy"]
            )
        
        with col3:
            period = st.selectbox(
                "Backtest Period",
                options=["1mo", "3mo", "6mo", "1y", "2y", "5y"],
                index=3
            )
        
        # Capital settings
        initial_capital = st.slider("Initial Capital ($)", 
                                    min_value=1000, 
                                    max_value=100000, 
                                    value=10000, 
                                    step=1000)
        
        if st.button("Run Backtest"):
            with st.spinner("Running backtest..."):
                # Get data
                data = get_stock_data(ticker, period=period)
                
                if data is not None and len(data) > 0:
                    # Run simulation
                    portfolio, metrics = simulate_paper_trade(data, strategy, initial_capital)
                    
                    if portfolio is not None and metrics is not None:
                        # Display performance metrics
                        st.markdown("### Backtest Results")
                        
                        col1, col2, col3 = st.columns(3)
                        col1.metric("Total Return", f"{metrics['Total Return']:.2f}%")
                        col2.metric("Annual Return", f"{metrics['Annual Return (%)']:.2f}%")
                        col3.metric("Sharpe Ratio", f"{metrics['Sharpe Ratio']:.2f}")
                        
                        col1, col2, col3 = st.columns(3)
                        col1.metric("Final Portfolio Value", f"${metrics['Final Value']:.2f}")
                        col2.metric("Volatility", f"{metrics['Annual Volatility (%)']:.2f}%")
                        col3.metric("Max Drawdown", f"{metrics['Max Drawdown (%)']:.2f}%")
                        
                        # Plot portfolio value
                        fig = plot_portfolio_performance(portfolio)
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Display trade history
                        st.markdown("### Trade History")
                        
                        # Create trade history from portfolio data
                        trades = []
                        for i in range(1, len(portfolio)):
                            if portfolio['Positions'].iloc[i] != portfolio['Positions'].iloc[i-1]:
                                if portfolio['Positions'].iloc[i] > portfolio['Positions'].iloc[i-1]:
                                    action = "BUY"
                                else:
                                    action = "SELL"
                                
                                trades.append({
                                    'Date': portfolio.index[i],
                                    'Action': action,
                                    'Price': data['Close'].iloc[i],
                                    'Position Size': abs(portfolio['Positions'].iloc[i] - portfolio['Positions'].iloc[i-1]),
                                    'Portfolio Value': portfolio['Total'].iloc[i]
                                })
                        
                        if trades:
                            trades_df = pd.DataFrame(trades)
                            st.dataframe(trades_df)
                        else:
                            st.info("No trades were executed during the backtest period.")
                        
                        # Risk warning
                        st.warning("""
                        **Note**: Past performance is not indicative of future results. Backtest 
                        results are based on historical data and do not account for market conditions, 
                        slippage, or other real-world trading factors.
                        """)
                    else:
                        st.error("Could not simulate trades with the selected strategy.")
                else:
                    st.error(f"Could not fetch data for {ticker}.")
    
    with tab2:
        st.markdown("### Manual Trading Simulator")
        st.markdown("""
        This simulator is under development. In the future, it will allow you to manually 
        place simulated trades on real-time or slightly delayed market data.
        
        Features coming soon:
        - Manual trade entry and exit
        - Real-time portfolio tracking
        - P&L analysis
        - Risk metrics
        - Performance comparison against benchmarks
        """)
        
        st.info("This module is coming soon. Check back for updates!")
    
    with tab3:
        st.markdown("### Paper Portfolio Tracker")
        st.markdown("""
        This feature is under development. It will allow you to create and track paper trading
        portfolios over time, with features including:
        
        - Multiple portfolio support
        - Diversification analysis
        - Sector allocation
        - Performance attribution
        - Benchmark comparison
        - Export and sharing options
        """)
        
        st.info("This module is coming soon. Check back for updates!")
    
    st.markdown("""
    ### About Paper Trading
    
    Paper trading is the practice of simulated trading with virtual money to test strategies
    without risking real capital. Benefits include:
    
    - **Risk-Free Learning**: Develop trading skills without financial consequences
    - **Strategy Testing**: Validate trading strategies before committing real capital
    - **Psychology Development**: Learn to manage emotions associated with trading
    - **Market Familiarity**: Gain experience with market mechanics and order types
    
    Paper trading is an essential step before live trading, but remember that it doesn't
    perfectly replicate the psychological aspects of risking real money.
    """)
