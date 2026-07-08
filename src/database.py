"""
database.py
-----------
Lightweight SQLite persistence layer. Stores every resume/JD upload and its
computed match score so multiple uploads and historical comparisons are
supported, as claimed on the resume ("Stored resume data in a SQL database
to support multiple uploads and deliver real-time skill-gap analysis").
"""

import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "resume_analyzer.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS analyses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            candidate_name TEXT,
            resume_filename TEXT,
            jd_title TEXT,
            match_score REAL,
            matched_skills TEXT,
            missing_skills TEXT,
            created_at TEXT
        )
        """
    )
    conn.commit()
    conn.close()


def save_analysis(candidate_name, resume_filename, jd_title, match_score,
                   matched_skills, missing_skills):
    conn = get_connection()
    conn.execute(
        """
        INSERT INTO analyses
        (candidate_name, resume_filename, jd_title, match_score,
         matched_skills, missing_skills, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            candidate_name,
            resume_filename,
            jd_title,
            match_score,
            ", ".join(matched_skills),
            ", ".join(missing_skills),
            datetime.utcnow().isoformat(),
        ),
    )
    conn.commit()
    conn.close()


def get_all_analyses():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM analyses ORDER BY created_at DESC").fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_analyses_for_jd(jd_title: str):
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM analyses WHERE jd_title = ? ORDER BY match_score DESC",
        (jd_title,),
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]
