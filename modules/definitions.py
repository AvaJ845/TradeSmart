import streamlit as st

def about_definitions_module():
    """
    About & Definitions module providing explanations of trading concepts
    """
    st.markdown('<p class="main-header">About & Definitions</p>', unsafe_allow_html=True)
    
    st.markdown("""
    Welcome to the TradeSmart platform, a comprehensive trading analysis and simulation tool. This module provides
    key definitions and concepts to help you understand the various analyses presented throughout the application.
    """)
    
    # Create tabs for different categories
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "General Trading", "Technical Analysis", "Options Trading", "Relative Value", "Risk Management"
    ])
    
    with tab1:
        st.markdown("## General Trading Concepts")
        
        general_terms = [
            {
                "term": "Day Trading",
                "definition": "The practice of buying and selling financial instruments within the same trading day. Day traders typically close all positions before the market closes to avoid overnight risk.",
                "key_points": [
                    "Involves high transaction frequency",
                    "Focuses on short-term price movements",
                    "Typically requires significant time commitment",
                    "Relies on technical analysis more than fundamentals",
                    "Returns are highly variable and success rates are statistically low"
                ]
            },
            {
                "term": "Paper Trading",
                "definition": "The practice of simulated trading with virtual money to test strategies without risking real capital. It's an essential practice for developing and refining trading strategies.",
                "key_points": [
                    "No real money at risk",
                    "Useful for testing new strategies",
                    "Helps develop discipline and trading psychology",
                    "May not fully replicate real market conditions (slippage, emotions)",
                    "Should be followed by small position sizes when transitioning to real trading"
                ]
            },
            {
                "term": "Market Order",
                "definition": "An order to buy or sell a security immediately at the best available current price. Market orders guarantee execution but not price.",
                "key_points": [
                    "Executes immediately at current market price",
                    "Prioritizes execution speed over price",
                    "Can be subject to slippage in volatile markets",
                    "Best used for highly liquid securities"
                ]
            },
            {
                "term": "Limit Order",
                "definition": "An order to buy or sell a security at a specified price or better. Limit orders guarantee price but not execution.",
                "key_points": [
                    "Executes only at specified price or better",
                    "May not execute if price doesn't reach limit price",
                    "Reduces risk of slippage",
                    "Can be used to 'scale in' by setting multiple orders at different prices"
                ]
            },
            {
                "term": "Slippage",
                "definition": "The difference between the expected price of a trade and the price at which the trade is actually executed. Slippage often occurs during periods of high volatility or low liquidity.",
                "key_points": [
                    "More common in illiquid markets",
                    "Can significantly impact trading performance",
                    "Often larger with market orders",
                    "Should be factored into backtests and strategy development"
                ]
            },
            {
                "term": "Market Liquidity",
                "definition": "The degree to which a security can be quickly bought or sold without affecting its price. High liquidity means large transactions can occur with minimal price impact.",
                "key_points": [
                    "Higher liquidity typically means tighter bid-ask spreads",
                    "More liquid markets are generally safer for day trading",
                    "Stocks with high average daily volume are more liquid",
                    "Liquidity can evaporate quickly during market stress"
                ]
            },
            {
                "term": "Bid-Ask Spread",
                "definition": "The difference between the highest price a buyer is willing to pay (bid) and the lowest price a seller is willing to accept (ask). Narrower spreads indicate higher liquidity.",
                "key_points": [
                    "Represents transaction cost",
                    "Narrower in more liquid securities",
                    "Widens during volatility",
                    "Day traders must overcome the spread to profit"
                ]
            }
        ]
        
        for term in general_terms:
            with st.expander(term["term"]):
                st.markdown(f"### {term['term']}")
                st.markdown(term["definition"])
                
                st.markdown("#### Key Points:")
                for point in term["key_points"]:
                    st.markdown(f"- {point}")
    
    with tab2:
        st.markdown("## Technical Analysis Indicators")
        
        technical_terms = [
            {
                "term": "Relative Strength Index (RSI)",
                "definition": "A momentum oscillator that measures the speed and change of price movements on a scale from 0 to 100. Traditional interpretation considers RSI above 70 as overbought and below 30 as oversold.",
                "calculation": "RSI = 100 - (100 / (1 + RS)), where RS = Average Gain / Average Loss over a specified period (typically 14 days)",
                "interpretation": [
                    "Above 70: Potentially overbought (selling opportunity)",
                    "Below 30: Potentially oversold (buying opportunity)",
                    "Divergence: When price makes new high/low but RSI doesn't, suggests potential reversal",
                    "Centerline (50) crossover can signal trend shifts"
                ]
            },
            {
                "term": "Moving Average Convergence Divergence (MACD)",
                "definition": "A trend-following momentum indicator that shows the relationship between two moving averages of a security's price. The MACD line is calculated by subtracting the 26-period EMA from the 12-period EMA.",
                "calculation": "MACD Line = 12-period EMA - 26-period EMA, Signal Line = 9-period EMA of MACD Line, Histogram = MACD Line - Signal Line",
                "interpretation": [
                    "MACD crossing above signal line: Bullish signal",
                    "MACD crossing below signal line: Bearish signal",
                    "MACD above zero: Uptrend, below zero: Downtrend",
                    "Histogram growing: Trend momentum increasing",
                    "Divergence between MACD and price can signal potential reversals"
                ]
            },
            {
                "term": "Bollinger Bands",
                "definition": "A volatility indicator consisting of three lines: a simple moving average (middle band) and an upper and lower band that are standard deviations away from the middle band.",
                "calculation": "Middle Band = 20-day SMA, Upper Band = 20-day SMA + (20-day standard deviation × 2), Lower Band = 20-day SMA - (20-day standard deviation × 2)",
                "interpretation": [
                    "Price touching upper band: Potentially overbought",
                    "Price touching lower band: Potentially oversold",
                    "Bands narrowing: Decreasing volatility, potential breakout ahead",
                    "Bands widening: Increasing volatility",
                    "'Bollinger Band squeeze' followed by breakout can signal strong momentum"
                ]
            },
            {
                "term": "Moving Averages",
                "definition": "A calculation used to analyze data points by creating a series of averages of different subsets of the full data set. In trading, moving averages smooth out price action and help identify trends.",
                "calculation": "Simple Moving Average (SMA): Average of closing prices over N periods. Exponential Moving Average (EMA): Weighted average giving more importance to recent prices.",
                "interpretation": [
                    "Price above MA: Uptrend, price below MA: Downtrend",
                    "MA crossovers: When shorter-term MA crosses above longer-term MA (Golden Cross), bullish; when crossing below (Death Cross), bearish",
                    "Multiple MAs: When arranged in order (shortest to longest or vice versa), indicates strong trend",
                    "MA as support/resistance: Price often bounces off MAs during trends"
                ]
            },
            {
                "term": "Stochastic Oscillator",
                "definition": "A momentum indicator comparing a particular closing price of a security to a range of its prices over a certain period of time. It follows the speed or momentum of price.",
                "calculation": "%K = (Current Close - Lowest Low) / (Highest High - Lowest Low) × 100, %D = 3-day SMA of %K",
                "interpretation": [
                    "Above 80: Potentially overbought",
                    "Below 20: Potentially oversold",
                    "%K crossing above %D: Bullish signal",
                    "%K crossing below %D: Bearish signal",
                    "Divergence with price can signal potential reversals"
                ]
            },
            {
                "term": "Fibonacci Retracement",
                "definition": "A method of technical analysis that uses horizontal lines to indicate areas of support or resistance at the key Fibonacci levels before the price continues in the original direction.",
                "calculation": "Based on the Fibonacci sequence, the key retracement levels are 23.6%, 38.2%, 50%, 61.8%, and 78.6%",
                "interpretation": [
                    "Common retracement levels: 38.2%, 50%, and 61.8%",
                    "Used to identify potential reversal points during a trend pullback",
                    "Often more reliable when multiple Fibonacci levels coincide with other technical indicators",
                    "Can be used for both uptrends (drawing from bottom to top) and downtrends (drawing from top to bottom)"
                ]
            },
            {
                "term": "Volume",
                "definition": "The number of shares or contracts traded in a security or market during a given period. It is an important indicator of market activity and liquidity.",
                "interpretation": [
                    "Rising price with rising volume: Strong trend confirmation",
                    "Rising price with falling volume: Potential trend weakness",
                    "Falling price with rising volume: Strong downtrend confirmation",
                    "Falling price with falling volume: Potential downtrend weakness",
                    "Volume spikes often signal potential reversals or breakouts"
                ]
            }
        ]
        
        for term in technical_terms:
            with st.expander(term["term"]):
                st.markdown(f"### {term['term']}")
                st.markdown(term["definition"])
                
                st.markdown("#### Calculation:")
                st.markdown(term["calculation"])
                
                st.markdown("#### Interpretation:")
                for point in term["interpretation"]:
                    st.markdown(f"- {point}")
    
    with tab3:
        st.markdown("## Options Trading Concepts")
        
        options_terms = [
            {
                "term": "Call Option",
