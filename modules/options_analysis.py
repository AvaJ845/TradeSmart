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
                            calls_filtered['Status'] = 'OTM'
                            calls_filtered.loc[calls_filtered['Strike Price'] < last
