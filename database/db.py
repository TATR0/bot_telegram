import sqlite3
# ==== БАЗА ДАННЫХ ====
DB_PATH = "bot.db"

def get_db():
    return sqlite3.connect(DB_PATH)

def init_db():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS services (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        number TEXT,
        owner_id INTEGER,
        created_at TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS admins (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        service_id INTEGER,
        user_id INTEGER
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        service_id INTEGER,
        client_user_id INTEGER,
        client_name TEXT,
        phone TEXT,
        brand TEXT,
        model TEXT,
        plate TEXT,
        service_type TEXT,
        urgency TEXT,
        comment TEXT,
        status TEXT,
        created_at TEXT
    )
    """)

    conn.commit()
    conn.close()