import streamlit as st
import warnings
import traceback

# Import local modules
from modules.stock_analysis import stock_analysis_module
from modules.options_analysis import options_analysis_module
from modules.market_anomaly import market_anomaly_scanner_module
from modules.paper_trading import paper_trading_module
from modules.dividend_analysis import dividend_analysis_module
from modules.definitions import about_definitions_module
from utils.home import home_page

# Ignore warnings
warnings.filterwarnings('ignore')
st.set_option('deprecation.showPyplotGlobalUse', None)

# Set page config
st.set_page_config(page_title="TradeSmart", page_icon="📈", layout="wide")

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #2E86C1;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #3498DB;
        margin-bottom: 0.5rem;
    }
    .info-text {
        font-size: 1rem;
        color: #566573;
    }
    .highlight {
        color: #E74C3C;
        font-weight: bold;
    }
    .disclaimer {
        background-color: #FADBD8;
        padding: 10px;
        border-radius: 5px;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state if not already done
if 'initialized' not in st.session_state:
    st.session_state.initialized = True
    st.session_state.last_error = None

# Sidebar Navigation
st.sidebar.markdown('<p class="main-header">TradeSmart</p>', unsafe_allow_html=True)
st.sidebar.markdown('<p class="info-text">Trading Analysis Platform</p>', unsafe_allow_html=True)

# Navigation options
app_mode = st.sidebar.selectbox(
    "Select Module",
    ["Home", "Stock Analysis", "Options Analysis", "Market Anomaly Scanner", 
     "Paper Trading Simulator", "Dividend Analysis", "About & Definitions"]
)

# Disclaimer
st.sidebar.markdown('<div class="disclaimer">⚠️ <b>Disclaimer:</b> This app is for educational purposes only. No trading strategy can guarantee returns. Always do your own due diligence before trading.</div>', unsafe_allow_html=True)

# Dictionary of modules
modules = {
    "Home": home_page,
    "Stock Analysis": stock_analysis_module,
    "Options Analysis": options_analysis_module,
    "Market Anomaly Scanner": market_anomaly_scanner_module,
    "Paper Trading Simulator": paper_trading_module,
    "Dividend Analysis": dividend_analysis_module,
    "About & Definitions": about_definitions_module
}

# Run the selected module with enhanced error handling
try:
    with st.spinner(f'Loading {app_mode} module...'):
        modules[app_mode]()
except Exception as e:
    st.error("⚠️ An error occurred!")
    st.error(f"Module: {app_mode}")
    st.error(f"Error: {str(e)}")
    if st.checkbox("Show detailed error trace"):
        st.code(traceback.format_exc())
    st.session_state.last_error = str(e)
    st.info("💡 Try refreshing the page or selecting a different module.")
