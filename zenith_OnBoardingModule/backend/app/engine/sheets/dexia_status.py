"""
Dexia Team status sheet processor.
"""

import pandas as pd
import re
from app.engine.sheets.helper import (
    find_latest_week_ending_sheet,
    normalize_text,
    is_leave_status,
    remove_template_headers,
    has_meaningful_content,
    DAY_NAMES,
    store_daily_status_batch,
    should_include_day
)
from app.core.mongodb import MongoDB


async def process_file(file_path: str, **kwargs):
    """
    Process Dexia Team status sheet.
    
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
    
    # Load the Excel file
    xlsx_file = pd.ExcelFile(file_path)
    
    # Find the latest Week Ending sheet
    target_sheet = find_latest_week_ending_sheet(xlsx_file)
    if not target_sheet:
        target_sheet = xlsx_file.sheet_names[0]
    
    # Read the sheet
    df = pd.read_excel(file_path, sheet_name=target_sheet, header=None)
    
    # Locate the header row and the Monday-Friday day columns
    header_row = None
    day_cols = []
    for i in range(min(15, len(df))):
        for j, val in enumerate(df.iloc[i]):
            if 'monday' in normalize_text(val) and not day_cols:
                day_cols = list(range(j, j + 5))
                header_row = i
                break
        if day_cols:
            break
    
    if not day_cols:
        day_cols = [2, 3, 4, 5, 6]
        header_row = 0
    
    # Use team leads from employee table instead of parsing from sheet
    member_to_lead = employee_team_leads
    
    # Set data start row
    data_start = (header_row + 1) if header_row is not None else 1
    
    # Check for unfilled status
    unfilled_vlinkers = []
    i = data_start
    while i < len(df):
        vlinker = df.iloc[i, 0]
        if pd.isna(vlinker) or str(vlinker).strip() == '':
            i += 1
            continue
        vlinker_str = str(vlinker).strip()
        
        if vlinker_str in offboarded_vlinkers:
            i += 1
            while i < len(df) and (pd.isna(df.iloc[i, 0]) or str(df.iloc[i, 0]).strip() == ''):
                i += 1
            continue
        
        tl = member_to_lead.get(vlinker_str, '')
        
        # Collect all rows belonging to this member block
        block_rows = [i]
        i += 1
        while i < len(df):
            first_col = df.iloc[i, 0]
            if pd.notna(first_col) and str(first_col).strip() != '':
                break
            if df.iloc[i].isna().all() or df.iloc[i].astype(str).str.strip().eq('').all():
                i += 1
                continue
            block_rows.append(i)
            i += 1
        
        unfilled_days = []
        for d_idx, day_col in enumerate(day_cols):
            if d_idx >= len(DAY_NAMES):
                break
            day_name = DAY_NAMES[d_idx]
            
            # Only include days that have already passed or are today
            # TEMPORARILY DISABLED: if not should_include_day(day_name):
            #     continue
            
            # Combine all non-empty cells for this day across the member's block rows
            day_parts = []
            for r in block_rows:
                if r < len(df) and day_col < len(df.columns):
                    val = df.iloc[r, day_col]
                    if pd.notna(val) and str(val).strip() != '':
                        day_parts.append(str(val).strip())
            daily_update = ' '.join(day_parts) if day_parts else ''
            
            # Empty -> unfilled
            if daily_update == '':
                unfilled_days.append(day_name)
                continue
            
            # Leave -> not unfilled
            if is_leave_status(daily_update):
                continue
            
            # Template with empty sections -> unfilled
            if re.search(r'Your Name', daily_update, re.IGNORECASE):
                cleaned = remove_template_headers(daily_update)
                if len(cleaned) > 20:
                    continue
                else:
                    unfilled_days.append(day_name)
                continue
            
            # Meaningful content -> filled
            if has_meaningful_content(daily_update, min_length=15):
                continue
            
            # Otherwise unfilled
            unfilled_days.append(day_name)
        
        if unfilled_days:
            unfilled_vlinkers.append({
                'Vlinker': vlinker_str,
                'Team Lead': tl,
                'Unfilled Count': len(unfilled_days),
                'Unfilled Days': ', '.join(unfilled_days),
            })
    
    # Extract team structure
    team_leads = list(set(member_to_lead.values()))
    team_structure = {}
    for lead in team_leads:
        team_structure[lead] = [member for member, tl in member_to_lead.items() if tl == lead and member != lead]

    # Store daily status data for each user/day
    status_records = []
    
    # Iterate through data again to collect all status records
    i = data_start
    while i < len(df):
        vlinker = df.iloc[i, 0]
        if pd.isna(vlinker) or str(vlinker).strip() == '':
            i += 1
            continue
        vlinker_str = str(vlinker).strip()
        
        tl = member_to_lead.get(vlinker_str, '')
        
        # Collect all rows belonging to this member block
        block_rows = [i]
        i += 1
        while i < len(df):
            first_col = df.iloc[i, 0]
            if pd.notna(first_col) and str(first_col).strip() != '':
                break
            if df.iloc[i].isna().all() or df.iloc[i].astype(str).str.strip().eq('').all():
                i += 1
                continue
            block_rows.append(i)
            i += 1
        
        # Store daily status for each day
        for d_idx, day_col in enumerate(day_cols):
            if d_idx >= len(DAY_NAMES):
                break
            day_name = DAY_NAMES[d_idx]
            
            # Combine all non-empty cells for this day across the member's block rows
            day_parts = []
            for r in block_rows:
                if r < len(df) and day_col < len(df.columns):
                    val = df.iloc[r, day_col]
                    if pd.notna(val) and str(val).strip() != '':
                        day_parts.append(str(val).strip())
            daily_update = ' '.join(day_parts) if day_parts else ''
            
            # Add to status records
            status_records.append({
                'user_name': vlinker_str,
                'team_lead': tl if tl else None,
                'sheet_name': target_sheet,
                'sheet_date': target_sheet,
                'day_of_week': day_name,
                'status_content': daily_update,
                'team_name': 'Dexia Team'
            })
    
    # Store all status records in batch
    if status_records:
        stored_count = await store_daily_status_batch(status_records)
        print(f"Stored {stored_count} daily status records for Dexia Team")

    return {
        'sheet_name': target_sheet,
        'sheet_type': 'row_based',
        'team_leads': team_leads,
        'team_structure': team_structure,
        'unfilled_status': unfilled_vlinkers,
        'total_unfilled': sum(item['Unfilled Count'] for item in unfilled_vlinkers),
        'offboarded_count': len(offboarded_vlinkers)
    }
