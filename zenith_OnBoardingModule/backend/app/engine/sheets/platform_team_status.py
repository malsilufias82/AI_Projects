"""
Platform Team status sheet processor.
"""

import pandas as pd
import re
from datetime import datetime
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
    Process Platform Team status sheet.
    
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
    
    # Read the Platform Team file to get sheet names
    PlateformTeam_file = pd.ExcelFile(file_path)

    # Find the latest sheet by date (no 'Week Ending' pattern matching)
    target_sheet = None
    matching_sheets = []
    
    # Look for any sheet with a date
    for sheet_name in reversed(PlateformTeam_file.sheet_names):
        date_match = re.search(r'(\d{1,2})[-/](\d{1,2})(?:[-/](\d{2,4}))?', sheet_name)
        if date_match:
            matching_sheets.append(sheet_name)
    
    if matching_sheets:
        # Find the most recent by date
        latest_date = None
        for sheet_name in matching_sheets:
            date_match = re.search(r'(\d{1,2})[-/](\d{1,2})(?:[-/](\d{2,4}))?', sheet_name)
            if date_match:
                day, month, year = date_match.groups()
                if year is None:
                    year = '2026'
                elif len(year) == 2:
                    year_int = int(year)
                    year = '20' + year if year_int < 50 else '19' + year
                
                try:
                    sheet_date = pd.to_datetime(f"{day}-{month}-{year}", format="%d-%m-%Y")
                    if latest_date is None or sheet_date > latest_date:
                        latest_date = sheet_date
                        target_sheet = sheet_name
                except ValueError:
                    pass
        
        if not target_sheet:
            target_sheet = matching_sheets[0]
    else:
        # No sheets with dates found, use first sheet
        target_sheet = PlateformTeam_file.sheet_names[0] if PlateformTeam_file.sheet_names else None

    if target_sheet:
        df = pd.read_excel(file_path, sheet_name=target_sheet, header=None)
    else:
        df = pd.read_excel(file_path, header=None)

    # The Platform Team sheet is column-based:
    # - Each column represents one person
    # - Row 0 (index 0): BLK Team labels
    # - Row 1 (index 1): Vlinker names
    # - Row 2 (index 2): Team Lead names
    # - Row 3 (index 3): Role Description
    # - Row 7-11 (indices 7-11): Monday to Friday daily updates

    # Extract Vlinker and Team Lead rows
    vlinker_row = df.iloc[1, 1:].reset_index(drop=True)  # Row 1, skip first label column
    tl_row = df.iloc[2, 1:].reset_index(drop=True)  # Row 2, skip first label column

    # Create a mapping of TL -> list of vlinkers
    tl_to_vlinkers = {}
    for vlinker, tl in zip(vlinker_row, tl_row):
        if pd.notna(vlinker) and pd.notna(tl):
            tl_str = str(tl).strip()
            vlinker_str = str(vlinker).strip()
            if tl_str != "TL" and tl_str != "":
                if tl_str not in tl_to_vlinkers:
                    tl_to_vlinkers[tl_str] = []
                tl_to_vlinkers[tl_str].append(vlinker_str)

    # Also identify the Team Leads themselves (where Team Lead column is "TL")
    tl_names = [str(v).strip() for v, tl in zip(vlinker_row, tl_row) if pd.notna(v) and str(tl).strip() == "TL"]

    # Build team structure from employee data
    team_structure = employee_team_leads
    team_leads = list(team_structure.keys())
    
    # Rows 7-11 (indices 7-11): Monday to Friday daily updates
    day_indices = [7, 8, 9, 10, 11]
    
    # Build a vlinker -> Team Lead mapping so we always report the TL name
    tl_to_vlinkers = {}
    for vlinker, tl in zip(vlinker_row, tl_row):
        if pd.isna(vlinker) or pd.isna(tl):
            continue
        v_str = str(vlinker).strip()
        t_str = str(tl).strip()
        if v_str == '' or t_str == '' or v_str.upper() == 'TL' or t_str.upper() == 'TL':
            continue
        if t_str not in tl_to_vlinkers:
            tl_to_vlinkers[t_str] = []
        tl_to_vlinkers[t_str].append(v_str)
    
    vlinker_to_tl = {}
    for tl_name, members in tl_to_vlinkers.items():
        for member in members:
            vlinker_to_tl[member] = tl_name
    
    unfilled_vlinkers = []
    
    for col_idx in range(len(vlinker_row)):
        vlinker = vlinker_row.iloc[col_idx]
        tl = tl_row.iloc[col_idx]
        
        # Skip if vlinker or TL is NaN/empty
        if pd.isna(vlinker) or pd.isna(tl):
            continue
        
        vlinker_str = str(vlinker).strip()
        tl_str = str(tl).strip()
        
        # Skip header labels (case-insensitive)
        if vlinker_str.upper() == "VLINKER" or tl_str.upper() == "TEAM LEAD":
            continue
        
        # Resolve actual TL name from mapping
        actual_tl = vlinker_to_tl.get(vlinker_str, tl_str)
        
        # Skip offboarded vlinkers and Team Leads themselves
        if vlinker_str in offboarded_vlinkers:
            continue
        if tl_str.upper() == "TL" or actual_tl.upper() == vlinker_str.upper():
            continue
        
        unfilled_days = []
        
        for day_i, day_idx in enumerate(day_indices):
            daily_update = df.iloc[day_idx, col_idx + 1]  # +1 because we skipped label column
            day_name = DAY_NAMES[day_i] if day_i < len(DAY_NAMES) else f"Day {day_i + 1}"
            
            # Empty/NaN -> unfilled
            if pd.isna(daily_update) or str(daily_update).strip() == '':
                unfilled_days.append(day_name)
                continue
            
            daily_str = str(daily_update).strip()
            
            # Leave check using helper function
            if is_leave_status(daily_str):
                continue
            
            # Remove template headers and check for meaningful content
            cleaned = remove_template_headers(daily_str)
            
            # If after removing template, less than 25 meaningful chars remain -> unfilled
            if len(cleaned) < 25:
                unfilled_days.append(day_name)
        
        if unfilled_days:
            unfilled_vlinkers.append({
                'Vlinker': vlinker_str,
                'Team Lead': actual_tl,
                'Unfilled Count': len(unfilled_days),
                'Unfilled Days': ', '.join(unfilled_days),
            })

    # Store daily status data for each user/day
    status_records = []
    sheet_date = target_sheet if target_sheet else PlateformTeam_file.sheet_names[0]
    
    for col_idx in range(len(vlinker_row)):
        vlinker = vlinker_row.iloc[col_idx]
        tl = tl_row.iloc[col_idx]
        
        # Skip if vlinker or TL is NaN/empty
        if pd.isna(vlinker) or pd.isna(tl):
            continue
        
        vlinker_str = str(vlinker).strip()
        tl_str = str(tl).strip()
        
        # Skip header labels (case-insensitive)
        if vlinker_str.upper() == "VLINKER" or tl_str.upper() == "TEAM LEAD":
            continue
        
        # Resolve actual TL name from mapping
        actual_tl = vlinker_to_tl.get(vlinker_str, tl_str)
        
        # Store daily status for each day
        for day_i, day_idx in enumerate(day_indices):
            daily_update = df.iloc[day_idx, col_idx + 1]  # +1 because we skipped label column
            day_name = DAY_NAMES[day_i] if day_i < len(DAY_NAMES) else f"Day {day_i + 1}"
            
            # Only include days that have already passed or are today
            # TEMPORARILY DISABLED: if not should_include_day(day_name):
            #     continue
            
            # Get the status content
            status_content = ""
            if not pd.isna(daily_update) and str(daily_update).strip() != '':
                status_content = str(daily_update).strip()
            
            # Add to status records
            status_records.append({
                'user_name': vlinker_str,
                'team_lead': actual_tl if actual_tl and actual_tl.upper() != 'TL' else None,
                'sheet_name': sheet_date,
                'sheet_date': sheet_date,
                'day_of_week': day_name,
                'status_content': status_content,
                'team_name': 'Platform Team'
            })
    
    # Store all status records in batch
    if status_records:
        stored_count = await store_daily_status_batch(status_records)
        print(f"Stored {stored_count} daily status records for Platform Team")

    return {
        'sheet_name': target_sheet if target_sheet else PlateformTeam_file.sheet_names[0],
        'sheet_type': 'column_based',
        'team_leads': team_leads,
        'team_structure': team_structure,
        'unfilled_status': unfilled_vlinkers,
        'total_unfilled': sum(item['Unfilled Count'] for item in unfilled_vlinkers),
        'offboarded_count': len(offboarded_vlinkers)
    }