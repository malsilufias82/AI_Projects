
from openpyxl import load_workbook

wb = load_workbook("data/BLK Onboarding Tracker.xlsx")

print("📑 Sheet names in BLK Onboarding Tracker:", wb.sheetnames)
print()

for sheet_name in wb.sheetnames:
    ws = wb[sheet_name]
    print(f"=== Sheet: {sheet_name} ===")
    
    # Get first row as headers
    headers = []
    for cell in ws[1]:
        headers.append(cell.value)
    print("Headers:", headers)
    
    # Get first 3 data rows
    print("\nFirst 3 rows:")
    for i, row in enumerate(ws.iter_rows(min_row=2, max_row=4), 2):
        row_values = [cell.value for cell in row]
        print(f"Row {i}: {row_values}")
    print()
