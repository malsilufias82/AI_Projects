
#!/usr/bin/env python3
from pathlib import Path
import openpyxl

excel_path = Path(__file__).parent / "data" / "Project_Phoenix_ Status Update- Product Team.xlsx"
sheet_name = "Week Ending 28-06-2026"

wb = openpyxl.load_workbook(excel_path, data_only=True)
ws = wb[sheet_name]

print(f"Checking {sheet_name} for employees under Sanjeev Biswas:")
for row_idx, row in enumerate(ws.iter_rows(values_only=True), 1):
    if row_idx < 5:
        continue  # skip header rows
    employee_name = row[3] if row[3] else ""
    team_lead = row[4] if row[4] else ""
    if "Sanjeev" in str(employee_name) or "Sanjeev" in str(team_lead):
        print(f"\nRow {row_idx}:")
        print(f"  Employee: {employee_name}")
        print(f"  Team Lead: {team_lead}")
        print(f"  Columns G-L (daily updates):")
        for col_idx in range(6, min(12, len(row))):
            val = row[col_idx]
            if val:
                print(f"    Column {chr(65+col_idx)}: {repr(val)}")

wb.close()
