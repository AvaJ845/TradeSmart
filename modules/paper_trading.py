import pandas as pd
import numpy as np

def simulate_paper_trade(data, strategy_type, initial_capital=10000):
    """
    Simulate paper trading based on different strategy types
    
    Parameters:
    data (pd.DataFrame): OHLCV DataFrame with price data
    strategy_type (str): Type of strategy to simulate
    initial_capital (float): Starting capital for simulation
    
    Returns:
    tuple: (portfolio_performance, performance_metrics)
    """
    from utils.indicators import calculate_technical_indicators, get_trading_signals
    
    # Calculate indicators
    indicators = calculate_technical_indicators(data)
    if indicators is None:
        return None, None
        
    # Get signals based on strategy type
    if strategy_type == "Technical Indicators":
        signals = get_trading_signals(indicators)
    elif strategy_type == "Moving Average Crossover":
        # Simple MA crossover strategy
        signals = pd.DataFrame(index=data.index)
        signals['Price'] = data['Close']
        signals['Strong_Buy'] = (indicators['MA20'] > indicators['MA50']) & (indicators['MA20'].shift(1) <= indicators['MA50'].shift(1))
        signals['Strong_Sell'] = (indicators['MA20'] < indicators['MA50']) & (indicators['MA20'].shift(1) >= indicators['MA50'].shift(1))
    elif strategy_type == "RSI Strategy":
        # RSI strategy
        signals = pd.DataFrame(index=data.index)
        signals['Price'] = data['Close']
        signals['Strong_Buy'] = (indicators['RSI'] < 30) & (indicators['RSI'].shift(1) < 30) & (indicators['RSI'] > indicators['RSI'].shift(1))
        signals['Strong_Sell'] = (indicators['RSI'] > 70) & (indicators['RSI'].shift(1) > 70) & (indicators['RSI'] < indicators['RSI'].shift(1))
    elif strategy_type == "MACD Strategy":
        # MACD strategy
        signals = pd.DataFrame(index=data.index)
        signals['Price'] = data['Close']
        signals['Strong_Buy'] = (indicators['MACD'] > indicators['MACD_Signal']) & (indicators['MACD'].shift(1) <= indicators['MACD_Signal'].shift(1))
        signals['Strong_Sell'] = (indicators['MACD'] < indicators['MACD_Signal']) & (indicators['MACD'].shift(1) >= indicators['MACD_Signal'].shift(1))
    else:
        return None, None
    
    # Run backtest with the signals
    return backtest_strategy(signals, initial_capital)

def backtest_strategy(signals, initial_capital=10000, risk_per_trade=0.01):
    """
    Backtest a trading strategy based on generated signals
    
    Parameters:
    signals (pd.DataFrame): DataFrame with trading signals
    initial_capital (float): Starting capital for the backtest
    risk_per_trade (float): Percentage of capital to risk per trade
    
    Returns:
    tuple: (portfolio_performance, performance_metrics)
    """
    if signals is None or len(signals) == 0:
        return None, None
    
    # Initialize portfolio tracking
    portfolio = pd.DataFrame(index=signals.index)
    portfolio['Price'] = signals['Price']
    portfolio['Cash'] = initial_capital
    portfolio['Positions'] = 0
    portfolio['Total'] = initial_capital
    
    # Trading parameters
    current_position = 0
    position_entry_price = 0
    
    for i in range(1, len(signals)):
        # Previous row's values
        prev_price = signals['Price'].iloc[i-1]
        current_price = signals['Price'].iloc[i]
        
        # Copy previous day's values
        portfolio.iloc[i] = portfolio.iloc[i-1]
        
        # Strong buy signal and no current position
        if signals['Strong_Buy'].iloc[i] and current_position == 0:
            # Calculate position size based on risk management
            risk_amount = portfolio.iloc[i-1]['Total'] * risk_per_trade
            position_size = int(risk_amount / current_price)
            
            # Enter long position
            current_position = position_size
            position_entry_price = current_price
            
            # Update portfolio
            portfolio.iloc[i]['Positions'] = current_position
            portfolio.iloc[i]['Cash'] -= current_position * current_price
        
        # Strong sell signal and have a current position
        elif signals['Strong_Sell'].iloc[i] and current_position > 0:
            # Calculate profit/loss
            profit_loss = (current_price - position_entry_price) * current_position
            
            # Update portfolio
            portfolio.iloc[i]['Cash'] += current_position * current_price
            portfolio.iloc[i]['Positions'] = 0
            current_position = 0
            position_entry_price = 0
        
        # Calculate total portfolio value
        portfolio.iloc[i]['Total'] = (
            portfolio.iloc[i]['Cash'] + 
            portfolio.iloc[i]['Positions'] * current_price
        )
    
    # Calculate performance metrics
    returns = portfolio['Total'].pct_change()
    
    metrics = {
        'Total Return': ((portfolio['Total'].iloc[-1] / initial_capital) - 1) * 100,
        'Annual Return (%)': returns.mean() * 252 * 100,
        'Annual Volatility (%)': returns.std() * np.sqrt(252) * 100,
        'Sharpe Ratio': (returns.mean() * 252) / (returns.std() * np.sqrt(252)),
        'Max Drawdown (%)': calculate_max_drawdown(portfolio['Total']) * 100,
        'Final Value': portfolio['Total'].iloc[-1]
    }
    
    return portfolio, metrics

def calculate_max_drawdown(series):
    """
    Calculate the maximum drawdown of a portfolio value series
    
    Parameters:
    series (pd.Series): Portfolio value series
    
    Returns:
    float: Maximum drawdown as a decimal
    """
    cumulative_max = series.cummax()
    drawdown = (series - cumulative_max) / cumulative_max
    return drawdown.min()

# Define the paper_trading_module
class PaperTradingModule:
    def __init__(self):
        # ...initialize module...
        pass

    def execute_trade(self, trade_details):
        # ...logic for executing a paper trade...
        pass

    def get_trade_history(self):
        # ...logic for retrieving trade history...
        pass

# Export the module
__all__ = ['paper_trading_module']
paper_trading_module = PaperTradingModule()
