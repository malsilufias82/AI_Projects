# Find sheet name containing 'Week ending' in BudDB.xlsx and extract TL names for BudDB.xl file 
import pandas as pd
import re

# Read the BudDB.xlsx file to get sheet names
buddb_file = pd.ExcelFile("BudDB.xlsx")

# Find sheet name containing 'Week Ending' (case insensitive, handle spelling errors)
target_sheet = None
for sheet_name in reversed(buddb_file.sheet_names):
    # Use a more flexible pattern to handle spelling errors like "Weeek" vs "Week"
    if re.search(r'we+ek?\s+endin?g', sheet_name, re.IGNORECASE):
        target_sheet = sheet_name
        break

if target_sheet:
    print(f"\nFound matching sheet: {target_sheet}")
    df = pd.read_excel("BudDB.xlsx", sheet_name=target_sheet)
else:
    print("\nNo sheet found matching 'Week ending' pattern, reading first sheet")
    df = pd.read_excel("BudDB.xlsx")

# Store the raw data
raw_data = df.copy()

# Extract Team Lead names: Get Vlinker names where Team Lead column is "TL"
# Skip first 2 rows (headers at row 0 and 1)
data_rows = raw_data.iloc[2:]

# Find rows where Team Lead column (column 3, index 3) is "TL"
tl_rows = data_rows[data_rows.iloc[:, 3] == "TL"]

# Get the Vlinker names (column 2, index 2) from these rows
unique_tl_names = tl_rows.iloc[:, 2].dropna().unique()

print(f"\nUnique Team Lead names ({len(unique_tl_names)}):")
for tl in sorted(unique_tl_names):
    print(f"- {tl}")

   
   
   
    tl_data = []

# Load vlinker status to identify offboarded vlinkers
vlinker_status_df = pd.read_excel('DU.xlsx', sheet_name='VLink Team Details', header=2)

# Get vlinker names (column 2) and their TLs (column 3)--for BudDB xl file 
vlinker_column = raw_data.iloc[2:, 2]  # Vlinker names
tl_column = raw_data.iloc[2:, 3]  # Team Lead names

# Get list of offboarded vlinkers to exclude
offboarded_vlinkers = set(vlinker_status_df[vlinker_status_df['Status'] == 'Offboarded VLink']['VLinker'].tolist())

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

print('Team Lead to Vlinkers mapping (excluding offboarded vlinkers):')
print(tl_df.to_string(index=False))



# Identify vlinkers who haven't filled their daily status updates--BudDB.xl file

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

# Create dataframe of unfilled vlinkers
unfilled_df = pd.DataFrame(unfilled_vlinkers)

if not unfilled_df.empty:
    print("Vlinkers who haven't filled their daily status updates:")
    print(unfilled_df.to_string(index=False))
else:
    print("All vlinkers have filled their daily status updates or are on leave.")

    
    
