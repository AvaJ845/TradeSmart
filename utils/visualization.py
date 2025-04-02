import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

def plot_price_chart(data, ticker, include_volume=True):
    """
    Create a candlestick chart for stock price data
    
    Parameters:
    data (pd.DataFrame): OHLCV DataFrame with price data
    ticker (str): Ticker symbol for the chart title
    include_volume (bool): Whether to include volume subplot
    
    Returns:
    plotly.graph_objects.Figure: Plotly figure object
    """
    if include_volume:
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
    else:
        fig = go.Figure()
        
        fig.add_trace(
            go.Candlestick(
                x=data.index,
                open=data['Open'],
                high=data['High'],
                low=data['Low'],
                close=data['Close'],
                name=ticker
            )
        )
        
        fig.update_layout(
            title=f"{ticker} Price Chart",
            xaxis_title="Date",
            yaxis_title="Price ($)",
            height=500
        )
    
    return fig

def plot_technical_indicators(data, indicator_name):
    """
    Create a chart for a specific technical indicator
    
    Parameters:
    data (pd.DataFrame): DataFrame with technical indicators
    indicator_name (str): Name of the indicator to plot
    
    Returns:
    plotly.graph_objects.Figure: Plotly figure object
    """
    fig = go.Figure()
    
    if indicator_name == "RSI":
        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=data['RSI'],
                name="RSI",
                line=dict(color='purple', width=1)
            )
        )
        
        # Add overbought/oversold lines
        fig.add_shape(
            type="line",
            x0=data.index[0],
            y0=70,
            x1=data.index[-1],
            y1=70,
            line=dict(color="red", width=2, dash="dash")
        )
        
        fig.add_shape(
            type="line",
            x0=data.index[0],
            y0=30,
            x1=data.index[-1],
            y1=30,
            line=dict(color="green", width=2, dash="dash")
        )
        
        fig.update_layout(
            title="Relative Strength Index (RSI)",
            xaxis_title="Date",
            yaxis_title="RSI Value",
            height=400
        )
    
    elif indicator_name == "MACD":
        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=data['MACD'],
                name="MACD",
                line=dict(color='blue', width=1)
            )
        )
        
        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=data['MACD_Signal'],
                name="Signal Line",
                line=dict(color='red', width=1)
            )
        )
        
        fig.add_trace(
            go.Bar(
                x=data.index,
                y=data['MACD_Hist'],
                name="Histogram",
                marker=dict(color='green')
            )
        )
        
        fig.update_layout(
            title="Moving Average Convergence Divergence (MACD)",
            xaxis_title="Date",
            yaxis_title="Value",
            height=400
        )
    
    elif indicator_name == "Bollinger":
        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=data['Close'],
                name="Price",
                line=dict(color='black', width=1)
            )
        )
        
        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=data['BB_High'],
                name="Upper Band",
                line=dict(color='red', width=1, dash='dash')
            )
        )
        
        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=data['BB_Mid'],
                name="Middle Band (20 SMA)",
                line=dict(color='blue', width=1)
            )
        )
        
        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=data['BB_Low'],
                name="Lower Band",
                line=dict(color='green', width=1, dash='dash')
            )
        )
        
        fig.update_layout(
            title="Bollinger Bands",
            xaxis_title="Date",
            yaxis_title="Price",
            height=400
        )
    
    elif indicator_name == "Stochastic":
        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=data['Stoch_K'],
                name="%K Line",
                line=dict(color='blue', width=1)
            )
        )
        
        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=data['Stoch_D'],
                name="%D Line",
                line=dict(color='red', width=1)
            )
        )
        
        # Add overbought/oversold lines
        fig.add_shape(
            type="line",
            x0=data.index[0],
            y0=80,
            x1=data.index[-1],
            y1=80,
            line=dict(color="red", width=2, dash="dash")
        )
        
        fig.add_shape(
            type="line",
            x0=data.index[0],
            y0=20,
            x1=data.index[-1],
            y1=20,
            line=dict(color="green", width=2, dash="dash")
        )
        
        fig.update_layout(
            title="Stochastic Oscillator",
            xaxis_title="Date",
            yaxis_title="Value",
            height=400
        )
    
    elif indicator_name == "Moving Averages":
        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=data['Close'],
                name="Price",
                line=dict(color='black', width=1)
            )
        )
        
        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=data['MA20'],
                name="MA20",
                line=dict(color='blue', width=1)
            )
        )
        
        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=data['MA50'],
                name="MA50",
                line=dict(color='red', width=1)
            )
        )
        
        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=data['MA200'],
                name="MA200",
                line=dict(color='green', width=1)
            )
        )
        
        fig.update_layout(
            title="Moving Averages",
            xaxis_title="Date",
            yaxis_title="Price",
            height=400
        )
    
    return fig

def plot_trading_signals(signals):
    """
    Create a chart with trading signals
    
    Parameters:
    signals (pd.DataFrame): DataFrame with trading signals
    
    Returns:
    plotly.graph_objects.Figure: Plotly figure object
    """
    fig = go.Figure()
    
    # Add price line
    fig.add_trace(
        go.Scatter(
            x=signals.index,
            y=signals['Price'],
            name="Price",
            line=dict(color='black', width=1)
        )
    )
    
    # Add buy signals
    buy_signals = signals[signals['Strong_Buy']]
    if not buy_signals.empty:
        fig.add_trace(
            go.Scatter(
                x=buy_signals.index,
                y=buy_signals['Price'],
                name="Buy Signal",
                mode="markers",
                marker=dict(
                    color='green',
                    size=10,
                    symbol="triangle-up",
                    line=dict(width=2, color='darkgreen')
                )
            )
        )
    
    # Add sell signals
    sell_signals = signals[signals['Strong_Sell']]
    if not sell_signals.empty:
        fig.add_trace(
            go.Scatter(
                x=sell_signals.index,
                y=sell_signals['Price'],
                name="Sell Signal",
                mode="markers",
                marker=dict(
                    color='red',
                    size=10,
                    symbol="triangle-down",
                    line=dict(width=2, color='darkred')
                )
            )
        )
    
    fig.update_layout(
        title="Trading Signals",
        xaxis_title="Date",
        yaxis_title="Price",
        height=500
    )
    
    return fig

def plot_portfolio_performance(portfolio, signals=None):
    """
    Create a chart showing portfolio performance over time
    
    Parameters:
    portfolio (pd.DataFrame): DataFrame with portfolio values
    signals (pd.DataFrame, optional): DataFrame with trading signals
    
    Returns:
    plotly.graph_objects.Figure: Plotly figure object
    """
    fig = go.Figure()
    
    fig.add_trace(
        go.Scatter(
            x=portfolio.index,
            y=portfolio['Total'],
            name="Portfolio Value",
            line=dict(color='blue', width=2)
        )
    )
    
    # Add Buy and Sell markers if signals are provided
    if signals is not None:
        portfolio_buy = portfolio[signals['Strong_Buy']]
        portfolio_sell = portfolio[signals['Strong_Sell']]
        
        if not portfolio_buy.empty:
            fig.add_trace(
                go.Scatter(
                    x=portfolio_buy.index,
                    y=portfolio_buy['Total'],
                    name="Buy",
                    mode="markers",
                    marker=dict(color='green', size=10, symbol="circle")
                )
            )
            
        if not portfolio_sell.empty:
            fig.add_trace(
                go.Scatter(
                    x=portfolio_sell.index,
                    y=portfolio_sell['Total'],
                    name="Sell",
                    mode="markers",
                    marker=dict(color='red', size=10, symbol="circle")
                )
            )
    
    fig.update_layout(
        title="Portfolio Value Over Time",
        xaxis_title="Date",
        yaxis_title="Value ($)",
        height=500
    )
    
    return fig

def plot_relative_performance(data1, data2, ticker1, ticker2):
    """
    Create a chart showing relative performance between two securities
    
    Parameters:
    data1 (pd.DataFrame): OHLCV DataFrame for first security
    data2 (pd.DataFrame): OHLCV DataFrame for second security
    ticker1 (str): Ticker symbol for first security
    ticker2 (str): Ticker symbol for second security
    
    Returns:
    plotly.graph_objects.Figure: Plotly figure object
    """
    # Normalize prices to starting value
    data1_norm = data1['Close'] / data1['Close'].iloc[0]
    data2_norm = data2['Close'] / data2['Close'].iloc[0]
    
    # Calculate relative performance
    relative_perf = data1_norm / data2_norm
    
    # Create figure with secondary y-axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Add normalized price lines
    fig.add_trace(
        go.Scatter(
            x=data1_norm.index,
            y=data1_norm.values,
            name=ticker1,
            line=dict(color='blue')
        ),
        secondary_y=False
    )
    
    fig.add_trace(
        go.Scatter(
            x=data2_norm.index,
            y=data2_norm.values,
            name=ticker2,
            line=dict(color='red')
        ),
        secondary_y=False
    )
    
    # Add relative performance line
    fig.add_trace(
        go.Scatter(
            x=relative_perf.index,
            y=relative_perf.values,
            name=f"{ticker1}/{ticker2} Ratio",
            line=dict(color='green', dash='dash')
        ),
        secondary_y=True
    )
    
    # Update layout
    fig.update_layout(
        title=f"Relative Performance: {ticker1} vs {ticker2}",
        xaxis_title="Date",
        yaxis_title="Normalized Price",
        yaxis2_title=f"{ticker1}/{ticker2} Ratio",
        height=400,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    return fig
