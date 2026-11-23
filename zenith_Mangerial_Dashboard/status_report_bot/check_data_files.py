
import openpyxl
from pathlib import Path

data_dir = Path(__file__).parent / "data"

for file in data_dir.glob("*.xlsx"):
    print(f"\n--- {file.name} ---")
    try:
        wb = openpyxl.load_workbook(file, read_only=True)
        print("Sheets:", wb.sheetnames)
        wb.close()
    except Exception as e:
        print(f"Error: {e}")
