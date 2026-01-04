import sqlite3, hashlib

DB_FILE = "students.db"

def hash_password(p):
    return hashlib.sha256(p.encode()).hexdigest()

def init_users():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password_hash TEXT NOT NULL,
            role TEXT CHECK(role IN ('admin','teacher','student')) NOT NULL
        )
    """)
    conn.commit()

    users = [
        ("admin", hash_password("admin123"), "admin"),
        ("teacher", hash_password("teach123"), "teacher"),
        ("student1", hash_password("stud123"), "student")
    ]

    for u in users:
        try:
            cur.execute("INSERT INTO users VALUES (?,?,?)", u)
        except sqlite3.IntegrityError:
            pass  # user already exists
    conn.commit()
    conn.close()
    print("✅ Default users created:")
    print("admin/admin123, teacher/teach123, student1/stud123")

if __name__ == "__main__":
    init_users()
