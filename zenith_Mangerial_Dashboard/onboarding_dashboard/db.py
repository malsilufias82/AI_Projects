"""
Database utility functions
"""
import sqlite3
import hashlib
import secrets
from pathlib import Path
from init_db import init_db

# Always use built-in hashlib for consistency, even if werkzeug is available
print("Using built-in hashlib for password hashing")

def generate_password_hash(password):
    salt = secrets.token_hex(16)
    hash_obj = hashlib.sha256((password + salt).encode('utf-8'))
    return f"$sha256${salt}${hash_obj.hexdigest()}"

def check_password_hash(stored_hash, password):
    if not stored_hash or not password:
        return False
    if stored_hash.startswith('$sha256$'):
        parts = stored_hash.split('$')
        if len(parts) != 4:
            return False
        salt = parts[2]
        stored_hex = parts[3]
        computed_hash = hashlib.sha256((password + salt).encode('utf-8')).hexdigest()
        return computed_hash == stored_hex
    else:
        # Handle werkzeug-style hashes just in case (we'll recreate users anyway)
        return False


DB_PATH = Path("data/onboarding.db")


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# ------------------------------
# Employee operations
# ------------------------------
def get_all_employees():
    conn = get_db_connection()
    employees = conn.execute("SELECT * FROM employees ORDER BY vlinker").fetchall()
    conn.close()
    return employees


def get_employee_by_id(employee_id):
    conn = get_db_connection()
    employee = conn.execute("SELECT * FROM employees WHERE id = ?", (employee_id,)).fetchone()
    conn.close()
    return employee


def get_employee_by_vlinker(vlinker):
    conn = get_db_connection()
    employee = conn.execute("SELECT * FROM employees WHERE vlinker = ?", (vlinker,)).fetchone()
    conn.close()
    return employee


def add_employee(employee_data):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO employees (
            employee_id, client, project, vlinker, team_lead, status,
            role_description, work_location, onboarding, fte_contractor,
            current_city, client_credential_received, start_date
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        employee_data.get("employee_id"),
        employee_data.get("client"),
        employee_data.get("project"),
        employee_data.get("vlinker"),
        employee_data.get("team_lead"),
        employee_data.get("status"),
        employee_data.get("role_description"),
        employee_data.get("work_location"),
        employee_data.get("onboarding"),
        employee_data.get("fte_contractor"),
        employee_data.get("current_city"),
        employee_data.get("client_credential_received"),
        employee_data.get("start_date")
    ))
    employee_id = cursor.lastrowid
    conn.commit()
    
    # Assign all existing tasks to new employee with default status
    all_tasks = get_all_tasks()
    for task in all_tasks:
        add_employee_task(employee_id, task["id"])
    
    conn.close()
    return employee_id


def update_employee(employee_id, employee_data):
    conn = get_db_connection()
    conn.execute("""
        UPDATE employees
        SET employee_id = ?, client = ?, project = ?, vlinker = ?, team_lead = ?, status = ?,
            role_description = ?, work_location = ?, onboarding = ?, fte_contractor = ?,
            current_city = ?, client_credential_received = ?, start_date = ?
        WHERE id = ?
    """, (
        employee_data.get("employee_id"),
        employee_data.get("client"),
        employee_data.get("project"),
        employee_data.get("vlinker"),
        employee_data.get("team_lead"),
        employee_data.get("status"),
        employee_data.get("role_description"),
        employee_data.get("work_location"),
        employee_data.get("onboarding"),
        employee_data.get("fte_contractor"),
        employee_data.get("current_city"),
        employee_data.get("client_credential_received"),
        employee_data.get("start_date"),
        employee_id
    ))
    conn.commit()
    conn.close()


# ------------------------------
# Task operations
# ------------------------------
def get_all_tasks():
    conn = get_db_connection()
    tasks = conn.execute("SELECT * FROM tasks ORDER BY id").fetchall()
    conn.close()
    return tasks


def get_task_by_id(task_id):
    conn = get_db_connection()
    task = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    conn.close()
    return task


def add_task(task_data):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO tasks (day, area, action, how_to)
        VALUES (?, ?, ?, ?)
    """, (
        task_data.get("day"),
        task_data.get("area"),
        task_data.get("action"),
        task_data.get("how_to")
    ))
    task_id = cursor.lastrowid
    conn.commit()
    
    # Assign new task to all existing employees with default status
    all_employees = get_all_employees()
    for emp in all_employees:
        add_employee_task(emp["id"], task_id)
    
    conn.close()
    return task_id


def update_task(task_id, task_data):
    conn = get_db_connection()
    conn.execute("""
        UPDATE tasks
        SET day = ?, area = ?, action = ?, how_to = ?
        WHERE id = ?
    """, (
        task_data.get("day"),
        task_data.get("area"),
        task_data.get("action"),
        task_data.get("how_to"),
        task_id
    ))
    conn.commit()
    conn.close()


# ------------------------------
# EmployeeTask operations
# ------------------------------
def get_employee_tasks(employee_id):
    conn = get_db_connection()
    employee_tasks = conn.execute("""
        SELECT et.*, t.day, t.area, t.action, t.how_to
        FROM employee_tasks et
        JOIN tasks t ON et.task_id = t.id
        WHERE et.employee_id = ?
        ORDER BY t.id
    """, (employee_id,)).fetchall()
    conn.close()
    return employee_tasks


def get_all_employee_tasks():
    conn = get_db_connection()
    employee_tasks = conn.execute("""
        SELECT et.*, e.vlinker, t.day, t.area, t.action, t.how_to
        FROM employee_tasks et
        JOIN employees e ON et.employee_id = e.id
        JOIN tasks t ON et.task_id = t.id
        ORDER BY e.id, t.id
    """).fetchall()
    conn.close()
    return employee_tasks


def add_employee_task(employee_id, task_id, status="Pending", comment=""):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO employee_tasks (employee_id, task_id, status, comment)
            VALUES (?, ?, ?, ?)
        """, (employee_id, task_id, status, comment))
        conn.commit()
    except sqlite3.IntegrityError:
        # Task already assigned, skip
        pass
    finally:
        conn.close()


def update_employee_task(employee_id, task_id, status=None, comment=None):
    conn = get_db_connection()
    if status is not None and comment is not None:
        conn.execute("""
            UPDATE employee_tasks
            SET status = ?, comment = ?
            WHERE employee_id = ? AND task_id = ?
        """, (status, comment, employee_id, task_id))
    elif status is not None:
        conn.execute("""
            UPDATE employee_tasks
            SET status = ?
            WHERE employee_id = ? AND task_id = ?
        """, (status, employee_id, task_id))
    elif comment is not None:
        conn.execute("""
            UPDATE employee_tasks
            SET comment = ?
            WHERE employee_id = ? AND task_id = ?
        """, (comment, employee_id, task_id))
    conn.commit()
    conn.close()


# ------------------------------
# User operations
# ------------------------------
def get_user_by_id(user_id):
    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    conn.close()
    return user


def get_user_by_username(username):
    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    conn.close()
    return user


def get_all_users():
    conn = get_db_connection()
    users = conn.execute("SELECT * FROM users ORDER BY username").fetchall()
    conn.close()
    return users


def register_user(username, password, role, employee_id=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        password_hash = generate_password_hash(password)
        cursor.execute("""
            INSERT INTO users (username, password_hash, role, employee_id)
            VALUES (?, ?, ?, ?)
        """, (username, password_hash, role, employee_id))
        user_id = cursor.lastrowid
        conn.commit()
        return user_id
    except sqlite3.IntegrityError:
        return None  # Username already exists
    finally:
        conn.close()


def authenticate_user(username, password):
    user = get_user_by_username(username)
    if user and check_password_hash(user["password_hash"], password):
        return user
    return None


def update_user(user_id, username=None, password=None, role=None, employee_id=None):
    conn = get_db_connection()
    user = get_user_by_id(user_id)
    if not user:
        conn.close()
        return False

    updates = []
    params = []
    if username:
        updates.append("username = ?")
        params.append(username)
    if password:
        password_hash = generate_password_hash(password)
        updates.append("password_hash = ?")
        params.append(password_hash)
    if role:
        updates.append("role = ?")
        params.append(role)
    if employee_id is not None:
        updates.append("employee_id = ?")
        params.append(employee_id)

    if updates:
        params.append(user_id)
        conn.execute(f"UPDATE users SET {', '.join(updates)} WHERE id = ?", params)
        conn.commit()
        conn.close()
        return True
    conn.close()
    return False


# ------------------------------
# Helper: Import from existing Excel file (optional)
# ------------------------------
def import_from_excel(excel_path):
    import pandas as pd
    from openpyxl import load_workbook

    # Read Resource List
    xl = pd.ExcelFile(excel_path)
    df_resources = pd.read_excel(xl, "Resource List", header=1)
    df_resources = df_resources.dropna(how="all")

    # Read Phase1 - Machine Setup for tasks and employee start dates
    wb = load_workbook(excel_path, data_only=True)
    ws_phase1 = wb["Phase1 - Machine Setup"]

    # Import tasks
    tasks = []
    for row_idx in range(6, ws_phase1.max_row + 1):
        day = ws_phase1.cell(row=row_idx, column=2).value
        area = ws_phase1.cell(row=row_idx, column=3).value
        action = ws_phase1.cell(row=row_idx, column=4).value
        how_to = ws_phase1.cell(row=row_idx, column=5).value
        if action:
            tasks.append({"day": day, "area": area, "action": action, "how_to": how_to})

    for task_data in tasks:
        add_task(task_data)

    # Import employees and their start dates
    employees = []
    employee_cols = {}
    for col_idx in range(9, ws_phase1.max_column + 1):
        vlinker = ws_phase1.cell(row=2, column=col_idx).value
        if vlinker:
            vlinker = str(vlinker).strip()
            employee_cols[vlinker] = col_idx

    for _, row in df_resources.iterrows():
        vlinker_col = None
        for col in df_resources.columns:
            if "vlinker" in str(col).lower() or "name" in str(col).lower():
                vlinker_col = col
                break
        if not vlinker_col or pd.isna(row[vlinker_col]):
            continue

        vlinker = str(row[vlinker_col]).strip()
        start_date = None
        if vlinker in employee_cols:
            start_date = ws_phase1.cell(row=3, column=employee_cols[vlinker]).value

        employee_data = {
            "employee_id": str(row.get("Employee ID", "")) if pd.notna(row.get("Employee ID")) else None,
            "client": str(row.get("Client", "")) if pd.notna(row.get("Client")) else None,
            "project": str(row.get("Project", "")) if pd.notna(row.get("Project")) else None,
            "vlinker": vlinker,
            "team_lead": str(row.get("Team Lead", "")) if pd.notna(row.get("Team Lead")) else None,
            "status": str(row.get("Status", "")) if pd.notna(row.get("Status")) else None,
            "role_description": str(row.get("Role Description", "")) if pd.notna(row.get("Role Description")) else None,
            "work_location": str(row.get("Work Location", "")) if pd.notna(row.get("Work Location")) else None,
            "onboarding": str(row.get("Onboarding", "")) if pd.notna(row.get("Onboarding")) else None,
            "fte_contractor": str(row.get("FTE/Contractor", "")) if pd.notna(row.get("FTE/Contractor")) else None,
            "current_city": str(row.get("Current City", "")) if pd.notna(row.get("Current City")) else None,
            "client_credential_received": str(row.get("Client Credential Received", "")) if pd.notna(row.get("Client Credential Received")) else None,
            "start_date": str(start_date) if start_date is not None else None
        }
        employees.append(employee_data)

    for emp_data in employees:
        add_employee(emp_data)

    print(f"Successfully imported {len(employees)} employees and {len(tasks)} tasks!")


if __name__ == "__main__":
    init_db()
