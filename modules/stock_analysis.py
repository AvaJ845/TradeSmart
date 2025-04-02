import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from utils.data_fetcher import get_stock_data
from utils.indicators import calculate_technical_indicators, get_trading_signals
from utils.backtest import backtest_strategy
from utils.visualization import (
    plot_price_chart, 
    plot_technical_indicators, 
    plot_trading_signals,
    plot_portfolio_performance
)

def stock_analysis_module():
    """
    Stock analysis module for technical analysis and signal generation
    """
    st.markdown('<p class="main-header">Stock Analysis</p>', unsafe_allow_html=True)
    
    # Input parameters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        ticker = st.text_input("Enter Ticker Symbol", "AAPL")
    
    with col2:
        period = st.selectbox(
            "Select Time Period",
            options=["1mo", "3mo", "6mo", "1y", "2y", "5y", "max"],
            index=3
        )
        
    with col3:
        interval = st.selectbox(
            "Select Time Interval",
            options=["1d", "1wk", "1mo"],
            index=0
        )
    
    # Fetch stock data
    if st.button("Analyze"):
        with st.spinner("Fetching data and analyzing..."):
            # Get stock data
            data = get_stock_data(ticker, period, interval)
            
            if data is not None:
                # Calculate technical indicators
                indicators = calculate_technical_indicators(data)
                
                if indicators is not None:
                    # Generate trading signals
                    signals = get_trading_signals(indicators)
                    
                    # Display stock information
                    st.markdown(f"### {ticker} Technical Analysis")
                    
                    # Create tabs for different analyses
                    tab1, tab2, tab3, tab4 = st.tabs(["Price & Volume", "Technical Indicators", "Trading Signals", "Backtest"])
                    
                    with tab1:
                        # Price and volume chart
                        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                                           vertical_spacing=0.1, 
                                           row_heights=[0.7, 0.3])
                        
                        # Add candlestick chart
                        fig.add_trace(
                            go.Candlestick(
                                x=data.index,
                                open=data['Open'],
                                high=data['High'],
                                low=data['Low'],
                                close=data['Close'],
                                name="OHLC"
                            ),
                            row=1, col=1
                        )
                        
                        # Add Moving Averages
                        fig.add_trace(
                            go.Scatter(
                                x=indicators.index,
                                y=indicators['MA20'],
                                name="MA20",
                                line=dict(color='blue', width=1)
                            ),
                            row=1, col=1
                        )
                        
                        fig.add_trace(
                            go.Scatter(
                                x=indicators.index,
                                y=indicators['MA50'],
                                name="MA50",
                                line=dict(color='red', width=1)
                            ),
                            row=1, col=1
                        )
                        
                        fig.add_trace(
                            go.Scatter(
                                x=indicators.index,
                                y=indicators['MA200'],
                                name="MA200",
                                line=dict(color='green', width=1)
                            ),
                            row=1, col=1
                        )
                        
                        # Add volume chart
                        fig.add_trace(
                            go.Bar(
                                x=data.index,
                                y=data['Volume'],
                                name="Volume",
                                marker=dict(color='rgba(0, 0, 100, 0.5)')
                            ),
                            row=2, col=1
                        )
                        
                        fig.update_layout(
                            title=f"{ticker} Price and Volume Chart",
                            xaxis_title="Date",
                            yaxis_title="Price ($)",
                            height=600,
                            showlegend=True,
                            xaxis_rangeslider_visible=False
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                    
                    with tab2:
                        # Technical indicators visualization
                        # Create subtabs for different indicators
                        indicator_tabs = st.tabs(["RSI", "MACD", "Bollinger Bands", "Stochastic"])
                        
                        with indicator_tabs[0]:
                            # RSI Chart
                            fig = plot_technical_indicators(indicators, "RSI")
                            st.plotly_chart(fig, use_container_width=True)
                            
                            st.markdown("""
                            **RSI Interpretation:**
                            - Above 70: Potentially overbought (selling opportunity)
                            - Below 30: Potentially oversold (buying opportunity)
                            - Trend confirmation: RSI following the trend confirms strength
                            """)
                        
                        with indicator_tabs[1]:
                            # MACD Chart
                            fig = plot_technical_indicators(indicators, "MACD")
                            st.plotly_chart(fig, use_container_width=True)
                            
                            st.markdown("""
                            **MACD Interpretation:**
                            - MACD crossing above signal line: Bullish signal
                            - MACD crossing below signal line: Bearish signal
                            - Histogram growing: Trend strength increasing
                            - Divergence between MACD and price: Potential reversal
                            """)
                        
                        with indicator_tabs[2]:
                            # Bollinger Bands
                            fig = plot_technical_indicators(indicators, "Bollinger")
                            st.plotly_chart(fig, use_container_width=True)
                            
                            st.markdown("""
                            **Bollinger Bands Interpretation:**
                            - Price touching upper band: Potentially overbought
                            - Price touching lower band: Potentially oversold
                            - Bands narrowing: Decreasing volatility, potential breakout ahead
                            - Bands widening: Increasing volatility
                            """)
                        
                        with indicator_tabs[3]:
                            # Stochastic Oscillator
                            fig = plot_technical_indicators(indicators, "Stochastic")
                            st.plotly_chart(fig, use_container_width=True)
                            
                            st.markdown("""
                            **Stochastic Oscillator Interpretation:**
                            - Above 80: Potentially overbought
                            - Below 20: Potentially oversold
                            - %K crossing above %D: Bullish signal
                            - %K crossing below %D: Bearish signal
                            """)
                    
                    with tab3:
                        # Trading Signals
                        if signals is not None:
                            # Visualize signals on price chart
                            fig = plot_trading_signals(signals)
                            st.plotly_chart(fig, use_container_width=True)
                            
                            # Signal summary
                            st.markdown("### Signal Summary")
                            
                            # Latest signals
                            latest_date = signals.index[-1]
                            
                            # Create signal strength indicator
                            signal_strength = 0
                            if signals['RSI_Buy'].iloc[-1]: signal_strength += 1
                            if signals['MACD_Buy'].iloc[-1]: signal_strength += 1
                            if signals['MA_Cross_Buy'].iloc[-1]: signal_strength += 1
                            if signals['BB_Buy'].iloc[-1]: signal_strength += 1
                            if signals['Stoch_Buy'].iloc[-1]: signal_strength += 1
                            
                            if signals['RSI_Sell'].iloc[-1]: signal_strength -= 1
                            if signals['MACD_Sell'].iloc[-1]: signal_strength -= 1
                            if signals['MA_Cross_Sell'].iloc[-1]: signal_strength -= 1
                            if signals['BB_Sell'].iloc[-1]: signal_strength -= 1
                            if signals['Stoch_Sell'].iloc[-1]: signal_strength -= 1
                            
                            # Determine overall signal
                            if signal_strength >= 3:
                                signal = "Strong Buy"
                                color = "green"
                            elif signal_strength >= 1:
                                signal = "Buy"
                                color = "lightgreen"
                            elif signal_strength <= -3:
                                signal = "Strong Sell"
                                color = "red"
                            elif signal_strength <= -1:
                                signal = "Sell"
                                color = "lightcoral"
                            else:
                                signal = "Neutral"
                                color = "gray"
                                
                            st.markdown(f"<h3 style='color:{color}'>{signal}</h3>", unsafe_allow_html=True)
                            
                            # Display individual signals
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.markdown("#### Buy Signals")
                                st.markdown(f"RSI: {'✅' if signals['RSI_Buy'].iloc[-1] else '❌'}")
                                st.markdown(f"MACD: {'✅' if signals['MACD_Buy'].iloc[-1] else '❌'}")
                                st.markdown(f"MA Crossover: {'✅' if signals['MA_Cross_Buy'].iloc[-1] else '❌'}")
                                st.markdown(f"Bollinger Bands: {'✅' if signals['BB_Buy'].iloc[-1] else '❌'}")
                                st.markdown(f"Stochastic: {'✅' if signals['Stoch_Buy'].iloc[-1] else '❌'}")
                            
                            with col2:
                                st.markdown("#### Sell Signals")
                                st.markdown(f"RSI: {'✅' if signals['RSI_Sell'].iloc[-1] else '❌'}")
                                st.markdown(f"MACD: {'✅' if signals['MACD_Sell'].iloc[-1] else '❌'}")
                                st.markdown(f"MA Crossover: {'✅' if signals['MA_Cross_Sell'].iloc[-1] else '❌'}")
                                st.markdown(f"Bollinger Bands: {'✅' if signals['BB_Sell'].iloc[-1] else '❌'}")
                                st.markdown(f"Stochastic: {'✅' if signals['Stoch_Sell'].iloc[-1] else '❌'}")
                                
                            # Signal history
                            st.markdown("### Recent Signal History")
                            recent_signals = pd.DataFrame(index=signals.index[-10:])
                            recent_signals['Strong Buy'] = signals['Strong_Buy'][-10:]
                            recent_signals['Strong Sell'] = signals['Strong_Sell'][-10:]
                            recent_signals['Price'] = signals['Price'][-10:]
                            
                            st.dataframe(recent_signals)
                    
                    with tab4:
                        # Backtest results
                        portfolio, metrics = backtest_strategy(signals)
                        
                        if portfolio is not None and metrics is not None:
                            # Display performance metrics
                            st.markdown("### Backtest Performance")
                            
                            col1, col2, col3, col4 = st.columns(4)
                            col1.metric("Total Return", f"{metrics['Total Return']:.2f}%")
                            col2.metric("Annual Return", f"{metrics['Annual Return (%)']:.2f}%")
                            col3.metric("Sharpe Ratio", f"{metrics['Sharpe Ratio']:.2f}")
                            col4.metric("Final Value", f"${metrics['Final Value']:.2f}")
                            
                            # Portfolio value over time
                            fig = plot_portfolio_performance(portfolio, signals)
                            st.plotly_chart(fig, use_container_width=True)
                            
                            # Comparison with buy-and-hold
                            st.markdown("### Strategy Comparison")
                            
                            # Calculate buy and hold returns
                            buy_hold_return = ((data['Close'].iloc[-1] / data['Close'].iloc[0]) - 1) * 100
                            strategy_return = metrics['Total Return']
                            
                            # Create comparison chart
                            comparison_data = {
                                'Strategy': ['Buy and Hold', 'Trading Strategy'],
                                'Return (%)': [buy_hold_return, strategy_return]
                            }
                            
                            fig = go.Figure([
                                go.Bar(
                                    x=comparison_data['Strategy'],
                                    y=comparison_data['Return (%)'],
                                    marker_color=['lightblue', 'darkblue']
                                )
                            ])
                            
                            fig.update_layout(
                                title="Strategy Comparison",
                                xaxis_title="Strategy",
                                yaxis_title="Return (%)",
                                height=400
                            )
                            
                            st.plotly_chart(fig, use_container_width=True)
                            
                            # Risk warning
                            st.warning("""
                            **Note**: Past performance is not indicative of future results. The backtest 
                            results are based on historical data and do not account for market conditions, 
                            slippage, or other real-world trading factors.
                            """)
                else:
                    st.error("Could not calculate technical indicators with the provided data.")
            else:
                st.error(f"Could not fetch data for {ticker}. Please check the ticker symbol and try again.")
