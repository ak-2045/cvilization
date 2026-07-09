import sqlite3
import json
import logging
from typing import List, Dict, Any, Optional
from database.connection import get_db_connection

logger = logging.getLogger("cvilization.repository")

def get_personal_info() -> Dict[str, Any]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM personal_info WHERE id = 1")
    row = cursor.fetchone()
    conn.close()
    if row:
        return dict(row)
    return {}

def update_personal_info(data: Dict[str, Any]) -> None:
    conn = get_db_connection()
    cursor = conn.cursor()
    fields = [
        "name", "phone", "email", "college_email", "github", "github_link", "linkedin",
        "linkedin_link", "portfolio", "location", "degree", "branch", "college",
        "graduation_year", "cgpa", "roll_number", "profile_photo"
    ]
    query = "UPDATE personal_info SET " + ", ".join([f"{f} = ?" for f in fields]) + " WHERE id = 1"
    values = [data.get(f, "") for f in fields]
    cursor.execute(query, values)
    conn.commit()
    conn.close()

def _update_sort_order(table_name: str, ordered_ids: List[int]) -> None:
    conn = get_db_connection()
    cursor = conn.cursor()
    for index, item_id in enumerate(ordered_ids):
        cursor.execute(f"UPDATE {table_name} SET sort_order = ? WHERE id = ?", (index + 1, item_id))
    conn.commit()
    conn.close()

def get_education(only_selected: bool = False) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    query = "SELECT * FROM education"
    if only_selected:
        query += " WHERE is_selected = 1"
    query += " ORDER BY sort_order ASC"
    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def add_education(data: Dict[str, Any]) -> int:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT IFNULL(MAX(sort_order), 0) FROM education")
    max_order = cursor.fetchone()[0]
    cursor.execute("""
        INSERT INTO education (degree, institute, board_university, cgpa_percentage, year, is_selected, sort_order)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (data["degree"], data["institute"], data["board_university"], data["cgpa_percentage"], data["year"], data.get("is_selected", 1), max_order + 1))
    new_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return new_id

def update_education(item_id: int, data: Dict[str, Any]) -> None:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE education
        SET degree = ?, institute = ?, board_university = ?, cgpa_percentage = ?, year = ?, is_selected = ?
        WHERE id = ?
    """, (data["degree"], data["institute"], data["board_university"], data["cgpa_percentage"], data["year"], data.get("is_selected", 1), item_id))
    conn.commit()
    conn.close()

def delete_education(item_id: int) -> None:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM education WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()

def toggle_education(item_id: int, is_selected: bool) -> None:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE education SET is_selected = ? WHERE id = ?", (is_selected, item_id))
    conn.commit()
    conn.close()

def reorder_education(ordered_ids: List[int]) -> None:
    _update_sort_order("education", ordered_ids)

def get_experiences(only_selected: bool = False) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    query = "SELECT * FROM experiences"
    if only_selected:
        query += " WHERE is_selected = 1"
    query += " ORDER BY sort_order ASC"
    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()
    
    result = []
    for r in rows:
        d = dict(r)
        d["technologies"] = json.loads(d["technologies"]) if d["technologies"] else []
        d["bullets"] = json.loads(d["bullets"]) if d["bullets"] else []
        result.append(d)
    return result

def add_experience(data: Dict[str, Any]) -> int:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT IFNULL(MAX(sort_order), 0) FROM experiences")
    max_order = cursor.fetchone()[0]
    cursor.execute("""
        INSERT INTO experiences (role, company, location, dates, technologies, bullets, is_selected, sort_order)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data["role"], 
        data["company"], 
        data["location"], 
        data["dates"], 
        json.dumps(data.get("technologies", [])), 
        json.dumps(data.get("bullets", [])), 
        data.get("is_selected", 1), 
        max_order + 1
    ))
    new_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return new_id

def update_experience(item_id: int, data: Dict[str, Any]) -> None:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE experiences
        SET role = ?, company = ?, location = ?, dates = ?, technologies = ?, bullets = ?, is_selected = ?
        WHERE id = ?
    """, (
        data["role"], 
        data["company"], 
        data["location"], 
        data["dates"], 
        json.dumps(data.get("technologies", [])), 
        json.dumps(data.get("bullets", [])), 
        data.get("is_selected", 1), 
        item_id
    ))
    conn.commit()
    conn.close()

def delete_experience(item_id: int) -> None:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM experiences WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()

def toggle_experience(item_id: int, is_selected: bool) -> None:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE experiences SET is_selected = ? WHERE id = ?", (is_selected, item_id))
    conn.commit()
    conn.close()

def reorder_experiences(ordered_ids: List[int]) -> None:
    _update_sort_order("experiences", ordered_ids)

def get_projects(only_selected: bool = False) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    query = "SELECT * FROM projects"
    if only_selected:
        query += " WHERE is_selected = 1"
    query += " ORDER BY sort_order ASC"
    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()
    
    result = []
    for r in rows:
        d = dict(r)
        d["tech_stack"] = json.loads(d["tech_stack"]) if d["tech_stack"] else []
        d["bullets"] = json.loads(d["bullets"]) if d["bullets"] else []
        result.append(d)
    return result

def add_project(data: Dict[str, Any]) -> int:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT IFNULL(MAX(sort_order), 0) FROM projects")
    max_order = cursor.fetchone()[0]
    cursor.execute("""
        INSERT INTO projects (title, description, tech_stack, github_link, live_demo_link, duration, bullets, is_selected, sort_order)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data["title"], 
        data["description"], 
        json.dumps(data.get("tech_stack", [])), 
        data.get("github_link", ""), 
        data.get("live_demo_link", ""), 
        data.get("duration", ""), 
        json.dumps(data.get("bullets", [])), 
        data.get("is_selected", 1), 
        max_order + 1
    ))
    new_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return new_id

def update_project(item_id: int, data: Dict[str, Any]) -> None:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE projects
        SET title = ?, description = ?, tech_stack = ?, github_link = ?, live_demo_link = ?, duration = ?, bullets = ?, is_selected = ?
        WHERE id = ?
    """, (
        data["title"], 
        data["description"], 
        json.dumps(data.get("tech_stack", [])), 
        data.get("github_link", ""), 
        data.get("live_demo_link", ""), 
        data.get("duration", ""), 
        json.dumps(data.get("bullets", [])), 
        data.get("is_selected", 1), 
        item_id
    ))
    conn.commit()
    conn.close()

def delete_project(item_id: int) -> None:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM projects WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()

def toggle_project(item_id: int, is_selected: bool) -> None:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE projects SET is_selected = ? WHERE id = ?", (is_selected, item_id))
    conn.commit()
    conn.close()

def reorder_projects(ordered_ids: List[int]) -> None:
    _update_sort_order("projects", ordered_ids)

def get_skills(only_selected: bool = False) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    query = "SELECT * FROM skills"
    if only_selected:
        query += " WHERE is_selected = 1"
    query += " ORDER BY sort_order ASC"
    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()
    
    result = []
    for r in rows:
        d = dict(r)
        d["items"] = json.loads(d["items"]) if d["items"] else []
        result.append(d)
    return result

def add_skill(data: Dict[str, Any]) -> int:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT IFNULL(MAX(sort_order), 0) FROM skills")
    max_order = cursor.fetchone()[0]
    cursor.execute("""
        INSERT INTO skills (category, items, is_selected, sort_order)
        VALUES (?, ?, ?, ?)
    """, (data["category"], json.dumps(data.get("items", [])), data.get("is_selected", 1), max_order + 1))
    new_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return new_id

def update_skill(item_id: int, data: Dict[str, Any]) -> None:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE skills
        SET category = ?, items = ?, is_selected = ?
        WHERE id = ?
    """, (data["category"], json.dumps(data.get("items", [])), data.get("is_selected", 1), item_id))
    conn.commit()
    conn.close()

def delete_skill(item_id: int) -> None:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM skills WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()

def toggle_skill(item_id: int, is_selected: bool) -> None:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE skills SET is_selected = ? WHERE id = ?", (is_selected, item_id))
    conn.commit()
    conn.close()

def reorder_skills(ordered_ids: List[int]) -> None:
    _update_sort_order("skills", ordered_ids)

def get_certifications(only_selected: bool = False) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    query = "SELECT * FROM certifications"
    if only_selected:
        query += " WHERE is_selected = 1"
    query += " ORDER BY sort_order ASC"
    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def add_certification(data: Dict[str, Any]) -> int:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT IFNULL(MAX(sort_order), 0) FROM certifications")
    max_order = cursor.fetchone()[0]
    cursor.execute("""
        INSERT INTO certifications (name, date, issuer, credential_url, is_selected, sort_order)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (data["name"], data["date"], data["issuer"], data.get("credential_url", ""), data.get("is_selected", 1), max_order + 1))
    new_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return new_id

def update_certification(item_id: int, data: Dict[str, Any]) -> None:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE certifications
        SET name = ?, date = ?, issuer = ?, credential_url = ?, is_selected = ?
        WHERE id = ?
    """, (data["name"], data["date"], data["issuer"], data.get("credential_url", ""), data.get("is_selected", 1), item_id))
    conn.commit()
    conn.close()

def delete_certification(item_id: int) -> None:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM certifications WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()

def toggle_certification(item_id: int, is_selected: bool) -> None:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE certifications SET is_selected = ? WHERE id = ?", (is_selected, item_id))
    conn.commit()
    conn.close()

def reorder_certifications(ordered_ids: List[int]) -> None:
    _update_sort_order("certifications", ordered_ids)

def get_achievements(only_selected: bool = False) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    query = "SELECT * FROM achievements"
    if only_selected:
        query += " WHERE is_selected = 1"
    query += " ORDER BY sort_order ASC"
    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def add_achievement(data: Dict[str, Any]) -> int:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT IFNULL(MAX(sort_order), 0) FROM achievements")
    max_order = cursor.fetchone()[0]
    cursor.execute("""
        INSERT INTO achievements (category, description, is_selected, sort_order)
        VALUES (?, ?, ?, ?)
    """, (data["category"], data["description"], data.get("is_selected", 1), max_order + 1))
    new_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return new_id

def update_achievement(item_id: int, data: Dict[str, Any]) -> None:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE achievements
        SET category = ?, description = ?, is_selected = ?
        WHERE id = ?
    """, (data["category"], data["description"], data.get("is_selected", 1), item_id))
    conn.commit()
    conn.close()

def delete_achievement(item_id: int) -> None:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM achievements WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()

def toggle_achievement(item_id: int, is_selected: bool) -> None:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE achievements SET is_selected = ? WHERE id = ?", (is_selected, item_id))
    conn.commit()
    conn.close()

def reorder_achievements(ordered_ids: List[int]) -> None:
    _update_sort_order("achievements", ordered_ids)

def get_latest_job_description() -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM job_descriptions ORDER BY id DESC LIMIT 1")
    row = cursor.fetchone()
    conn.close()
    if row:
        return dict(row)
    return None

def add_job_description(title: str, raw_text: str, analysis_json: Optional[str] = None) -> int:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO job_descriptions (title, raw_text, analysis_json)
        VALUES (?, ?, ?)
    """, (title, raw_text, analysis_json))
    new_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return new_id

def get_full_resume_state() -> Dict[str, Any]:
    return {
        "personal_info": get_personal_info(),
        "education": get_education(),
        "experiences": get_experiences(),
        "projects": get_projects(),
        "skills": get_skills(),
        "certifications": get_certifications(),
        "achievements": get_achievements()
    }

def restore_full_resume_state(state: Dict[str, Any]) -> None:
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("PRAGMA foreign_keys = OFF")

    if "personal_info" in state and state["personal_info"]:
        p = state["personal_info"]
        cursor.execute("DELETE FROM personal_info")
        cursor.execute("""
        INSERT INTO personal_info (
            id, name, phone, email, college_email, github, github_link, linkedin, linkedin_link,
            portfolio, location, degree, branch, college, graduation_year, cgpa, roll_number, profile_photo
        ) VALUES (
            1, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
        )
        """, (
            p.get("name", ""), p.get("phone", ""), p.get("email", ""), p.get("college_email", ""),
            p.get("github", ""), p.get("github_link", ""), p.get("linkedin", ""), p.get("linkedin_link", ""),
            p.get("portfolio", ""), p.get("location", ""), p.get("degree", ""), p.get("branch", ""),
            p.get("college", ""), p.get("graduation_year", ""), p.get("cgpa", ""), p.get("roll_number", ""),
            p.get("profile_photo", "")
        ))

    if "education" in state:
        cursor.execute("DELETE FROM education")
        for item in state["education"]:
            cursor.execute("""
            INSERT INTO education (id, degree, institute, board_university, cgpa_percentage, year, is_selected, sort_order)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (item.get("id"), item["degree"], item["institute"], item["board_university"], item["cgpa_percentage"], item["year"], item.get("is_selected", 1), item.get("sort_order", 0)))

    if "experiences" in state:
        cursor.execute("DELETE FROM experiences")
        for item in state["experiences"]:
            cursor.execute("""
            INSERT INTO experiences (id, role, company, location, dates, technologies, bullets, is_selected, sort_order)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                item.get("id"),
                item["role"],
                item["company"],
                item["location"],
                item["dates"],
                json.dumps(item.get("technologies", [])),
                json.dumps(item.get("bullets", [])),
                item.get("is_selected", 1),
                item.get("sort_order", 0)
            ))

    if "projects" in state:
        cursor.execute("DELETE FROM projects")
        for item in state["projects"]:
            cursor.execute("""
            INSERT INTO projects (id, title, description, tech_stack, github_link, live_demo_link, duration, bullets, is_selected, sort_order)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                item.get("id"),
                item["title"],
                item["description"],
                json.dumps(item.get("tech_stack", [])),
                item.get("github_link", ""),
                item.get("live_demo_link", ""),
                item.get("duration", ""),
                json.dumps(item.get("bullets", [])),
                item.get("is_selected", 1),
                item.get("sort_order", 0)
            ))

    if "skills" in state:
        cursor.execute("DELETE FROM skills")
        for item in state["skills"]:
            cursor.execute("""
            INSERT INTO skills (id, category, items, is_selected, sort_order)
            VALUES (?, ?, ?, ?, ?)
            """, (
                item.get("id"),
                item["category"],
                json.dumps(item.get("items", [])),
                item.get("is_selected", 1),
                item.get("sort_order", 0)
            ))

    if "certifications" in state:
        cursor.execute("DELETE FROM certifications")
        for item in state["certifications"]:
            cursor.execute("""
            INSERT INTO certifications (id, name, date, issuer, credential_url, is_selected, sort_order)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                item.get("id"),
                item["name"],
                item["date"],
                item["issuer"],
                item.get("credential_url", ""),
                item.get("is_selected", 1),
                item.get("sort_order", 0)
            ))

    if "achievements" in state:
        cursor.execute("DELETE FROM achievements")
        for item in state["achievements"]:
            cursor.execute("""
            INSERT INTO achievements (id, category, description, is_selected, sort_order)
            VALUES (?, ?, ?, ?, ?)
            """, (
                item.get("id"),
                item["category"],
                item["description"],
                item.get("is_selected", 1),
                item.get("sort_order", 0)
            ))

    conn.commit()
    conn.close()

def save_to_history(state: Dict[str, Any]) -> None:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO history (state_json) VALUES (?)", (json.dumps(state),))
    cursor.execute("SELECT id FROM history ORDER BY id DESC")
    history_ids = [row[0] for row in cursor.fetchall()]
    if len(history_ids) > 50:
        ids_to_delete = history_ids[50:]
        cursor.execute(f"DELETE FROM history WHERE id IN ({','.join(['?']*len(ids_to_delete))})", ids_to_delete)
    conn.commit()
    conn.close()

def get_history_states() -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT state_json FROM history ORDER BY id ASC")
    rows = cursor.fetchall()
    conn.close()
    return [json.loads(row[0]) for row in rows]

def clear_history() -> None:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM history")
    conn.commit()
    conn.close()
