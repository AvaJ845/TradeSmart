import streamlit as st
import warnings
from importlib import import_module

# Ignore warnings
warnings.filterwarnings('ignore')

# Set page config first (must be called before any other Streamlit commands)
st.set_page_config(page_title="TradeSmart", page_icon="📈", layout="wide")

# Safe module imports with error handling
def safe_import(module_name):
    try:
        return import_module(module_name)
    except ImportError as e:
        st.error(f"Failed to load module {module_name}: {str(e)}")
        return None

# Import modules
modules = {
    "Home": safe_import("utils.home").home_page,
    "Stock Analysis": safe_import("modules.stock_analysis").stock_analysis_module,
    "Options Analysis": safe_import("modules.options_analysis").options_analysis_module,
    "Market Anomaly Scanner": safe_import("modules.market_anomaly").market_anomaly_scanner_module,
    "Paper Trading Simulator": safe_import("modules.paper_trading").paper_trading_module,
    "Dividend Analysis": safe_import("modules.dividend_analysis").dividend_analysis_module,
    "About & Definitions": safe_import("modules.definitions").about_definitions_module
}

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

# Run the selected module with enhanced error handling
try:
    if app_mode in modules and modules[app_mode]:
        with st.spinner(f'Loading {app_mode} module...'):
            modules[app_mode]()
    else:
        st.error(f"Module {app_mode} is not available")
except Exception as e:
    st.error("⚠️ An error occurred!")
    st.error(f"Module: {app_mode}")
    st.error(f"Error: {str(e)}")
    if st.checkbox("Show detailed error trace"):
        st.code(traceback.format_exc())
    st.session_state.last_error = str(e)
    st.info("💡 Try refreshing the page or selecting a different module.")
