"""
Phoenix Team status sheet processor.
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
    Process Phoenix Team status sheet.
    
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
    
    # Read the xlsx file to get sheet names
    xlsx_file = pd.ExcelFile(file_path)

    # Find sheet name containing 'Week Ending' (case insensitive, handle spelling errors)
    target_sheet = None
    for sheet_name in reversed(xlsx_file.sheet_names):
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

    # Extract Team Lead names (column index 4 based on the structure)
    # Skip header row (row 1) and get unique TL names
    tl_column = raw_data.iloc[2:, 4]  # Skip first 2 rows, column 4 is Team Lead
    unique_tl_names = tl_column.dropna().unique()

    # Filter out "TL" which indicates the Vlinker is a TL themselves (no TL above them)
    unique_tl_names = [tl for tl in unique_tl_names if tl != "TL"]

    # Use team leads from employee table instead of parsing from sheet
    member_to_lead = employee_team_leads

    # Build team structure from employee data
    team_structure = {}
    for member, tl in member_to_lead.items():
        if tl not in team_structure:
            team_structure[tl] = []
        team_structure[tl].append(member)

    team_leads = list(team_structure.keys())

    # Check for unfilled status (assuming columns 5-9 for Monday-Friday like other sheets)
    unfilled_vlinkers = []
    data_start = 2  # Skip first 2 rows (headers)
    
    for idx, row in raw_data.iloc[data_start:].iterrows():
        vlinker = row.iloc[3]  # Column 3 is Vlinker name
        tl = row.iloc[4]  # Column 4 is Team Lead
        
        # Skip if vlinker is offboarded
        if vlinker in offboarded_vlinkers:
            continue
        
        # Skip if vlinker or TL is NaN
        if pd.isna(vlinker) or pd.isna(tl):
            continue
        
        # Skip if this person is a Team Lead (TL column says "TL")
        if tl == "TL":
            continue
        
        # Check daily updates for each day (columns 10-14 for Monday-Friday)
        unfilled_days = []
        
        for col_idx in range(10, 15):
            if col_idx >= len(row):
                break
            daily_update = row.iloc[col_idx]
            day_name = DAY_NAMES[col_idx - 10] if col_idx - 10 < len(DAY_NAMES) else f"Day {col_idx - 9}"
            
            # Only include days that have already passed or are today
            # TEMPORARILY DISABLED: if not should_include_day(day_name):
            #     continue
            
            # Check if empty/None/NaN - count as unfilled
            if daily_update is None or pd.isna(daily_update) or pd.isnull(daily_update) or str(daily_update).strip() == '':
                unfilled_days.append(day_name)
                continue
            
            daily_str = str(daily_update).strip()
            
            # Check if it's leave - if on leave, don't count as unfilled for this day
            if is_leave_status(daily_str):
                continue
            
            # Check if it's the "Your Name" template with empty sections
            if re.search(r'Your Name', daily_str, re.IGNORECASE):
                cleaned = remove_template_headers(daily_str)
                if len(cleaned) > 20:
                    continue
                else:
                    unfilled_days.append(day_name)
                continue
            
            # If it has meaningful content, consider it filled
            if has_meaningful_content(daily_str, min_length=15):
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

    # Store daily status data for each user/day
    status_records = []
    sheet_date = target_sheet if target_sheet else xlsx_file.sheet_names[0]
    
    # Iterate through data to collect all status records
    for idx, row in raw_data.iloc[data_start:].iterrows():
        vlinker = row.iloc[3]  # Column 3 is Vlinker name
        tl = row.iloc[4]  # Column 4 is Team Lead
        
        # Skip if vlinker or TL is NaN
        if pd.isna(vlinker) or pd.isna(tl):
            continue
        
        vlinker_str = str(vlinker).strip()
        tl_str = str(tl).strip()
        
        # Store daily status for each day (columns 10-14 for Monday-Friday)
        for col_idx in range(10, 15):
            if col_idx >= len(row):
                break
            daily_update = row.iloc[col_idx]
            day_name = DAY_NAMES[col_idx - 10] if col_idx - 10 < len(DAY_NAMES) else f"Day {col_idx - 9}"
            
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
                'team_name': 'Product Team'
            })
    
    # Store all status records in batch
    if status_records:
        stored_count = await store_daily_status_batch(status_records)
        print(f"Stored {stored_count} daily status records for Product Team")

    return {
        'sheet_name': target_sheet if target_sheet else xlsx_file.sheet_names[0],
        'sheet_type': 'row_based',
        'team_leads': team_leads,
        'team_structure': team_structure,
        'unfilled_status': unfilled_vlinkers,
        'total_unfilled': sum(item['Unfilled Count'] for item in unfilled_vlinkers),
        'offboarded_count': len(offboarded_vlinkers)
    }
