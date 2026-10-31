import streamlit as st
import pandas as pd
import mysql.connector
from mysql.connector import Error
import time
from typing import Iterator, Optional

# Configure Streamlit page
st.set_page_config(page_title="XAMPP Data Pipeline", layout="wide")
st.title("📊 XAMPP MySQL Data Pipeline")

# Database Configuration (XAMPP Defaults)
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',  # XAMPP default is empty
    'database': 'test_db'  # Create this in phpMyAdmin first
}

class XAMPPMySQLConnector:
    """Handles connection and queries to XAMPP MySQL"""
    def __init__(self, config):
        self.config = config
        self.connection = None
    
    def __enter__(self):
        """Connect when entering context"""
        try:
            self.connection = mysql.connector.connect(**self.config)
            return self
        except Error as e:
            st.error(f"Connection failed: {e}")
            raise
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Close connection when exiting context"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
    
    @st.cache_data(ttl=300, show_spinner="Fetching table list...")
    def get_tables(_self) -> list:
        """Get list of tables in database"""
        with _self.connection.cursor() as cursor:
            cursor.execute("SHOW TABLES")
            return [table[0] for table in cursor.fetchall()]
    
    def stream_table_data(self, table_name: str, batch_size: int = 1000) -> Iterator[pd.DataFrame]:
        """Generator that yields data in batches"""
        offset = 0
        with self.connection.cursor(dictionary=True) as cursor:
            while True:
                cursor.execute(
                    f"SELECT * FROM {table_name} LIMIT {batch_size} OFFSET {offset}"
                )
                batch = cursor.fetchall()
                if not batch:
                    break
                yield pd.DataFrame(batch)
                offset += batch_size

class DataExplorerUI:
    """Streamlit UI components"""
    def __init__(self):
        self.connector = XAMPPMySQLConnector(DB_CONFIG)
    
    def show_connection_status(self):
        """Display connection status badge"""
        try:
            with self.connector:
                st.sidebar.success("✅ Connected to XAMPP MySQL")
        except:
            st.sidebar.error("❌ Connection failed")
    
    def table_selection(self):
        """Table selection dropdown"""
        with self.connector:
            tables = self.connector.get_tables()
        selected_table = st.sidebar.selectbox(
            "Choose Table",
            tables,
            index=0
        )
        batch_size = st.sidebar.number_input(
            "Rows per batch",
            min_value=100,
            max_value=5000,
            value=1000
        )
        return selected_table, batch_size
    
    def data_preview(self, table_name: str, batch_size: int):
        """Display data with pagination"""
        with self.connector:
            data_stream = self.connector.stream_table_data(table_name, batch_size)
            
            if st.button("Load Data"):
                progress_bar = st.progress(0)
                status_text = st.empty()
                all_data = []
                
                for i, batch in enumerate(data_stream):
                    all_data.append(batch)
                    progress = min((i + 1) * batch_size / (batch_size * 10), 1.0)  # Demo limit
                    progress_bar.progress(progress)
                    status_text.text(f"Loaded {len(all_data) * batch_size} rows...")
                    time.sleep(0.1)  # For visualization
                
                if all_data:
                    full_df = pd.concat(all_data)
                    st.session_state['current_data'] = full_df
                    progress_bar.empty()
                    status_text.success(f"✅ Loaded {len(full_df)} total rows")
                
                if 'current_data' in st.session_state:
                    st.dataframe(st.session_state['current_data'])
                    
                    # Export options
                    col1, col2 = st.columns(2)
                    csv = st.session_state['current_data'].to_csv(index=False).encode('utf-8')
                    col1.download_button(
                        "Download CSV",
                        data=csv,
                        file_name=f"{table_name}.csv",
                        mime="text/csv"
                    )
                    
                    if col2.button("Analyze Data"):
                        self.show_analysis(st.session_state['current_data'])

    def show_analysis(self, df: pd.DataFrame):
        """Basic data analysis"""
        st.subheader("Data Analysis")
        
        # Column selection
        analysis_col = st.selectbox("Select column to analyze", df.columns)
        
        # Basic stats
        st.write("### Statistics")
        st.write(df[analysis_col].describe())
        
        # Visualization
        st.write("### Distribution")
        st.bar_chart(df[analysis_col].value_counts())

# Main App Execution
if __name__ == "__main__":
    # Initialize UI
    ui = DataExplorerUI()
    
    # Sidebar controls
    st.sidebar.header("Database Controls")
    ui.show_connection_status()
    
    # Main interface
    selected_table, batch_size = ui.table_selection()
    st.header(f"Table: `{selected_table}`")
    
    # Data display
    ui.data_preview(selected_table, batch_size)