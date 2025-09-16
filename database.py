import sqlite3

DB_FILE = "students.db"

def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def create_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students(
            id INTEGER PRIMARY KEY,
            first_name VARCHAR(50),
            last_name VARCHAR(50),
            number VARCHAR(15),
            birthdate DATE,
            email TEXT UNIQUE NOT NULL
        )
    """)
    conn.commit()
    cursor.close()
    conn.close()
