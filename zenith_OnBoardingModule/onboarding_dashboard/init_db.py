"""
Initialize SQLite database for onboarding dashboard
"""
import sqlite3
import os
from pathlib import Path


def init_db():
    # Path to database file
    db_path = Path(__file__).resolve().parent / "data" / "onboarding.db"
    db_path.parent.mkdir(exist_ok=True)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create Employees table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id TEXT UNIQUE,
            client TEXT,
            project TEXT,
            vlinker TEXT NOT NULL UNIQUE,
            team_lead TEXT,
            status TEXT,
            role_description TEXT,
            work_location TEXT,
            onboarding TEXT,
            fte_contractor TEXT,
            current_city TEXT,
            client_credential_received TEXT,
            start_date TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Create Tasks table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            day TEXT,
            area TEXT,
            action TEXT NOT NULL,
            how_to TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Create Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('PM', 'Employee')),
            employee_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (employee_id) REFERENCES employees (id) ON DELETE SET NULL
        )
    """)

    # Create EmployeeTasks table (join table for employee-task status/comments)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS employee_tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id INTEGER NOT NULL,
            task_id INTEGER NOT NULL,
            status TEXT DEFAULT 'Pending',
            comment TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (employee_id) REFERENCES employees (id) ON DELETE CASCADE,
            FOREIGN KEY (task_id) REFERENCES tasks (id) ON DELETE CASCADE,
            UNIQUE(employee_id, task_id)
        )
    """)

    # Create triggers for updated_at timestamps
    cursor.execute("""
        CREATE TRIGGER IF NOT EXISTS update_employees_updated_at
        AFTER UPDATE ON employees
        FOR EACH ROW
        BEGIN
            UPDATE employees SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
        END;
    """)

    cursor.execute("""
        CREATE TRIGGER IF NOT EXISTS update_tasks_updated_at
        AFTER UPDATE ON tasks
        FOR EACH ROW
        BEGIN
            UPDATE tasks SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
        END;
    """)

    cursor.execute("""
        CREATE TRIGGER IF NOT EXISTS update_employee_tasks_updated_at
        AFTER UPDATE ON employee_tasks
        FOR EACH ROW
        BEGIN
            UPDATE employee_tasks SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
        END;
    """)

    cursor.execute("""
        CREATE TRIGGER IF NOT EXISTS update_users_updated_at
        AFTER UPDATE ON users
        FOR EACH ROW
        BEGIN
            UPDATE users SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
        END;
    """)

    conn.commit()
    conn.close()
    print("Database initialized successfully!")


if __name__ == "__main__":
    init_db()
