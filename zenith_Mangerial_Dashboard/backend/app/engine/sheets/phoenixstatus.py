# Find sheet name containing 'Week Ending' and extract TL names
import pandas as pd
import re

# Read the xlsx file to get sheet names
xlsx_file = pd.ExcelFile("input.xlsx")

# Find sheet name containing 'Week Ending' (case insensitive, handle spelling errors)
target_sheet = None
for sheet_name in reversed(xlsx_file.sheet_names):
    # Use a more flexible pattern to handle spelling errors like "Weeek" vs "Week"
    if re.search(r'we+ek?\s+endin?g', sheet_name, re.IGNORECASE):
        target_sheet = sheet_name
        break

if target_sheet:
    print(f"\nFound matching sheet: {target_sheet}")
    df = pd.read_excel("input.xlsx", sheet_name=target_sheet)
else:
    print("\nNo sheet found matching 'Week Ending' pattern, reading first sheet")
    df = pd.read_excel("input.xlsx")

# Store the raw data
raw_data = df.copy()


# Extract Team Lead names (column index 4 based on the structure)
# Skip header row (row 1) and get unique TL names
tl_column = raw_data.iloc[2:, 4]  # Skip first 2 rows, column 4 is Team Lead
unique_tl_names = tl_column.dropna().unique()

# Filter out "TL" which indicates the Vlinker is a TL themselves (no TL above them)
unique_tl_names = [tl for tl in unique_tl_names if tl != "TL"]

print(f"\nUnique Team Lead names ({len(unique_tl_names)}):")
for tl in sorted(unique_tl_names):
    print(f"- {tl}")


    # Find sheet name containing 'Week Ending' (case insensitive, handle spelling errors)
target_sheet = None
for sheet_name in reversed(xlsx_file.sheet_names):
    print(sheet_name)
    # Use a more flexible pattern to handle spelling errors like "Weeek" vs "Week"
    if re.search(r'we+ek?\s+endin?g', sheet_name, re.IGNORECASE):
        target_sheet = sheet_name
        break

vlink_team_details_sheet = "VLink Team Details"