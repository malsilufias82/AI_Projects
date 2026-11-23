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


DB_PATH = Path(__file__).resolve().parent / "data" / "onboarding.db"


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

    init_db()

    def clean_value(value):
        if pd.isna(value):
            return None
        if hasattr(value, "strftime"):
            return value.strftime("%Y-%m-%d")
        value = str(value).strip()
        return value or None

    def merge_values(*values):
        merged = []
        for value in values:
            if value is None:
                continue
            for item in str(value).split("; "):
                item = item.strip()
                if item and item not in merged:
                    merged.append(item)
        return "; ".join(merged) or None

    # Read Resource List
    xl = pd.ExcelFile(excel_path)
    df_resources = pd.read_excel(xl, "Resource List", header=1)
    df_resources = df_resources.dropna(how="all")
    resource_columns = {
        str(column).strip().casefold(): column
        for column in df_resources.columns
    }

    def resource_value(row, column):
        actual_column = resource_columns.get(column.strip().casefold())
        return clean_value(row.get(actual_column)) if actual_column is not None else None

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

    existing_tasks = {
        (task["day"], task["area"], task["action"], task["how_to"])
        for task in get_all_tasks()
    }
    inserted_tasks = 0
    for task_data in tasks:
        task_key = tuple(task_data[field] for field in ("day", "area", "action", "how_to"))
        if task_key in existing_tasks:
            continue
        add_task(task_data)
        existing_tasks.add(task_key)
        inserted_tasks += 1

    # Merge duplicate workbook rows by VLinker and retain distinct assignments.
    employees_by_vlinker = {}
    employee_cols = {}
    for col_idx in range(9, ws_phase1.max_column + 1):
        vlinker = ws_phase1.cell(row=2, column=col_idx).value
        if vlinker:
            vlinker = str(vlinker).strip()
            employee_cols[vlinker] = col_idx

    vlinker_col = next(
        (
            col for col in df_resources.columns
            if "vlinker" in str(col).lower() or "name" in str(col).lower()
        ),
        None,
    )
    if vlinker_col is None:
        raise ValueError("Resource List does not contain a VLinker/name column")

    for _, row in df_resources.iterrows():
        vlinker = clean_value(row[vlinker_col])
        if not vlinker:
            continue
        start_date = None
        if vlinker in employee_cols:
            start_date = ws_phase1.cell(row=3, column=employee_cols[vlinker]).value

        employee_data = {
            "employee_id": resource_value(row, "Employee ID"),
            "client": resource_value(row, "Client"),
            "project": resource_value(row, "Project"),
            "vlinker": vlinker,
            "team_lead": resource_value(row, "Team Lead"),
            "status": resource_value(row, "Status"),
            "role_description": resource_value(row, "Role Description"),
            "work_location": resource_value(row, "Work Location"),
            "onboarding": resource_value(row, "Onboarding"),
            "fte_contractor": resource_value(row, "FTE/Contractor"),
            "current_city": resource_value(row, "Current City"),
            "client_credential_received": resource_value(row, "Client Credential Received"),
            "start_date": clean_value(start_date),
        }
        key = vlinker.casefold()
        if key not in employees_by_vlinker:
            employees_by_vlinker[key] = employee_data
            continue
        current = employees_by_vlinker[key]
        for field, value in employee_data.items():
            if field == "vlinker":
                continue
            current[field] = merge_values(current.get(field), value)

    existing_employees = {
        str(employee["vlinker"]).strip().casefold(): employee
        for employee in get_all_employees()
        if employee["vlinker"]
    }
    inserted_employees = 0
    updated_employees = 0
    assignment_fields = {"client", "project", "team_lead"}
    for key, employee_data in employees_by_vlinker.items():
        existing = existing_employees.get(key)
        if existing is None:
            add_employee(employee_data)
            inserted_employees += 1
            continue

        merged_data = dict(employee_data)
        changed = False
        for field, incoming in employee_data.items():
            stored = existing[field]
            if field in assignment_fields:
                merged_data[field] = merge_values(stored, incoming)
            elif stored:
                merged_data[field] = stored
            if merged_data[field] != stored:
                changed = True
        if changed:
            update_employee(existing["id"], merged_data)
            updated_employees += 1

    print(
        "Import merge complete: "
        f"{inserted_employees} employees added, "
        f"{updated_employees} existing employees enriched, "
        f"{inserted_tasks} tasks added; "
        f"{len(employees_by_vlinker) - inserted_employees} employees and "
        f"{len(tasks) - inserted_tasks} tasks already present."
    )


if __name__ == "__main__":
    init_db()
