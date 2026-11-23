"""
Create a default PM user (admin/admin)
"""
from db import register_user, get_user_by_username, get_db_connection


def main():
    username = "admin"
    password = "admin"
    role = "PM"

    # Delete existing admin user if present
    conn = get_db_connection()
    conn.execute("DELETE FROM users WHERE username = ?", (username,))
    conn.commit()
    conn.close()

    user_id = register_user(username, password, role)
    if user_id:
        print(f"Default PM user created successfully!")
        print(f"Username: {username}")
        print(f"Password: {password}")
        print("IMPORTANT: Change this password immediately after logging in!")
    else:
        print("Failed to create user!")


if __name__ == "__main__":
    main()
