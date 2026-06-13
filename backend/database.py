import sqlite3
import os

DB_FILE = "shadow_garden_iot.db"

def init_db():
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS latest_sensor_data (
                device TEXT PRIMARY KEY,
                temperature REAL,
                humidity REAL,
                moisture REAL,
                air_quality REAL,
                last_update TEXT
            )
        ''')
        conn.commit()
        conn.close()
        print("[OK] Connected to SQLite database")
    except Exception as e:
        print(f"[ERROR] Failed to connect to SQLite: {e}")

init_db()

def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn
