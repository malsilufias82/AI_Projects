
import openpyxl
from pathlib import Path

output_file = Path(__file__).parent / "debug_output.txt"

with open(output_file, "w", encoding="utf-8") as f:
    f.write("=== Checking generated report (latest) ===\n")
    report_file = Path(r"c:\Users\anamika.mishra\Downloads\status_report_bot\status_report_bot\status_report_latest.xlsx")
    if report_file.exists():
        wb = openpyxl.load_workbook(report_file, read_only=True, data_only=True)
        ws = wb.active
        for i, row in enumerate(ws.iter_rows(values_only=True), 1):
            f.write(f"Row {i}: {row}\n")
        wb.close()
    else:
        f.write("Not found\n")

print(f"Output written to {output_file}")
