import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    host = os.getenv("DB_HOST", "localhost")
    if host == "localhost":
        print("WARNING: Using DB_HOST fallback 'localhost'. Ensure environment variables are set in Render!")
    
    return mysql.connector.connect(
        host=host,
        port=int(os.getenv("DB_PORT", 3306)),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASS", ""),
        database=os.getenv("DB_NAME", "kodbank"),
        ssl_disabled=False,
        connect_timeout=10 # Fail fast instead of hanging
    )

def init_db():
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

if __name__ == "__main__":
    init_db()
