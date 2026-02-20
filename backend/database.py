import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    # Use 12010 as default port for Aiven
    host = os.getenv("DB_HOST", "localhost")
    port = int(os.getenv("DB_PORT", 12010))
    user = os.getenv("DB_USER", "root")
    password = os.getenv("DB_PASS", "")
    database_name = os.getenv("DB_NAME", "")

    return mysql.connector.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        database=database_name,
        ssl_disabled=False,
        connect_timeout=10
    )

def init_db():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Create kodusers table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS kodusers (
            uid INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(255) UNIQUE NOT NULL,
            email VARCHAR(255) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            phone VARCHAR(20),
            role ENUM('Customer', 'Manager', 'Admin') DEFAULT 'Customer',
            balance DECIMAL(15, 2) DEFAULT 100000.00
        )
        """)
        
        # Create CJWT table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS CJWT (
            tid INT AUTO_INCREMENT PRIMARY KEY,
            token TEXT NOT NULL,
            uid INT NOT NULL,
            expiry DATETIME NOT NULL,
            FOREIGN KEY (uid) REFERENCES kodusers(uid)
        )
        """)
        
        conn.commit()
        cursor.close()
        conn.close()
        print("Database initialized successfully.")
    except Exception as e:
        print(f"init_db error: {e}")

if __name__ == "__main__":
    init_db()
