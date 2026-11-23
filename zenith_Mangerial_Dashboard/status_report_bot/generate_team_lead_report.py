
#!/usr/bin/env python3
"""Generate Team Lead Status Report"""

import sys
import json
import os
import re
from pathlib import Path
from datetime import datetime, date
import openpyxl
from openpyxl.styles import Font, Alignment, PatternFill

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from config import load_config
from excel_reader import ExcelReader, EmployeeRecord


def is_same_week(date1: date, date2: date) -> bool:
    """Check if two dates are in the same ISO week."""
    return date1.isocalendar()[:2] == date2.isocalendar()[:2]

def parse_week_date(sheet_name: str) -> date | None:
    """Parse week ending date from sheet name (supports multiple formats)."""
    # Try multiple date patterns
    patterns = [
        r"(\d{1,2})-(\d{1,2})-(\d{4})",  # DD-MM-YYYY
        r"Week Ending (\d{1,2})-(\d{1,2})-(\d{4})",  # Week Ending DD-MM-YYYY
        r"Week ending (\d{1,2})-(\d{1,2})",  # Week ending DD-MM (assume current year)
    ]

    for pattern in patterns:
        match = re.search(pattern, sheet_name)
        if match:
            try:
                if len(match.groups()) == 3:
                    day, month, year = map(int, match.groups())
                    return date(year, month, day)
                elif len(match.groups()) == 2:
                    day, month = map(int, match.groups())
                    return date(datetime.now().year, month, day)
            except ValueError:
                continue
    return None


class SkippedEmployeesTracker:
    """Tracks employees who are pending for 2 consecutive weeks and marks them as skipped."""

    def __init__(self, history_file: Path):
        self.history_file = history_file
        self.history = self._load()

    def _load(self):
        if not os.path.exists(self.history_file):
            return {"last_processed_week": None, "employees": {}}
        try:
            with open(self.history_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return {"last_processed_week": None, "employees": {}}

    def _save(self):
        os.makedirs(os.path.dirname(self.history_file), exist_ok=True)
        with open(self.history_file, "w", encoding="utf-8") as f:
            json.dump(self.history, f, indent=2)

    def update_for_week(self, week_date: date, employee_statuses: dict[str, bool]):
        """
        Update the tracker for a specific week.
        employee_statuses is a dict of emp_key -> is_pending
        """
        week_key = week_date.strftime("%Y-%m-%d")

        # Only process if we haven't processed this week before
        if self.history.get("last_processed_week") == week_key:
            return

        # Reset for new week
        self.history["last_processed_week"] = week_key

        for emp_key, is_pending in employee_statuses.items():
            current = self.history["employees"].get(emp_key, {"consecutive_pending": 0, "is_skipped": False})

            # If already skipped, keep as skipped
            if current["is_skipped"]:
                continue

            # Update consecutive pending count
            if is_pending:
                current["consecutive_pending"] += 1
            else:
                current["consecutive_pending"] = 0  # Reset if they completed

            # Mark as skipped if 2 consecutive pending weeks
            if current["consecutive_pending"] >= 2:
                current["is_skipped"] = True

            self.history["employees"][emp_key] = current

        self._save()

    def is_skipped(self, emp_key: str) -> bool:
        """Check if an employee is marked as skipped."""
        return self.history.get("employees", {}).get(emp_key, {}).get("is_skipped", False)


def get_all_available_weeks(config):
    """Collect all unique week dates available across all Excel files (local or SharePoint)."""
    week_groups = {}  # key: (year, week_number), value: latest date in week
    from excel_reader import ExcelReader
    reader = ExcelReader(config)

    for team_file in config.team_excel_files:
        file_path_or_url = team_file["file_path"]
        file_type = team_file.get("type", "local")
        temp_file_path = None
        
        try:
            if file_type == "sharepoint":
                # Download to temp file using ExcelReader's methods
                import tempfile
                
                temp_dir = tempfile.mkdtemp(prefix="status_report_bot_")
                temp_file_path = os.path.join(temp_dir, f"{team_file['team_name'].replace(' ', '_')}.xlsx")
                
                downloaded = reader._download_sharepoint_file(file_path_or_url, temp_file_path)
                
                if not downloaded:
                    continue
                
                actual_file_path = temp_file_path
            else:
                actual_file_path = file_path_or_url
            
            wb = openpyxl.load_workbook(actual_file_path, read_only=True)
            for sheet_name in wb.sheetnames:
                week_date = parse_week_date(sheet_name)
                if week_date:
                    iso_cal = week_date.isocalendar()
                    week_key = (iso_cal.year, iso_cal.week)
                    # Keep the latest date in each week
                    if week_key not in week_groups or week_date > week_groups[week_key]:
                        week_groups[week_key] = week_date
            wb.close()
        except Exception as e:
            continue
        finally:
            if temp_file_path and os.path.exists(temp_file_path):
                try:
                    os.remove(temp_file_path)
                    os.rmdir(os.path.dirname(temp_file_path))
                except Exception:
                    pass

    return sorted(list(week_groups.values()))  # Return in chronological order


def generate_report_for_week(week_date, config, reader, skipped_tracker):
    """Generate a single report for a specific week."""
    records, sheet_info = reader.read_employee_records(target_week_date=week_date)

    if not records:
        print(f"No records found for week {week_date.strftime('%d-%m-%Y')}, skipping report.")
        return

    # Group records by Team Lead and track employee statuses
    tl_records = {}
    employee_statuses = {}
    for rec in records:
        # Skip invalid employee names that are template strings
        skip_keywords = ["what did you do", "impediments", "what will you do", "?", "yesterday", "today", "name", "employee", "team", "lead", "date", "monday", "tuesday", "wednesday", "thursday", "friday", "✅", "🔄", "⏳", "🚧", "📝", "status", "report", "your", "pillar", "vlinker", "role", "stories", "format", "none", "sick", "unassigned", "on leave", "leave", "developer", "perl", "full", "stack", "product", "engineering", "afe", "c++"]
        if any(kw in rec.employee_name.lower() for kw in skip_keywords):
            continue
        tl = rec.team_lead or "Unassigned"
        if tl not in tl_records:
            tl_records[tl] = []
        tl_records[tl].append(rec)

        emp_key = f"{rec.employee_name}::{rec.team_lead}"  # Unique key for employee+TL
        is_leave = hasattr(rec, "is_leave") and rec.is_leave
        is_pending = (not is_leave) and (rec.status.lower() == "pending")
        employee_statuses[emp_key] = is_pending

    # Update skipped tracker with this week's data
    skipped_tracker.update_for_week(week_date, employee_statuses)

    # Get list of skipped employees
    skipped_employees = []
    for rec in records:
        emp_key = f"{rec.employee_name}::{rec.team_lead}"
        if skipped_tracker.is_skipped(emp_key):
            skipped_employees.append(rec.employee_name)

    # Create Excel workbook
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Team Lead Status Report"

    # Write week/sheet info at top
    current_row = 1
    for team_name, sheet_names in sheet_info.items():
        sheet_names_str = ", ".join(sheet_names)
        ws.cell(row=current_row, column=1, value=f"{team_name}:")
        ws.cell(row=current_row, column=2, value=sheet_names_str)
        current_row += 1

    # Add a blank row
    current_row += 1

    # Write headers
    headers = ["Name", "Status", "Status Report Reviewed by TL"]
    for col_num, header in enumerate(headers, 1):
        cell = ws.cell(row=current_row, column=col_num, value=header)
        cell.font = Font(bold=True)
        cell.alignment = Alignment(horizontal="center", vertical="center")
        cell.fill = PatternFill(start_color="D3D3D3", end_color="D3D3D3", fill_type="solid")
    current_row +=1

    # Write data rows
    tl_pending = {}  # Track pending employees per TL
    for tl_name, team_records in sorted(tl_records.items()):
        # Determine team status: Completed if all NON-skipped, NON-leave team members are Completed
        non_skipped = []
        tl_pending[tl_name] = []
        for rec in team_records:
            emp_key = f"{rec.employee_name}::{rec.team_lead}"
            is_skipped = skipped_tracker.history.get("employees", {}).get(emp_key, {}).get("is_skipped", False)
            is_leave = hasattr(rec, "is_leave") and rec.is_leave
            if is_skipped or is_leave:
                continue
            non_skipped.append(rec)
            if rec.status.lower() == "pending":
                tl_pending[tl_name].append(rec.employee_name)

        all_completed = all(rec.status.lower() == "completed" for rec in non_skipped)
        team_status = "Completed" if all_completed else "Pending"

        # Write TL row
        tl_cell = ws.cell(row=current_row, column=1, value=tl_name)
        tl_cell.alignment = Alignment(horizontal="left", vertical="center")
        tl_cell.font = Font(bold=True)

        tl_status_cell = ws.cell(row=current_row, column=2, value=team_status)
        tl_status_cell.alignment = Alignment(horizontal="center", vertical="center")
        if team_status == "Completed":
            tl_status_cell.fill = PatternFill(start_color="CCFFCC", end_color="CCFFCC", fill_type="solid")
        else:
            tl_status_cell.fill = PatternFill(start_color="FFCCCC", end_color="FFCCCC", fill_type="solid")

        tl_review_cell = ws.cell(row=current_row, column=3, value="")
        tl_review_cell.alignment = Alignment(horizontal="center", vertical="center")
        current_row += 1

        # Write team member rows (skip the team lead themselves)
        for rec in team_records:
            if rec.employee_name == tl_name:
                continue  # Skip team lead duplicate entry
            emp_key = f"{rec.employee_name}::{rec.team_lead}"
            is_skipped = skipped_tracker.is_skipped(emp_key)
            
            # Indent team member name
            emp_name = f"  └─ {rec.employee_name}"
            if is_skipped:
                emp_name += " (Skipped)"
            if hasattr(rec, "is_leave") and rec.is_leave:
                emp_name += " (On Leave)"
            
            emp_cell = ws.cell(row=current_row, column=1, value=emp_name)
            emp_cell.alignment = Alignment(horizontal="left", vertical="center")
            
            emp_status = rec.status
            if hasattr(rec, "is_leave") and rec.is_leave:
                emp_status = "Completed"
            if is_skipped:
                emp_status = "Skipped"
            
            emp_status_cell = ws.cell(row=current_row, column=2, value=emp_status)
            emp_status_cell.alignment = Alignment(horizontal="center", vertical="center")
            if emp_status == "Completed":
                emp_status_cell.fill = PatternFill(start_color="CCFFCC", end_color="CCFFCC", fill_type="solid")
            elif emp_status == "Pending":
                emp_status_cell.fill = PatternFill(start_color="FFCCCC", end_color="FFCCCC", fill_type="solid")
            elif emp_status == "Skipped":
                emp_status_cell.fill = PatternFill(start_color="FFFFCC", end_color="FFFFCC", fill_type="solid")
            
            emp_review_cell = ws.cell(row=current_row, column=3, value="")
            emp_review_cell.alignment = Alignment(horizontal="center", vertical="center")
            current_row += 1

    # Auto-adjust column widths
    for column in ws.columns:
        max_length = 0
        column_letter = column[0].column_letter
        for cell in column:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
        adjusted_width = min(max_length + 2, 50)
        ws.column_dimensions[column_letter].width = adjusted_width

    # Save the report with week ending date and timestamp
    date_str = week_date.strftime("%d-%m-%Y")
    timestamp = datetime.now().strftime("%H%M%S")
    report_filename = f"status_report_week_ending_{date_str}_{timestamp}.xlsx"
    report_path = Path(__file__).parent / "reports" / report_filename
    report_path.parent.mkdir(exist_ok=True)
    wb.save(report_path)
    # Also save a copy to the project root as "status_report_latest.xlsx"
    import shutil
    latest_report_path = Path(__file__).parent / "status_report_latest.xlsx"
    shutil.copyfile(report_path, latest_report_path)
    
    print(f"\nReport for week ending {date_str} generated at: {report_path}")
    print(f"   - Also saved to: {latest_report_path}")
    print(f"   - {len(tl_records)} Team Leads")

    # Calculate pending TLs (excluding skipped employees)
    pending_tls = []
    for tl_name in tl_records.keys():
        if len(tl_pending.get(tl_name, [])) > 0:
            pending_tls.append(tl_name)

    print(f"   - {len(pending_tls)} Teams with pending status reports")
    print(f"   - {len(skipped_employees)} Skipped employees (pending for 2+ weeks): {', '.join(skipped_employees) if skipped_employees else 'None'}")


def generate_team_lead_report(target_date_str: str | None = None):
    config = load_config()
    reader = ExcelReader(config)
    skipped_tracker = SkippedEmployeesTracker(Path(__file__).parent / "data" / "skipped_employees.json")

    if target_date_str:
        # Process single target week
        try:
            day, month, year = map(int, target_date_str.split("-"))
            if len(str(year)) == 2:
                year += 2000
            target_date = date(year, month, day)
        except Exception as e:
            print(f"❌ Invalid date format: {target_date_str}. Please use DD-MM-YYYY or DD-MM-YY.")
            return
        generate_report_for_week(target_date, config, reader, skipped_tracker)
    else:
        # Process all available weeks in chronological order
        all_weeks = get_all_available_weeks(config)
        if not all_weeks:
            print("No week dates found in any Excel files.")
            return

        print(f"Found {len(all_weeks)} weeks to process.")
        for week_date in all_weeks:
            generate_report_for_week(week_date, config, reader, skipped_tracker)


if __name__ == "__main__":
    import sys
    target_date_str = None
    if len(sys.argv) > 1:
        target_date_str = sys.argv[1]
    generate_team_lead_report(target_date_str)
