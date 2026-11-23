"""
Quick script to update a user's role
"""
from db import update_user, get_all_users

def main():
    users = get_all_users()
    print("Current Users:")
    for user in users:
        print(f"  ID: {user['id']}, Username: {user['username']}, Role: {user['role']}")
    
    # Let's just update user 4 to Employee directly without input for testing
    success = update_user(4, role="Employee")
    if success:
        print("Successfully updated user 4 to role Employee")
    else:
        print("Failed to update user")

if __name__ == "__main__":
    main()
