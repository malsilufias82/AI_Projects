
import openpyxl

wb = openpyxl.load_workbook('reports/status_report_week_ending_10-07-2026_195844.xlsx', data_only=True)
ws = wb.active
for row in ws.iter_rows(values_only=True):
    print(row)
wb.close()
