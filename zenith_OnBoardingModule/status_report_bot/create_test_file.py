
import openpyxl
from pathlib import Path

data_dir = Path(__file__).parent / "data"
data_dir.mkdir(exist_ok=True)

wb = openpyxl.Workbook()

# First sheet: 10-07-2026
ws1 = wb.active
ws1.title = "10-07-2026"
ws1["B2"] = "Aashita Jain"
ws1["B3"] = "Arun Jain"
ws1["C2"] = "TL"
ws1["C3"] = "Aashita Jain"
ws1["D4"] = "On Leave"  # Aashita is on leave
ws1["E5"] = "Completed some work"  # Arun completed work

# Second sheet: 12-07-2026
ws2 = wb.create_sheet("12-07-2026")
ws2["B2"] = "Yuvraj Kaushik"
ws2["B3"] = "Aashita Jain"
ws2["C2"] = "Aashita Jain"
ws2["C3"] = "TL"
ws2["F4"] = "Yuvraj completed his report"  # Yuvraj has completed

wb.save(data_dir / "test_platform_team.xlsx")

print("Created test_platform_team.xlsx in data folder!")
