import sqlite3

DB_PATH = "ransomshield.db"

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS analytics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        simulations_run INTEGER DEFAULT 0,
        phishing_clicked INTEGER DEFAULT 0,
        quizzes_taken INTEGER DEFAULT 0,
        avg_quiz_score REAL DEFAULT 0
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        message TEXT
    )
    """)

    conn.commit()
    conn.close()
