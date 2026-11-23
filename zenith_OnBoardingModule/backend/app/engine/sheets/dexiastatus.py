import pandas as pd
import re

# Read the xlsx file to get sheet names
xlsx_file = pd.ExcelFile("DexiaTeam.xlsx")

# Find sheet name containing 'Week Ending' (case insensitive, handle spelling errors)
target_sheet = None
for sheet_name in reversed(xlsx_file.sheet_names):
    # Use a more flexible pattern to handle spelling errors like "Weeek" vs "Week"
    if re.search(r'we+ek?\s+endin?g', sheet_name, re.IGNORECASE):
        target_sheet = sheet_name
        break

if target_sheet:
    print(f"\nFound matching sheet: {target_sheet}")
    df = pd.read_excel("DexiaTeam.xlsx", sheet_name=target_sheet)
else:
    print("\nNo sheet found matching 'Week Ending' pattern, reading first sheet")
    df = pd.read_excel("DexiaTeam.xlsx")

# Store the raw data
raw_data = df.copy()

# The first column contains the team member names
member_column = raw_data.iloc[:, 0]  # Column 0 is Team Member Name
all_names = member_column.dropna().astype(str).str.strip().unique()

# Arun Kumar Jain is the Team Lead; the rest are team members
tl_name = "Rachit Mathur"
team_members = [name for name in all_names if name.lower() != tl_name.lower()]

print(f"\nTeam Lead: {tl_name}")
print(f"\nTeam Members ({len(team_members)}):")
for member in sorted(team_members):
    print(f"- {member}")


    # Load offboarded vlinkers from DU.xlsx VLink Team Details sheet
try:
    vlink_team_details = pd.read_excel("DU.xlsx", sheet_name="VLink Team Details", header=2)
    offboarded_vlinkers = set(
        vlink_team_details[vlink_team_details['Status'] == 'Offboarded VLink']['VLinker']
        .dropna()
        .astype(str)
        .str.strip()
        .tolist()
    )
    print(f"Loaded {len(offboarded_vlinkers)} offboarded vlinkers from DU.xlsx")
except Exception as e:
    print(f"Could not load offboarded list from DU.xlsx: {e}")
    offboarded_vlinkers = set()

# Load the latest "Week Ending" sheet from PMITeam1.xlsx
xlsx_file = pd.ExcelFile("DexiaTeam.xlsx")
target_sheet = None
for sheet_name in reversed(xlsx_file.sheet_names):
    if re.search(r'we+ek?\s+endin?g', sheet_name, re.IGNORECASE):
        target_sheet = sheet_name
        break
if not target_sheet:
    target_sheet = xlsx_file.sheet_names[0]

print(f"Using DexiaTeam sheet: {target_sheet}")
df = pd.read_excel("DexiaTeam.xlsx", sheet_name=target_sheet, header=None)
raw_data = df.copy()

# Locate the header row and the Monday-Friday day columns
def normalize_text(val):
    if pd.isna(val):
        return ""
    return re.sub(r'[^\w\s]', '', str(val).lower().strip())

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

day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']

# Build a simple vlinker -> team lead mapping (first name in each contiguous group is the lead)
data_start = (header_row + 1) if header_row is not None else 1
member_to_lead = {}
current_lead = None
for i in range(data_start, len(df)):
    v = df.iloc[i, 0]
    if pd.isna(v) or str(v).strip() == '':
        if df.iloc[i].isna().all() or df.iloc[i].astype(str).str.strip().eq('').all():
            current_lead = None
        continue
    v_str = str(v).strip()
    if v_str.lower() in ('', 'nan', 'unnamed', 'none'):
        continue
    if current_lead is None:
        current_lead = v_str
        member_to_lead[current_lead] = current_lead
    else:
        member_to_lead[v_str] = current_lead

# Leave patterns (case insensitive)
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
        if d_idx >= len(day_names):
            break
        day_name = day_names[d_idx]

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
        is_leave = False
        for leave_pattern in leave_patterns:
            if re.search(leave_pattern, daily_str, re.IGNORECASE):
                is_leave = True
                break
        if is_leave:
            continue

        # Template with empty sections -> unfilled
        if re.search(r'Your Name', daily_str, re.IGNORECASE):
            cleaned = daily_str
            cleaned = re.sub(r'Your Name\s*', '', cleaned, flags=re.IGNORECASE)
            cleaned = re.sub(r'✅ Work Completed Today\s*:\s*', '', cleaned, flags=re.IGNORECASE)
            cleaned = re.sub(r'🔄 Work in Progress\s*:\s*', '', cleaned, flags=re.IGNORECASE)
            cleaned = re.sub(r'⏳ Planned for Tomorrow\s*:\s*', '', cleaned, flags=re.IGNORECASE)
            cleaned = re.sub(r'🚧 Blockers.*?📝 Additional Notes\s*:\s*', '', cleaned, flags=re.DOTALL | re.IGNORECASE)
            cleaned = re.sub(r'📝 Additional Notes\s*:\s*', '', cleaned, flags=re.IGNORECASE)
            cleaned = re.sub(r'-\s*', '', cleaned)
            cleaned = cleaned.strip()
            if len(cleaned) > 20:
                continue
            else:
                unfilled_days.append(day_name)
            continue

        # Meaningful content -> filled
        if len(daily_str.strip('"\'').strip()) > 15:
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

unfilled_df = pd.DataFrame(unfilled_vlinkers)

if not unfilled_df.empty:
    print("Vlinkers who haven't filled their daily status updates:")
    print(unfilled_df.to_string(index=False))
    print(f"\nTotal unfilled daily status entries: {unfilled_df['Unfilled Count'].sum()}")
else:
    print("All vlinkers have filled their daily status updates or are on leave.")
    print("Total unfilled daily status entries: 0")