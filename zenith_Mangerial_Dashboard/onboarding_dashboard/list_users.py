"""
List all users in the database
"""
from db import get_all_users, get_db_connection, check_password_hash


def main():
    print("All Users:")
    print("-" * 50)
    users = get_all_users()
    if not users:
        print("No users found!")
        return
    for user in users:
        print(f"ID: {user['id']}")
        print(f"Username: {user['username']}")
        print(f"Role: {user['role']}")
        print(f"Employee ID: {user['employee_id']}")
        print(f"Password Hash: {user['password_hash']}")
        
        # Test password check
        test_pw = "admin"
        is_valid = check_password_hash(user['password_hash'], test_pw)
        print(f"Password '{test_pw}' valid? {is_valid}")
        print("-" * 30)


if __name__ == "__main__":
    main()
