import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
from datetime import datetime

from utils.data_fetcher import get_stock_data, get_dividend_data

def dividend_analysis_module():
    """
    Dividend Analysis module for evaluating dividend stocks and income potential
    """
    st.markdown('<p class="main-header">Dividend Analysis</p>', unsafe_allow_html=True)
    
    st.markdown("""
    This module helps you analyze dividend-paying stocks to evaluate income potential,
    dividend sustainability, and growth characteristics.
    """)
    
    # Input fields
    col1, col2 = st.columns(2)
    
    with col1:
        ticker = st.text_input("Enter Ticker Symbol", "JNJ")
    
    with col2:
        analysis_type = st.selectbox(
            "Analysis Type",
            options=["Dividend Profile", "Income Projection", "Dividend Growth"]
        )
    
    if st.button("Analyze Dividends"):
        with st.spinner("Fetching dividend data..."):
            # Get stock data
            stock_data = get_stock_data(ticker, period="5y")
            
            if stock_data is None:
                st.error(f"Could not fetch stock data for {ticker}")
                return
            
            # Get dividend data
            dividend_data = get_dividend_data(ticker)
            
            if dividend_data is None:
                st.error(f"Could not fetch dividend data for {ticker}")
                return
            
            # Display basic info
            st.markdown(f"## {ticker} Dividend Analysis")
            
            # Get last price
            last_price = stock_data['Close'].iloc[-1]
            
            # Display current metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Current Price", f"${last_price:.2f}")
            
            with col2:
                st.metric("Dividend Yield", f"{dividend_data['Dividend Yield (%)']:.2f}%")
            
            with col3:
                st.metric("Payout Ratio", f"{dividend_data['Payout Ratio']:.2f}%")
            
            with col4:
                st.metric("5Y Dividend Growth", f"{dividend_data['Dividend Growth (5Y) (%)']:.2f}%")
            
            # Different analysis based on selection
            if analysis_type == "Dividend Profile":
                st.markdown("### Dividend Profile")
                
                # Dividend history
                annual_dividends = pd.Series(dividend_data['Annual Dividends'])
                
                if not annual_dividends.empty:
                    # Create dividend history chart
                    fig = go.Figure()
                    
                    fig.add_trace(
                        go.Bar(
                            x=list(annual_dividends.index),
                            y=list(annual_dividends.values),
                            name="Annual Dividends",
                            marker=dict(color='green')
                        )
                    )
                    
                    fig.update_layout(
                        title="Annual Dividend History",
                        xaxis_title="Year",
                        yaxis_title="Dividend Amount ($)",
                        height=400
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Dividend metrics
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("#### Dividend Metrics")
                        st.markdown(f"**Years of Consecutive Growth:** {dividend_data['Years of Growth']}")
                        st.markdown(f"**Last Dividend Date:** {dividend_data['Last Dividend Date']}")
                        
                        if dividend_data['Next Ex-Dividend'] is not None:
                            st.markdown(f"**Next Ex-Dividend Date:** {datetime.fromtimestamp(dividend_data['Next Ex-Dividend']/1000).strftime('%Y-%m-%d')}")
                    
                    with col2:
                        st.markdown("#### Dividend Sustainability")
                        
                        # Dividend sustainability assessment
                        if dividend_data['Payout Ratio'] < 40:
                            st.markdown("**Payout Ratio:** 🟢 Low (< 40%)")
                            st.markdown("**Assessment:** Very sustainable, room for growth")
                        elif dividend_data['Payout Ratio'] < 60:
                            st.markdown("**Payout Ratio:** 🟡 Moderate (40-60%)")
                            st.markdown("**Assessment:** Sustainable, balanced approach")
                        elif dividend_data['Payout Ratio'] < 80:
                            st.markdown("**Payout Ratio:** 🟠 High (60-80%)")
                            st.markdown("**Assessment:** Potentially sustainable, limited growth potential")
                        else:
                            st.markdown("**Payout Ratio:** 🔴 Very High (> 80%)")
                            st.markdown("**Assessment:** May not be sustainable long-term")
                    
                    # Dividend vs price chart
                    if not annual_dividends.empty and len(stock_data) > 0:
                        st.markdown("### Dividend vs Price")
                        
                        # Resample stock data to yearly for comparison
                        yearly_prices = stock_data['Close'].resample('Y').last()
                        
                        # Only keep years that match dividend data
                        matching_years = set(annual_dividends.index).intersection(set(yearly_prices.index.year))
                        
                        if matching_years:
                            # Create comparison chart
                            fig = go.Figure()
                            
                            # Filter yearly prices
                            filtered_prices = yearly_prices[yearly_prices.index.year.isin(matching_years)]
                            
                            # Normalize prices for comparison
                            price_series = pd.Series({year: price for year, price in zip(filtered_prices.index.year, filtered_prices.values)})
                            norm_prices = price_series / price_series.iloc[0] * 100
                            
                            # Normalize dividends
                            filtered_dividends = pd.Series({year: div for year, div in annual_dividends.items() if year in matching_years})
                            norm_dividends = filtered_dividends / filtered_dividends.iloc[0] * 100
                            
                            fig.add_trace(
                                go.Scatter(
                                    x=list(norm_prices.index),
                                    y=list(norm_prices.values),
                                    name="Price (normalized)",
                                    line=dict(color='blue')
                                )
                            )
                            
                            fig.add_trace(
                                go.Scatter(
                                    x=list(norm_dividends.index),
                                    y=list(norm_dividends.values),
                                    name="Dividend (normalized)",
                                    line=dict(color='green')
                                )
                            )
                            
                            fig.update_layout(
                                title="Dividend vs Price Growth (Normalized to 100)",
                                xaxis_title="Year",
                                yaxis_title="Normalized Value",
                                height=400
                            )
                            
                            st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning(f"No dividend history available for {ticker}")
            
            elif analysis_type == "Income Projection":
                st.markdown("### Dividend Income Projection")
                
                # Projection inputs
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    investment = st.number_input("Initial Investment ($)", value=10000, min_value=1000, step=1000)
                
                with col2:
                    years = st.slider("Projection Years", min_value=1, max_value=30, value=10)
                
                with col3:
                    growth_rate = st.slider("Annual Dividend Growth (%)", 
                                          min_value=0.0, 
                                          max_value=15.0, 
                                          value=dividend_data['Dividend Growth (5Y) (%)'] if dividend_data['Dividend Growth (5Y) (%)'] > 0 else 5.0,
                                          step=0.5)
                
                # Calculate initial shares and dividend
                shares = investment / last_price
                current_annual_dividend = last_price * (dividend_data['Dividend Yield (%)'] / 100)
                initial_annual_income = shares * current_annual_dividend
                
                # Project future income
                projection = []
                cumulative_income = 0
                annual_income = initial_annual_income
                
                for year in range(1, years + 1):
                    cumulative_income += annual_income
                    projection.append({
                        'Year': year,
                        'Annual Income': annual_income,
                        'Cumulative Income': cumulative_income,
                        'Yield on Cost': (annual_income / investment) * 100
                    })
                    annual_income *= (1 + growth_rate / 100)
                
                # Display projection results
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Initial Annual Income", f"${initial_annual_income:.2f}")
                
                with col2:
                    st.metric("Final Annual Income", f"${projection[-1]['Annual Income']:.2f}")
                
                with col3:
                    st.metric("Total Income Over Period", f"${projection[-1]['Cumulative Income']:.2f}")
                
                # Create projection chart
                fig = go.Figure()
                
                fig.add_trace(
                    go.Bar(
                        x=[p['Year'] for p in projection],
                        y=[p['Annual Income'] for p in projection],
                        name="Annual Income",
                        marker=dict(color='green')
                    )
                )
                
                fig.add_trace(
                    go.Scatter(
                        x=[p['Year'] for p in projection],
                        y=[p['Cumulative Income'] for p in projection],
                        name="Cumulative Income",
                        line=dict(color='blue', width=2),
                        yaxis="y2"
                    )
                )
                
                fig.update_layout(
                    title="Projected Dividend Income",
                    xaxis_title="Year",
                    yaxis_title="Annual Income ($)",
                    yaxis2=dict(
                        title="Cumulative Income ($)",
                        overlaying="y",
                        side="right"
                    ),
                    height=500,
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="right",
                        x=1
                    )
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Display projection table
                st.markdown("### Income Projection Table")
                projection_df = pd.DataFrame(projection)
                formatted_df = projection_df.copy()
                formatted_df['Annual Income'] = formatted_df['Annual Income'].apply(lambda x: f'${x:,.2f}')
                formatted_df['Cumulative Income'] = formatted_df['Cumulative Income'].apply(lambda x: f'${x:,.2f}')
                formatted_df['Yield on Cost'] = formatted_df['Yield on Cost'].apply(lambda x: f'{x:.2f}%')
                st.dataframe(formatted_df)
                
                st.markdown("""
                **Note**: This projection assumes:
                - Constant dividend growth rate
                - No reinvestment of dividends
                - No changes in share count (splits, buybacks)
                - No share price appreciation
                
                Actual results will likely differ based on company performance and market conditions.
                """)
            
            elif analysis_type == "Dividend Growth":
                st.markdown("### Dividend Growth Analysis")
                
                annual_dividends = pd.Series(dividend_data['Annual Dividends'])
                
                if not annual_dividends.empty and len(annual_dividends) > 1:
                    # Calculate year-over-year growth rates
                    growth_rates = []
                    years = list(annual_dividends.index)
                    
                    for i in range(1, len(years)):
                        prev_div = annual_dividends[years[i-1]]
                        curr_div = annual_dividends[years[i]]
                        
                        if prev_div > 0:
                            growth_rate = ((curr_div / prev_div) - 1) * 100
                            growth_rates.append({
                                'Year': years[i],
                                'Dividend': curr_div,
                                'Growth (%)': growth_rate
                            })
                    
                    # Create growth rate chart
                    fig = go.Figure()
                    
                    fig.add_trace(
                        go.Bar(
                            x=[g['Year'] for g in growth_rates],
                            y=[g['Growth (%)'] for g in growth_rates],
                            name="YoY Growth Rate",
                            marker=dict(color=[
                                'green' if g['Growth (%)'] >= 0 else 'red' for g in growth_rates
                            ])
                        )
                    )
                    
                    fig.add_shape(
                        type="line",
                        x0=min([g['Year'] for g in growth_rates]),
                        y0=0,
                        x1=max([g['Year'] for g in growth_rates]),
                        y1=0,
                        line=dict(color="black", width=1, dash="dash")
                    )
                    
                    fig.update_layout(
                        title="Year-over-Year Dividend Growth Rates",
                        xaxis_title="Year",
                        yaxis_title="Growth Rate (%)",
                        height=400
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Calculate compound annual growth rate (CAGR) for different periods
                    st.markdown("### Historical Growth Rates")
                    
                    years_list = list(annual_dividends.index)
                    current_year = years_list[-1]
                    
                    growth_periods = []
                    
                    # Calculate 3, 5, and 10 year CAGRs if data is available
                    for period in [3, 5, 10]:
                        if len(years_list) > period:
                            start_year = years_list[-period-1]
                            start_div = annual_dividends[start_year]
                            end_div = annual_dividends[current_year]
                            
                            cagr = ((end_div / start_div) ** (1 / period) - 1) * 100
                            
                            growth_periods.append({
                                'Period': f"{period}-Year",
                                'CAGR (%)': cagr,
                                'Start Dividend': start_div,
                                'End Dividend': end_div
                            })
                    
                    # Add all-time CAGR
                    first_year = years_list[0]
                    first_div = annual_dividends[first_year]
                    last_div = annual_dividends[current_year]
                    all_period = current_year - first_year
                    
                    if all_period > 0:
                        all_cagr = ((last_div / first_div) ** (1 / all_period) - 1) * 100
                        
                        growth_periods.append({
                            'Period': f"All ({all_period}-Year)",
                            'CAGR (%)': all_cagr,
                            'Start Dividend': first_div,
                            'End Dividend': last_div
                        })
                    
                    # Display growth periods
                    if growth_periods:
                        cagr_df = pd.DataFrame(growth_periods)
                        st.dataframe(cagr_df.style.format({
                            'CAGR (%)': '{:.2f}%',
                            'Start Dividend': '${:.4f}',
                            'End Dividend': '${:.4f}'
                        }))
                        
                        # Create CAGR comparison chart
                        fig = go.Figure()
                        
                        fig.add_trace(
                            go.Bar(
                                x=[g['Period'] for g in growth_periods],
                                y=[g['CAGR (%)'] for g in growth_periods],
                                marker=dict(color='blue')
                            )
                        )
                        
                        fig.update_layout(
                            title="Dividend Compound Annual Growth Rate (CAGR)",
                            xaxis_title="Period",
                            yaxis_title="CAGR (%)",
                            height=400
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Growth consistency analysis
                        positive_growth_years = sum(1 for g in growth_rates if g['Growth (%)'] > 0)
                        consistency = (positive_growth_years / len(growth_rates)) * 100
                        
                        st.markdown("### Growth Consistency Analysis")
                        st.markdown(f"**Years with Positive Growth:** {positive_growth_years} out of {len(growth_rates)} ({consistency:.1f}%)")
                        
                        if consistency >= 90:
                            st.markdown("**Consistency Rating:** 🟢 Excellent (90%+ positive growth years)")
                        elif consistency >= 75:
                            st.markdown("**Consistency Rating:** 🟡 Good (75-90% positive growth years)")
                        elif consistency >= 50:
                            st.markdown("**Consistency Rating:** 🟠 Fair (50-75% positive growth years)")
                        else:
                            st.markdown("**Consistency Rating:** 🔴 Poor (< 50% positive growth years)")
                        
                        # Growth trend analysis
                        recent_growth = np.mean([g['Growth (%)'] for g in growth_rates[-3:]])
                        all_growth = np.mean([g['Growth (%)'] for g in growth_rates])
                        
                        st.markdown(f"**Recent 3-Year Average Growth:** {recent_growth:.2f}%")
                        st.markdown(f"**All-Time Average Growth:** {all_growth:.2f}%")
                        
                        if recent_growth > all_growth * 1.1:
                            st.markdown("**Growth Trend:** 📈 Accelerating (recent growth > historical average)")
                        elif recent_growth < all_growth * 0.9:
                            st.markdown("**Growth Trend:** 📉 Decelerating (recent growth < historical average)")
                        else:
                            st.markdown("**Growth Trend:** ➡️ Stable (recent growth similar to historical average)")
                else:
                    st.warning("Insufficient dividend history to analyze growth patterns")
    
    st.markdown("""
    ### About Dividend Investing
    
    Dividend investing focuses on stocks that pay regular dividends, providing investors with:
    
    - **Regular Income**: Predictable cash flow independent of market price movements
    - **Compounding Potential**: Reinvested dividends can significantly enhance long-term returns
    - **Lower Volatility**: Dividend stocks often exhibit less price volatility
    - **Inflation Protection**: Companies with growing dividends help protect against inflation
    
    **Key Metrics to Consider:**
    - **Dividend Yield**: Annual dividend divided by share price
    - **Payout Ratio**: Percentage of earnings paid as dividends
    - **Dividend Growth Rate**: Historical rate of dividend increases
    - **Dividend Consistency**: Track record of maintaining or increasing dividends
    
    Remember that high yields may come with higher risks, and sustainable moderate yields
    with consistent growth often perform better over long time periods.
    """)
