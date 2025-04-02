import yfinance as yf
import streamlit as st
import pandas as pd

def get_stock_data(ticker, period='1y', interval='1d'):
    """
    Fetch stock data from Yahoo Finance
    
    Parameters:
    ticker (str): Ticker symbol
    period (str): Period to fetch data for (e.g., '1d', '1mo', '1y')
    interval (str): Interval between data points (e.g., '1m', '1h', '1d')
    
    Returns:
    pandas.DataFrame: DataFrame with OHLCV data or None if there was an error
    """
    try:
        data = yf.download(ticker, period=period, interval=interval)
        return data
    except Exception as e:
        st.error(f"Error fetching data for {ticker}: {e}")
        return None

def fetch_option_chain(ticker):
    """
    Fetch options chain data for a given ticker
    
    Parameters:
    ticker (str): Ticker symbol
    
    Returns:
    tuple: (expiration, calls, puts) or (None, [], []) if there was an error
    """
    try:
        stock = yf.Ticker(ticker)
        expirations = stock.options
        
        if not expirations:
            return None, [], []
            
        # Get the nearest expiration date
        expiration = expirations[0]
        
        # Fetch calls and puts
        calls = stock.option_chain(expiration).calls
        puts = stock.option_chain(expiration).puts
        
        return expiration, calls, puts
    except Exception as e:
        st.error(f"Error fetching options data: {e}")
        return None, [], []

def get_stock_info(ticker):
    """
    Fetch fundamental stock information
    
    Parameters:
    ticker (str): Ticker symbol
    
    Returns:
    dict: Stock information or None if there was an error
    """
    try:
        stock = yf.Ticker(ticker)
        return stock.info
    except Exception as e:
        st.error(f"Error fetching stock info for {ticker}: {e}")
        return None

def get_dividend_data(ticker):
    """
    Fetch and analyze dividend data for a stock
    
    Parameters:
    ticker (str): Ticker symbol
    
    Returns:
    dict: Dividend analysis or None if there was an error
    """
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        dividends = stock.dividends
        
        if dividends.empty:
            return {
                'Dividend Yield (%)': 0,
                'Payout Ratio': 0,
                'Dividend Growth (5Y)': 0,
                'Years of Growth': 0,
                'Last Dividend Date': None,
                'Next Ex-Dividend': None,
                'Annual Dividends': [],
            }
            
        # Calculate metrics
        annual_dividends = dividends.groupby(dividends.index.year).sum()
        
        div_yield = info.get('dividendYield', 0)
        if div_yield:
            div_yield *= 100  # Convert to percentage
            
        growth_5y = 0
        if len(annual_dividends) >= 5:
            growth_5y = (annual_dividends.iloc[-1] / annual_dividends.iloc[-5]) ** (1/5) - 1
            growth_5y *= 100  # Convert to percentage
            
        # Calculate years of consecutive dividend growth
        years_growth = 0
        for i in range(len(annual_dividends)-1, 0, -1):
            if annual_dividends.iloc[i] > annual_dividends.iloc[i-1]:
                years_growth += 1
            else:
                break
                
        return {
            'Dividend Yield (%)': div_yield,
            'Payout Ratio': info.get('payoutRatio', 0) * 100 if info.get('payoutRatio') else 0,
            'Dividend Growth (5Y) (%)': growth_5y,
            'Years of Growth': years_growth,
            'Last Dividend Date': dividends.index[-1].strftime('%Y-%m-%d') if not dividends.empty else None,
            'Next Ex-Dividend': info.get('exDividendDate', None),
            'Annual Dividends': annual_dividends.to_dict(),
        }
    except Exception as e:
        st.error(f"Error fetching dividend data: {e}")
        return None
