import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

from utils.data_fetcher import get_stock_data, get_stock_info
from utils.indicators import calculate_technical_indicators
from utils.statistics import (
    find_relative_value_anomalies,
    find_market_anomalies,
    analyze_pair_correlation
)
from utils.visualization import plot_relative_performance

def market_anomaly_scanner_module():
    """
    Market Anomaly Scanner module for finding relative value discrepancies and market anomalies
    """
    st.markdown('<p class="main-header">Market Anomaly & Relative Value Scanner</p>', unsafe_allow_html=True)
    
    # Create tabs for different types of scans
    tab1, tab2, tab3 = st.tabs(["Relative Value Anomalies", "Market Anomalies", "Custom Pairs"])
    
    with tab1:
        st.markdown("""
        ### Relative Value Analysis
        
        This scanner identifies securities that appear cheap or expensive relative to similar assets, 
        analyzes why these discrepancies exist, and evaluates whether they're likely to converge or diverge over time.
        """)
        
        # Input parameters
        scan_type = st.selectbox(
            "Select Analysis Type",
            options=["All Pairs", "Stock Pairs", "Sector vs Components", "Bond/Rate Spreads"],
            index=0
        )
        
        period = st.selectbox(
            "Analysis Period",
            options=["1mo", "3mo", "6mo", "1y"],
            index=1
        )
        
        if st.button("Find Relative Value Anomalies"):
            with st.spinner("Analyzing relative value discrepancies..."):
                # Configure analysis based on selection
                if scan_type == "All Pairs":
                    anomalies = find_relative_value_anomalies(period=period)
                elif scan_type == "Stock Pairs":
                    # Only analyze stock pairs
                    anomalies = find_relative_value_anomalies(
                        stock_pairs=[
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
                        ],
                        sector_etfs=None,
                        bond_pairs=None,
                        period=period
                    )
                elif scan_type == "Sector vs Components":
                    # Only analyze sector ETFs vs components
                    anomalies = find_relative_value_anomalies(
                        stock_pairs=None,
                        sector_etfs={
                            'Technology': ('XLK', ['AAPL', 'MSFT', 'NVDA']),
                            'Financial': ('XLF', ['JPM', 'BAC', 'GS']),
                            'Healthcare': ('XLV', ['JNJ', 'PFE', 'UNH']),
                            'Energy': ('XLE', ['XOM', 'CVX', 'COP']),
                            'Consumer Staples': ('XLP', ['PG', 'KO', 'PEP']),
                            'Utilities': ('XLU', ['NEE', 'DUK', 'SO'])
                        },
                        bond_pairs=None,
                        period=period
                    )
                elif scan_type == "Bond/Rate Spreads":
                    # Only analyze bond pairs
                    anomalies = find_relative_value_anomalies(
                        stock_pairs=None,
                        sector_etfs=None,
                        bond_pairs=[
                            ('SHY', 'IEF'),  # Short-term vs Intermediate
                            ('IEF', 'TLT'),  # Intermediate vs Long-term
                            ('LQD', 'IEF'),  # Investment Grade Corporate vs Intermediate Treasury
                            ('HYG', 'LQD'),  # High Yield vs Investment Grade Corporate
                            ('MBB', 'IEF'),  # Mortgage-Backed vs Intermediate Treasury
                            ('EMB', 'LQD')   # Emerging Markets vs Investment Grade Corporate
                        ],
                        period=period
                    )
                
                if anomalies is not None and not anomalies.empty:
                    st.markdown("### Relative Value Anomalies Detected")
                    
                    # Sort by absolute Z-score to show most significant anomalies first
                    anomalies['Abs_Z'] = anomalies['Z-Score'].abs()
                    anomalies = anomalies.sort_values('Abs_Z', ascending=False).drop('Abs_Z', axis=1)
                    
                    # Display the anomalies in a table
                    st.dataframe(anomalies[['Type', 'Securities', 'Anomaly', 'Z-Score', 'Relative Change (%)', 'Outlook', 'Trade Idea']].style.format({
                        'Z-Score': '{:.2f}',
                        'Relative Change (%)': '{:.2f}%'
                    }))
                    
                    # Create an expander for each significant anomaly
                    for i, (_, anomaly) in enumerate(anomalies.iterrows()):
                        if i >= 5:  # Limit to top 5 anomalies for display
                            break
                            
                        with st.expander(f"{anomaly['Securities']} - {anomaly['Anomaly']} (Z-Score: {anomaly['Z-Score']:.2f})"):
                            # Display detailed analysis
                            st.markdown(f"**Securities:** {anomaly['Securities']}")
                            st.markdown(f"**Anomaly Type:** {anomaly['Anomaly']}")
                            st.markdown(f"**Z-Score:** {anomaly['Z-Score']:.2f}")
                            st.markdown(f"**Relative Change:** {anomaly['Relative Change (%)']:.2f}%")
                            
                            # Reasons for anomaly
                            st.markdown("#### Potential Reasons for Discrepancy")
                            for reason in anomaly['Reasons']:
                                st.markdown(f"- {reason}")
                            
                            # Outlook and trade idea
                            st.markdown(f"**Convergence/Divergence Outlook:** {anomaly['Outlook']}")
                            st.markdown(f"**Potential Trade Idea:** {anomaly['Trade Idea']}")
                            
                            # Time horizon recommendation
                            if abs(anomaly['Z-Score']) > 2.5:
                                time_horizon = "Short to Medium-Term (1-3 months)"
                            elif abs(anomaly['Z-Score']) > 1.5:
                                time_horizon = "Medium-Term (3-6 months)"
                            else:
                                time_horizon = "Long-Term (6+ months)"
                            
                            st.markdown(f"**Suggested Time Horizon:** {time_horizon}")
                            
                            # Add warning about risks
                            st.warning("""
                            **Risk Factors:** Relative value trades can take longer than expected to converge,
                            and in some cases, discrepancies can widen further before converging. Always use
                            appropriate position sizing and risk management.
                            """)
                            
                            # Try to plot the relative performance if we have the securities
                            securities = anomaly['Securities'].split(" / ")
                            if len(securities) == 2 and anomaly['Type'] in ['Stock Pair', 'Bond Pair']:
                                try:
                                    sec1, sec2 = securities
                                    data1 = get_stock_data(sec1, period="1y")
                                    data2 = get_stock_data(sec2, period="1y")
                                    
                                    if data1 is not None and data2 is not None:
                                        fig = plot_relative_performance(data1, data2, sec1, sec2)
                                        st.plotly_chart(fig, use_container_width=True)
                                        
                                except Exception as e:
                                    st.error(f"Error plotting relative performance: {e}")
                else:
                    st.info("No significant relative value anomalies detected with the current parameters.")
    
    with tab2:
        st.markdown("### Traditional Market Anomalies")
        
        # Input parameters
        watchlist = st.text_area(
            "Enter Tickers to Scan (comma-separated)",
            "AAPL, MSFT, AMZN, GOOGL, META, TSLA, NVDA, JPM, V, JNJ"
        )
        
        period = st.selectbox(
            "Analysis Period",
            options=["1wk", "1mo", "3mo", "6mo", "1y"],
            index=1,
            key="traditional_anomalies_period"
        )
        
        if st.button("Scan for Market Anomalies"):
            with st.spinner("Scanning for anomalies..."):
                # Parse ticker list
                tickers = [ticker.strip() for ticker in watchlist.split(',')]
                
                # Find anomalies
                anomalies = find_market_anomalies(tickers, period)
                
                if anomalies is not None and not anomalies.empty:
                    st.markdown("### Potential Market Anomalies Detected")
                    
                    # Display the anomalies
                    st.dataframe(anomalies.style.format({
                        'Price': '${:.2f}',
                        'Change (%)': '{:.2f}%',
                        'Volume Ratio': '{:.1f}x',
                        'Recent Gap (%)': '{:.2f}%',
                        'RSI': '{:.1f}',
                        'Volatility (%)': '{:.1f}%'
                    }))
                    
                    # Visualize the most interesting anomalies
                    st.markdown("### Highlighted Anomalies")
                    
                    for i, anomaly in enumerate(anomalies.iterrows()):
                        if i >= 3:  # Limit to top 3 anomalies
                            break
                            
                        ticker = anomaly[1]['Ticker']
                        data = get_stock_data(ticker, period="6mo")
                        
                        if data is not None:
                            # Create plot
                            fig = go.Figure()
                            
                            fig.add_trace(
                                go.Candlestick(
                                    x=data.index,
                                    open=data['Open'],
                                    high=data['High'],
                                    low=data['Low'],
                                    close=data['Close'],
                                    name="Price"
                                )
                            )
                            
                            # Add volume as bar chart
                            fig.add_trace(
                                go.Bar(
                                    x=data.index,
                                    y=data['Volume'],
                                    name="Volume",
                                    yaxis="y2",
                                    marker=dict(color='rgba(0,0,100,0.3)')
                                )
                            )
                            
                            fig.update_layout(
                                title=f"{ticker} - {anomaly[1]['Change (%)']:.2f}% Change",
                                xaxis_title="Date",
                                yaxis_title="Price",
                                yaxis2=dict(
                                    title="Volume",
                                    overlaying="y",
                                    side="right",
                                    showgrid=False
                                ),
                                height=400,
                                showlegend=True
                            )
                            
                            st.plotly_chart(fig, use_container_width=True)
                            
                            # Explain anomaly
                            reasons = []
                            
                            if anomaly[1]['Volume Ratio'] > 3:
                                reasons.append(f"Unusual volume ({anomaly[1]['Volume Ratio']:.1f}x average)")
                            
                            if abs(anomaly[1]['Recent Gap (%)']) > 3:
                                reasons.append(f"Recent gap of {anomaly[1]['Recent Gap (%)']:.2f}%")
                            
                            if 'RSI' in anomaly[1] and anomaly[1]['RSI'] is not None:
                                if anomaly[1]['RSI'] < 30:
                                    reasons.append(f"Oversold (RSI: {anomaly[1]['RSI']:.1f})")
                                elif anomaly[1]['RSI'] > 70:
                                    reasons.append(f"Overbought (RSI: {anomaly[1]['RSI']:.1f})")
                            
                            st.markdown(f"**Key Observations:** {', '.join(reasons)}")
                            
                            # Suggestion
                            if 'RSI' in anomaly[1] and anomaly[1]['RSI'] is not None and anomaly[1]['RSI'] < 30:
                                st.markdown("**Potential Opportunity:** Consider watching for reversal signals")
                            elif 'RSI' in anomaly[1] and anomaly[1]['RSI'] is not None and anomaly[1]['RSI'] > 70:
                                st.markdown("**Potential Opportunity:** Be cautious of potential pullback")
                            
                            st.markdown("---")
                else:
                    st.info("No significant anomalies detected in the selected tickers.")
    
    with tab3:
        st.markdown("### Custom Pair Analysis")
        
        st.markdown("""
        Compare any two securities to identify relative value opportunities and analyze whether 
        discrepancies are likely to widen or converge.
        """)
        
        # Input fields for custom pairs
        col1, col2 = st.columns(2)
        
        with col1:
            security1 = st.text_input("Security 1 (Ticker)", "AAPL")
        
        with col2:
            security2 = st.text_input("Security 2 (Ticker)", "MSFT")
        
        analysis_period = st.selectbox(
            "Analysis Period",
            options=["1mo", "3mo", "6mo", "1y", "2y", "5y"],
            index=2,
            key="custom_pair_period"
        )
        
        if st.button("Analyze Custom Pair"):
            with st.spinner("Analyzing custom pair..."):
                try:
                    # Get data
                    data1 = get_stock_data(security1, period=analysis_period)
                    data2 = get_stock_data(security2, period=analysis_period)
                    
                    if data1 is None or data2 is None or len(data1) < 20 or len(data2) < 20:
                        st.error(f"Insufficient data for {security1} or {security2}")
                    else:
                        # Get correlation analysis
                        corr_stats = analyze_pair_correlation(security1, security2, period=analysis_period)
                        
                        if corr_stats is None:
                            st.error("Could not analyze correlation between the securities")
                            return
                        
                        # Get fundamental data if available
                        stock1_info = get_stock_info(security1)
                        stock2_info = get_stock_info(security2)
                        
                        # Create performance chart
                        fig = plot_relative_performance(data1, data2, security1, security2)
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Display metrics
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            stock1_return = (data1['Close'].iloc[-1] / data1['Close'].iloc[0] - 1) * 100
                            stock2_return = (data2['Close'].iloc[-1] / data2['Close'].iloc[0] - 1) * 100
                            
                            st.metric(f"{security1} Return", f"{stock1_return:.2f}%")
                            st.metric(f"{security2} Return", f"{stock2_return:.2f}%")
                        
                        with col2:
                            st.metric("Relative Return", f"{corr_stats['rel_perf_change']:.2f}%")
                            st.metric("Z-Score", f"{corr_stats['zscore']:.2f}")
                        
                        with col3:
                            # Display correlation
                            st.metric("Price Correlation", f"{corr_stats['correlation']:.2f}")
                            
                            # Classify the anomaly strength
                            if abs(corr_stats['zscore']) > 2:
                                anomaly_strength = "Strong"
                                color = "red" if corr_stats['zscore'] > 0 else "green"
                            elif abs(corr_stats['zscore']) > 1:
                                anomaly_strength = "Moderate"
                                color = "orange" if corr_stats['zscore'] > 0 else "lightgreen"
                            else:
                                anomaly_strength = "Weak/None"
                                color = "gray"
                                
                            st.markdown(f"<p style='color:{color};font-weight:bold;font-size:20px;'>Anomaly Strength: {anomaly_strength}</p>", unsafe_allow_html=True)
                        
                        # Analysis and interpretation
                        st.markdown("### Analysis & Interpretation")
                        
                        # Determine which security is outperforming
                        if corr_stats['zscore'] > 0:
                            outperformer = security1
                            underperformer = security2
                        else:
                            outperformer = security2
                            underperformer = security1
                        
                        st.markdown(f"**Relative Performance:** {outperformer} is outperforming {underperformer}")
                        
                        # Valuation comparison if available
                        has_fundamentals = True
                        try:
                            if stock1_info is None or stock2_info is None:
                                has_fundamentals = False
                            else:
                                stock1_pe = stock1_info.get('trailingPE', float('nan'))
                                stock2_pe = stock2_info.get('trailingPE', float('nan'))
                                
                                stock1_ps = stock1_info.get('priceToSalesTrailing12Months', float('nan'))
                                stock2_ps = stock2_info.get('priceToSalesTrailing12Months', float('nan'))
                                
                                if np.isnan(stock1_pe) or np.isnan(stock2_pe) or np.isnan(stock1_ps) or np.isnan(stock2_ps):
                                    has_fundamentals = False
                        except:
                            has_fundamentals = False
                        
                        if has_fundamentals:
                            st.markdown("#### Valuation Comparison")
                            
                            metrics_df = pd.DataFrame({
                                'Metric': ['P/E Ratio', 'P/S Ratio'],
                                security1: [stock1_pe, stock1_ps],
                                security2: [stock2_pe, stock2_ps],
                                'Ratio': [stock1_pe/stock2_pe, stock1_ps/stock2_ps]
                            })
                            
                            st.dataframe(metrics_df.style.format({
                                security1: '{:.2f}',
                                security2: '{:.2f}',
                                'Ratio': '{:.2f}'
                            }))
                            
                            # Fundamental analysis
                            pe_ratio = stock1_pe / stock2_pe
                            ps_ratio = stock1_ps / stock2_ps
                            
                            # Check if valuation supports performance
                            pe_supports_performance = (pe_ratio < 1 and corr_stats['zscore'] > 0) or (pe_ratio > 1 and corr_stats['zscore'] < 0)
                            ps_supports_performance = (ps_ratio < 1 and corr_stats['zscore'] > 0) or (ps_ratio > 1 and corr_stats['zscore'] < 0)
                            
                            if pe_supports_performance and ps_supports_performance:
                                st.markdown("**Valuation Assessment:** Fundamentals support current performance divergence - may continue to DIVERGE")
                            elif not pe_supports_performance and not ps_supports_performance:
                                st.markdown("**Valuation Assessment:** Fundamentals contradict current performance - likely to CONVERGE")
                            else:
                                st.markdown("**Valuation Assessment:** Mixed fundamental signals - monitor additional factors")
                        
                        # Correlation analysis
                        st.markdown("#### Correlation Analysis")
                        
                        if corr_stats['correlation'] > 0.8:
                            st.markdown("The securities show **strong positive correlation**, suggesting they typically move together. Significant divergences may present mean-reversion opportunities.")
                        elif corr_stats['correlation'] > 0.5:
                            st.markdown("The securities show **moderate positive correlation**. Some divergence is normal, but extreme divergence may present trading opportunities.")
                        elif corr_stats['correlation'] > 0:
                            st.markdown("The securities show **weak positive correlation**. They often move independently, making relative value trades more speculative.")
                        else:
                            st.markdown("The securities show **negative correlation**, suggesting they typically move in opposite directions. This pair may be suitable for hedging strategies.")
                        
                        # Trading recommendation
                        st.markdown("#### Trading Recommendation")
                        
                        if abs(corr_stats['zscore']) > 2:
                            if corr_stats['zscore'] > 0:
                                st.markdown(f"**Potential Trade:** LONG {security2}, SHORT {security1}")
                                st.markdown(f"{security1} appears relatively expensive compared to {security2} based on historical relationship.")
                            else:
                                st.markdown(f"**Potential Trade:** LONG {security1}, SHORT {security2}")
                                st.markdown(f"{security2} appears relatively expensive compared to {security1} based on historical relationship.")
                            
                            st.markdown("**Time Horizon:** Medium-term (1-3 months)")
                            st.markdown("**Risk Level:** Medium to High")
                        elif abs(corr_stats['zscore']) > 1:
                            if corr_stats['zscore'] > 0:
                                st.markdown(f"**Potential Trade:** Consider monitoring for opportunity to LONG {security2}, SHORT {security1}")
                            else:
                                st.markdown(f"**Potential Trade:** Consider monitoring for opportunity to LONG {security1}, SHORT {security2}")
                            
                            st.markdown("**Time Horizon:** Medium to Long-term (3-6 months)")
                            st.markdown("**Risk Level:** Medium")
                        else:
                            st.markdown("**Recommendation:** No significant relative value opportunity at this time")
                            st.markdown("The current relationship between these securities is within normal historical ranges.")
                        
                        # Risk warning
                        st.warning("""
                        **Risk Factors:** Relative value trades can take longer than expected to converge,
                        and in some cases, discrepancies can widen further before converging. Always use
                        appropriate position sizing and risk management. Past relationships may not hold in the future.
                        """)
                
                except Exception as e:
                    st.error(f"Error analyzing custom pair: {e}")
    
    st.markdown("""
    ### About Relative Value & Market Anomalies
    
    **Relative Value Anomalies** occur when related securities deviate from their typical price relationships.
    These anomalies may represent opportunities for convergence trades:
    
    - **Stock Pairs:** Competitors or companies in the same sector that typically move together
    - **Sector vs. Components:** ETFs trading at unusual premiums/discounts to their underlying stocks
    - **Bond/Rate Spreads:** Credit spreads, yield curve relationships, or fixed income anomalies
    
    **Why Discrepancies Occur:**
    - Temporary supply/demand imbalances
    - Different investor bases and market segmentation
    - Information asymmetry or delayed market reactions
    - Structural market constraints (tax issues, regulations)
    - Liquidity differences between securities
    
    **Convergence vs. Divergence:**
    - **Convergence:** Discrepancies tend to return to their historical average over time
    - **Divergence:** Discrepancies can sometimes continue to widen due to fundamental changes
    
    **Trade Implementation:**
    - Long the relatively cheap security, short the relatively expensive one
    - Use appropriate position sizing and set clear stop-loss levels
    - Consider the appropriate time horizon for convergence to occur
    """)
