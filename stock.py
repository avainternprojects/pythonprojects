import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Page configuration
st.set_page_config(
    page_title="Indian Stock Price Predictor",
    page_icon="🇮🇳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #FF9933;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #138808;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
    }
    .info-text {
        background-color: #F5F5F5;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #FF9933;
        margin-bottom: 1rem;
    }
    .prediction-box {
        background-color: #E8F5E9;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #138808;
        margin-top: 1rem;
    }
    .indian-flag {
        font-size: 2rem;
        text-align: center;
        margin-bottom: 1rem;
    }
    .stButton>button {
        background-color: #138808;
        color: white;
        font-weight: bold;
        border-radius: 0.5rem;
        padding: 0.5rem 1rem;
        border: none;
        width: 100%;
    }
    .stButton>button:hover {
        background-color: #0D6E0D;
    }
    .stock-button {
        background-color: #F0F8FF;
        border: 1px solid #138808;
        color: #138808;
    }
    .stock-button:hover {
        background-color: #138808;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# Title and description
st.markdown("<div class='indian-flag'>🇮🇳</div>", unsafe_allow_html=True)
st.markdown("<h1 class='main-header'>📈 Indian Stock Price Prediction App</h1>", unsafe_allow_html=True)
st.markdown("""
<div class='info-text'>
    This app predicts future stock prices for Indian companies listed on NSE. 
    Use NSE symbols with ".NS" suffix (e.g., RELIANCE.NS, TCS.NS, INFY.NS).
    The app uses machine learning to forecast future prices.
</div>
""", unsafe_allow_html=True)

# Initialize session state
if 'analyze_clicked' not in st.session_state:
    st.session_state.analyze_clicked = False

# Indian stock information
INDIAN_STOCKS = {
    "RELIANCE.NS": "Reliance Industries",
    "TCS.NS": "Tata Consultancy Services",
    "HDFCBANK.NS": "HDFC Bank",
    "INFY.NS": "Infosys",
    "ICICIBANK.NS": "ICICI Bank",
    "SBIN.NS": "State Bank of India",
    "BHARTIARTL.NS": "Bharti Airtel",
    "WIPRO.NS": "Wipro",
    "ITC.NS": "ITC Limited",
    "LT.NS": "Larsen & Toubro",
    "AXISBANK.NS": "Axis Bank",
    "KOTAKBANK.NS": "Kotak Mahindra Bank",
    "ASIANPAINT.NS": "Asian Paints",
    "HINDUNILVR.NS": "Hindustan Unilever",
    "MARUTI.NS": "Maruti Suzuki",
    "SUNPHARMA.NS": "Sun Pharmaceutical",
    "BAJFINANCE.NS": "Bajaj Finance",
    "TITAN.NS": "Titan Company",
    "ONGC.NS": "Oil & Natural Gas Corp",
    "NTPC.NS": "NTPC Limited"
}

# Sidebar for user inputs
with st.sidebar:
    st.header("⚙️ Settings")
    
    # Indian stock selection
    stock_selection = st.selectbox(
        "Select Indian Stock",
        options=list(INDIAN_STOCKS.keys()),
        format_func=lambda x: f"{x.split('.')[0]} - {INDIAN_STOCKS[x]}",
        index=0
    )
    
    # Or enter custom NSE symbol
    custom_symbol = st.text_input("Or Enter NSE Symbol", placeholder="e.g., RELIANCE.NS")
    
    # Use custom symbol if provided
    if custom_symbol:
        stock_symbol = custom_symbol.upper()
        if not stock_symbol.endswith('.NS'):
            stock_symbol = stock_symbol + '.NS'
    else:
        stock_symbol = stock_selection
    
    # Date range selection
    st.markdown("---")
    st.subheader("Date Range")
    
    # Date preset options for Indian market
    date_preset = st.selectbox(
        "Quick Select",
        ["Last 1 month", "Last 3 months", "Last 6 months", "Last 1 year", "Last 2 years", "Custom"]
    )
    
    today = datetime.now().date()
    
    if date_preset == "Last 1 month":
        start_date = today - timedelta(days=30)
        end_date = today
    elif date_preset == "Last 3 months":
        start_date = today - timedelta(days=90)
        end_date = today
    elif date_preset == "Last 6 months":
        start_date = today - timedelta(days=180)
        end_date = today
    elif date_preset == "Last 1 year":
        start_date = today - timedelta(days=365)
        end_date = today
    elif date_preset == "Last 2 years":
        start_date = today - timedelta(days=730)
        end_date = today
    else:  # Custom
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Start Date", value=today - timedelta(days=365))
        with col2:
            end_date = st.date_input("End Date", value=today)
    
    # Adjust dates for Indian market holidays
    if end_date > today:
        end_date = today
        st.warning("End date adjusted to today.")
    
    # Prediction parameters
    st.markdown("---")
    st.subheader("Prediction Settings")
    
    prediction_days = st.slider(
        "Days to Predict", 
        min_value=1, 
        max_value=90, 
        value=30,
        help="Number of trading days to predict into the future"
    )
    
    # Model selection
    model_type = st.selectbox(
        "Prediction Model",
        ["Linear Regression", "Polynomial Regression", "Moving Average"]
    )
    
    # Show additional info
    show_info = st.checkbox("Show Stock Information", value=True)
    
    # Submit button
    st.markdown("---")
    if st.button("📊 Analyze & Predict", type="primary", use_container_width=True):
        st.session_state.analyze_clicked = True
        st.rerun()

# Function to properly handle yfinance data
def get_stock_data(symbol, start_date, end_date):
    """Fetch and properly process stock data from yfinance"""
    try:
        # Download stock data
        stock_data = yf.download(
            symbol, 
            start=start_date, 
            end=end_date, 
            progress=False,
            auto_adjust=True
        )
        
        if stock_data.empty:
            return None, "No data found"
        
        # Fix: Handle MultiIndex columns properly
        # If columns are MultiIndex, flatten them
        if isinstance(stock_data.columns, pd.MultiIndex):
            # Flatten the MultiIndex columns
            stock_data.columns = ['_'.join(col).strip() for col in stock_data.columns.values]
        
        # Reset index to make Date a column
        stock_data = stock_data.reset_index()
        
        # Rename columns to standard names
        column_mapping = {}
        for col in stock_data.columns:
            col_str = str(col)
            if 'Date' in col_str or col_str == 'Date':
                column_mapping[col] = 'Date'
            elif 'Close' in col_str or col_str == 'Adj Close':
                column_mapping[col] = 'Close'
            elif 'Open' in col_str:
                column_mapping[col] = 'Open'
            elif 'High' in col_str:
                column_mapping[col] = 'High'
            elif 'Low' in col_str:
                column_mapping[col] = 'Low'
            elif 'Volume' in col_str:
                column_mapping[col] = 'Volume'
        
        stock_data.rename(columns=column_mapping, inplace=True)
        
        # Ensure required columns exist
        if 'Close' not in stock_data.columns and 'Adj Close' in stock_data.columns:
            stock_data['Close'] = stock_data['Adj Close']
        
        return stock_data, "Success"
    
    except Exception as e:
        return None, str(e)

# Main content area
if st.session_state.analyze_clicked:
    # Display progress
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # Fetch stock data
    status_text.text("Fetching stock data from NSE...")
    progress_bar.progress(20)
    
    try:
        # Format dates for yfinance
        start_date_str = start_date.strftime("%Y-%m-%d")
        end_date_str = end_date.strftime("%Y-%m-%d")
        
        # Get stock data using our function
        df, message = get_stock_data(stock_symbol, start_date_str, end_date_str)
        
        if df is None:
            st.error(f"""
            ❌ {message} for symbol '{stock_symbol}'. 
            
            **Possible reasons:**
            1. The NSE symbol might be incorrect
            2. The stock might be delisted or suspended
            3. Data might not be available for the selected date range
            4. Make sure to use ".NS" suffix for NSE stocks
            
            **Try:**
            - Selecting a stock from the dropdown list
            - Using a valid NSE symbol with ".NS" suffix
            - Adjusting the date range
            - Checking if the market was open on selected dates
            """)
            
            # Try to get recent data to verify symbol
            try:
                test_data = yf.download(stock_symbol, period="1mo", progress=False)
                if not test_data.empty:
                    st.success(f"✅ Found recent data for {stock_symbol}!")
                    st.write(f"Available data from {test_data.index[0].date()} to {test_data.index[-1].date()}")
                    st.info("Try using a shorter date range (Last 1 month or Last 3 months)")
            except:
                st.warning(f"Symbol '{stock_symbol}' not found. Please use a valid NSE symbol.")
                
            st.stop()
        
        if len(df) < 10:
            st.error("Not enough data for analysis. Please select a longer date range.")
            st.stop()
        
        progress_bar.progress(40)
        status_text.text("Processing stock data...")
        
        # Ensure Date column is datetime
        df['Date'] = pd.to_datetime(df['Date'])
        
        # Sort by date
        df = df.sort_values('Date')
        
        # Calculate moving averages
        window_20 = min(20, len(df))
        window_50 = min(50, len(df))
        df['MA20'] = df['Close'].rolling(window=window_20).mean()
        df['MA50'] = df['Close'].rolling(window=window_50).mean()
        
        # Calculate daily returns in percentage
        df['Daily_Return'] = df['Close'].pct_change() * 100
        
        progress_bar.progress(60)
        status_text.text("Training prediction model...")
        
        # Prepare data for prediction
        prediction_df = df[['Date', 'Close']].copy().dropna()
        
        if len(prediction_df) < 10:
            st.error("Not enough data for prediction. Please select a longer date range.")
            st.stop()
        
        # Create features for prediction
        prediction_df['Days'] = (prediction_df['Date'] - prediction_df['Date'].min()).dt.days
        X = prediction_df['Days'].values.reshape(-1, 1)
        y = prediction_df['Close'].values
        
        # Train different models based on selection
        if model_type == "Linear Regression":
            from sklearn.linear_model import LinearRegression
            model = LinearRegression()
            model.fit(X, y)
            
            # Predict future dates
            last_day = prediction_df['Days'].max()
            future_days = np.array(range(last_day + 1, last_day + prediction_days + 1)).reshape(-1, 1)
            future_predictions = model.predict(future_days)
            
        elif model_type == "Polynomial Regression":
            from sklearn.preprocessing import PolynomialFeatures
            from sklearn.linear_model import LinearRegression
            
            poly = PolynomialFeatures(degree=2)
            X_poly = poly.fit_transform(X)
            
            model = LinearRegression()
            model.fit(X_poly, y)
            
            # Predict future dates
            last_day = prediction_df['Days'].max()
            future_days = np.array(range(last_day + 1, last_day + prediction_days + 1)).reshape(-1, 1)
            future_days_poly = poly.transform(future_days)
            future_predictions = model.predict(future_days_poly)
            
        else:  # Moving Average
            recent_prices = prediction_df['Close'].tail(20).values
            if len(recent_prices) > 10:
                avg_change = np.mean(np.diff(recent_prices[-10:]))
            else:
                avg_change = 0
            
            future_predictions = []
            last_price = prediction_df['Close'].iloc[-1]
            for i in range(prediction_days):
                predicted = last_price + avg_change * (i+1)
                future_predictions.append(predicted)
            future_predictions = np.array(future_predictions)
        
        progress_bar.progress(80)
        status_text.text("Generating visualizations...")
        
        # Create future dates (skip weekends for Indian market)
        last_date = prediction_df['Date'].max()
        future_dates = []
        current_date = last_date
        
        for i in range(prediction_days):
            current_date += timedelta(days=1)
            # Skip weekends (Saturday=5, Sunday=6)
            while current_date.weekday() >= 5:
                current_date += timedelta(days=1)
            future_dates.append(current_date)
        
        # Create prediction dataframe
        predictions_df = pd.DataFrame({
            'Date': future_dates[:prediction_days],
            'Predicted_Close': future_predictions
        })
        
        # Calculate prediction metrics
        last_actual_price = prediction_df['Close'].iloc[-1]
        predicted_price = future_predictions[-1]
        price_change = predicted_price - last_actual_price
        percent_change = (price_change / last_actual_price) * 100
        
        progress_bar.progress(100)
        status_text.text("Analysis complete!")
        progress_bar.empty()
        status_text.empty()
        
        # Display results
        stock_name = INDIAN_STOCKS.get(stock_symbol, stock_symbol)
        st.success(f"✅ Successfully analyzed {stock_name} ({stock_symbol})")
        
        # Display key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Current Price", f"₹{last_actual_price:.2f}")
        
        with col2:
            st.metric(
                f"{prediction_days}-Day Prediction", 
                f"₹{predicted_price:.2f}",
                delta=f"{percent_change:.2f}%",
                delta_color="normal" if percent_change >= 0 else "inverse"
            )
        
        with col3:
            high_price = df['Close'].max()
            st.metric("All-Time High (Period)", f"₹{high_price:.2f}")
        
        with col4:
            low_price = df['Close'].min()
            st.metric("All-Time Low (Period)", f"₹{low_price:.2f}")
        
        # Display stock information if requested
        if show_info:
            with st.expander("📊 Stock Details", expanded=True):
                try:
                    stock_info = yf.Ticker(stock_symbol).info
                    
                    info_cols = st.columns(3)
                    with info_cols[0]:
                        st.write("**Company Info**")
                        st.write(f"Name: {stock_info.get('longName', stock_name)}")
                        st.write(f"Sector: {stock_info.get('sector', 'N/A')}")
                        st.write(f"Industry: {stock_info.get('industry', 'N/A')}")
                    
                    with info_cols[1]:
                        st.write("**Market Info**")
                        market_cap = stock_info.get('marketCap')
                        if market_cap:
                            if market_cap >= 1e12:
                                display_cap = f"₹{market_cap/1e12:.2f} Lakh Cr"
                            elif market_cap >= 1e7:
                                display_cap = f"₹{market_cap/1e7:.2f} Cr"
                            else:
                                display_cap = f"₹{market_cap:,.2f}"
                            st.write(f"Market Cap: {display_cap}")
                        
                        pe_ratio = stock_info.get('trailingPE')
                        if pe_ratio:
                            st.write(f"P/E Ratio: {pe_ratio:.2f}")
                    
                    with info_cols[2]:
                        st.write("**Performance**")
                        day_high = stock_info.get('dayHigh', 'N/A')
                        day_low = stock_info.get('dayLow', 'N/A')
                        st.write(f"Day Range: ₹{day_low} - ₹{day_high}")
                        
                        volume = stock_info.get('volume', 'N/A')
                        if volume and volume > 1e6:
                            st.write(f"Volume: {volume/1e6:.1f}M shares")
                except:
                    st.write("Detailed information not available")
        
        # Create tabs for different views
        tab1, tab2, tab3, tab4 = st.tabs(["📈 Price Chart", "🔮 Predictions", "📊 Statistics", "📋 Data"])
        
        with tab1:
            # Create interactive chart
            fig = go.Figure()
            
            # Add price line
            fig.add_trace(go.Scatter(
                x=df['Date'], 
                y=df['Close'],
                mode='lines',
                name='Closing Price',
                line=dict(color='#138808', width=2),
                hovertemplate='Date: %{x}<br>Price: ₹%{y:.2f}<extra></extra>'
            ))
            
            # Add moving averages if available
            if 'MA20' in df.columns:
                ma20_data = df[df['MA20'].notna()]
                if len(ma20_data) > 0:
                    fig.add_trace(go.Scatter(
                        x=ma20_data['Date'], 
                        y=ma20_data['MA20'],
                        mode='lines',
                        name='20-Day MA',
                        line=dict(color='orange', width=1, dash='dash')
                    ))
            
            if 'MA50' in df.columns:
                ma50_data = df[df['MA50'].notna()]
                if len(ma50_data) > 0:
                    fig.add_trace(go.Scatter(
                        x=ma50_data['Date'], 
                        y=ma50_data['MA50'],
                        mode='lines',
                        name='50-Day MA',
                        line=dict(color='red', width=1, dash='dash')
                    ))
            
            # Add predictions
            fig.add_trace(go.Scatter(
                x=predictions_df['Date'], 
                y=predictions_df['Predicted_Close'],
                mode='lines+markers',
                name='Predictions',
                line=dict(color='#FF9933', width=2, dash='dot'),
                marker=dict(size=6)
            ))
            
            fig.update_layout(
                title=f"{stock_name} Stock Price - {model_type} Predictions",
                xaxis_title="Date",
                yaxis_title="Price (₹)",
                hovermode='x unified',
                height=500,
                showlegend=True
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with tab2:
            # Show prediction details
            st.subheader(f"📅 Next {prediction_days} Trading Days Predictions")
            
            # Create a table of predictions
            pred_display = predictions_df.copy()
            pred_display['Date'] = pred_display['Date'].dt.strftime('%Y-%m-%d')
            pred_display['Predicted_Close'] = pred_display['Predicted_Close'].round(2)
            pred_display['Change'] = pred_display['Predicted_Close'] - last_actual_price
            pred_display['Change %'] = (pred_display['Change'] / last_actual_price * 100).round(2)
            
            pred_display.columns = ['Date', 'Predicted Price (₹)', 'Change (₹)', 'Change (%)']
            
            st.dataframe(pred_display, use_container_width=True)
            
            # Calculate and display overall prediction
            st.markdown("---")
            col1, col2 = st.columns(2)
            with col1:
                st.metric(
                    "Current Price",
                    f"₹{last_actual_price:.2f}"
                )
            with col2:
                st.metric(
                    f"Target Price ({prediction_days} days)",
                    f"₹{predicted_price:.2f}",
                    delta=f"{percent_change:.2f}%",
                    delta_color="normal" if percent_change >= 0 else "inverse"
                )
            
            # Download predictions
            csv = pred_display.to_csv(index=False)
            st.download_button(
                label="📥 Download Predictions (CSV)",
                data=csv,
                file_name=f"{stock_symbol.replace('.NS', '')}_predictions.csv",
                mime="text/csv"
            )
        
        with tab3:
            # Show statistics
            st.subheader("📊 Statistical Analysis")
            
            stat_cols = st.columns(2)
            
            with stat_cols[0]:
                st.write("**Price Statistics**")
                stats_data = {
                    'Metric': ['Mean', 'Median', 'Std Dev', 'Min', 'Max', 'Current'],
                    'Value (₹)': [
                        f"₹{df['Close'].mean():.2f}",
                        f"₹{df['Close'].median():.2f}",
                        f"₹{df['Close'].std():.2f}",
                        f"₹{df['Close'].min():.2f}",
                        f"₹{df['Close'].max():.2f}",
                        f"₹{last_actual_price:.2f}"
                    ]
                }
                stats_df = pd.DataFrame(stats_data)
                st.dataframe(stats_df, use_container_width=True, hide_index=True)
            
            with stat_cols[1]:
                st.write("**Daily Returns Analysis**")
                if 'Daily_Return' in df.columns:
                    positive_days = (df['Daily_Return'] > 0).sum()
                    negative_days = (df['Daily_Return'] < 0).sum()
                    
                    returns_data = {
                        'Metric': ['Mean Return', 'Std Dev', 'Max Gain', 'Max Loss', 'Positive Days', 'Negative Days'],
                        'Value': [
                            f"{df['Daily_Return'].mean():.2f}%",
                            f"{df['Daily_Return'].std():.2f}%",
                            f"{df['Daily_Return'].max():.2f}%",
                            f"{df['Daily_Return'].min():.2f}%",
                            f"{positive_days} ({(positive_days/len(df)*100):.1f}%)",
                            f"{negative_days} ({(negative_days/len(df)*100):.1f}%)"
                        ]
                    }
                    returns_df = pd.DataFrame(returns_data)
                    st.dataframe(returns_df, use_container_width=True, hide_index=True)
                else:
                    st.write("Daily return data not available")
        
        with tab4:
            # Show raw data
            st.subheader("📋 Historical Data")
            
            # Format data for display
            display_df = df.copy()
            display_df['Date'] = display_df['Date'].dt.strftime('%Y-%m-%d')
            
            # Select columns to display
            display_cols = ['Date']
            for col in ['Open', 'High', 'Low', 'Close']:
                if col in display_df.columns:
                    display_cols.append(col)
            
            if 'Volume' in display_df.columns:
                display_cols.append('Volume')
            
            for col in ['MA20', 'MA50', 'Daily_Return']:
                if col in display_df.columns:
                    display_cols.append(col)
            
            display_df = display_df[display_cols]
            
            # Format numeric columns
            for col in ['Open', 'High', 'Low', 'Close', 'MA20', 'MA50']:
                if col in display_df.columns:
                    display_df[col] = display_df[col].round(2)
            
            if 'Daily_Return' in display_df.columns:
                display_df['Daily_Return'] = display_df['Daily_Return'].round(2)
            
            if 'Volume' in display_df.columns:
                # Format volume with commas
                display_df['Volume'] = display_df['Volume'].apply(lambda x: f"{int(x):,}" if pd.notnull(x) else x)
            
            st.dataframe(display_df, use_container_width=True, height=400)
            
            # Download data
            csv = display_df.to_csv(index=False)
            st.download_button(
                label="📥 Download Historical Data (CSV)",
                data=csv,
                file_name=f"{stock_symbol.replace('.NS', '')}_historical.csv",
                mime="text/csv"
            )
        
    except Exception as e:
        st.error(f"❌ An error occurred: {str(e)}")
        import traceback
        st.code(traceback.format_exc())
        
        st.info("💡 **Troubleshooting tips for Indian stocks:**")
        st.markdown("""
        1. **Use correct NSE symbol** with ".NS" suffix (e.g., RELIANCE.NS)
        2. **Check if stock is actively traded** on NSE
        3. **Select appropriate date range** (avoid future dates)
        4. **Try popular stocks** from the dropdown list
        5. **Ensure internet connection** is working
        
        **Note:** Indian market data might have delays on Yahoo Finance
        """)
        
        # Reset button
        if st.button("🔄 Reset and Try Again"):
            st.session_state.analyze_clicked = False
            st.rerun()

else:
    # Show welcome screen
    col1, col2, col3 = st.columns([1, 3, 1])
    
    with col2:
        st.markdown("""
        <div style='text-align: center;'>
            <div style='font-size: 60px; margin-bottom: 10px;'>🇮🇳📈</div>
            <h2>Indian Stock Price Predictor</h2>
            <p style='font-size: 1.1rem; color: #666;'>
                Predict prices for Indian stocks listed on National Stock Exchange (NSE)<br>
                Get insights, visualize trends, and make informed investment decisions
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Features section
        feature_cols = st.columns(3)
        
        with feature_cols[0]:
            st.markdown("""
            <div style='text-align: center;'>
                <div style='font-size: 40px;'>🏢</div>
                <h4>Indian Stocks</h4>
                <p>Top NSE listed companies</p>
            </div>
            """, unsafe_allow_html=True)
        
        with feature_cols[1]:
            st.markdown("""
            <div style='text-align: center;'>
                <div style='font-size: 40px;'>🔮</div>
                <h4>AI Predictions</h4>
                <p>ML models for forecasting</p>
            </div>
            """, unsafe_allow_html=True)
        
        with feature_cols[2]:
            st.markdown("""
            <div style='text-align: center;'>
                <div style='font-size: 40px;'>📊</div>
                <h4>Indian Rupees</h4>
                <p>All prices in ₹</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Quick start instructions
        st.markdown("""
        ### 🚀 How to Use
        
        1. **Select an Indian stock** from the dropdown or enter NSE symbol
        2. **Choose date range** using quick select options
        3. **Set prediction days** (trading days to predict)
        4. **Select prediction model** (Linear, Polynomial, etc.)
        5. **Click "Analyze & Predict"** to see results
        
        **💡 Tip:** Start with RELIANCE.NS or TCS.NS to see how it works!
        
        **Note:** All prices are in Indian Rupees (₹)
        """)
        
        # Display popular Indian stocks
        st.markdown("### 📋 Popular Indian Stocks")
        
        # Create a table of popular Indian stocks
        stock_table_data = []
        for symbol, name in list(INDIAN_STOCKS.items())[:12]:  # Show first 12
            stock_table_data.append([symbol, name])
        
        stock_df = pd.DataFrame(stock_table_data, columns=["NSE Symbol", "Company Name"])
        st.dataframe(stock_df, use_container_width=True, hide_index=True)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; font-size: 0.9rem;'>
    <p><strong>⚠️ Disclaimer:</strong> This tool is for educational purposes only. 
    Stock predictions are not financial advice. Past performance does not guarantee future results.</p>
    <p>Data provided by Yahoo Finance • Focused on Indian NSE Stocks • Made with Streamlit</p>
    <p style='color: #138808; font-weight: bold;'>🇮🇳 Investing in Indian Markets 🇮🇳</p>
</div>
""", unsafe_allow_html=True)