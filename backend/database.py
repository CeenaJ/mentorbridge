import sqlite3
import hashlib
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "mentorbridge.db")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register_student(name, email, password, field, target_university, goals, achievements):
    conn = get_db()
    try:
        conn.execute("""
            INSERT INTO students (name, email, password, field, target_university, goals, achievements)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (name, email, hash_password(password), field, target_university, goals, achievements))
        conn.commit()
        student = conn.execute("SELECT * FROM students WHERE email=?", (email,)).fetchone()
        return {"success": True, "student": dict(student)}
    except sqlite3.IntegrityError:
        return {"success": False, "error": "Email already registered"}
    finally:
        conn.close()

def login_student(email, password):
    conn = get_db()
    student = conn.execute(
        "SELECT * FROM students WHERE email=? AND password=?",
        (email, hash_password(password))
    ).fetchone()
    conn.close()
    if student:
        return {"success": True, "student": dict(student)}
    return {"success": False, "error": "Invalid email or password"}

def get_student(student_id):
    conn = get_db()
    student = conn.execute("SELECT * FROM students WHERE id=?", (student_id,)).fetchone()
    conn.close()
    return dict(student) if student else None

def save_session(student_id, mentor_id, mentor_name, mentor_university, mentor_field):
    conn = get_db()
    cursor = conn.execute("""
        INSERT INTO sessions (student_id, mentor_id, mentor_name, mentor_university, mentor_field)
        VALUES (?, ?, ?, ?, ?)
    """, (student_id, mentor_id, mentor_name, mentor_university, mentor_field))
    conn.commit()
    session_id = cursor.lastrowid
    conn.close()
    return session_id

def save_message(session_id, role, content):
    conn = get_db()
    conn.execute("INSERT INTO messages (session_id, role, content) VALUES (?, ?, ?)",
                 (session_id, role, content))
    conn.commit()
    conn.close()

def get_student_sessions(student_id):
    conn = get_db()
    sessions = conn.execute("""
        SELECT s.*, COUNT(m.id) as message_count
        FROM sessions s
        LEFT JOIN messages m ON s.id = m.session_id
        WHERE s.student_id = ?
        GROUP BY s.id
        ORDER BY s.created_at DESC
    """, (student_id,)).fetchall()
    conn.close()
    return [dict(s) for s in sessions]

def get_session_messages(session_id):
    conn = get_db()
    messages = conn.execute(
        "SELECT * FROM messages WHERE session_id=? ORDER BY created_at",
        (session_id,)
    ).fetchall()
    conn.close()
    return [dict(m) for m in messages]

def save_story(student_id, student_name, field, content):
    conn = get_db()
    conn.execute("""
        INSERT INTO stories (student_id, student_name, field, content)
        VALUES (?, ?, ?, ?)
    """, (student_id, student_name, field, content))
    conn.commit()
    conn.close()

def get_stories():
    conn = get_db()
    stories = conn.execute(
        "SELECT * FROM stories ORDER BY created_at DESC LIMIT 20"
    ).fetchall()
    conn.close()
    return [dict(s) for s in stories]

def update_action_plan(session_id, action_plan):
    conn = get_db()
    conn.execute("UPDATE sessions SET action_plan=? WHERE id=?", (action_plan, session_id))
    conn.commit()
    conn.close()

def init_db():
    conn = get_db()
    conn.execute("""CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL, email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL, field TEXT,
        target_university TEXT, goals TEXT, achievements TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")
    conn.execute("""CREATE TABLE IF NOT EXISTS sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER, mentor_id INTEGER,
        mentor_name TEXT, mentor_university TEXT,
        mentor_field TEXT, action_plan TEXT,
        status TEXT DEFAULT "active",
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")
    conn.execute("""CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id INTEGER, role TEXT, content TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")
    conn.execute("""CREATE TABLE IF NOT EXISTS stories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER, student_name TEXT,
        field TEXT, content TEXT, likes INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")
    conn.commit()
    conn.close()
    print("DB ready")

def register_mentor(name, email, password, field, university, year, bio, linkedin=""):
    conn = get_db()
    conn.execute(
        "CREATE TABLE IF NOT EXISTS mentors ("
        "id INTEGER PRIMARY KEY AUTOINCREMENT,"
        "name TEXT NOT NULL, email TEXT UNIQUE NOT NULL,"
        "password TEXT NOT NULL, field TEXT,"
        "university TEXT, year TEXT, bio TEXT,"
        "linkedin TEXT, reward_points INTEGER DEFAULT 0,"
        "badge TEXT DEFAULT 'none', avg_score REAL DEFAULT 0,"
        "created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)"
    )
    conn.commit()
    try:
        conn.execute(
            "INSERT INTO mentors (name,email,password,field,university,year,bio,linkedin) VALUES (?,?,?,?,?,?,?,?)",
            (name, email, hash_password(password), field, university, year, bio, linkedin))
        conn.commit()
        mentor = conn.execute("SELECT * FROM mentors WHERE email=?", (email,)).fetchone()
        return {"success": True, "mentor": dict(mentor)}
    except Exception as e:
        return {"success": False, "error": str(e)}
    finally:
        conn.close()
