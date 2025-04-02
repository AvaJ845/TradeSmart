import pandas as pd
import numpy as np
from ta.trend import MACD
from ta.momentum import RSIIndicator, StochasticOscillator
from ta.volatility import BollingerBands

def calculate_technical_indicators(data):
    """
    Calculate various technical indicators for a given price dataset
    
    Parameters:
    data (pd.DataFrame): OHLCV DataFrame with price data
    
    Returns:
    pd.DataFrame: Original DataFrame with added technical indicators
    """
    if data is None or len(data) < 20:
        return None
    
    # Copy the dataframe
    df = data.copy()
    
    # MACD
    macd = MACD(close=df['Close'])
    df['MACD'] = macd.macd()
    df['MACD_Signal'] = macd.macd_signal()
    df['MACD_Hist'] = macd.macd_diff()
    
    # RSI
    rsi = RSIIndicator(close=df['Close'])
    df['RSI'] = rsi.rsi()
    
    # Bollinger Bands
    bollinger = BollingerBands(close=df['Close'])
    df['BB_High'] = bollinger.bollinger_hband()
    df['BB_Low'] = bollinger.bollinger_lband()
    df['BB_Mid'] = bollinger.bollinger_mavg()
    
    # Moving Averages
    df['MA20'] = df['Close'].rolling(window=20).mean()
    df['MA50'] = df['Close'].rolling(window=50).mean()
    df['MA200'] = df['Close'].rolling(window=200).mean()
    
    # Stochastic Oscillator
    stoch = StochasticOscillator(high=df['High'], low=df['Low'], close=df['Close'])
    df['Stoch_K'] = stoch.stoch()
    df['Stoch_D'] = stoch.stoch_signal()
    
    # Volume Indicators
    df['Volume_MA20'] = df['Volume'].rolling(window=20).mean()
    
    return df

def get_trading_signals(data):
    """
    Generate trading signals based on technical indicators
    
    Parameters:
    data (pd.DataFrame): DataFrame with technical indicators
    
    Returns:
    pd.DataFrame: DataFrame with trading signals
    """
    if data is None or 'RSI' not in data.columns:
        return None
    
    signals = pd.DataFrame(index=data.index)
    signals['Price'] = data['Close']
    
    # RSI Signals
    signals['RSI_Buy'] = (data['RSI'] < 30) & (data['RSI'].shift(1) < 30) & (data['RSI'] > data['RSI'].shift(1))
    signals['RSI_Sell'] = (data['RSI'] > 70) & (data['RSI'].shift(1) > 70) & (data['RSI'] < data['RSI'].shift(1))
    
    # MACD Signals
    signals['MACD_Buy'] = (data['MACD'] > data['MACD_Signal']) & (data['MACD'].shift(1) <= data['MACD_Signal'].shift(1))
    signals['MACD_Sell'] = (data['MACD'] < data['MACD_Signal']) & (data['MACD'].shift(1) >= data['MACD_Signal'].shift(1))
    
    # Moving Average Crossovers
    signals['MA_Cross_Buy'] = (data['MA20'] > data['MA50']) & (data['MA20'].shift(1) <= data['MA50'].shift(1))
    signals['MA_Cross_Sell'] = (data['MA20'] < data['MA50']) & (data['MA20'].shift(1) >= data['MA50'].shift(1))
    
    # Bollinger Band Signals
    signals['BB_Buy'] = data['Close'] <= data['BB_Low']
    signals['BB_Sell'] = data['Close'] >= data['BB_High']
    
    # Stochastic Oscillator
    signals['Stoch_Buy'] = (data['Stoch_K'] < 20) & (data['Stoch_K'] > data['Stoch_D']) & (data['Stoch_K'].shift(1) <= data['Stoch_D'].shift(1))
    signals['Stoch_Sell'] = (data['Stoch_K'] > 80) & (data['Stoch_K'] < data['Stoch_D']) & (data['Stoch_K'].shift(1) >= data['Stoch_D'].shift(1))
    
    # Combined Signals (more conservative approach)
    signals['Strong_Buy'] = (signals['RSI_Buy'] & signals['MACD_Buy']) | (signals['RSI_Buy'] & signals['MA_Cross_Buy']) | (signals['MACD_Buy'] & signals['MA_Cross_Buy'])
    signals['Strong_Sell'] = (signals['RSI_Sell'] & signals['MACD_Sell']) | (signals['RSI_Sell'] & signals['MA_Cross_Sell']) | (signals['MACD_Sell'] & signals['MA_Cross_Sell'])
    
    return signals

def calculate_implied_volatility(option_price, stock_price, strike_price, time_to_expiry, is_call=True, risk_free_rate=0.05):
    """
    Approximate implied volatility using a simple approach
    
    Parameters:
    option_price (float): Price of the option
    stock_price (float): Price of the underlying stock
    strike_price (float): Strike price of the option
    time_to_expiry (float): Time to expiration in years
    is_call (bool): True if call option, False if put option
    risk_free_rate (float): Risk-free interest rate
    
    Returns:
    float: Approximated implied volatility
    """
    # Simple approximation for demo purposes
    if is_call:
        return (option_price / (stock_price * np.sqrt(time_to_expiry))) * 2
    else:
        return (option_price / (strike_price * np.sqrt(time_to_expiry))) * 2
