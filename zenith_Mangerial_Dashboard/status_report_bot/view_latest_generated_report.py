
#!/usr/bin/env python3
"""Read and display the latest generated status report"""
import openpyxl
from pathlib import Path

def main():
    reports_folder = Path(__file__).parent / "reports"
    report_files = sorted(
        [f for f in reports_folder.iterdir() if f.suffix == ".xlsx" and not f.name.startswith("~$")],
        key=lambda f: f.stat().st_mtime,
        reverse=True
    )
    
    if not report_files:
        print("No reports found!")
        return
    
    latest_report = report_files[0]
    print(f"Latest report: {latest_report.name}")
    print("=" * 80)
    
    wb = openpyxl.load_workbook(latest_report, data_only=True)
    ws = wb.active
    
    for row in ws.iter_rows(values_only=True):
        print("\t".join(str(cell) if cell is not None else "" for cell in row))
    
    wb.close()

if __name__ == "__main__":
    main()
