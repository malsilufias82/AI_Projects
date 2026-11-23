import os
import sys
from datetime import datetime
from pymongo import MongoClient

# MongoDB connection
MONGODB_URI = os.getenv('MONGODB_URL', 'mongodb://localhost:27017')
MONGODB_DB = os.getenv('MONGODB_DATABASE', 'zenith')


def extract_pocs(employee):
    """Extract POC details from the blk_manager hierarchy in employee data."""
    pocs = []
    manager_fields = [
        ('blk_manager', 'Manager'),
        ('blk_manager_level_2', 'Manager Level 2'),
        ('blk_manager_level_3', 'Manager Level 3'),
        ('blk_manager_level_4', 'Manager Level 4'),
        ('blk_manager_level_5', 'Manager Level 5'),
    ]
    
    for field, role in manager_fields:
        name = employee.get(field)
        if name and isinstance(name, str) and name.strip():
            # Avoid duplicates
            if not any(poc['name'] == name.strip() for poc in pocs):
                pocs.append({
                    'name': name.strip(),
                    'email': None,
                    'phone': None,
                    'role': role
                })
    
    return pocs


def get_unique_clients(employees):
    """Extract unique clients from employee records."""
    clients = {}
    for employee in employees:
        client_name = employee.get('client')
        if not client_name or client_name in clients:
            continue
        
        pocs = extract_pocs(employee)
        clients[client_name] = {
            'name': client_name,
            'contact_persons': pocs,
            'address': employee.get('work_location', ''),
            'status': 'active',
            'description': f'Client created from employee data',
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
            'deleted_at': None
        }
    
    return clients


def get_unique_projects(employees, client_map):
    """Extract unique projects from employee records, linked to clients."""
    projects = {}
    
    for employee in employees:
        project_name = employee.get('project')
        client_name = employee.get('client')
        
        if not project_name or not client_name:
            continue
        
        # Skip if client doesn't exist in our map
        if client_name not in client_map:
            continue
        
        project_key = (client_name, project_name)
        if project_key in projects:
            continue
        
        client_id = client_map[client_name]
        pocs = extract_pocs(employee)
        
        # Convert billing_start_date timestamp to YYYY-MM-DD if available
        start_date = ''
        billing_start = employee.get('billing_start_date')
        if billing_start:
            try:
                start_date = datetime.fromtimestamp(int(billing_start) / 1000).strftime('%Y-%m-%d')
            except (ValueError, TypeError):
                pass
        
        # Use team_lead from employee data
        team_lead = employee.get('team_lead', '')
        if not team_lead:
            team_lead = employee.get('blk_team_sub_project', '')
        
        projects[project_key] = {
            'name': project_name,
            'client_id': client_id,
            'pocs': pocs,
            'description': f'Project: {project_name} for {client_name}',
            'status': 'active',
            'start_date': start_date,
            'end_date': '',
            'team_lead': team_lead,
            'pillar': employee.get('pillar', ''),
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
            'deleted_at': None
        }
    
    return projects


def seed_from_employees():
    """Seed clients and projects collections from employee data."""
    client = MongoClient(MONGODB_URI)
    db = client[MONGODB_DB]
    employees_collection = db['employees']
    clients_collection = db['clients']
    projects_collection = db['projects']
    
    # Fetch all active employees
    employees = list(employees_collection.find({'is_deleted': {'$ne': True}}))
    print(f"Found {len(employees)} employees")
    
    if not employees:
        print("No employees found. Exiting.")
        return
    
    # Get unique clients
    client_docs = get_unique_clients(employees)
    print(f"Found {len(client_docs)} unique clients")
    
    # Insert clients and build name-to-id mapping
    client_map = {}
    if client_docs:
        # Remove existing clients with same names
        client_names = list(client_docs.keys())
        existing_clients = clients_collection.find({'name': {'$in': client_names}})
        for existing in existing_clients:
            client_map[existing['name']] = str(existing['_id'])
        
        # Filter out existing clients
        new_client_docs = {name: doc for name, doc in client_docs.items() if name not in client_map}
        
        if new_client_docs:
            result = clients_collection.insert_many(list(new_client_docs.values()))
            for idx, inserted_id in enumerate(result.inserted_ids):
                client_name = list(new_client_docs.keys())[idx]
                client_map[client_name] = str(inserted_id)
            print(f"Inserted {len(result.inserted_ids)} new clients")
        else:
            print("All clients already exist")
    
    # Get unique projects
    project_docs = get_unique_projects(employees, client_map)
    print(f"Found {len(project_docs)} unique projects")
    
    # Insert projects
    if project_docs:
        # Remove existing projects with same name and client
        existing_project_keys = set(project_docs.keys())
        existing_projects = projects_collection.find({
            '$or': [
                {'name': name, 'client_id': client_id}
                for (client_name, name), doc in project_docs.items()
                for client_id in [doc['client_id']]
            ]
        })
        for existing in existing_projects:
            key = (existing['client_id'], existing['name'])
            if key in existing_project_keys:
                del project_docs[key]
        
        if project_docs:
            result = projects_collection.insert_many(list(project_docs.values()))
            print(f"Inserted {len(result.inserted_ids)} new projects")
        else:
            print("All projects already exist")
    
    print(f"Summary:")
    print(f"  - Total clients: {clients_collection.count_documents({'deleted_at': None})}")
    print(f"  - Total projects: {projects_collection.count_documents({'deleted_at': None})}")
    
    client.close()


def main():
    print("Seeding clients and projects from employees...")
    try:
        seed_from_employees()
        print("Seeding completed successfully!")
    except Exception as e:
        print(f"Error during seeding: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
