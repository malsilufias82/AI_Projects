
from openpyxl import load_workbook

wb = load_workbook("data/BLK Onboarding Tracker.xlsx")
print("All sheet names in BLK tracker:")
for name in wb.sheetnames:
    print(f"- '{name}'")
