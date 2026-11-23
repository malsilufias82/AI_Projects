
import openpyxl
from pathlib import Path
import sys
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent / "src"))

def debug_parse_platform_sheet(ws, team_name):
    print("=== debug_parse_platform_sheet ===")
    from dataclasses import dataclass

    @dataclass
    class EmployeeRecord:
        employee_name: str
        employee_id: str = ""
        team: str = ""
        team_lead: str = ""
        project: str = ""
        status: str = "Pending"
        is_leave: bool = False
        last_updated: datetime | None = None

    records = []
    skip_emp_keywords = ["name", "employee", "team", "lead", "date", "monday", "tuesday", 
                         "wednesday", "thursday", "friday", "✅", "🔄", "⏳", "🚧", "📝", "status", 
                         "report", "your", "pillar", "vlinker", "role", "stories", "format", 
                         "saurabh", "none", "developer", "perl", "full", "stack",
                         "product", "engineering", "afe", "c++", "what did you do", 
                         "impediments", "what will you do", "?", "yesterday", "today"]
    print(f"skip_emp_keywords: {skip_emp_keywords}")

    # First, read the header rows to get employee names and team leads
    rows = list(ws.iter_rows(values_only=True))
    print(f"Total rows in sheet: {len(rows)}")
    for i, row in enumerate(rows):
        print(f"Row {i}: {row}")
    if len(rows) < 6:
        print("Too few rows!")
        return []

    employees_row_idx = 1  # 0-based (2nd row in 1-based)
    team_leads_row_idx = 2  # 0-based (3rd row in 1-based)

    team_leads_row = rows[team_leads_row_idx]
    employees_row = rows[employees_row_idx]
    print(f"\nemployees_row (index {employees_row_idx}): {employees_row}")
    print(f"team_leads_row (index {team_leads_row_idx}): {team_leads_row}")

    # Now iterate over columns
    for col_idx in range(len(employees_row)):
        print(f"\nChecking column {col_idx}:")
        employee_name = employees_row[col_idx]
        print(f"  employee_name: {employee_name} (type: {type(employee_name)})")
        team_lead = team_leads_row[col_idx] if col_idx < len(team_leads_row) else None
        print(f"  team_lead: {team_lead} (type: {type(team_lead)})")

        if not employee_name or not isinstance(employee_name, str):
            print("  Skipping: no employee name or not a string")
            continue
        employee_name = employee_name.strip()
        if len(employee_name) < 2:
            print("  Skipping: name too short")
            continue
        skip = False
        for kw in skip_emp_keywords:
            if kw in employee_name.lower():
                print(f"  Skipping: contains keyword '{kw}'")
                skip = True
                break
        if skip:
            continue

        # Now check if any daily updates exist for this employee in the rows below
        is_leave = False
        is_completed = False
        print("  Checking data rows:")
        # Check data rows (starting from employee_row_idx + 1)
        for row_idx in range(employees_row_idx + 1, min(len(rows), employees_row_idx + 20)):
            row = rows[row_idx]
            if col_idx >= len(row):
                print(f"    Row {row_idx}: column {col_idx} out of range")
                continue
            cell_val = row[col_idx]
            print(f"    Row {row_idx}, col {col_idx}: cell_val={cell_val} (type: {type(cell_val)})")
            if cell_val and isinstance(cell_val, str):
                cell_val = cell_val.strip()
                if len(cell_val) == 0:
                    print(f"      Empty string")
                    continue
                print(f"      Checking for leave: '{cell_val.lower()}'")
                if "leave" in cell_val.lower():
                    is_leave = True
                    print(f"      Found leave!")
                    break
                
                # Check _has_actual_content (let's copy that too!)
                cleaned_val = cell_val.strip()
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
                ]
                for ts in template_strings:
                    cleaned_val = cleaned_val.replace(ts, "")
                # Remove punctuation and whitespace
                cleaned_val = cleaned_val.translate(str.maketrans('', '', ':-_• \n\t\r'))
                cleaned_val = cleaned_val.strip()
                has_actual_content = len(cleaned_val) >0 
                print(f"      has_actual_content: {has_actual_content} (cleaned_val: '{cleaned_val}')")
                
                if has_actual_content:
                    is_completed = True
                    print(f"      Found actual content!")

        # Determine status
        if is_leave:
            status = "Completed"
        elif is_completed:
            status = "Completed"
        else:
            status = "Pending"

        tl_str = str(team_lead).strip() if (team_lead and isinstance(team_lead, str)) else ""
        print(f"  tl_str: '{tl_str}'")
        if tl_str == "TL":
            # If it says "TL", the employee is their own TL
            tl_str = employee_name
        elif not tl_str or tl_str == "Team Lead":
            tl_str = "Unassigned"

        print(f"  Adding record: {employee_name} (status={status}, is_leave={is_leave}, tl={tl_str})")

        record = EmployeeRecord(
            employee_name=employee_name,
            team=team_name,
            team_lead=tl_str,
            status=status,
            is_leave=is_leave,
            last_updated=datetime.now()
        )

        if not any(r.employee_name == record.employee_name for r in records):
            records.append(record)

    print(f"\nReturning {len(records)} records")
    return records


file_path = Path(__file__).parent / "data" / "test_platform_team.xlsx"
wb = openpyxl.load_workbook(file_path, read_only=True, data_only=True)
ws1 = wb["10-07-2026"]
records = debug_parse_platform_sheet(ws1, "Platform Engineering")
print(f"\nFinal records: {records}")
wb.close()
