
from openpyxl import load_workbook

wb = load_workbook("data/BLK Onboarding Tracker.xlsx", data_only=True)
ws = wb["Phase1 - Machine Setup"]

print("=== Looking for BLK Login Credentials task ===")
for row_idx in range(6, ws.max_row + 1):
    day = ws.cell(row=row_idx, column=2).value
    area = ws.cell(row=row_idx, column=3).value
    action = ws.cell(row=row_idx, column=4).value
    if action and "BLK" in str(action) and "Credential" in str(action):
        print(f"Row {row_idx}: day={day}, area={area}, action={action}")
