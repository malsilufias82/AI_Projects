
#!/usr/bin/env python3
"""Check the status_report.xlsx in data folder"""
import openpyxl
from pathlib import Path

def main():
    data_dir = Path(__file__).parent / "data"
    status_report_path = data_dir / "status_report.xlsx"
    
    if not status_report_path.exists():
        print("status_report.xlsx not found!")
        return
    
    print(f"Opening {status_report_path}")
    wb = openpyxl.load_workbook(status_report_path, read_only=True, data_only=True)
    print("Sheet names:", wb.sheetnames)
    
    for sheet_name in wb.sheetnames:
        print(f"\n--- Sheet: {sheet_name} ---")
        ws = wb[sheet_name]
        for i, row in enumerate(ws.iter_rows(values_only=True)):
            print(f"Row {i}: {row}")
            if i > 20:
                break
    
    wb.close()

if __name__ == "__main__":
    main()
