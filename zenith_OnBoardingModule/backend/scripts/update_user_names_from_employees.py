"""
Script to update user first_name and last_name from employee full_name.

This script reads employees from MongoDB, splits their full_name into first_name
and last_name, and updates the corresponding user records.
"""

from pymongo import MongoClient
from bson import ObjectId

# Connect to MongoDB
client = MongoClient('localhost', 27017)
db = client['zenith']

# Get collections
employees_collection = db['employees']
users_collection = db['users']

# Get all employees
employees = employees_collection.find({'full_name': {'$ne': None, '$ne': ''}})

updated_count = 0
skipped_count = 0
error_count = 0

print("Starting user name update from employees...")

for employee in employees:
    try:
        full_name = employee.get('full_name')
        user_id = employee.get('user_id')
        
        if not full_name or not user_id:
            skipped_count += 1
            continue
        
        # Split full_name based on space
        # If multiple spaces, last item is last_name, everything before is first_name
        name_parts = full_name.strip().split()
        
        if len(name_parts) == 0:
            skipped_count += 1
            continue
        elif len(name_parts) == 1:
            first_name = name_parts[0]
            last_name = ""
        else:
            first_name = " ".join(name_parts[:-1])
            last_name = name_parts[-1]
        
        # Find and update the user
        result = users_collection.update_one(
            {'_id': ObjectId(user_id)},
            {
                '$set': {
                    'first_name': first_name,
                    'last_name': last_name
                }
            }
        )
        
        if result.modified_count > 0:
            updated_count += 1
            print(f"Updated user {user_id}: {first_name} {last_name}")
        else:
            skipped_count += 1
            print(f"Skipped user {user_id} (not found or no change)")
            
    except Exception as e:
        error_count += 1
        print(f"Error processing employee {employee.get('_id')}: {e}")

print(f"\nSummary:")
print(f"Updated: {updated_count}")
print(f"Skipped: {skipped_count}")
print(f"Errors: {error_count}")
print("Done!")
