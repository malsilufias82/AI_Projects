
#!/usr/bin/env python3
from pathlib import Path
import openpyxl

excel_path = Path(__file__).parent / "data" / "Project_Phoenix_ Status Update- Product Team.xlsx"
sheet_name = "Week Ending 28-06-2026"

wb = openpyxl.load_workbook(excel_path, data_only=True)
ws = wb[sheet_name]

template_strings = [
    "Your Name",
    "✅ Work Completed Today",
    "🔄 Work in Progress",
    "⏳ Planned for Tomorrow",
    "🚧 Blockers / Support Needed / Impact of the blocker",
    "📝 Additional Notes",
    "Today's activity",
    "Completed Today",
    "Work in Progress",
    "Planned for Tomorrow",
    "Blockers / Support Needed",
    "Additional Notes",
    "-",
    "\n",
    "\t"
]

for row_idx, row in enumerate(ws.iter_rows(values_only=True), 1):
    if row_idx in [6, 7, 8]:  # rows for H N Sridhara, Paritosh, Sanjeev
        print(f"\n=== Row {row_idx} ===")
        print(f"Employee: {row[3]}")
        for col_idx in range(6, 11):
            if col_idx < len(row):
                val = row[col_idx]
                if val:
                    print(f"  Col {col_idx} (G-K): {repr(val)}")
                    cleaned_val = val.strip()
                    for ts in template_strings:
                        cleaned_val = cleaned_val.replace(ts, "")
                    cleaned_val = cleaned_val.strip()
                    print(f"  Cleaned value: {repr(cleaned_val)}, len: {len(cleaned_val)}")

wb.close()
