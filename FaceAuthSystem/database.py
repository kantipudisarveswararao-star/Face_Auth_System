import sqlite3
import pickle
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "users.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            face_encoding BLOB NOT NULL,
            image_path TEXT
        )
    """)
    conn.commit()
    conn.close()

def add_user(name, password, face_encoding, image_path):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        encoding_blob = pickle.dumps(face_encoding)
        cursor.execute(
            "INSERT INTO users (name, password, face_encoding, image_path) VALUES (?, ?, ?, ?)",
            (name, password, encoding_blob, image_path)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def get_user_by_name(name):
    """Fetch a single user record by username."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, password, face_encoding, image_path FROM users WHERE name = ?", (name,))
    row = cursor.fetchone()
    conn.close()
    if row is None:
        return None
    return {
        "id": row[0],
        "name": row[1],
        "password": row[2],
        "face_encoding": pickle.loads(row[3]),
        "image_path": row[4]
    }

def get_all_users():
    """Fetch all user records (used for face matching against the whole database)."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, password, face_encoding, image_path FROM users")
    rows = cursor.fetchall()
    conn.close()
    users = []
    for row in rows:
        users.append({
            "id": row[0],
            "name": row[1],
            "password": row[2],
            "face_encoding": pickle.loads(row[3]),
            "image_path": row[4]
        })
    return users

def username_exists(name):
    return get_user_by_name(name) is not None
