import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    # Use 12010 as default port for Aiven
    host = os.getenv("DB_HOST", "mysql-2e4f6a95-b46705115-547f.j.aivencloud.com")
    port = int(os.getenv("DB_PORT", 12010))
    user = os.getenv("DB_USER", "avnadmin")
    password = os.getenv("DB_PASS", "") 
    database_name = os.getenv("DB_NAME", "defaultdb")

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
        cursor.execute("CREATE TABLE IF NOT EXISTS kodusers (uid INT AUTO_INCREMENT PRIMARY KEY, username VARCHAR(255) UNIQUE, email VARCHAR(255) UNIQUE, password VARCHAR(255), phone VARCHAR(20), role VARCHAR(20) DEFAULT 'Customer', balance DECIMAL(15, 2) DEFAULT 100000.00)")
        cursor.execute("CREATE TABLE IF NOT EXISTS CJWT (tid INT AUTO_INCREMENT PRIMARY KEY, token TEXT, uid INT, expiry DATETIME)")
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Init Error: {e}")
