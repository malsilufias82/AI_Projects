
import openpyxl

wb = openpyxl.load_workbook('reports/status_report_week_ending_10-07-2026_195844.xlsx', data_only=True)
ws = wb.active

with open('report_content.txt', 'w', encoding='utf-8') as f:
    for row in ws.iter_rows(values_only=True):
        f.write('\t'.join(str(cell) if cell is not None else '' for cell in row) + '\n')

wb.close()
print("Report content written to report_content.txt")
