"""
excel_reader.py
----------------
Reads status from the specific Excel files (local or SharePoint):
- Project_Phoenix_ Status Update - Platform team.xlsx
- Project_Phoenix_ Status Update- Product Team.xlsx
- Data Team - Daily Tracker.xlsx
"""

import re
import io
import os
import tempfile
from urllib.parse import urlparse, parse_qs, unquote
from dataclasses import dataclass
from datetime import datetime, date
from typing import List, Optional

import openpyxl
import requests
from msal import ConfidentialClientApplication

from config import AppConfig
from logger import get_logger

GRAPH_BASE_URL = "https://graph.microsoft.com/v1.0"


@dataclass
class EmployeeRecord:
    """A single employee's status record."""
    employee_name: str
    employee_id: str = ""
    team: str = ""
    team_lead: str = ""
    project: str = ""
    status: str = "Pending"  # "Completed" or "Pending"
    is_leave: bool = False
    last_updated: Optional[datetime] = None


class ExcelReader:
    """Reads and parses status from the team Excel files."""
    
    @staticmethod
    def _is_same_week(date1: date, date2: date) -> bool:
        """Check if two dates are in the same ISO week."""
        return date1.isocalendar()[:2] == date2.isocalendar()[:2]
    
    @staticmethod
    def _has_actual_content(cell_val: str) -> bool:
        """Check if cell has actual content beyond template placeholders."""
        if not cell_val or not isinstance(cell_val, str):
            return False
        
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
        
        return len(cleaned_val) > 0

    @staticmethod
    def _parse_sharepoint_url(sharepoint_url):
        """
        Try to parse SharePoint URL to get drive and file info.
        For OneDrive for Business URLs like /personal/... or /sites/...
        """
        parsed = urlparse(sharepoint_url)
        query = parse_qs(parsed.query)
        host = parsed.netloc
        
        # Try to get file name from query
        file_name = None
        if 'file' in query:
            file_name = unquote(query['file'][0])
        
        # Check if it's OneDrive for Business (personal)
        if '/personal/' in parsed.path:
            parts = parsed.path.split('/personal/')
            if len(parts) > 1:
                upn_part = parts[1].split('/')[0]  # like jitender_sachdeva_vlinkinfo_com
                # For OneDrive for Business, Graph endpoint is /users/{upn}/drive/root:/{file_path}:/content
                # But we need the file path in their OneDrive. Alternatively, try to get from sourcedoc.
                # For now, first try the simple download approach with auth, then fall back if needed.
                return {
                    'type': 'personal',
                    'host': host,
                    'upn': upn_part.replace('_', '@', 1).replace('_', '.'),
                    'file_name': file_name
                }
        
        # Check if it's a site
        if '/sites/' in parsed.path:
            return {
                'type': 'site',
                'host': host,
                'site_path': parsed.path.split('/sites/', 1)[1].split('/')[0]
            }
        
        return None

    def __init__(self, config: AppConfig):
        self.config = config
        self.logger = get_logger(__name__, config.logs_folder, config.log_level)
        self._msal_app = None
        self._graph_token = None
        
        # Initialize MSAL app if credentials are provided
        if config.client_id and config.client_secret and config.tenant_id:
            self._msal_app = ConfidentialClientApplication(
                client_id=config.client_id,
                client_credential=config.client_secret,
                authority=f"https://login.microsoftonline.com/{config.tenant_id}",
            )
        else:
            self.logger.warning("Microsoft Graph credentials not found in config; SharePoint files may fail to download without auth.")

    def _get_graph_token(self):
        """Get Microsoft Graph access token using MSAL."""
        if self._graph_token:
            return self._graph_token
        
        if not self._msal_app:
            return None
        
        result = self._msal_app.acquire_token_for_client(scopes=[self.config.graph_scope])
        if "access_token" not in result:
            error_desc = result.get("error_description", "Unknown auth error")
            self.logger.error(f"Failed to acquire Graph API token: {error_desc}")
            return None
        
        self._graph_token = result["access_token"]
        return self._graph_token

    def _download_sharepoint_file(self, sharepoint_url, save_path):
        """
        Download file from SharePoint URL, trying both unauthenticated and authenticated methods.
        """
        # First try the unauthenticated approach with various URL patterns
        candidates = []
        if '?' in sharepoint_url:
            candidates.append(sharepoint_url + '&download=1')
        else:
            candidates.append(sharepoint_url + '?download=1')
        
        if ':x:/g/' in sharepoint_url:
            c2 = sharepoint_url.replace(':x:/g/', ':x:/t/')
            c2 = c2.split('?')[0] + '?download=1' if '?' in c2 else c2 + '?download=1'
            candidates.append(c2)
        
        if ':x:/r/' in sharepoint_url:
            c3 = sharepoint_url.replace(':x:/r/', ':x:/t/')
            c3 = c3.split('?')[0] + '?download=1' if '?' in c3 else c3 + '?download=1'
            candidates.append(c3)
        
        if '?' in sharepoint_url:
            base = sharepoint_url.split('?')[0]
            candidates.append(base + '?download=1')
        
        # Try unauthenticated first
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        for candidate in candidates:
            try:
                self.logger.debug(f"Trying unauthenticated download from: {candidate}")
                resp = requests.get(candidate, headers=headers, allow_redirects=True, timeout=30)
                if resp.status_code == 200:
                    ct = resp.headers.get('content-type', '')
                    if (any(x in ct for x in ['spreadsheet', 'excel', 'zip', 'octet-stream']) or 
                        len(resp.content) > 1000 and resp.content[:2] == b'PK'):  # PK is zip/xlsx magic number
                        with open(save_path, 'wb') as f:
                            f.write(resp.content)
                        self.logger.info("Successfully downloaded file via unauthenticated method.")
                        return True
            except Exception as e:
                self.logger.debug(f"Unauthenticated download failed for {candidate}: {e}")
        
        # If unauthenticated failed and we have Graph credentials, try Graph API
        token = self._get_graph_token()
        if token:
            self.logger.info("Trying authenticated download via Microsoft Graph...")
            # Parse the SharePoint URL to try to get drive item info
            parsed = self._parse_sharepoint_url(sharepoint_url)
            if parsed and parsed['type'] == 'personal' and parsed['file_name']:
                # This is a simplistic approach; for real use, you'd need more robust parsing
                # or have the user provide the Graph path directly
                self.logger.warning("Graph API download for personal OneDrive requires exact file path, which we can't reliably get from the share link.")
                # For now, fall back
        
        return False

    def read_employee_records(self, target_week_date: date | None = None) -> tuple[List[EmployeeRecord], dict[str, str]]:
        """Read all team files and combine employee records.
        Returns (records, sheet_info) where sheet_info maps team name to list of sheet names.
        If target_week_date is provided, uses all sheets matching that week.
        """
        all_records: List[EmployeeRecord] = []
        sheet_info = {}
        
        for team_file in self.config.team_excel_files:
            file_path_or_url = team_file["file_path"]
            team_name = team_file["team_name"]
            sheet_pattern = team_file["sheet_pattern"]
            file_type = team_file.get("type", "local")
            
            try:
                records, sheet_names = self._read_single_file(file_path_or_url, team_name, sheet_pattern, file_type, target_week_date)
                if sheet_names:
                    all_records.extend(records)
                    sheet_info[team_name] = sheet_names
                    self.logger.info(f"Read {len(records)} records for {team_name} from sheets: {sheet_names}")
                else:
                    self.logger.warning(f"No matching sheet found for {team_name}")
            except Exception as e:
                self.logger.error(f"Failed to read {team_name}: {e}")

        self.logger.info(f"Total of {len(all_records)} records from all files.")
        return all_records, sheet_info

    def _find_all_sheets_for_week(self, sheet_names: List[str], target_date: date) -> List[str]:
        """Find all sheets that are in the same week as the target date."""
        matching_sheets = []
        for sheet_name in sheet_names:
            parsed_date = self._parse_sheet_date(sheet_name)
            if parsed_date and self._is_same_week(parsed_date, target_date):
                matching_sheets.append(sheet_name)
        return matching_sheets

    def _read_single_file(self, file_path_or_url: str, team_name: str, sheet_pattern: str, file_type: str = "local", target_week_date: date | None = None) -> tuple[List[EmployeeRecord], List[str]]:
        """Read a single team's Excel file (local or SharePoint). Returns (records, list_of_sheet_names)."""
        temp_file_path = None
        
        try:
            if file_type == "sharepoint":
                # Download SharePoint file to temp location
                temp_dir = tempfile.mkdtemp(prefix="status_report_bot_")
                temp_file_path = os.path.join(temp_dir, f"{team_name.replace(' ', '_')}.xlsx")
                self.logger.info(f"Downloading SharePoint file for {team_name} to {temp_file_path}")
                
                downloaded = self._download_sharepoint_file(file_path_or_url, temp_file_path)
                
                if not downloaded:
                    self.logger.error(f"Failed to download SharePoint file for {team_name}")
                    return [], []
                
                actual_file_path = temp_file_path
            else:
                # Local file
                actual_file_path = file_path_or_url
            
            wb = openpyxl.load_workbook(actual_file_path, read_only=True, data_only=True)
            
            # Find all sheets matching target week date, or latest if no target or no match
            sheet_names = []
            if target_week_date:
                sheet_names = self._find_all_sheets_for_week(wb.sheetnames, target_week_date)
                if not sheet_names:
                    # No sheets for target week, try to find latest sheet
                    self.logger.warning(f"No sheet for {target_week_date.strftime('%d-%m-%Y')} found in {actual_file_path}, trying latest sheet")
                    latest_sheet = self._find_latest_sheet(wb.sheetnames, sheet_pattern)
                    if latest_sheet:
                        sheet_names = [latest_sheet]
            else:
                latest_sheet = self._find_latest_sheet(wb.sheetnames, sheet_pattern)
                if latest_sheet:
                    sheet_names = [latest_sheet]
            
            if not sheet_names:
                wb.close()
                if target_week_date:
                    self.logger.warning(f"No sheet for {target_week_date.strftime('%d-%m-%Y')} or latest sheet found in {actual_file_path}")
                else:
                    self.logger.warning(f"No sheet matching pattern {sheet_pattern} found in {actual_file_path}")
                return [], []

            records: List[EmployeeRecord] = []
            seen_employees = set()
            for sheet_name in sheet_names:
                self.logger.info(f"Using sheet: {sheet_name} for {team_name}")
                ws = wb[sheet_name]

                # Parse based on file path/team name
                if "Platform" in actual_file_path or "Platform" in team_name:
                    sheet_records = self._parse_platform_sheet(ws, team_name)
                elif "Product" in actual_file_path or "Product" in team_name:
                    sheet_records = self._parse_product_sheet(ws, team_name)
                else:  # Data Team, Dexia, PMI, PTR all use data team format
                    sheet_records = self._parse_data_team_sheet(ws, team_name)
                
                # Add only new employees (not already in records)
                for rec in sheet_records:
                    if rec.employee_name not in seen_employees:
                        seen_employees.add(rec.employee_name)
                        records.append(rec)

            wb.close()
            return records, sheet_names
        finally:
            # Clean up temp file if used
            if temp_file_path and os.path.exists(temp_file_path):
                try:
                    os.remove(temp_file_path)
                    os.rmdir(os.path.dirname(temp_file_path))
                except Exception:
                    pass

    def _find_sheet_for_date(self, sheet_names: List[str], target_date: date) -> Optional[str]:
        """Find the sheet that is in the same week as the target date."""
        for sheet_name in sheet_names:
            parsed_date = self._parse_sheet_date(sheet_name)
            if parsed_date and self._is_same_week(parsed_date, target_date):
                return sheet_name
        return None

    def _find_closest_sheet(self, sheet_names: List[str], target_date: date) -> Optional[str]:
        """Find the closest sheet to the target date."""
        sheets_with_dates = []
        for sheet_name in sheet_names:
            parsed_date = self._parse_sheet_date(sheet_name)
            if parsed_date:
                sheets_with_dates.append((parsed_date, sheet_name))
        
        if not sheets_with_dates:
            return None
        
        # Find closest date
        closest_sheet = None
        min_diff = float('inf')
        for parsed_date, sheet_name in sheets_with_dates:
            diff = abs((parsed_date - target_date).days)
            if diff < min_diff:
                min_diff = diff
                closest_sheet = sheet_name
        
        return closest_sheet

    def _find_latest_sheet(self, sheet_names: List[str], pattern: str) -> Optional[str]:
        """Find the latest week's sheet based on the pattern, ignoring future dates."""
        today = date.today()
        matching_sheets = []
        regex = re.compile(pattern)

        for sheet_name in sheet_names:
            if regex.match(sheet_name):
                # Try to parse date
                parsed_date = self._parse_sheet_date(sheet_name)
                if parsed_date and parsed_date <= today:
                    matching_sheets.append((parsed_date, sheet_name))

        if not matching_sheets:
            return None

        # Sort by date descending and pick first
        matching_sheets.sort(key=lambda x: x[0], reverse=True)
        return matching_sheets[0][1]

    def _parse_sheet_date(self, sheet_name: str) -> Optional[date]:
        """Parse date from sheet name."""
        # Try multiple formats - handle single-digit days/months
        date_patterns = [
            r"(\d{1,2})-(\d{1,2})-(\d{4})",  # DD-MM-YYYY or D-M-YYYY
            r"Week Ending (\d{1,2})-(\d{1,2})-(\d{4})",  # Week Ending DD-MM-YYYY
            r"Week ending (\d{1,2})-(\d{1,2})",  # Week ending DD-MM (assume current year)
        ]

        for patt in date_patterns:
            match = re.search(patt, sheet_name)
            if match:
                try:
                    if len(match.groups()) == 3:
                        day, month, year = map(int, match.groups())
                        return date(year, month, day)
                    elif len(match.groups()) == 2:
                        day, month = map(int, match.groups())
                        # Assume current year
                        return date(datetime.now().year, month, day)
                except ValueError:
                    continue

        return None

    def _parse_platform_sheet(self, ws, team_name: str) -> List[EmployeeRecord]:
        """Parse Platform Engineering sheet (horizontal layout)."""
        records: List[EmployeeRecord] = []
        skip_emp_keywords = ["name", "employee", "team", "lead", "date", "monday", "tuesday", 
                         "wednesday", "thursday", "friday", "✅", "🔄", "⏳", "🚧", "📝", "status", 
                         "report", "your", "pillar", "vlinker", "role", "stories", "format", 
                         "saurabh", "none", "developer", "perl", "full", "stack",
                         "product", "engineering", "afe", "c++", "what did you do", 
                         "impediments", "what will you do", "?", "yesterday", "today"]

        # First, read the header rows to get employee names and team leads
        rows = list(ws.iter_rows(values_only=True))
        if len(rows) < 6:
            return []

        employees_row_idx = 1  # 0-based (2nd row in 1-based)
        team_leads_row_idx = 2  # 0-based (3rd row in 1-based)

        team_leads_row = rows[team_leads_row_idx]
        employees_row = rows[employees_row_idx]

        # Now iterate over columns
        for col_idx in range(len(employees_row)):
            employee_name = employees_row[col_idx]
            team_lead = team_leads_row[col_idx] if col_idx < len(team_leads_row) else None

            if not employee_name or not isinstance(employee_name, str):
                continue
            employee_name = employee_name.strip()
            if len(employee_name) < 2:
                continue
            if any(kw in employee_name.lower() for kw in skip_emp_keywords):
                continue

            # Now check if any daily updates exist for this employee in the rows below
            is_leave = False
            is_completed = False

            # Check data rows (starting from employee_row_idx + 1)
            for row_idx in range(employees_row_idx + 1, min(len(rows), employees_row_idx + 20)):
                row = rows[row_idx]
                if col_idx >= len(row):
                    continue
                cell_val = row[col_idx]
                if cell_val and isinstance(cell_val, str):
                    cell_val = cell_val.strip()
                    if len(cell_val) == 0:
                        continue
                    if "leave" in cell_val.lower():
                        is_leave = True
                        break
                    
                    if self._has_actual_content(cell_val):
                        is_completed = True

            # Determine status
            if is_leave:
                status = "Completed"
            elif is_completed:
                status = "Completed"
            else:
                status = "Pending"

            tl_str = str(team_lead).strip() if (team_lead and isinstance(team_lead, str)) else ""
            if tl_str == "TL":
                # If it says "TL", the employee is their own TL
                tl_str = employee_name
            elif not tl_str or tl_str == "Team Lead":
                tl_str = "Unassigned"

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

        return records

    def _parse_product_sheet(self, ws, team_name: str) -> List[EmployeeRecord]:
        """Parse Product Engineering sheet (vertical layout)."""
        records: List[EmployeeRecord] = []
        skip_emp_keywords = ["name", "employee", "team", "lead", "date", "monday", "tuesday", 
                         "wednesday", "thursday", "friday", "✅", "🔄", "⏳", "🚧", "📝", "status", 
                         "report", "your", "pillar", "vlinker", "role", "stories", "format",
                         "none", "sick", "unassigned", "on leave", "leave",
                         "what did you do", "impediments", "what will you do", "?", "yesterday", "today"]

        rows = list(ws.iter_rows(values_only=True))

        for row_idx, row in enumerate(rows, 0):
            if row_idx < 4:  # skip first few header rows
                continue
            if not any(cell is not None and str(cell).strip() for cell in row):
                continue

            if len(row) > 4:
                employee_name = row[3]  # column D (index 3, 0-based)
                team_lead = row[4]      # column E (index 4, 0-based)
                leave_status = row[5]

                if not employee_name or not isinstance(employee_name, str):
                    continue
                employee_name = employee_name.strip()
                if len(employee_name) < 2:
                    continue
                if any(kw in employee_name.lower() for kw in skip_emp_keywords):
                    continue

                is_leave = False
                # Check leave_status and also check day columns for leave keywords
                if leave_status and isinstance(leave_status, str) and "leave" in leave_status.lower():
                    is_leave = True
                if not is_leave:
                    for i in range(6, min(11, len(row))):
                        val = row[i]
                        if val and isinstance(val, str):
                            val_lower = val.lower()
                            if "leave" in val_lower:
                                is_leave = True
                                break

                is_completed = False
                if not is_leave:
                    # Check all columns from index 6 onwards for actual content
                    for i in range(6, len(row)):
                        val = row[i]
                        if val and isinstance(val, str) and len(val.strip()) > 0:
                            if self._has_actual_content(val):
                                is_completed = True
                                break

                status = "Completed" if (is_completed or is_leave) else "Pending"

                tl_str = str(team_lead).strip() if team_lead else ""
                if tl_str == "TL":
                    tl_str = employee_name
                elif not tl_str:
                    tl_str = "Unassigned"

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

        return records

    def _parse_data_team_sheet(self, ws, team_name: str) -> List[EmployeeRecord]:
        """Parse Data Team, Dexia, PMI, PTR sheet."""
        temp_records: List[EmployeeRecord] = []
        skip_emp_keywords = ["name", "employee", "team", "lead", "date", "monday", "tuesday", 
                         "wednesday", "thursday", "friday", "✅", "🔄", "⏳", "🚧", "📝", "status", 
                         "report", "your", "pillar", "vlinker", "role", "stories", "format",
                         "none", "sick", "unassigned", "on leave", "leave",
                         "what did you do", "impediments", "what will you do", "?", "yesterday", "today"]

        rows = list(ws.iter_rows(values_only=True))
        
        row_idx = 0
        while row_idx < len(rows):
            row = rows[row_idx]
            
            # Check if this row is an employee row (starts with name, second cell is "What did you do yesterday?")
            if (len(row) > 1 and 
                isinstance(row[0], str) and 
                row[0].strip() and 
                isinstance(row[1], str) and 
                "what did you do" in row[1].lower()):
                
                employee_name = row[0].strip()
                
                if len(employee_name) < 2:
                    row_idx += 4
                    continue
                if any(kw in employee_name.lower() for kw in skip_emp_keywords):
                    row_idx +=4
                    continue
                
                # Now check the three rows for this employee for content or leave
                is_leave = False
                is_completed = False
                
                # Check row (current), row+1, row+2 for content or leave
                for offset in [0, 1, 2]:
                    check_row_idx = row_idx + offset
                    if check_row_idx >= len(rows):
                        break
                    check_row = rows[check_row_idx]
                    # Check all day columns (indices 2-6)
                    for day_col in range(2, min(7, len(check_row))):
                        val = check_row[day_col]
                        if val and isinstance(val, str):
                            val = val.strip()
                            if len(val) > 0:
                                if "leave" in val.lower():
                                    is_leave = True
                                    break
                                if self._has_actual_content(val):
                                    is_completed = True
                                    break
                    if is_leave or is_completed:
                        break
                
                status = "Completed" if (is_completed or is_leave) else "Pending"
                tl_str = "Unassigned"
                record = EmployeeRecord(
                    employee_name=employee_name,
                    team=team_name,
                    team_lead=tl_str,
                    status=status,
                    is_leave=is_leave,
                    last_updated=datetime.now()
                )
                if not any(r.employee_name == record.employee_name for r in temp_records):
                    temp_records.append(record)
                    
                # Skip next 3 rows (what will you do, impediments, empty)
                row_idx +=4
            else:
                row_idx +=1
        
        # Now, set team lead to first valid employee and update all records' team_lead
        if temp_records:
            team_lead_name = temp_records[0].employee_name
            for rec in temp_records:
                rec.team_lead = team_lead_name
        
        return temp_records

