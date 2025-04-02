import streamlit as st
from utils.data_fetcher import get_stock_data

def home_page():
    """
    Display the home page of the TradeSmart application.
    """
    st.markdown('<p class="main-header">TradeSmart: Advanced Trading Analysis Platform</p>', unsafe_allow_html=True)
    
    st.markdown("""
    Welcome to TradeSmart, a comprehensive trading analysis platform designed to help you make more informed trading decisions.
    
    ### Features:
    - **📊 Stock Analysis**: Technical indicators, pattern recognition, and trading signals
    - **💰 Options Analysis**: Options chain visualization, pricing models, and strategy evaluation
    - **🔍 Market Anomaly Scanner**: Find potential trading opportunities through market discrepancies
    - **💼 Paper Trading Simulator**: Test strategies without risking real money
    - **💵 Dividend Analysis**: Research dividend stocks and income potential
    - **📚 Knowledge Base**: Trading definitions and concepts
    
    ### Getting Started:
    1. Select a module from the sidebar
    2. Enter ticker symbols for analysis
    3. Review the generated insights and visualizations
    """)
    
    st.markdown('<p class="sub-header">⚠️ Important Disclaimer</p>', unsafe_allow_html=True)
    st.warning("""
    This application is for educational and informational purposes only. No trading strategy can guarantee returns, especially the 20-30% levels mentioned. Trading stocks, options, and other financial instruments involves significant risk of loss.
    
    Always perform your own research and consider consulting with a financial advisor before making investment decisions.
    """)
    
    # Quick search functionality
    st.markdown('<p class="sub-header">Quick Analysis</p>', unsafe_allow_html=True)
    quick_ticker = st.text_input("Enter a ticker symbol for quick analysis:", "AAPL")
    
    if st.button("Run Quick Analysis"):
        data = get_stock_data(quick_ticker, period='6mo')
        if data is not None:
            # Show basic info
            st.markdown(f"### {quick_ticker} Overview")
            
            # Get last price and change
            last_price = data['Close'].iloc[-1]
            price_change = (data['Close'].iloc[-1] / data['Close'].iloc[-2] - 1) * 100
            
            # Create columns for metrics
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Last Price", f"${last_price:.2f}", f"{price_change:.2f}%")
            col2.metric("Volume", f"{data['Volume'].iloc[-1]:,.0f}", f"{(data['Volume'].iloc[-1]/data['Volume'].mean()-1)*100:.1f}%")
            col3.metric("52W High", f"${data['Close'].max():.2f}")
            col4.metric("52W Low", f"${data['Close'].min():.2f}")
            
            # Import visualization here to avoid circular imports
            from utils.visualization import plot_price_chart
            
            # Plot price chart
            fig = plot_price_chart(data, quick_ticker)
            st.plotly_chart(fig, use_container_width=True)
