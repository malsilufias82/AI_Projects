
import openpyxl
from pathlib import Path

data_dir = Path(__file__).parent / "data"
data_dir.mkdir(exist_ok=True)

wb = openpyxl.Workbook()

# First sheet: 10-07-2026
ws1 = wb.active
ws1.title = "10-07-2026"
# Row 0: Header (ignored)
ws1.append(["Column1", "Column2", "Column3", "Column4"])
# Row 1: Employees
ws1.append(["", "Aashita Jain", "Arun Jain", ""])
# Row 2: Team Leads
ws1.append(["", "TL", "Aashita Jain", ""])
# Rows 3-6: Data (to reach >=6 rows total!)
ws1.append(["", "On Leave", "", ""])  # Aashita is on leave
ws1.append(["", "", "Work completed", ""])  # Arun has content
ws1.append(["", "", "", ""])  # Extra row
ws1.append(["", "", "", ""])  # Extra row

# Second sheet: 12-07-2026
ws2 = wb.create_sheet("12-07-2026")
# Row 0: Header (ignored)
ws2.append(["Column1", "Column2", "Column3", "Column4"])
# Row 1: Employees
ws2.append(["", "Yuvraj Kaushik", "Aashita Jain", ""])
# Row 2: Team Leads
ws2.append(["", "Aashita Jain", "TL", ""])
# Rows3-6: Data
ws2.append(["", "Yuvraj's completed work", "", ""])  # Yuvraj has content
ws2.append(["", "", "", ""])  # Extra row
ws2.append(["", "", "", ""])  # Extra row
ws2.append(["", "", "", ""])  # Extra row

wb.save(data_dir / "test_platform_team.xlsx")
print("Created proper test_platform_team.xlsx!")
