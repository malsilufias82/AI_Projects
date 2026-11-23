
from openpyxl import load_workbook

wb = load_workbook("data/BLK Onboarding Tracker.xlsx", data_only=True)
ws = wb["Resource List"]
headers = [cell.value for cell in ws[2]]

for row_num in [3, 4, 5]:
    print(f"\nRow {row_num}:")
    row_values = [cell.value for cell in ws[row_num]]
    for i, (header, value) in enumerate(zip(headers, row_values)):
        print(f"  Column {i+1} ({header}): {value}")
