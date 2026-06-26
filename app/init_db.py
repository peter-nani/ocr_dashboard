import sqlite3
import os

DB_PATH = "/app/data/dashboard.db"

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create Users table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
    """)
    
    # Check if our new credentials exist, otherwise seed them cleanly
    cursor.execute("SELECT id FROM users WHERE username = 'operator'")
    if not cursor.fetchone():
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", ("operator", "matrix99"))
        conn.commit()
        
    conn.close()

if __name__ == "__main__":
    init_db()