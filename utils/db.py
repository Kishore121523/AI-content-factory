import sqlite3

DB_NAME = "content_factory.db"

def get_connection():
    return sqlite3.connect(DB_NAME)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Create table with avatar_id column
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS characters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            gender TEXT,
            description TEXT,
            voice_style TEXT,
            avatar_id INTEGER
        )
    """)
    conn.commit()
    conn.close()
