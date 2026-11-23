"""
BudDB Team status sheet processor.
"""

import pandas as pd
import re
from app.core.mongodb import MongoDB
from app.engine.sheets.helper import (
    is_leave_status,
    remove_template_headers,
    has_meaningful_content,
    DAY_NAMES,
    store_daily_status_batch,
    should_include_day
)


async def process_file(file_path: str, **kwargs):
    """
    Process BudDB Team status sheet.
    
    Args:
        file_path: Path to the Excel file
        **kwargs: Additional arguments
        
    Returns:
        Dictionary with processing results
    """
    # Connect to MongoDB and load employee data
    await MongoDB.connect()
    
    employees_collection = MongoDB.get_collection("employees")
    
    # Load offboarded vlinkers from employee table
    offboarded_employees = await employees_collection.find({
        "$or": [
            {"active_inactive": "Inactive"},
            {"status": {"$regex": "offboard", "$options": "i"}},
            {"offboarded_from_client": {"$ne": None}}
        ]
    }).to_list(length=None)
    
    offboarded_vlinkers = set()
    for emp in offboarded_employees:
        if emp.get("vlinker"):
            offboarded_vlinkers.add(str(emp["vlinker"]).strip())
        if emp.get("full_name"):
            offboarded_vlinkers.add(str(emp["full_name"]).strip())
    
    # Load team leads from employee table
    team_lead_employees = await employees_collection.find({
        "team_lead": {"$ne": None, "$ne": ""}
    }).to_list(length=None)
    
    employee_team_leads = {}
    for emp in team_lead_employees:
        vlinker = emp.get("vlinker") or emp.get("full_name")
        team_lead = emp.get("team_lead")
        if vlinker and team_lead:
            employee_team_leads[str(vlinker).strip()] = str(team_lead).strip()
    
    # Disconnect from MongoDB
    # await MongoDB.disconnect()
    
    # Read the BudDB.xlsx file to get sheet names
    buddb_file = pd.ExcelFile(file_path)

    # Find sheet name containing 'Week Ending' (case insensitive, handle spelling errors)
    target_sheet = None
    for sheet_name in reversed(buddb_file.sheet_names):
        # Use a more flexible pattern to handle spelling errors like "Weeek" vs "Week"
        if re.search(r'we+ek?\s+endin?g', sheet_name, re.IGNORECASE):
            target_sheet = sheet_name
            break

    if target_sheet:
        df = pd.read_excel(file_path, sheet_name=target_sheet)
    else:
        df = pd.read_excel(file_path)

    # Store the raw data
    raw_data = df.copy()

    # Extract Team Lead names: Get Vlinker names where Team Lead column is "TL"
    # Skip first 2 rows (headers at row 0 and 1)
    data_rows = raw_data.iloc[2:]

    # Find rows where Team Lead column (column 3, index 3) is "TL"
    tl_rows = data_rows[data_rows.iloc[:, 3] == "TL"]

    # Get the Vlinker names (column 2, index 2) from these rows
    unique_tl_names = tl_rows.iloc[:, 2].dropna().unique()

    tl_data = []

    # Get vlinker names (column 2) and their TLs (column 3)
    vlinker_column = raw_data.iloc[2:, 2]  # Vlinker names
    tl_column = raw_data.iloc[2:, 3]  # Team Lead names

    # Create a dictionary to group vlinkers by TL
    tl_to_vlinkers = {}
    for vlinker, tl in zip(vlinker_column, tl_column):
        if pd.notna(vlinker) and pd.notna(tl) and tl != 'TL':
            # Exclude offboarded vlinkers
            if vlinker not in offboarded_vlinkers:
                if tl not in tl_to_vlinkers:
                    tl_to_vlinkers[tl] = []
                tl_to_vlinkers[tl].append(vlinker)

    # Create the dataframe
    for tl, vlinkers in tl_to_vlinkers.items():
        tl_data.append({
            'Team Lead': tl,
            'Count': len(vlinkers),
            'Vlinkers': ', '.join(vlinkers),
        })

    tl_df = pd.DataFrame(tl_data)
    tl_df = tl_df.sort_values('Team Lead').reset_index(drop=True)



    # Identify vlinkers who haven't filled their daily status updates

    # Define patterns for leave (case insensitive)
    leave_patterns = [
        r'\bLEAVE\b',
        r'\bOn leave\b',
        r'\bon planned leave\b',
        r'\bOn Leave\b',
        r'\bLeave\b',
        r'\bOn planned leave\b',
        r'\bOn leave\b',
        r'\bleave\b',
        r'\bSick leave\b',
        r'\bsick leave\b',
    ]

    # Day names corresponding to columns 5-9 (Monday-Friday)
    day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']

    unfilled_vlinkers = []
    # Check each vlinker's daily updates (columns 5-9 for Monday-Friday)
    for idx, row in raw_data.iloc[2:].iterrows():
        vlinker = row.iloc[2]  # Column 2 is Vlinker name
        tl = row.iloc[3]  # Column 3 is Team Lead
        
        # Skip if vlinker is offboarded
        if vlinker in offboarded_vlinkers:
            continue
        
        # Skip if vlinker or TL is NaN
        if pd.isna(vlinker) or pd.isna(tl):
            continue
        
        # Skip if this person is a Team Lead (TL column says "TL")
        if tl == "TL":
            continue
        
        # Check daily updates for each day (columns 5-9)
        unfilled_days = []
        
        for col_idx in range(5, 10):
            daily_update = row.iloc[col_idx]
            day_name = day_names[col_idx - 5]
            
            # Only include days that have already passed or are today
            # TEMPORARILY DISABLED: if not should_include_day(day_name):
            #     continue
            
            # Check if empty/None/NaN - count as unfilled
            if daily_update is None or pd.isna(daily_update) or pd.isnull(daily_update) or str(daily_update).strip() == '':
                unfilled_days.append(day_name)
                continue
            
            daily_str = str(daily_update).strip()
            
            # Check if it's leave - if on leave, don't count as unfilled for this day
            is_leave = False
            for leave_pattern in leave_patterns:
                if re.search(leave_pattern, daily_str, re.IGNORECASE):
                    is_leave = True
                    break
            
            # If on leave for this day, skip to next day
            if is_leave:
                continue
            
            # Check if it's the "Your Name" template with empty sections
            if re.search(r'Your Name', daily_str, re.IGNORECASE):
                # Remove all template headers and check what's left
                cleaned = daily_str
                # Remove all section headers
                cleaned = re.sub(r'Your Name\s*', '', cleaned, flags=re.IGNORECASE)
                cleaned = re.sub(r'✅ Work Completed Today\s*:\s*', '', cleaned, flags=re.IGNORECASE)
                cleaned = re.sub(r'🔄 Work in Progress\s*:\s*', '', cleaned, flags=re.IGNORECASE)
                cleaned = re.sub(r'⏳ Planned for Tomorrow\s*:\s*', '', cleaned, flags=re.IGNORECASE)
                cleaned = re.sub(r'🚧 Blockers.*?📝 Additional Notes\s*:\s*', '', cleaned, flags=re.DOTALL | re.IGNORECASE)
                cleaned = re.sub(r'📝 Additional Notes\s*:\s*', '', cleaned, flags=re.IGNORECASE)
                cleaned = re.sub(r'-\s*', '', cleaned)  # Remove dashes
                cleaned = cleaned.strip()
                
                # If after removing template, there's meaningful content (more than 20 chars), consider filled
                if len(cleaned) > 20:
                    continue
                else:
                    unfilled_days.append(day_name)
                continue
            
            # If it has meaningful content (more than 15 chars), consider it filled
            # This catches any status update with actual text
            if len(daily_str.strip('"\'').strip()) > 15:
                continue
            
            # Otherwise, mark as unfilled
            unfilled_days.append(day_name)
        
        # If they have unfilled days, add to list
        if unfilled_days:
            unfilled_vlinkers.append({
                'Vlinker': vlinker,
                'Team Lead': tl,
                'Unfilled Count': len(unfilled_days),
                'Unfilled Days': ', '.join(unfilled_days),
            })

    # Extract team structure
    team_leads = list(tl_to_vlinkers.keys())
    team_structure = tl_to_vlinkers

    # Store daily status data for each user/day
    status_records = []
    sheet_date = target_sheet if target_sheet else buddb_file.sheet_names[0]
    
    # Check each vlinker's daily updates (columns 5-9 for Monday-Friday)
    for idx, row in raw_data.iloc[2:].iterrows():
        vlinker = row.iloc[2]  # Column 2 is Vlinker name
        tl = row.iloc[3]  # Column 3 is Team Lead
        
        # Skip if vlinker or TL is NaN
        if pd.isna(vlinker) or pd.isna(tl):
            continue
        
        vlinker_str = str(vlinker).strip()
        tl_str = str(tl).strip()
        
        # Store daily status for each day
        for col_idx in range(5, 10):
            daily_update = row.iloc[col_idx]
            day_name = DAY_NAMES[col_idx - 5]
            
            # Only include days that have already passed or are today
            # TEMPORARILY DISABLED: if not should_include_day(day_name):
            #     continue
            
            # Get the status content
            status_content = ""
            if daily_update is not None and not pd.isna(daily_update) and not pd.isnull(daily_update):
                status_content = str(daily_update).strip()
            
            # Add to status records
            status_records.append({
                'user_name': vlinker_str,
                'team_lead': tl_str if tl_str != 'TL' else None,
                'sheet_name': sheet_date,
                'sheet_date': sheet_date,
                'day_of_week': day_name,
                'status_content': status_content,
                'team_name': 'Data Team'
            })
    
    # Store all status records in batch
    if status_records:
        stored_count = await store_daily_status_batch(status_records)
        print(f"Stored {stored_count} daily status records for Data Team")

    return {
        'sheet_name': target_sheet if target_sheet else buddb_file.sheet_names[0],
        'sheet_type': 'row_based',
        'team_leads': team_leads,
        'team_structure': team_structure,
        'unfilled_status': unfilled_vlinkers,
        'total_unfilled': sum(item['Unfilled Count'] for item in unfilled_vlinkers),
        'offboarded_count': len(offboarded_vlinkers)
    }
