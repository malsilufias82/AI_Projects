#Find sheet for date 19-07-2026 in PlateformTeam.xlsx and extract TL names + team members
import pandas as pd
import re
from datetime import datetime

# Read the PlateformTeam.xlsx file to get sheet names
PlateformTeam_file = pd.ExcelFile("PlateformTeam.xlsx")

# Target date
target_week = "19-07-2026"

# First try to find sheet matching the target date (with or without 'Week Ending' prefix)
target_sheet = None
for sheet_name in PlateformTeam_file.sheet_names:
    if target_week in sheet_name:
        target_sheet = sheet_name
        break

# If not found by date, try matching 'Week Ending' pattern
if target_sheet is None:
    matching_sheets = []
    for sheet_name in PlateformTeam_file.sheet_names:
        if re.search(r'we+ek?\s+endin?g', sheet_name, re.IGNORECASE):
            matching_sheets.append(sheet_name)
    
    print(f"Week Ending matching sheets: {matching_sheets}")
    
    # Fall back to most recent week by parsing dates
    latest_date = None
    for sheet_name in matching_sheets:
        date_match = re.search(r'(\d{1,2})[-/](\d{1,2})(?:[-/](\d{2,4}))?', sheet_name)
        if date_match:
            day, month, year = date_match.groups()
            if year is None:
                year = str(datetime.now().year)
            elif len(year) == 2:
                year_int = int(year)
                if year_int >= 50:
                    year = '19' + year
                else:
                    year = '20' + year
            try:
                sheet_date = datetime.strptime(f"{day}-{month}-{year}", "%d-%m-%Y")
                if latest_date is None or sheet_date > latest_date:
                    latest_date = sheet_date
                    target_sheet = sheet_name
            except ValueError:
                pass
    
    if target_sheet is None and matching_sheets:
        target_sheet = matching_sheets[-1]

if target_sheet:
    print(f"\nSelected sheet: {target_sheet}")
    df = pd.read_excel("PlateformTeam.xlsx", sheet_name=target_sheet, header=None)
else:
    print("\nNo sheet found, reading first sheet")
    df = pd.read_excel("PlateformTeam.xlsx", header=None)

# The 19-07-2026 sheet in PlateformTeam.xlsx is transposed:
# - Each column represents one person
# - Row 1 (index 1): Vlinker names
# - Row 2 (index 2): Team Lead names
# - Row 3 (index 3): Role Description
# - Row 7 onwards: Daily updates

# Extract Vlinker and Team Lead rows
vlinker_row = df.iloc[1, 1:].reset_index(drop=True)  # Skip first label column
tl_row = df.iloc[2, 1:].reset_index(drop=True)  # Skip first label column

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

print(f"\nUnique Team Lead names ({len(tl_names)}):")
for tl in sorted(tl_names):
    print(f"- {tl}")

print("\n\nTeam Lead to Vlinkers mapping:")
for tl in sorted(tl_to_vlinkers.keys()):
    vlinkers = tl_to_vlinkers[tl]
    print(f"\n{tl} ({len(vlinkers)} vlinkers):")
    for v in vlinkers:
        print(f"  - {v}")

  # Identify vlinkers who haven't filled their daily status updates--PlateformTeam.xlsx
# Load offboarded vlinkers from DU.xlsx VLink Team Details sheet
try:
    vlink_team_details = pd.read_excel("DU.xlsx", sheet_name="VLink Team Details", header=2)
    offboarded_list = set(
        vlink_team_details[vlink_team_details['Status'] == 'Offboarded VLink']['VLinker']
        .dropna()
        .astype(str)
        .str.strip()
        .tolist()
    )
except Exception as e:
    offboarded_list = set()

# Load PlateformTeam.xlsx and find the 19-07-2026 sheet
target_week = "19-07-2026"
PlateformTeam_file = pd.ExcelFile("PlateformTeam.xlsx")

target_sheet = None
for sheet_name in PlateformTeam_file.sheet_names:
    if target_week in sheet_name:
        target_sheet = sheet_name
        break

if target_sheet is None:
    print(f"Sheet for {target_week} not found.")
else:
    print(f"Selected sheet: {target_sheet}")
    df = pd.read_excel("PlateformTeam.xlsx", sheet_name=target_sheet, header=None)
    
    # Detect which row holds vlinker names and which holds team lead names
    # The first column (index 0) usually contains the labels for each row
    label_1 = re.sub(r'[^\w\s]', '', str(df.iloc[1, 0]).lower().strip())
    label_2 = re.sub(r'[^\w\s]', '', str(df.iloc[2, 0]).lower().strip())
    
    if 'vlinker' in label_1 or label_1 == 'name':
        vlinker_row_idx = 1
        tl_row_idx = 2
    elif 'team lead' in label_1 or label_1 == 'tl' or 'lead' in label_1:
        vlinker_row_idx = 2
        tl_row_idx = 1
    elif 'vlinker' in label_2 or label_2 == 'name':
        vlinker_row_idx = 2
        tl_row_idx = 1
    else:
        # Fallback: the row with more "TL" markers is the Team Lead row
        tl_count_1 = sum(1 for v in df.iloc[1, 1:] if str(v).strip().upper() == 'TL')
        tl_count_2 = sum(1 for v in df.iloc[2, 1:] if str(v).strip().upper() == 'TL')
        if tl_count_1 > tl_count_2:
            tl_row_idx = 1
            vlinker_row_idx = 2
        else:
            tl_row_idx = 2
            vlinker_row_idx = 1
    
    vlinker_row = df.iloc[vlinker_row_idx, 1:].reset_index(drop=True)
    tl_row = df.iloc[tl_row_idx, 1:].reset_index(drop=True)
    
    print(f"Row {vlinker_row_idx} used as Vlinker row, Row {tl_row_idx} used as Team Lead row")
    
    # Rows 7-11 (indices 7-11): Monday to Friday daily updates
    day_indices = [7, 8, 9, 10, 11]
    day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    
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
    
    # Leave patterns
    leave_patterns = [r'\bleave\b', r'\bon leave\b', r'\bon planned leave\b', r'\bsick leave\b']
    
    # Template header patterns to remove when checking for meaningful content
    template_headers = [
        r'Your Name\s*',
        r'✅\s*(Today\'s Activities|Work Completed Today|Work Completed on \w+)?\s*:?\s*',
        r'🔄\s*Work in Progress\s*:?\s*',
        r'⏳\s*Planned for (Tomorrow|Next Working Day)\s*:?\s*',
        r'🚧\s*Blockers / Support Needed / Impact( of the blocker)?\s*:?\s*',
        r'📝\s*Additional Notes\s*:?\s*',
    ]
    
    unfilled_vlinkers = []
    
    for col_idx in range(len(vlinker_row)):
        vlinker = vlinker_row.iloc[col_idx]
        tl = tl_row.iloc[col_idx]
        
        # Skip if vlinker or TL is NaN/empty
        if pd.isna(vlinker) or pd.isna(tl):
            continue
        
        vlinker_str = str(vlinker).strip()
        tl_str = str(tl).strip()
        
        # Resolve actual TL name from mapping
        actual_tl = vlinker_to_tl.get(vlinker_str, tl_str)
        
        # Skip offboarded vlinkers and Team Leads themselves
        if vlinker_str in offboarded_list:
            continue
        if tl_str.upper() == "TL" or actual_tl.upper() == vlinker_str.upper():
            continue
        
        unfilled_days = []
        
        for day_i, day_idx in enumerate(day_indices):
            daily_update = df.iloc[day_idx, col_idx + 1]  # +1 because we skipped label column
            day_name = day_names[day_i]
            
            # Empty/NaN -> unfilled
            if pd.isna(daily_update) or str(daily_update).strip() == '':
                unfilled_days.append(day_name)
                continue
            
            daily_str = str(daily_update).strip()
            
            # Leave check
            is_leave = False
            for leave_pattern in leave_patterns:
                if re.search(leave_pattern, daily_str, re.IGNORECASE):
                    is_leave = True
                    break
            if is_leave:
                continue
            
            # Remove template headers and check for remaining meaningful content
            cleaned = daily_str
            for pattern in template_headers:
                cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE)
            cleaned = re.sub(r'[-*•]\s*', '', cleaned)  # Remove bullet dashes
            cleaned = cleaned.strip()
            
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
    
    unfilled_df = pd.DataFrame(unfilled_vlinkers)
    
    if not unfilled_df.empty:
        print("\nVlinkers who haven't filled their daily status updates:")
        print(unfilled_df.to_string(index=False))
    else:
        print("\nAll vlinkers have filled their daily status updates or are on leave.")

        