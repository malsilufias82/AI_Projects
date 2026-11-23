"""
PMI Team 1 status sheet processor.
"""

import pandas as pd
import re
from app.core.mongodb import MongoDB
from app.engine.sheets.helper import (
    is_leave_status,
    remove_template_headers,
    has_meaningful_content,
    DAY_NAMES,
    store_daily_status_batch
)


async def process_file(file_path: str, **kwargs):
    """
    Process PMI Team 1 status sheet.
    
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

    target_sheet = None
    for sheet_name in reversed(xlsx_file.sheet_names):
        if re.search(r'we+ek?\s+endin?g', sheet_name, re.IGNORECASE):
            target_sheet = sheet_name
            break

    if target_sheet:
        df = pd.read_excel(file_path, sheet_name=target_sheet, header=None)
    else:
        df = pd.read_excel(file_path, header=None)

    # Keep the raw data available for later cells
    raw_data = df.copy()

    # Build team structure from employee data
    team_structure = employee_team_leads
    team_leads = list(team_structure.keys())

    # Locate the header row and the "Team Member" / "Team Lead" columns
    def normalize_text(val):
        if pd.isna(val):
            return ""
        return re.sub(r'[^\w\s]', '', str(val).lower().strip())

    vlinker_col = None
    tl_col = None
    header_row = None

    name_headers = {
        'team member name', 'member name', 'employee name', 'emp name',
        'vlinker', 'vlinkers', 'name', 'emp. name'
    }
    tl_headers = {
        'team lead', 'tl', 'lead', 'reporting manager', 'manager', 'team lead name'
    }

    for i in range(min(15, len(df))):
        row = df.iloc[i]
        for j, val in enumerate(row):
            norm = normalize_text(val)
            if norm in name_headers and vlinker_col is None:
                vlinker_col = j
                header_row = i
            if norm in tl_headers and tl_col is None:
                tl_col = j
                header_row = i
        if vlinker_col is not None and tl_col is not None:
            break

    # Fallback: if there is a hidden Team Lead column, look for one that contains "TL"
    if vlinker_col is not None and tl_col is None:
        start = (header_row + 1) if header_row is not None else 1
        for j in range(len(df.columns)):
            if j == vlinker_col:
                continue
            tl_count = 0
            lead_name_count = 0
            for i in range(start, min(len(df), start + 30)):
                val = df.iloc[i, j]
                if pd.isna(val):
                    continue
                s = str(val).strip()
                if s.upper() == 'TL':
                    tl_count += 1
                elif s and not s.isdigit() and len(s.split()) <= 6:
                    lead_name_count += 1
            if tl_count > 0 and lead_name_count > 0:
                tl_col = j
                break

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

    # Build a simple vlinker -> team lead mapping from employee data
    data_start = (header_row + 1) if header_row is not None else 1
    member_to_lead = employee_team_leads

    unfilled_vlinkers = []
    # Iterate member blocks (each member spans multiple rows)
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

        tl = member_to_lead.get(vlinker_str, vlinker_str)

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

            daily_str = daily_update.strip()

            # Leave -> not unfilled
            if is_leave_status(daily_str):
                continue

            # Template with empty sections -> unfilled
            if re.search(r'Your Name', daily_str, re.IGNORECASE):
                cleaned = remove_template_headers(daily_str)
                if len(cleaned) > 20:
                    continue
                else:
                    unfilled_days.append(day_name)
                continue

            # Meaningful content -> filled
            if has_meaningful_content(daily_str, min_length=15):
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

    # Store daily status data for each user/day
    status_records = []
    sheet_date = target_sheet if target_sheet else xlsx_file.sheet_names[0]
    
    # Iterate through data again to collect all status records
    i = data_start
    while i < len(df):
        vlinker = df.iloc[i, 0]
        if pd.isna(vlinker) or str(vlinker).strip() == '':
            i += 1
            continue
        vlinker_str = str(vlinker).strip()
        
        tl = member_to_lead.get(vlinker_str, vlinker_str)
        
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
                'team_lead': tl if tl != vlinker_str else None,
                'sheet_name': sheet_date,
                'sheet_date': sheet_date,
                'day_of_week': day_name,
                'status_content': daily_update,
                'team_name': 'PMI Team 1'
            })
    
    # Store all status records in batch
    if status_records:
        stored_count = await store_daily_status_batch(status_records)
        print(f"Stored {stored_count} daily status records for PMI Team 1")

    return {
        'sheet_name': target_sheet if target_sheet else xlsx_file.sheet_names[0],
        'sheet_type': 'row_based',
        'team_leads': team_leads,
        'team_structure': team_structure,
        'unfilled_status': unfilled_vlinkers,
        'total_unfilled': sum(item['Unfilled Count'] for item in unfilled_vlinkers),
        'offboarded_count': len(offboarded_vlinkers)
    }
