
#!/usr/bin/env python3
from openpyxl import load_workbook
from pathlib import Path

reports_dir = Path(__file__).parent / "reports"
latest_report = max(reports_dir.glob("status_report_week_ending_*.xlsx"), key=lambda p: p.stat().st_mtime)

print(f"📊 Latest Report: {latest_report.name}\n")
wb = load_workbook(latest_report)
ws = wb.active

for row in ws.iter_rows(values_only=True):
    print("\t".join(str(cell) if cell is not None else "" for cell in row))
