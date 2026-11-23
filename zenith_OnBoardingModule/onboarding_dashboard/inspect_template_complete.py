
import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import PatternFill

# First use pandas to get all headers
df_template = pd.read_excel("data/template-new_emp.xlsx", header=None)
print("=== Template Excel Column Headers (Row 1 in Excel) ===")
headers = df_template.iloc[0].tolist()
for idx, h in enumerate(headers):
    print(f"Column {idx} (Excel col {chr(65+idx)}): {h}")

print("\n\n=== Now Checking Excel File for Cells with Fill Color ===\n")
wb = load_workbook("data/template-new_emp.xlsx")
ws = wb.active
for col_idx in range(1, ws.max_column +1):
    cell = ws.cell(row=1, column=col_idx)  # check header row first
    fill = cell.fill
    color_found = False
    if isinstance(fill, PatternFill):
        if fill.start_color.index not in ["00000000", "FFFFFFFF"]:
            print(f"Header Cell {cell.coordinate} (value: '{headers[col_idx-1]}') has fill color: index={fill.start_color.index}, rgb={fill.start_color.rgb if hasattr(fill.start_color, 'rgb') else 'N/A'}")
            color_found = True
    # Also check row 3 (first data row) for any green cells just in case
    cell_row3 = ws.cell(row=3, column=col_idx)
    fill_row3 = cell_row3.fill
    if isinstance(fill_row3, PatternFill) and fill_row3.start_color.index not in ["00000000", "FFFFFFFF"]:
        print(f"Data Row 3 Cell {cell_row3.coordinate} (value: '{cell_row3.value}') has fill color: index={fill_row3.start_color.index}, rgb={fill_row3.start_color.rgb if hasattr(fill_row3.start_color, 'rgb') else 'N/A'}")
