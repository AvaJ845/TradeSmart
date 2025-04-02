import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np

from utils.data_fetcher import get_stock_data, fetch_option_chain
from utils.indicators import calculate_implied_volatility

def options_analysis_module():
    """
    Options Analysis module for options chain visualization and strategy evaluation
    """
    st.markdown('<p class="main-header">Options Analysis</p>', unsafe_allow_html=True)
    
    # Input parameters
    col1, col2 = st.columns(2)
    
    with col1:
        ticker = st.text_input("Enter Ticker Symbol", "AAPL")
    
    with col2:
        analysis_type = st.selectbox(
            "Analysis Type",
            options=["Options Chain", "Strategy Builder", "Implied Volatility Analysis"]
        )
    
    if st.button("Analyze Options"):
        with st.spinner("Fetching options data..."):
            # Fetch stock data for context
            stock_data = get_stock_data(ticker, period='1mo')
            
            if stock_data is not None:
                last_price = stock_data['Close'].iloc[-1]
                
                # Fetch options data
                expiration, calls, puts = fetch_option_chain(ticker)
                
                if expiration is not None and not calls.empty and not puts.empty:
                    st.markdown(f"### {ticker} Options Analysis")
                    st.markdown(f"Current Stock Price: **${last_price:.2f}**")
                    st.markdown(f"Expiration Date: **{expiration}**")
                    
                    # Based on analysis type
                    if analysis_type == "Options Chain":
                        # Create tabs for calls and puts
                        call_tab, put_tab = st.tabs(["Calls", "Puts"])
                        
                        with call_tab:
                            st.markdown("### Call Options")
                            
                            # Filter and format call options
                            calls_filtered = calls[['strike', 'lastPrice', 'bid', 'ask', 'volume', 'openInterest', 'impliedVolatility']]
                            calls_filtered.columns = ['Strike Price', 'Last Price', 'Bid', 'Ask', 'Volume', 'Open Interest', 'Implied Volatility']
                            calls_filtered['Implied Volatility'] = calls_filtered['Implied Volatility'] * 100
                            
                            # Calculate ITM/OTM
                            calls_filtered['Status'] = calls_filtered.apply(lambda row: 'ITM' if row['Strike Price'] < last_price else 'OTM', axis=1)
                            
                            # Display filtered options
                            st.dataframe(calls_filtered)
                        
                        with put_tab:
                            st.markdown("### Put Options")
                            
                            # Filter and format put options
                            puts_filtered = puts[['strike', 'lastPrice', 'bid', 'ask', 'volume', 'openInterest', 'impliedVolatility']]
                            puts_filtered.columns = ['Strike Price', 'Last Price', 'Bid', 'Ask', 'Volume', 'Open Interest', 'Implied Volatility']
                            puts_filtered['Implied Volatility'] = puts_filtered['Implied Volatility'] * 100
                            
                            # Calculate ITM/OTM
                            puts_filtered['Status'] = puts_filtered.apply(lambda row: 'ITM' if row['Strike Price'] > last_price else 'OTM', axis=1)
                            
                            # Display filtered options
                            st.dataframe(puts_filtered)
                    
                    elif analysis_type == "Strategy Builder":
                        st.markdown("### Options Strategy Builder")
                        st.info("Strategy builder feature is under development. Coming soon!")
                    
                    elif analysis_type == "Implied Volatility Analysis":
                        st.markdown("### Implied Volatility Analysis")
                        
                        # Implied Volatility visualization
                        fig = go.Figure()
                        
                        # Add call options IV
                        fig.add_trace(
                            go.Scatter(
                                x=calls['strike'],
                                y=calls['impliedVolatility'] * 100,
                                mode='markers',
                                name='Call IV',
                                marker=dict(color='green', size=10)
                            )
                        )
                        
                        # Add put options IV
                        fig.add_trace(
                            go.Scatter(
                                x=puts['strike'],
                                y=puts['impliedVolatility'] * 100,
                                mode='markers',
                                name='Put IV',
                                marker=dict(color='red', size=10)
                            )
                        )
                        
                        # Add vertical line for current stock price
                        fig.add_shape(
                            type="line",
                            x0=last_price,
                            y0=0,
                            x1=last_price,
                            y1=max(max(calls['impliedVolatility'] * 100), max(puts['impliedVolatility'] * 100)),
                            line=dict(color="blue", width=2, dash="dash")
                        )
                        
                        fig.update_layout(
                            title=f"{ticker} Options Implied Volatility",
                            xaxis_title="Strike Price",
                            yaxis_title="Implied Volatility (%)",
                            height=500
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Summary statistics
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.metric("Mean Call IV", f"{calls['impliedVolatility'].mean() * 100:.2f}%")
                        
                        with col2:
                            st.metric("Mean Put IV", f"{puts['impliedVolatility'].mean() * 100:.2f}%")
                        
                        with col3:
                            st.metric("Current Stock Price", f"${last_price:.2f}")
                else:
                    st.error(f"No options data available for {ticker}")
            else:
                st.error(f"Could not fetch stock data for {ticker}")
