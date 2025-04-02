import pandas as pd
import numpy as np
import yfinance as yf

def calculate_zscore(series):
    """
    Calculate Z-score for a time series
    
    Parameters:
    series (pd.Series): Time series data
    
    Returns:
    float: Z-score of the latest value
    """
    mean = series.mean()
    std = series.std()
    
    if std == 0:
        return 0
    
    return (series.iloc[-1] - mean) / std

def analyze_pair_correlation(ticker1, ticker2, period='1y'):
    """
    Analyze correlation between two securities
    
    Parameters:
    ticker1 (str): First ticker symbol
    ticker2 (str): Second ticker symbol
    period (str): Period for data analysis
    
    Returns:
    dict: Correlation statistics
    """
    from utils.data_fetcher import get_stock_data
    
    # Get data
    data1 = get_stock_data(ticker1, period=period)
    data2 = get_stock_data(ticker2, period=period)
    
    if data1 is None or data2 is None or len(data1) < 20 or len(data2) < 20:
        return None
    
    # Calculate returns
    returns1 = data1['Close'].pct_change().dropna()
    returns2 = data2['Close'].pct_change().dropna()
    
    # Make sure the indices align
    common_idx = returns1.index.intersection(returns2.index)
    returns1 = returns1.loc[common_idx]
    returns2 = returns2.loc[common_idx]
    
    # Calculate correlation
    correlation = returns1.corr(returns2)
    
    # Calculate relative performance
    rel_perf_start = data1['Close'].iloc[0] / data2['Close'].iloc[0]
    rel_perf_end = data1['Close'].iloc[-1] / data2['Close'].iloc[-1]
    rel_perf_change = (rel_perf_end / rel_perf_start - 1) * 100
    
    # Calculate relative performance series
    relative_performance = (data1['Close'] / data1['Close'].iloc[0]) / (data2['Close'] / data2['Close'].iloc[0])
    
    # Calculate Z-score
    zscore = calculate_zscore(relative_performance)
    
    return {
        'correlation': correlation,
        'rel_perf_change': rel_perf_change,
        'zscore': zscore,
        'relative_performance': relative_performance
    }

def find_relative_value_anomalies(stock_pairs=None, sector_etfs=None, bond_pairs=None, period='3mo'):
    """
    Find relative value discrepancies between related securities
    
    Parameters:
    stock_pairs: List of tuples with related stocks (e.g., competitors, same sector)
    sector_etfs: Dictionary mapping sectors to their ETFs and component stocks
    bond_pairs: List of tuples with related bond ETFs or securities
    period: Time period for analysis
    
    Returns:
    DataFrame with anomalies and their analysis
    """
    from utils.data_fetcher import get_stock_data
    
    results = []
    
    # Default pairs if none provided
    if stock_pairs is None:
        stock_pairs = [
            ('AAPL', 'MSFT'),  # Tech giants
            ('JPM', 'BAC'),    # Major banks
            ('PFE', 'JNJ'),    # Pharma
            ('XOM', 'CVX'),    # Oil majors
            ('AMZN', 'WMT'),   # Retail
            ('KO', 'PEP'),     # Beverages
            ('NVDA', 'AMD'),   # Semiconductors
            ('DIS', 'NFLX'),   # Entertainment
            ('SBUX', 'MCD'),   # Food/Beverages
            ('GM', 'F')        # Automakers
        ]
    
    if sector_etfs is None:
        sector_etfs = {
            'Technology': ('XLK', ['AAPL', 'MSFT', 'NVDA']),
            'Financial': ('XLF', ['JPM', 'BAC', 'GS']),
            'Healthcare': ('XLV', ['JNJ', 'PFE', 'UNH']),
            'Energy': ('XLE', ['XOM', 'CVX', 'COP']),
            'Consumer Staples': ('XLP', ['PG', 'KO', 'PEP']),
            'Utilities': ('XLU', ['NEE', 'DUK', 'SO'])
        }
    
    if bond_pairs is None:
        bond_pairs = [
            # Treasury ETFs of different durations
            ('SHY', 'IEF'),  # Short-term vs Intermediate
            ('IEF', 'TLT'),  # Intermediate vs Long-term
            # Corporate vs Treasury of similar duration
            ('LQD', 'IEF'),  # Investment Grade Corporate vs Intermediate Treasury
            ('HYG', 'LQD'),  # High Yield vs Investment Grade Corporate
            ('MBB', 'IEF'),  # Mortgage-Backed vs Intermediate Treasury
            ('EMB', 'LQD')   # Emerging Markets vs Investment Grade Corporate
        ]
    
    # 1. Analyze stock pairs (relative performance, valuation metrics)
    for stock1, stock2 in stock_pairs:
        try:
            # Get data for both stocks
            data1 = get_stock_data(stock1, period=period)
            data2 = get_stock_data(stock2, period=period)
            
            if data1 is None or data2 is None or len(data1) < 20 or len(data2) < 20:
                continue
            
            # Get fundamental data
            stock1_info = yf.Ticker(stock1).info
            stock2_info = yf.Ticker(stock2).info
            
            # Calculate relative performance
            rel_perf_start = data1['Close'].iloc[0] / data2['Close'].iloc[0]
            rel_perf_end = data1['Close'].iloc[-1] / data2['Close'].iloc[-1]
            rel_perf_change = (rel_perf_end / rel_perf_start - 1) * 100
            
            # Calculate metrics for comparison
            stock1_pe = stock1_info.get('trailingPE', float('nan'))
            stock2_pe = stock2_info.get('trailingPE', float('nan'))
            
            stock1_ps = stock1_info.get('priceToSalesTrailing12Months', float('nan'))
            stock2_ps = stock2_info.get('priceToSalesTrailing12Months', float('nan'))
            
            stock1_pb = stock1_info.get('priceToBook', float('nan'))
            stock2_pb = stock2_info.get('priceToBook', float('nan'))
            
            # Calculate Z-score of the relative performance change
            # Get historical relative performance
            relative_performance = data1['Close'] / data2['Close']
            rel_perf_mean = relative_performance.mean()
            rel_perf_std = relative_performance.std()
            
            if rel_perf_std > 0:
                z_score = (rel_perf_end - rel_perf_mean) / rel_perf_std
            else:
                z_score = 0
            
            # Check for significant divergence (z-score > 2 or < -2)
            if abs(z_score) > 2:
                # Determine convergence or divergence potential
                if z_score > 0:
                    # Stock1 is outperforming Stock2 more than usual
                    divergence_type = f"{stock1} outperforming {stock2}"
                    # Check if fundamentals support this divergence
                    if not np.isnan(stock1_pe) and not np.isnan(stock2_pe):
                        pe_supports = stock1_pe < stock2_pe
                    else:
                        pe_supports = None
                else:
                    # Stock2 is outperforming Stock1 more than usual
                    divergence_type = f"{stock2} outperforming {stock1}"
                    # Check if fundamentals support this divergence
                    if not np.isnan(stock1_pe) and not np.isnan(stock2_pe):
                        pe_supports = stock1_pe > stock2_pe
                    else:
                        pe_supports = None
                
                # Analyze potential reasons for divergence
                reasons = []
                if not np.isnan(stock1_pe) and not np.isnan(stock2_pe):
                    pe_diff = stock1_pe / stock2_pe - 1
                    reasons.append(f"P/E ratio difference: {pe_diff:.1%}")
                
                if not np.isnan(stock1_ps) and not np.isnan(stock2_ps):
                    ps_diff = stock1_ps / stock2_ps - 1
                    reasons.append(f"P/S ratio difference: {ps_diff:.1%}")
                
                if not np.isnan(stock1_pb) and not np.isnan(stock2_pb):
                    pb_diff = stock1_pb / stock2_pb - 1
                    reasons.append(f"P/B ratio difference: {pb_diff:.1%}")
                
                # Convergence/divergence outlook
                if pe_supports is True:
                    outlook = "Fundamentals support current trend - may continue to DIVERGE"
                elif pe_supports is False:
                    outlook = "Fundamentals contradict trend - likely to CONVERGE"
                else:
                    outlook = "Insufficient fundamental data - monitor for news catalysts"
                
                results.append({
                    'Type': 'Stock Pair',
                    'Securities': f"{stock1} / {stock2}",
                    'Anomaly': divergence_type,
                    'Z-Score': z_score,
                    'Relative Change (%)': rel_perf_change,
                    'Current Ratio': rel_perf_end,
                    'Reasons': reasons,
                    'Outlook': outlook,
                    'Trade Idea': f"Long {stock2 if z_score > 0 else stock1}, Short {stock1 if z_score > 0 else stock2}" if abs(z_score) > 2.5 else "Monitor"
                })
        
        except Exception as e:
            continue
    
    # Processing sector ETFs and bond pairs would be similar to the stock pairs logic
    # ...
    
    return pd.DataFrame(results) if results else None

def find_market_anomalies(tickers, period='1mo'):
    """
    Find potential market anomalies across multiple stocks
    
    Parameters:
    tickers (list): List of ticker symbols to analyze
    period (str): Period for data analysis
    
    Returns:
    pd.DataFrame: DataFrame with anomaly information
    """
    from utils.data_fetcher import get_stock_data
    from utils.indicators import calculate_technical_indicators
    
    results = []
    
    for ticker in tickers:
        try:
            data = get_stock_data(ticker, period=period)
            if data is None or len(data) < 20:
                continue
                
            # Calculate recent volatility
            recent_volatility = data['Close'].pct_change().std() * np.sqrt(252) * 100
            
            # Calculate abnormal volume
            avg_volume = data['Volume'].mean()
            latest_volume = data['Volume'].iloc[-1]
            volume_ratio = latest_volume / avg_volume
            
            # Check for gap movements
            latest_gap = (data['Open'].iloc[-1] - data['Close'].iloc[-2]) / data['Close'].iloc[-2] * 100
            
            # Check for unusual option activity (for demonstration)
            unusual_options = False
            
            # Check RSI extremes
            indicators = calculate_technical_indicators(data)
            if indicators is not None and 'RSI' in indicators.columns:
                rsi = indicators['RSI'].iloc[-1]
                rsi_extreme = rsi < 20 or rsi > 80
            else:
                rsi = None
                rsi_extreme = False
            
            # Check for potential anomalies
            is_anomaly = (
                (volume_ratio > 3) or  # 3x average volume
                (abs(latest_gap) > 3) or  # 3% gap up or down
                rsi_extreme or
                unusual_options
            )
            
            if is_anomaly:
                results.append({
                    'Ticker': ticker,
                    'Price': data['Close'].iloc[-1],
                    'Change (%)': (data['Close'].iloc[-1] / data['Close'].iloc[-2] - 1) * 100,
                    'Volume Ratio': volume_ratio,
                    'Recent Gap (%)': latest_gap,
                    'RSI': rsi,
                    'Volatility (%)': recent_volatility,
                    'Unusual Options': unusual_options
                })
                
        except Exception as e:
            continue
            
    return pd.DataFrame(results) if results else None
