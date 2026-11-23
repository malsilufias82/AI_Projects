
from openpyxl import load_workbook

wb = load_workbook("data/BLK Onboarding Tracker.xlsx")
ws = wb["Resource List"]

# Headers are in row 2 (index 1 in 0-based)
headers = []
for cell in ws[2]:
    headers.append(cell.value)

# Data starts from row 3
data_rows = []
for row in ws.iter_rows(min_row=3, values_only=True):
    # Only add rows if at least one non-None value
    if any(row):
        data_rows.append(row)

import pandas as pd

df = pd.DataFrame(data_rows, columns=headers)

print("Resource List:")
print(df)
