import asyncio
import sys
from pathlib import Path

import pandas as pd

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.mongodb import MongoDB
from app.core.security import hash_password
from app.models.mongo_user import User, UserRole
from app.models.mongo_employee import Employee


async def seed_users():
    """Seed users from DU Teams Excel file."""
    
    # Connect to MongoDB
    await MongoDB.connect()
    
    # Load Excel file
    excel_path = Path(__file__).parent.parent.parent / "temp" / "DU Teams.xlsx"
    
    if not excel_path.exists():
        print(f"Error: Excel file not found at {excel_path}")
        await MongoDB.disconnect()
        return
    
    # Read Excel file (header is on row 2, not row 0)
    df = pd.read_excel(excel_path, sheet_name="VLink Team Details", header=2)
    
    # Remove rows with missing VLinker (name)
    df = df[df['VLinker'].notna()]
    
    users_collection = MongoDB.get_collection("users")
    employees_collection = MongoDB.get_collection("employees")
    
    created_count = 0
    updated_count = 0
    employee_created_count = 0
    employee_updated_count = 0
    skipped_count = 0
    error_count = 0
    
    for _, row in df.iterrows():
        vlinker = row.get('VLinker')
        employee_id = row.get('Employee ID')
        email_id = row.get('Email id')
        designation = row.get('Designation')
        status = row.get('Status')
        active_inactive = row.get('Active/Inactive')
        
        if pd.isna(vlinker) or str(vlinker).strip() == '':
            continue
        
        # Use email from sheet if available, otherwise generate from name
        if email_id and isinstance(email_id, str) and email_id.strip():
            email = email_id.strip()
            # Parse name from email for first_name/last_name
            email_parts = email.split('@')[0].split('.')
            first_name = email_parts[0] if email_parts else None
            last_name = ' '.join(email_parts[1:]) if len(email_parts) > 1 else None
        else:
            # Parse name from VLinker
            name_parts = str(vlinker).strip().split()
            first_name = name_parts[0] if name_parts else None
            last_name = ' '.join(name_parts[1:]) if len(name_parts) > 1 else None
            
            # Handle case where last name is just a period
            if last_name and last_name.strip() == '.':
                last_name = None
            
            # Generate email from name (simple pattern: firstname.lastname@vlinkinfo.com)
            if first_name:
                email_base = f"{first_name.lower()}.{last_name.lower() if last_name else ''}"
                email = email_base.rstrip('.') + "@vlinkinfo.com"
                email = email.replace(' ', '')
            else:
                print(f"Skipped: {vlinker} (no first name)")
                skipped_count += 1
                continue
        
        # Set default role (role from sheet is different from User model role)
        role = UserRole.USER
        
        # Determine employee role based on designation
        employee_role = "user"
        if designation and isinstance(designation, str):
            designation_lower = designation.lower()
            if 'vp' in designation_lower or 'vice president' in designation_lower:
                employee_role = "vp"
            elif 'manager' in designation_lower:
                employee_role = "manager"
            elif 'lead' in designation_lower:
                employee_role = "lead"
            elif 'sr.' in designation_lower or 'senior' in designation_lower:
                employee_role = "senior_engineer"
            elif 'engineer' in designation_lower:
                employee_role = "engineer"
            elif 'support' in designation_lower:
                employee_role = "support_engineer"
            elif 'qa' in designation_lower or 'quality' in designation_lower:
                employee_role = "qa_engineer"
            elif 'data engineer' in designation_lower:
                employee_role = "data_engineer"
            elif 'devops' in designation_lower:
                employee_role = "devops_engineer"
            elif 'database' in designation_lower or 'dba' in designation_lower:
                employee_role = "database_admin"
            elif 'analyst' in designation_lower:
                employee_role = "analyst"
            elif 'designer' in designation_lower:
                employee_role = "designer"
            elif 'associate' in designation_lower:
                employee_role = "associate"
            elif 'trainee' in designation_lower:
                employee_role = "trainee"
            elif 'intern' in designation_lower:
                employee_role = "intern"
        
        # Determine is_active based on status or active_inactive
        is_active = True
        if active_inactive and isinstance(active_inactive, str):
            status_lower = active_inactive.lower()
            if 'inactive' in status_lower:
                is_active = False
        elif status and isinstance(status, str):
            status_lower = status.lower()
            if 'offboard' in status_lower or 'inactive' in status_lower:
                is_active = False
        
        # Check if user already exists
        existing = await users_collection.find_one({"email": email})
        user_id = None
        
        if existing:
            user_id = str(existing.get("_id", ""))
            # Update existing user
            update_data = {
                "first_name": first_name,
                "last_name": last_name,
                "is_active": is_active,
                "role": role.value
            }
            
            try:
                result = await users_collection.update_one(
                    {"email": email},
                    {"$set": update_data}
                )
                updated_count += 1
                print(f"Updated: {email} - {first_name} {last_name if last_name else ''} - Role: {role.value}")
            except Exception as e:
                error_count += 1
                print(f"Error updating user {email}: {e}")
        else:
            # Set default password for new users
            default_password = "Vlink@123"
            hashed_pw = hash_password(default_password)
            
            # Create new user
            user = User(
                email=email,
                hashed_password=hashed_pw,
                first_name=first_name,
                last_name=last_name,
                is_active=is_active,
                role=role
            )
            
            try:
                result = await users_collection.insert_one(user.to_mongo())
                user_id = str(result.inserted_id)
                created_count += 1
                print(f"Created: {email} - {first_name} {last_name if last_name else ''} - Role: {role.value}")
            except Exception as e:
                error_count += 1
                print(f"Error creating user {email}: {e}")
        
        # Create or update employee record
        if user_id:
            # Check if employee already exists for this user
            existing_employee = await employees_collection.find_one({"user_id": user_id})
            
            # Convert NaN values to None
            def clean_value(val):
                if pd.isna(val):
                    return None
                if isinstance(val, float) and (val != val):  # NaN check
                    return None
                if isinstance(val, str):
                    return val.strip()
                if hasattr(val, 'strftime'):  # datetime object
                    return val.strftime('%Y-%m-%d')
                return str(val) if val is not None else None
            
            employee_data = {
                "user_id": user_id,
                "role": employee_role,
                "employee_id": clean_value(employee_id),
                "full_name": str(vlinker).strip(),
                "email": clean_value(email_id),
                "client": clean_value(row.get('Client')),
                "project": clean_value(row.get('Project')),
                "pillar": clean_value(row.get('Pillar')),
                "blk_team_sub_project": clean_value(row.get('BLK Team/Sub Project')),
                "vlinker": clean_value(vlinker),
                "team_lead": clean_value(row.get('Team Lead')),
                "active_inactive": clean_value(active_inactive),
                "status": clean_value(status),
                "active_pw_io": clean_value(row.get('Active PW/IO')),
                "billed": clean_value(row.get('Billed?')),
                "dev_qa": clean_value(row.get('Dev/QA')),
                "designation": clean_value(designation),
                "skill_set": clean_value(row.get('Skill set')),
                "work_location": clean_value(row.get('Work Location')),
                "kras": clean_value(row.get('KRAs')),
                "ai_level": clean_value(row.get('AI Level')),
                "ai_lead": clean_value(row.get('AI Lead')),
                "account_manager": clean_value(row.get('Account Manager')),
                "am_poc_in_blackrock": clean_value(row.get('AM POC in Blackrock')),
                "hr1_rm": clean_value(row.get('HR1 - RM')),
                "fm_id": clean_value(row.get('FM ID')),
                "hr1_fm": clean_value(row.get('HR1 - FM')),
                "onboarding_vlink": clean_value(row.get('Onboarding  \nVLink')),
                "bgv_start": clean_value(row.get('BGV Start ')),
                "bgv_clear": clean_value(row.get('BGV Clear')),
                "vcf_sent": clean_value(row.get('VCF sent')),
                "client_credential_received": clean_value(row.get('Client Credential Received')),
                "billing_start_date": clean_value(row.get('Billing Start Date')),
                "buffer": clean_value(row.get('Buffer')),
                "offboarded_from_client": clean_value(row.get('Off boarded from Client')),
                "new_project": clean_value(row.get('New Project')),
                "resignation_date": clean_value(row.get('Resignation Date')),
                "lwd_in_vlink": clean_value(row.get('LWD in VLink')),
                "offboarding_reason": clean_value(row.get('Offboarding Reason')),
                "offboarding_decision_date": clean_value(row.get('Off boarding decision date')),
                "renewal": clean_value(row.get('Renewal')),
                "expected_due_date": clean_value(row.get('Expected Due Date')),
                "country": clean_value(row.get('Country')),
                "blk_tl": clean_value(row.get('BLK TL')),
                "poc_project_reporting_mgr_at_blk": clean_value(row.get('PoC/Project/reporting mgr at BLK')),
                "blk_buddy": clean_value(row.get('BLK Buddy')),
                "blk_manager": clean_value(row.get('BLK manager')),
                "blk_manager_level_2": clean_value(row.get('BLK Manager Level 2')),
                "blk_manager_level_3": clean_value(row.get('BLK Manager Level 3')),
                "blk_manager_level_4": clean_value(row.get('BLK Manager Level 4')),
                "blk_manager_level_5": clean_value(row.get('BLK Manager Level 5')),
                "blk_manager_level_6": clean_value(row.get('BLK Manager Level 6')),
                "fte_contractor": clean_value(row.get('FTE/Contractor')),
                "contract_type": clean_value(row.get('Contract Type')),
                "vendor": clean_value(row.get('Vendor')),
                "employment_status": clean_value(row.get('Employment status')),
                "exp_in_emp_details": clean_value(row.get('Exp In Emp Details')),
                "replacement_details": clean_value(row.get('Replacement Details')),
                "commute": clean_value(row.get('Commute')),
                "current_city": clean_value(row.get('Current City')),
                "current_state": clean_value(row.get('Current State')),
                "home_town": clean_value(row.get('Home Town')),
                "permanent_city": clean_value(row.get('Permanent City')),
                "permanent_state": clean_value(row.get('Permanent State')),
                "location_as_per_hr": clean_value(row.get('Location as per HR')),
                "h_o_v": clean_value(row.get('H/O/V')),
                "bf_bl": clean_value(row.get('Bf/Bl')),
                "alias": clean_value(row.get('Alias')),
                "contact_number": clean_value(row.get('Contact Number')),
                "comments": clean_value(row.get('Comments')),
            }
            
            if existing_employee:
                # Update existing employee
                try:
                    await employees_collection.update_one(
                        {"user_id": user_id},
                        {"$set": employee_data}
                    )
                    employee_updated_count += 1
                    print(f"  -> Updated employee record")
                except Exception as e:
                    error_count += 1
                    print(f"  -> Error updating employee: {e}")
            else:
                # Create new employee
                try:
                    employee = Employee(**employee_data)
                    await employees_collection.insert_one(employee.to_mongo())
                    employee_created_count += 1
                    print(f"  -> Created employee record")
                except Exception as e:
                    error_count += 1
                    print(f"  -> Error creating employee: {e}")
    
    print(f"\nSummary:")
    print(f"Users Created: {created_count}")
    print(f"Users Updated: {updated_count}")
    print(f"Employees Created: {employee_created_count}")
    print(f"Employees Updated: {employee_updated_count}")
    print(f"Skipped: {skipped_count} (invalid data)")
    print(f"Errors: {error_count}")
    
    # Disconnect from MongoDB
    await MongoDB.disconnect()


if __name__ == "__main__":
    asyncio.run(seed_users())
