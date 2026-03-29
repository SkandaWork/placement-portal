import sqlite3

def get_db():
    conn = sqlite3.connect("placement.db")
    conn.row_factory = sqlite3.Row
    return conn

def create_tables():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS admin(
        id INTEGER PRIMARY KEY,
        username TEXT,
        password TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS students(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT,
        password TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS companies(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        hr_contact TEXT,
        website TEXT,
        password TEXT,
        status TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS drives(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_id INTEGER,
        job_title TEXT,
        description TEXT,
        eligibility TEXT,
        deadline TEXT,
        status TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS applications(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        drive_id INTEGER,
        status TEXT
    )
    """)

    conn.commit()

    cur.execute("INSERT OR IGNORE INTO admin VALUES (1,'admin','admin')")
    conn.commit()

    conn.close()