"""
Create an employee user
"""
from db import register_user, get_employee_by_vlinker, get_user_by_username


def main():
    print("Create Employee User")
    print("-" * 30)
    
    username = input("Enter username: ").strip()
    password = input("Enter password: ").strip()
    vlinker = input("Enter employee VLinker name (from Excel): ").strip()
    
    # Check if username exists
    if get_user_by_username(username):
        print(f"Error: Username '{username}' already exists!")
        return
    
    # Find employee by vlinker
    emp = get_employee_by_vlinker(vlinker)
    employee_id = emp['id'] if emp else None
    if not employee_id:
        print(f"Warning: No employee found with VLinker '{vlinker}'. User will not be linked to an employee.")
    
    # Create user
    user_id = register_user(username, password, 'Employee', employee_id)
    if user_id:
        print(f"\nEmployee user created successfully!")
        print(f"Username: {username}")
        print(f"Password: {password}")
        print("IMPORTANT: Change this password immediately after logging in!")
    else:
        print("Failed to create user!")


if __name__ == "__main__":
    main()
