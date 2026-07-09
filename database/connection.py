import sqlite3
import json
import logging
from config import DB_PATH
from utils.preloaded_data import (
    PERSONAL_INFO_DEFAULT,
    PRELOADED_EDUCATION,
    PRELOADED_EXPERIENCES,
    PRELOADED_PROJECTS,
    PRELOADED_SKILLS,
    PRELOADED_CERTIFICATIONS,
    PRELOADED_ACHIEVEMENTS
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("cvilization.db")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def initialize_database():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS personal_info (
        id INTEGER PRIMARY KEY,
        name TEXT,
        phone TEXT,
        email TEXT,
        college_email TEXT,
        github TEXT,
        github_link TEXT,
        linkedin TEXT,
        linkedin_link TEXT,
        portfolio TEXT,
        location TEXT,
        degree TEXT,
        branch TEXT,
        college TEXT,
        graduation_year TEXT,
        cgpa TEXT,
        roll_number TEXT,
        profile_photo TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS education (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        degree TEXT,
        institute TEXT,
        board_university TEXT,
        cgpa_percentage TEXT,
        year TEXT,
        is_selected BOOLEAN DEFAULT 1,
        sort_order INTEGER DEFAULT 0
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS experiences (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        role TEXT,
        company TEXT,
        location TEXT,
        dates TEXT,
        technologies TEXT,
        bullets TEXT,
        is_selected BOOLEAN DEFAULT 1,
        sort_order INTEGER DEFAULT 0
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS projects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        description TEXT,
        tech_stack TEXT,
        github_link TEXT,
        live_demo_link TEXT,
        duration TEXT,
        bullets TEXT,
        is_selected BOOLEAN DEFAULT 1,
        sort_order INTEGER DEFAULT 0
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS skills (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category TEXT,
        items TEXT,
        is_selected BOOLEAN DEFAULT 1,
        sort_order INTEGER DEFAULT 0
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS certifications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        date TEXT,
        issuer TEXT,
        credential_url TEXT,
        is_selected BOOLEAN DEFAULT 1,
        sort_order INTEGER DEFAULT 0
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS achievements (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category TEXT,
        description TEXT,
        is_selected BOOLEAN DEFAULT 1,
        sort_order INTEGER DEFAULT 0
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS job_descriptions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        raw_text TEXT,
        analysis_json TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        state_json TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()

    cursor.execute("SELECT COUNT(*) FROM personal_info")
    if cursor.fetchone()[0] == 0:
        cursor.execute("""
        INSERT INTO personal_info (
            id, name, phone, email, college_email, github, github_link, linkedin, linkedin_link,
            portfolio, location, degree, branch, college, graduation_year, cgpa, roll_number, profile_photo
        ) VALUES (
            1, :name, :phone, :email, :college_email, :github, :github_link, :linkedin, :linkedin_link,
            :portfolio, :location, :degree, :branch, :college, :graduation_year, :cgpa, :roll_number, :profile_photo
        )
        """, PERSONAL_INFO_DEFAULT)

    cursor.execute("SELECT COUNT(*) FROM education")
    if cursor.fetchone()[0] == 0:
        for item in PRELOADED_EDUCATION:
            cursor.execute("""
            INSERT INTO education (degree, institute, board_university, cgpa_percentage, year, is_selected, sort_order)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (item["degree"], item["institute"], item["board_university"], item["cgpa_percentage"], item["year"], item["is_selected"], item["sort_order"]))

    cursor.execute("SELECT COUNT(*) FROM experiences")
    if cursor.fetchone()[0] == 0:
        for item in PRELOADED_EXPERIENCES:
            cursor.execute("""
            INSERT INTO experiences (role, company, location, dates, technologies, bullets, is_selected, sort_order)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (item["role"], item["company"], item["location"], item["dates"], json.dumps(item["technologies"]), json.dumps(item["bullets"]), item["is_selected"], item["sort_order"]))

    cursor.execute("SELECT COUNT(*) FROM projects")
    if cursor.fetchone()[0] == 0:
        for item in PRELOADED_PROJECTS:
            cursor.execute("""
            INSERT INTO projects (title, description, tech_stack, github_link, live_demo_link, duration, bullets, is_selected, sort_order)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (item["title"], item["description"], json.dumps(item["tech_stack"]), item["github_link"], item["live_demo_link"], item["duration"], json.dumps(item["bullets"]), item["is_selected"], item["sort_order"]))

    cursor.execute("SELECT COUNT(*) FROM skills")
    if cursor.fetchone()[0] == 0:
        for item in PRELOADED_SKILLS:
            cursor.execute("""
            INSERT INTO skills (category, items, is_selected, sort_order)
            VALUES (?, ?, ?, ?)
            """, (item["category"], json.dumps(item["items"]), item["is_selected"], item["sort_order"]))

    cursor.execute("SELECT COUNT(*) FROM certifications")
    if cursor.fetchone()[0] == 0:
        for item in PRELOADED_CERTIFICATIONS:
            cursor.execute("""
            INSERT INTO certifications (name, date, issuer, credential_url, is_selected, sort_order)
            VALUES (?, ?, ?, ?, ?, ?)
            """, (item["name"], item["date"], item["issuer"], item["credential_url"], item["is_selected"], item["sort_order"]))

    cursor.execute("SELECT COUNT(*) FROM achievements")
    if cursor.fetchone()[0] == 0:
        for item in PRELOADED_ACHIEVEMENTS:
            cursor.execute("""
            INSERT INTO achievements (category, description, is_selected, sort_order)
            VALUES (?, ?, ?, ?)
            """, (item["category"], item["description"], item["is_selected"], item["sort_order"]))

    conn.commit()
    conn.close()

if __name__ == "__main__":
    initialize_database()
