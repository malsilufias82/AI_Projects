
from openpyxl import load_workbook

wb = load_workbook("data/BLK Onboarding Tracker.xlsx", data_only=True)
ws = wb["Phase1 - Machine Setup"]

# Get employee names and their column indices
employee_names = []
employee_cols = {}
for col_idx in range(9, ws.max_column + 1):
    cell_val = ws.cell(row=2, column=col_idx).value
    if cell_val:
        name = str(cell_val).strip()
        if name:
            employee_names.append(name)
            employee_cols[name] = col_idx

print("=== 'Receive BLK Login Credentials' task status for employees ===")
for emp in employee_names:
    col_idx = employee_cols[emp]
    status_val = ws.cell(row=13, column=col_idx).value  # task is at row 13
    print(f"{emp}: {status_val}")
