import streamlit as st
import pymysql
from pymysql import cursors
import pandas as pd
from io import BytesIO

class DatabaseConnection:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            try:
                cls._instance.connection = pymysql.connect(
                    host="localhost",
                    user="root",
                    password="",
                    database="custdata",
                    cursorclass=cursors.DictCursor
                )
                st.success("✅ Connected to MySQL successfully!")
            except pymysql.Error as e:
                st.error(f"❌ Connection failed: {e}")
                raise
        return cls._instance

    def execute_query(self, query, params=None):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, params or ())
                self.connection.commit()
                return cursor.fetchall()
        except pymysql.Error as e:
            self.connection.rollback()
            st.error(f"Database error: {e}")
            st.error(f"Failed query: {query}")
            raise

def init_db():
    try:
        db = DatabaseConnection()
        # Fixed: Using a properly formatted single-line SQL query
        create_table_query = """
        CREATE TABLE IF NOT EXISTS customers (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100),
            email VARCHAR(100),
            age INT,
            country VARCHAR(50)
        )
        """
        db.execute_query(create_table_query)
    except Exception as e:
        st.error(f"Initialization error: {e}")

def main():
    st.title("📝 Customer Management System")
    
    # Initialize database
    init_db()
    db = DatabaseConnection()

    # Add Customer Form
    with st.form("customer_form"):
        st.subheader("Add New Customer")
        name = st.text_input("Full Name*")
        email = st.text_input("Email*")
        age = st.number_input("Age", min_value=1, max_value=120, value=25)
        country = st.text_input("Country", "USA")
        
        if st.form_submit_button("Save Customer"):
            if name and email:
                try:
                    db.execute_query(
                        "INSERT INTO customers (name, email, age, country) VALUES (%s, %s, %s, %s)",
                        (name, email, age, country)
                    )
                    st.success("Customer saved successfully!")
                except Exception as e:
                    st.error(f"Failed to save customer: {e}")
            else:
                st.warning("Name and Email are required fields")

    # Display Data
    st.subheader("Current Customers")
    try:
        customers = db.execute_query("SELECT id, name, email, age, country FROM customers")
        if customers:
            df = pd.DataFrame(customers)
            st.dataframe(df)
            
            # Export buttons
            st.subheader("Export Data")
            csv = df.to_csv(index=False).encode('utf-8')
            excel = BytesIO()
            df.to_excel(excel, index=False, engine='openpyxl')
            
            col1, col2 = st.columns(2)
            with col1:
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name="customers.csv",
                    mime="text/csv"
                )
            with col2:
                st.download_button(
                    label="Download Excel",
                    data=excel.getvalue(),
                    file_name="customers.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
        else:
            st.info("No customers found in database")
    except Exception as e:
        st.error(f"Failed to fetch customers: {e}")

if __name__ == "__main__":
    main()