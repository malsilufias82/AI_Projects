
from openpyxl import load_workbook

wb = load_workbook("data/BLK Onboarding Tracker.xlsx", data_only=True)
ws_resources = wb["Resource List"]
headers = [cell.value for cell in ws_resources[2]]

print("Headers in Resource List (row 2):")
for i, h in enumerate(headers):
    if h is not None:
        print(f"  Column {i+1} (excel index): '{h}'")

print("\nHeaders in template-new_emp.xlsx (row 1):")
wb_template = load_workbook("data/template-new_emp.xlsx", data_only=True)
ws_template = wb_template.active
template_headers = [cell.value for cell in ws_template[1]]
for i, h in enumerate(template_headers):
    if h is not None:
        print(f"  Column {i+1}: '{h}'")

