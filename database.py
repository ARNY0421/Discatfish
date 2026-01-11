import sqlite3
import os

DB_PATH = "linker.db"

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                discord_id TEXT PRIMARY KEY,
                x_user_id TEXT,
                x_username TEXT,
                linked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()

def link_user(discord_id, x_user_id, x_username):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            INSERT OR REPLACE INTO users (discord_id, x_user_id, x_username)
            VALUES (?, ?, ?)
        """, (discord_id, x_user_id, x_username))
        conn.commit()

def get_linked_account(discord_id):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute("SELECT x_username FROM users WHERE discord_id = ?", (discord_id,))
        row = cursor.fetchone()
        return row[0] if row else None

if __name__ == "__main__":
    init_db()
    print("Database initialized.")
