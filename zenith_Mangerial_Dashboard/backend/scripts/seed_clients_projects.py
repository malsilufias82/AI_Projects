import os
import sys
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime

# MongoDB connection
MONGODB_URI = os.getenv('MONGODB_URL', 'mongodb://localhost:27017')
MONGODB_DB = os.getenv('MONGODB_DATABASE', 'zenith')

def seed_clients():
    """Seed clients collection with dummy data."""
    client = MongoClient(MONGODB_URI)
    db = client[MONGODB_DB]
    clients_collection = db['clients']
    
    clients = [
        {
            'name': 'Acme Corporation',
            'contact_persons': [
                {
                    'name': 'John Smith',
                    'email': 'john.smith@acme.com',
                    'phone': '+1-555-0123',
                    'role': 'Project Manager'
                },
                {
                    'name': 'Jane Doe',
                    'email': 'jane.doe@acme.com',
                    'phone': '+1-555-0124',
                    'role': 'Technical Lead'
                }
            ],
            'address': '123 Business Ave, Suite 100',
            'status': 'active',
            'description': 'Technology solutions provider',
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        },
        {
            'name': 'Tech Innovations Inc',
            'contact_persons': [
                {
                    'name': 'Michael Johnson',
                    'email': 'michael.johnson@techinnovations.com',
                    'phone': '+1-555-0987',
                    'role': 'Business Owner'
                }
            ],
            'address': '456 Tech Park, San Francisco',
            'status': 'active',
            'description': 'Innovative tech solutions',
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        },
        {
            'name': 'Global Finance Ltd',
            'contact_persons': [
                {
                    'name': 'Sarah Williams',
                    'email': 'sarah.williams@globalfinance.com',
                    'phone': '+1-555-0345',
                    'role': 'Finance Director'
                },
                {
                    'name': 'David Brown',
                    'email': 'david.brown@globalfinance.com',
                    'phone': '+1-555-0346',
                    'role': 'Technical Consultant'
                }
            ],
            'address': '789 Financial District, New York',
            'status': 'pending',
            'description': 'Financial services and consulting',
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        },
        {
            'name': 'Healthcare Solutions',
            'contact_persons': [
                {
                    'name': 'Emily Chen',
                    'email': 'emily.chen@healthcaresolutions.com',
                    'phone': '+1-555-0567',
                    'role': 'CTO'
                },
                {
                    'name': 'Robert Miller',
                    'email': 'robert.miller@healthcaresolutions.com',
                    'phone': '+1-555-0568',
                    'role': 'Medical Director'
                }
            ],
            'address': '321 Medical Center, Boston',
            'status': 'active',
            'description': 'Healthcare technology solutions',
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        },
        {
            'name': 'Retail Giants Inc',
            'contact_persons': [
                {
                    'name': 'Lisa Anderson',
                    'email': 'lisa.anderson@retailgiants.com',
                    'phone': '+1-555-0789',
                    'role': 'VP Operations'
                }
            ],
            'address': '555 Retail Plaza, Chicago',
            'status': 'active',
            'description': 'Retail management systems',
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        },
        {
            'name': 'Energy Corp',
            'contact_persons': [
                {
                    'name': 'James Wilson',
                    'email': 'james.wilson@energycorp.com',
                    'phone': '+1-555-0125',
                    'role': 'Engineering Manager'
                },
                {
                    'name': 'Patricia Davis',
                    'email': 'patricia.davis@energycorp.com',
                    'phone': '+1-555-0126',
                    'role': 'Project Lead'
                }
            ],
            'address': '777 Energy Park, Houston',
            'status': 'inactive',
            'description': 'Energy sector solutions',
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        },
        {
            'name': 'Education First',
            'contact_persons': [
                {
                    'name': 'Kevin Lee',
                    'email': 'kevin.lee@educationfirst.com',
                    'phone': '+1-555-0341',
                    'role': 'Director'
                }
            ],
            'address': '888 Education Blvd, Seattle',
            'status': 'active',
            'description': 'Educational technology platform',
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        },
        {
            'name': 'Logistics Pro',
            'contact_persons': [
                {
                    'name': 'Amanda White',
                    'email': 'amanda.white@logisticspro.com',
                    'phone': '+1-555-0234',
                    'role': 'Operations Manager'
                },
                {
                    'name': 'Chris Martin',
                    'email': 'chris.martin@logisticspro.com',
                    'phone': '+1-555-0235',
                    'role': 'Technical Lead'
                }
            ],
            'address': '999 Logistics Way, Miami',
            'status': 'pending',
            'description': 'Supply chain and logistics solutions',
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        },
        {
            'name': 'Media Works',
            'contact_persons': [
                {
                    'name': 'Nicole Brown',
                    'email': 'nicole.brown@mediaworks.com',
                    'phone': '+1-555-0456',
                    'role': 'Creative Director'
                }
            ],
            'address': '111 Media Center, Los Angeles',
            'status': 'active',
            'description': 'Media and entertainment solutions',
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
    ]
    
    # Insert clients
    result = clients_collection.insert_many(clients)
    print(f"Inserted {len(result.inserted_ids)} clients")
    
    # Return client IDs for projects
    return result.inserted_ids

def seed_projects(client_ids):
    """Seed projects collection with dummy data."""
    client = MongoClient(MONGODB_URI)
    db = client[MONGODB_DB]
    projects_collection = db['projects']
    
    # Map client IDs
    acme_id = str(client_ids[0])
    tech_id = str(client_ids[1])
    finance_id = str(client_ids[2])
    healthcare_id = str(client_ids[3])
    retail_id = str(client_ids[4])
    energy_id = str(client_ids[5])
    education_id = str(client_ids[6])
    logistics_id = str(client_ids[7])
    
    projects = [
        {
            'name': 'E-commerce Platform',
            'client_id': acme_id,
            'pocs': [
                {
                    'name': 'John Smith',
                    'email': 'john.smith@acme.com',
                    'phone': '+1-555-0123',
                    'role': 'Business Owner'
                }
            ],
            'description': 'Building a modern e-commerce platform',
            'status': 'active',
            'start_date': '2024-01-01',
            'end_date': '2024-12-31',
            'team_lead': '',
            'pillar': 'Engineering',
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        },
        {
            'name': 'Mobile App Development',
            'client_id': tech_id,
            'pocs': [
                {
                    'name': 'Michael Johnson',
                    'email': 'michael.johnson@techinnovations.com',
                    'phone': '+1-555-0987',
                    'role': 'Product Owner'
                }
            ],
            'description': 'Cross-platform mobile application',
            'status': 'on_hold',
            'start_date': '2024-03-01',
            'end_date': '2024-09-30',
            'team_lead': '',
            'pillar': 'Mobile',
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        },
        {
            'name': 'Data Analytics Dashboard',
            'client_id': acme_id,
            'pocs': [
                {
                    'name': 'Jane Doe',
                    'email': 'jane.doe@acme.com',
                    'phone': '+1-555-0124',
                    'role': 'Technical Sponsor'
                }
            ],
            'description': 'Real-time analytics dashboard',
            'status': 'completed',
            'start_date': '2023-06-01',
            'end_date': '2023-12-31',
            'team_lead': '',
            'pillar': 'Data',
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        },
        {
            'name': 'Financial Trading System',
            'client_id': finance_id,
            'pocs': [
                {
                    'name': 'Sarah Williams',
                    'email': 'sarah.williams@globalfinance.com',
                    'phone': '+1-555-0345',
                    'role': 'Finance Director'
                }
            ],
            'description': 'High-frequency trading platform',
            'status': 'active',
            'start_date': '2024-02-01',
            'end_date': '2025-02-28',
            'team_lead': '',
            'pillar': 'Finance',
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        },
        {
            'name': 'Patient Management System',
            'client_id': healthcare_id,
            'pocs': [
                {
                    'name': 'Emily Chen',
                    'email': 'emily.chen@healthcaresolutions.com',
                    'phone': '+1-555-0567',
                    'role': 'CTO'
                },
                {
                    'name': 'Robert Miller',
                    'email': 'robert.miller@healthcaresolutions.com',
                    'phone': '+1-555-0568',
                    'role': 'Medical Director'
                }
            ],
            'description': 'Comprehensive patient management solution',
            'status': 'active',
            'start_date': '2024-01-15',
            'end_date': '2024-12-15',
            'team_lead': '',
            'pillar': 'Healthcare',
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        },
        {
            'name': 'Inventory Management',
            'client_id': retail_id,
            'pocs': [
                {
                    'name': 'Lisa Anderson',
                    'email': 'lisa.anderson@retailgiants.com',
                    'phone': '+1-555-0789',
                    'role': 'VP Operations'
                }
            ],
            'description': 'Real-time inventory tracking system',
            'status': 'active',
            'start_date': '2024-04-01',
            'end_date': '2024-10-31',
            'team_lead': '',
            'pillar': 'Retail',
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        },
        {
            'name': 'Energy Monitoring Platform',
            'client_id': energy_id,
            'pocs': [
                {
                    'name': 'James Wilson',
                    'email': 'james.wilson@energycorp.com',
                    'phone': '+1-555-0125',
                    'role': 'Engineering Manager'
                }
            ],
            'description': 'IoT-based energy consumption monitoring',
            'status': 'inactive',
            'start_date': '2023-09-01',
            'end_date': '2024-03-31',
            'team_lead': '',
            'pillar': 'Energy',
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        },
        {
            'name': 'Learning Management System',
            'client_id': education_id,
            'pocs': [
                {
                    'name': 'Kevin Lee',
                    'email': 'kevin.lee@educationfirst.com',
                    'phone': '+1-555-0341',
                    'role': 'Director'
                }
            ],
            'description': 'Online learning platform for schools',
            'status': 'active',
            'start_date': '2024-05-01',
            'end_date': '2025-05-01',
            'team_lead': '',
            'pillar': 'Education',
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        },
        {
            'name': 'Supply Chain Optimization',
            'client_id': logistics_id,
            'pocs': [
                {
                    'name': 'Amanda White',
                    'email': 'amanda.white@logisticspro.com',
                    'phone': '+1-555-0234',
                    'role': 'Operations Manager'
                },
                {
                    'name': 'Chris Martin',
                    'email': 'chris.martin@logisticspro.com',
                    'phone': '+1-555-0235',
                    'role': 'Technical Lead'
                }
            ],
            'description': 'AI-powered supply chain optimization',
            'status': 'pending',
            'start_date': '2024-06-01',
            'end_date': '2025-06-01',
            'team_lead': '',
            'pillar': 'Logistics',
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        },
        {
            'name': 'Content Management System',
            'client_id': retail_id,
            'pocs': [
                {
                    'name': 'Lisa Anderson',
                    'email': 'lisa.anderson@retailgiants.com',
                    'phone': '+1-555-0789',
                    'role': 'VP Operations'
                }
            ],
            'description': 'Headless CMS for retail websites',
            'status': 'active',
            'start_date': '2024-03-15',
            'end_date': '2024-09-15',
            'team_lead': '',
            'pillar': 'Web',
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        },
        {
            'name': 'Telemedicine Platform',
            'client_id': healthcare_id,
            'pocs': [
                {
                    'name': 'Robert Miller',
                    'email': 'robert.miller@healthcaresolutions.com',
                    'phone': '+1-555-0568',
                    'role': 'Medical Director'
                }
            ],
            'description': 'Video consultation platform',
            'status': 'on_hold',
            'start_date': '2024-07-01',
            'end_date': '2025-01-31',
            'team_lead': '',
            'pillar': 'Healthcare',
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        },
        {
            'name': 'Media Streaming Service',
            'client_id': logistics_id,
            'pocs': [
                {
                    'name': 'Nicole Brown',
                    'email': 'nicole.brown@mediaworks.com',
                    'phone': '+1-555-0456',
                    'role': 'Creative Director'
                }
            ],
            'description': 'OTT platform for media content',
            'status': 'active',
            'start_date': '2024-02-15',
            'end_date': '2025-02-15',
            'team_lead': '',
            'pillar': 'Media',
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
    ]
    
    # Insert projects
    result = projects_collection.insert_many(projects)
    print(f"Inserted {len(result.inserted_ids)} projects")

def main():
    print("Seeding clients and projects...")
    
    try:
        # Seed clients first
        client_ids = seed_clients()
        
        # Seed projects with client IDs
        seed_projects(client_ids)
        
        print("Seeding completed successfully!")
    except Exception as e:
        print(f"Error during seeding: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
