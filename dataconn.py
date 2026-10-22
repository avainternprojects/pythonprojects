import pymysql

class DatabaseConnection:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.connection = pymysql.connect(
                host="localhost",
                user="root",
                password="",
                database="students",
                cursorclass=pymysql.cursors.DictCursor  # Optional: Returns results as dictionaries
            )
            print("✅ Connected to MySQL")
        return cls._instance

    def execute_query(self, query, params=None):
        cursor = self.connection.cursor()
        try:
            cursor.execute(query, params or ())
            self.connection.commit()
            return cursor.fetchall()
        except Exception as e:
            self.connection.rollback()
            print(f"❌ Error executing query: {e}")
            raise

def initialize_database():
    db = DatabaseConnection()
    
    # Create table (fixed syntax)
    db.execute_query("""
    CREATE TABLE IF NOT EXISTS customers (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(100),
        email VARCHAR(100),
        age INT,
        country VARCHAR(50)
    )
    """)
    
    # Insert sample data (parameterized to avoid SQL injection)
    if not db.execute_query("SELECT * FROM customers LIMIT 1"):
        sample_data = [
            ("Alice Johnson", "alice@example.com", 28, "USA"),
            ("Bob Smith", "bob@example.com", 34, "Canada"),
            ("Charlie Brown", "charlie@example.com", 22, "UK"),
            ("Diana Miller", "diana@example.com", 45, "Australia")
        ]
        for data in sample_data:
            db.execute_query(
                "INSERT INTO customers (name, email, age, country) VALUES (%s, %s, %s, %s)",
                data
            )
        print("📊 Sample data inserted!")
    
    # Fetch data
    customers = db.execute_query("SELECT * FROM customers")
    print("\nCustomers Table:")
    for row in customers:
        print(row)

if __name__ == "__main__":
    initialize_database()