"""Simple SQLite database for local Quizify."""
import sqlite3
import json
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).parent / 'quizify.db'


def init_db():
    """Initialize the database with required tables."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Uploads table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS uploads (
            upload_id TEXT PRIMARY KEY,
            filename TEXT NOT NULL,
            status TEXT NOT NULL,
            topic TEXT,
            error_message TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    ''')

    # Questions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS questions (
            question_id INTEGER PRIMARY KEY AUTOINCREMENT,
            upload_id TEXT NOT NULL,
            type TEXT NOT NULL,
            topic TEXT,
            question TEXT NOT NULL,
            options TEXT,
            correct_answer TEXT,
            explanation TEXT,
            expected_points TEXT,
            difficulty TEXT,
            filename TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY (upload_id) REFERENCES uploads(upload_id)
        )
    ''')

    conn.commit()
    conn.close()


def save_upload(upload_id, filename, status='processing'):
    """Save upload metadata."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    now = datetime.utcnow().isoformat()

    cursor.execute('''
        INSERT INTO uploads (upload_id, filename, status, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?)
    ''', (upload_id, filename, status, now, now))

    conn.commit()
    conn.close()


def update_upload_status(upload_id, status, topic=None, error=None):
    """Update upload status."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    now = datetime.utcnow().isoformat()

    if topic and error:
        cursor.execute('''
            UPDATE uploads SET status=?, topic=?, error_message=?, updated_at=?
            WHERE upload_id=?
        ''', (status, topic, error, now, upload_id))
    elif topic:
        cursor.execute('''
            UPDATE uploads SET status=?, topic=?, updated_at=?
            WHERE upload_id=?
        ''', (status, topic, now, upload_id))
    elif error:
        cursor.execute('''
            UPDATE uploads SET status=?, error_message=?, updated_at=?
            WHERE upload_id=?
        ''', (status, error, now, upload_id))
    else:
        cursor.execute('''
            UPDATE uploads SET status=?, updated_at=?
            WHERE upload_id=?
        ''', (status, now, upload_id))

    conn.commit()
    conn.close()


def save_questions(upload_id, filename, questions_data):
    """Save generated questions."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    now = datetime.utcnow().isoformat()
    topic = questions_data.get('topic', 'General')

    # Save MCQs
    for mcq in questions_data.get('mcqs', []):
        cursor.execute('''
            INSERT INTO questions (upload_id, type, topic, question, options,
                                 correct_answer, explanation, filename, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            upload_id, 'MCQ', topic, mcq['question'],
            json.dumps(mcq.get('options', [])),
            mcq.get('correct_answer', ''),
            mcq.get('explanation', ''),
            filename, now
        ))

    # Save short questions
    for sq in questions_data.get('short_questions', []):
        cursor.execute('''
            INSERT INTO questions (upload_id, type, topic, question,
                                 expected_points, difficulty, filename, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            upload_id, 'SHORT', topic, sq['question'],
            json.dumps(sq.get('expected_points', [])),
            sq.get('difficulty', 'medium'),
            filename, now
        ))

    conn.commit()
    conn.close()


def get_upload_by_id(upload_id):
    """Get upload metadata."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM uploads WHERE upload_id=?', (upload_id,))
    row = cursor.fetchone()
    conn.close()

    return dict(row) if row else None


def get_questions_by_upload_id(upload_id):
    """Get all questions for an upload."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM questions WHERE upload_id=? ORDER BY question_id', (upload_id,))
    rows = cursor.fetchall()
    conn.close()

    questions = []
    for row in rows:
        q = dict(row)
        # Parse JSON fields
        if q.get('options'):
            q['options'] = json.loads(q['options'])
        if q.get('expected_points'):
            q['expected_points'] = json.loads(q['expected_points'])
        questions.append(q)

    return questions


def list_uploads(limit=50):
    """List recent uploads."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM uploads ORDER BY created_at DESC LIMIT ?', (limit,))
    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]


# Initialize database on import
init_db()
