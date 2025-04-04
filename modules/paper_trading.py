import pandas as pd
import numpy as np
import streamlit as st
from datetime import datetime, timedelta
from utils.data_fetcher import get_stock_data
from utils.visualization import plot_portfolio_performance

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
    
    try:
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
            # Copy previous day's values
            portfolio.iloc[i] = portfolio.iloc[i-1]
            current_price = signals['Price'].iloc[i]
            
            # Strong buy signal and no current position
            if signals['Strong_Buy'].iloc[i] and current_position == 0:
                # Calculate position size based on risk management
                available_capital = portfolio.iloc[i-1]['Cash']
                risk_amount = min(available_capital * risk_per_trade, available_capital)
                position_size = int(risk_amount / current_price)
                
                if position_size > 0:
                    # Enter long position
                    current_position = position_size
                    position_entry_price = current_price
                    trade_value = current_position * position_entry_price
                    
                    # Update portfolio
                    portfolio.at[portfolio.index[i], 'Positions'] = current_position
                    portfolio.at[portfolio.index[i], 'Cash'] -= trade_value
            
            # Strong sell signal and have a current position
            elif signals['Strong_Sell'].iloc[i] and current_position > 0:
                # Calculate profit/loss and close position
                trade_value = current_position * current_price
                portfolio.at[portfolio.index[i], 'Cash'] += trade_value
                portfolio.at[portfolio.index[i], 'Positions'] = 0
                current_position = 0
                position_entry_price = 0
            
            # Update mark-to-market portfolio value
            portfolio.at[portfolio.index[i], 'Total'] = (
                portfolio.at[portfolio.index[i], 'Cash'] + 
                portfolio.at[portfolio.index[i], 'Positions'] * current_price
            )
        
        # Calculate performance metrics safely
        returns = portfolio['Total'].pct_change().fillna(0)
        mean_return = returns.mean()
        std_return = returns.std()
        sharpe_ratio = (mean_return * 252) / (std_return * np.sqrt(252)) if std_return > 0 else 0
        max_dd = calculate_max_drawdown(portfolio['Total'])
        final_value = portfolio['Total'].iloc[-1]
        total_return = ((final_value / initial_capital) - 1) * 100
        
        # Format metrics safely
        metrics = {
            'Total Return': round(total_return, 2),
            'Annual Return (%)': round(mean_return * 252 * 100, 2),
            'Annual Volatility (%)': round(std_return * np.sqrt(252) * 100, 2),
            'Sharpe Ratio': round(sharpe_ratio, 2),
            'Max Drawdown (%)': round(max_dd * 100, 2),
            'Final Value': round(final_value, 2)
        }
        
        return portfolio, metrics
        
    except Exception as e:
        print(f"Backtest error: {str(e)}")
        return None, None

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

class PaperTradingModule:
    def __init__(self):
        """Initialize paper trading module with trade history and account data"""
        self.trade_history = pd.DataFrame(columns=[
            'timestamp', 'symbol', 'type', 'price', 'quantity', 
            'value', 'balance_before', 'balance_after'
        ])
        self.account_balance = 10000.0  # Default starting balance
        self.positions = {}  # Current positions {symbol: quantity}
        
    def execute_trade(self, trade_details):
        """
        Execute a paper trade and update history
        
        Parameters:
        trade_details (dict): Contains trade information
            - symbol (str): Trading symbol
            - type (str): 'buy' or 'sell'
            - price (float): Execution price
            - quantity (int): Number of shares
            
        Returns:
        bool: True if trade successful, False otherwise
        """
        try:
            symbol = trade_details.get('symbol')
            trade_type = trade_details.get('type')
            price = float(trade_details.get('price', 0))
            quantity = int(trade_details.get('quantity', 0))
            
            if not all([symbol, trade_type, price > 0, quantity > 0]):
                return False
                
            trade_value = price * quantity
            balance_before = self.account_balance
            
            # Execute trade
            if trade_type.lower() == 'buy':
                if trade_value > self.account_balance:
                    return False
                self.account_balance -= trade_value
                self.positions[symbol] = self.positions.get(symbol, 0) + quantity
            
            elif trade_type.lower() == 'sell':
                if self.positions.get(symbol, 0) < quantity:
                    return False
                self.account_balance += trade_value
                self.positions[symbol] = self.positions.get(symbol, 0) - quantity
            
            # Record trade
            new_trade = pd.DataFrame([{
                'timestamp': pd.Timestamp.now(),
                'symbol': symbol,
                'type': trade_type,
                'price': round(price, 2),
                'quantity': quantity,
                'value': round(trade_value, 2),
                'balance_before': round(balance_before, 2),
                'balance_after': round(self.account_balance, 2)
            }])
            
            self.trade_history = pd.concat([self.trade_history, new_trade])
            return True
            
        except Exception as e:
            print(f"Trade execution error: {str(e)}")
            return False

    def get_trade_history(self):
        """
        Get the complete trade history
        
        Returns:
        pd.DataFrame: Trade history dataframe
        """
        return self.trade_history.copy()
    
    def get_account_summary(self):
        """
        Get current account status
        
        Returns:
        dict: Account summary including balance and positions
        """
        return {
            'balance': self.account_balance,
            'positions': self.positions.copy(),
            'total_trades': len(self.trade_history)
        }

def paper_trading_module():
    st.title("Paper Trading Simulator")
    st.write("Paper trading simulation functionality will be implemented here.")
    
    # Add placeholder for paper trading features
    st.info("This module is under development. Coming soon!")
    
    # Basic structure for future implementation
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Trading Account")
        st.number_input("Initial Balance ($)", min_value=0, value=10000)
        
    with col2:
        st.subheader("Trade Entry")
        st.text_input("Symbol")
        st.number_input("Quantity", min_value=1, value=1)
        st.selectbox("Order Type", ["Market", "Limit"])

# Export the module
__all__ = ['PaperTradingModule', 'simulate_paper_trade', 'backtest_strategy', 'paper_trading_module']
paper_trading_module = PaperTradingModule()

# Make sure to define the module's main function
if __name__ == "__main__":
    paper_trading_module()
