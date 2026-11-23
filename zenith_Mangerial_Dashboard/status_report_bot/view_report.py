
import openpyxl
from pathlib import Path

# Path to the generated report
report_path = Path(__file__).parent / "reports" / "status_report_week_ending_10-07-2026_120747.xlsx"

if not report_path.exists():
    print(f"Report not found at {report_path}")
else:
    wb = openpyxl.load_workbook(report_path, read_only=True, data_only=True)
    ws = wb.active
    print(f"Report contents for {report_path.name}:")
    print("=" * 80)
    for row in ws.iter_rows(values_only=True):
        # Join with tabs to make it readable
        print("\t".join(str(cell) if cell is not None else "" for cell in row))
    wb.close()
