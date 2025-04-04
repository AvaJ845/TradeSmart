import streamlit as st

def about_definitions_module():
    st.title("About & Definitions")
    
    st.markdown("## About TradeSmart")
    st.write("""
    TradeSmart is a comprehensive trading analysis platform designed to help users make 
    informed trading decisions through various analysis tools and educational resources.
    """)
    
    st.markdown("## Key Trading Definitions")
    
    definitions = {
        "Stock": "A type of security that represents ownership in a corporation.",
        "Option": "A contract giving the buyer the right to buy or sell an underlying asset at a specific price on or before a certain date.",
        "Dividend": "A distribution of a company's earnings to shareholders.",
        "Market Anomaly": "A distortion in the market that contradicts the efficient market hypothesis.",
        "Paper Trading": "Practice trading with virtual money to test strategies without risk."
    }  # Make sure all braces are properly closed
    
    for term, definition in definitions.items():
        with st.expander(term):
            st.write(definition)
