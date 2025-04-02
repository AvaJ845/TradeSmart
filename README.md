# TradeSmart: Modular Trading Analysis Platform

TradeSmart is a comprehensive trading analysis platform built with Python and Streamlit. It focuses on identifying relative value discrepancies between related securities and analyzing whether these gaps will converge or diverge over time.

## Features

### Market Anomaly & Relative Value Scanner
- Identifies securities that appear cheap or expensive relative to similar assets
- Analyzes stock pairs, sector ETFs vs. components, and bond/rate spreads
- Calculates Z-scores to quantify the degree of divergence from historical relationships
- Provides convergence/divergence outlook with specific trade recommendations
- Offers detailed analysis of why discrepancies exist (fundamentals, sentiment, flows, etc.)

### Stock Analysis
- Technical indicators (RSI, MACD, Bollinger Bands, etc.)
- Trading signal generation
- Strategy backtesting

### Options Analysis
- Options chain visualization
- Implied volatility analysis
- Options strategy builder with P/L visualization

### Paper Trading Simulator
- Backtest trading strategies on historical data
- Track hypothetical performance
- Risk metrics and portfolio analysis

### Dividend Analysis
- Dividend sustainability and growth analysis
- Income projection calculator
- Dividend vs price performance comparison

### Knowledge Base
- Comprehensive explanations of trading concepts
- Risk management principles
- Relative value trading definitions

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/tradesmart.git
cd tradesmart

# Create a virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
streamlit run app.py
```

## Project Structure

```
TradeSmart/
│
├── app.py                   # Main Streamlit application entry point
│
├── modules/
│   ├── __init__.py
│   ├── stock_analysis.py    # Stock technical analysis functionality
│   ├── options_analysis.py  # Options analysis and strategy builder
│   ├── market_anomaly.py    # Market anomaly and relative value scanner
│   ├── paper_trading.py     # Paper trading simulation module
│   ├── dividend_analysis.py # Dividend analysis functionality
│   └── definitions.py       # Trading definitions and concepts
│
├── utils/
│   ├── __init__.py
│   ├── data_fetcher.py      # Functions for fetching financial data
│   ├── indicators.py        # Technical indicator calculations
│   ├── backtest.py          # Backtesting functionality
│   ├── visualization.py     # Chart and plot generation
│   └── statistics.py        # Statistical analysis functions
│
├── requirements.txt         # Python dependencies
└── README.md                # Project documentation
```

## Disclaimer

This application is for educational purposes only and does not constitute financial advice. Trading involves significant risk of loss and is not suitable for all investors. Past performance is not indicative of future results.

No trading system or strategy can guarantee returns, especially at the 20-30% level. Always perform your own research and consider consulting with a financial advisor before making investment decisions.

## License

