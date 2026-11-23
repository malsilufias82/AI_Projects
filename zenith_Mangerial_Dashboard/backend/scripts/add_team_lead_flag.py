"""
Script to add is_team_lead flag to user table.

This script reads employees from MongoDB, identifies all unique team leads,
and updates the corresponding user records with is_team_lead flag.
Users who are not team leads will have is_team_lead set to false.

Usage:
    python add_team_lead_flag.py <mongodb_uri>

Example:
    python add_team_lead_flag.py "mongodb://localhost:27017"
"""

import sys
import os
from pymongo import MongoClient
from bson import ObjectId

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017')
db = client['zenith']

# Get collections
employees_collection = db['employees']
users_collection = db['users']

# Get all employees who report to Nivedita (these are the team leads)
team_lead_employees = employees_collection.find({
    'team_lead': {'$eq': 'Nivedita Sachdev'},
    # 'user_id': {'$ne': None, '$ne': ''}
})
team_lead_employees = list(team_lead_employees)
print(len(team_lead_employees))
print("Finding team leads (employees who report to Nivedita Sachdev)...")
print(team_lead_employees[:2])
# Create a set of team lead user IDs
team_lead_user_ids = set()

for employee in team_lead_employees:
    user_id = employee.get('user_id')
    full_name = employee.get('full_name')
    if user_id:
        team_lead_user_ids.add(user_id)
        print(f"Team lead: {full_name} -> User ID: {user_id}")

print(f"\nFound {len(team_lead_user_ids)} team leads")

updated_count = 0
set_to_false_count = 0
skipped_count = 0
error_count = 0

print("\nStarting is_team_lead flag update...")

# Get all users
users = users_collection.find({})
print(list(team_lead_user_ids)[:5])
for user in users:
    try:
        user_id_str = str(user.get('_id'))
        print(user_id_str in team_lead_user_ids)
        # exit()
        if user_id_str in team_lead_user_ids:
            print(user_id_str)
            # Set is_team_lead to true
            result = users_collection.update_one(
                {'_id': ObjectId(user_id_str)},
                {'$set': {'is_team_lead': True}}
            )
            
            if result.modified_count > 0:
                updated_count += 1
                print(f"Set is_team_lead=True for user {user_id_str}")
        else:
            # Set is_team_lead to false
            result = users_collection.update_one(
                {'_id': ObjectId(user_id_str)},
                {'$set': {'is_team_lead': False}}
            )
            
            set_to_false_count += 1
            print(f"Set is_team_lead=False for user {user_id_str}")

                
    except Exception as e:
        error_count += 1
        print(f"Error processing user {user.get('_id')}: {e}")

print(f"\nSummary:")
print(f"Set is_team_lead=True: {updated_count}")
print(f"Set is_team_lead=False: {set_to_false_count}")
print(f"Skipped (already set): {skipped_count}")
print(f"Errors: {error_count}")
print("Done!")
