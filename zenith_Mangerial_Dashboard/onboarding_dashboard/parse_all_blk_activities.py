
from openpyxl import load_workbook

wb = load_workbook("data/BLK Onboarding Tracker.xlsx")

print("=== Phase1 - Machine SetUp ===")
ws_machine = wb["Phase1 - Machine SetUp"]
machine_headers = []
for idx, cell in enumerate(ws_machine[1]):  # First row
    machine_headers.append((idx, cell.value))
print("Machine Setup Headers:", machine_headers)

print("\nFirst 10 rows, first 15 columns:")
for row_idx, row in enumerate(ws_machine.iter_rows(max_row=15, max_col=20, values_only=True), start=1):
    print(f"Row {row_idx}: {row}")

print("\n=== Phase2 - Project Setup ===")
ws_project = wb["Phase2 - Project Setup"]
project_headers = []
for idx, cell in enumerate(ws_project[1]):
    project_headers.append((idx, cell.value))
print("Project Setup Headers:", project_headers)
print("First 10 rows, first 15 columns:")
for row_idx, row in enumerate(ws_project.iter_rows(max_row=15, max_col=20, values_only=True), start=1):
    print(f"Row {row_idx}: {row}")
