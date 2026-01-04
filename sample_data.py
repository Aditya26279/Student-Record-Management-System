import sqlite3, hashlib, random

DB_FILE = "students.db"

def hash_password(p):
    """Hash password using SHA-256"""
    import hashlib
    return hashlib.sha256(p.encode()).hexdigest()

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    # Ensure tables exist
    cur.execute("""
        CREATE TABLE IF NOT EXISTS students (
            roll INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            marks INTEGER NOT NULL
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password_hash TEXT NOT NULL,
            role TEXT CHECK(role IN ('admin','teacher','student')) NOT NULL
        )
    """)
    conn.commit()
    return conn

def populate_students(conn):
    """Insert sample students"""
    sample_students = [
        (1, "Aarav Patel", random.randint(50, 100)),
        (2, "Diya Sharma", random.randint(50, 100)),
        (3, "Rohan Mehta", random.randint(50, 100)),
        (4, "Priya Singh", random.randint(50, 100)),
        (5, "Karan Gupta", random.randint(50, 100)),
        (6, "Ishita Desai", random.randint(50, 100)),
        (7, "Arjun Reddy", random.randint(50, 100)),
        (8, "Sneha Nair", random.randint(50, 100)),
        (9, "Manav Joshi", random.randint(50, 100)),
        (10, "Nisha Bhatia", random.randint(50, 100)),
        (11, "Vikram Rao", random.randint(50, 100)),
        (12, "Meera Kapoor", random.randint(50, 100)),
        (13, "Ritika Bose", random.randint(50, 100)),
        (14, "Tanishq Verma", random.randint(50, 100)),
        (15, "Pooja Das", random.randint(50, 100))
    ]
    cur = conn.cursor()
    for s in sample_students:
        try:
            cur.execute("INSERT INTO students (roll, name, marks) VALUES (?, ?, ?)", s)
        except sqlite3.IntegrityError:
            pass  # already exists
    conn.commit()
    print(f"✅ {len(sample_students)} student records inserted.")

def populate_users(conn):
    """Insert sample users (admin, teacher, 3 students)"""
    users = [
        ("admin", hash_password("admin123"), "admin"),
        ("teacher", hash_password("teach123"), "teacher"),
        ("student1", hash_password("stud123"), "student"),
        ("student2", hash_password("stud123"), "student"),
        ("student3", hash_password("stud123"), "student"),
    ]
    cur = conn.cursor()
    for u in users:
        try:
            cur.execute("INSERT INTO users VALUES (?, ?, ?)", u)
        except sqlite3.IntegrityError:
            pass
    conn.commit()
    print("👩‍🏫 Default users created:")
    print(" - admin / admin123")
    print(" - teacher / teach123")
    print(" - student1 / stud123")
    print(" - student2 / stud123")
    print(" - student3 / stud123")

def link_students_to_users(conn):
    """
    Optionally link student usernames (student1, student2...) to student roll numbers.
    You can use the numeric part of username as roll ID.
    """
    cur = conn.cursor()
    cur.execute("SELECT username FROM users WHERE role='student'")
    all_students = cur.fetchall()
    print("\n🔗 Linked students (username → roll):")
    for u in all_students:
        uname = u[0]
        try:
            roll = int(''.join([c for c in uname if c.isdigit()]))
        except ValueError:
            roll = 1
        cur.execute("SELECT name FROM students WHERE roll=?", (roll,))
        name_row = cur.fetchone()
        print(f"  {uname} → Roll {roll} ({name_row[0] if name_row else 'Not Found'})")

def main():
    conn = init_db()
    populate_students(conn)
    populate_users(conn)
    link_students_to_users(conn)
    conn.close()
    print("\n🎉 Database ready! Run `python3 app.py` to launch the GUI.")

if __name__ == "__main__":
    main()
