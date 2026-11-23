"""
Generic helper functions for Excel sheet processing.

This module contains reusable utility functions that can be used by
file-specific processing modules. Each Excel file type should have its
own processing module that imports these helpers as needed.
"""

import pandas as pd
import re
from datetime import datetime, date, timedelta
from typing import Set, Any, Optional, List, Dict
from app.core.mongodb import MongoDB


def normalize_text(val: Any) -> str:
    """
    Normalize text by removing special characters and converting to lowercase.
    
    Args:
        val: Value to normalize
        
    Returns:
        Normalized string
    """
    if pd.isna(val):
        return ""
    return re.sub(r'[^\w\s]', '', str(val).lower().strip())


def load_offboarded_vlinkers(du_file_path: str = "DU.xlsx") -> Set[str]:
    """
    Load offboarded vlinkers from DU.xlsx VLink Team Details sheet.
    
    Args:
        du_file_path: Path to DU.xlsx file
        
    Returns:
        Set of offboarded vlinker names
    """
    try:
        vlink_team_details = pd.read_excel(
            du_file_path, 
            sheet_name="VLink Team Details", 
            header=2
        )
        return set(
            vlink_team_details[vlink_team_details['Status'] == 'Offboarded VLink']['VLinker']
            .dropna()
            .astype(str)
            .str.strip()
            .tolist()
        )
    except Exception as e:
        print(f"Could not load offboarded list from {du_file_path}: {e}")
        return set()


def find_sheet_by_date(xlsx_file: pd.ExcelFile, target_date: str) -> Optional[str]:
    """
    Find a sheet containing the target date.
    
    Args:
        xlsx_file: ExcelFile object
        target_date: Date string in format DD-MM-YYYY
        
    Returns:
        Sheet name if found, None otherwise
    """
    for sheet_name in xlsx_file.sheet_names:
        if target_date in sheet_name:
            return sheet_name
    return None


def find_latest_week_ending_sheet(
    xlsx_file: pd.ExcelFile,
    week_ending_pattern: str = r'we+ek?\s+endin?g',
    week_ending_day: Optional[str] = None
) -> Optional[str]:
    """
    Find the latest sheet matching week ending pattern or containing a date.
    
    Args:
        xlsx_file: ExcelFile object
        week_ending_pattern: Regex pattern to match week ending sheets (default: 'we+ek?\\s+endin?g')
        week_ending_day: Specific day to filter (e.g., 'Friday', 'Sunday'). If None, matches any day.
        
    Returns:
        Latest sheet name matching the pattern, or first sheet if none found
    """
    matching_sheets = []
    for sheet_name in reversed(xlsx_file.sheet_names):
        if re.search(week_ending_pattern, sheet_name, re.IGNORECASE):
            # If specific day is specified, check if it's in the sheet name
            if week_ending_day:
                if week_ending_day.lower() in sheet_name.lower():
                    matching_sheets.append(sheet_name)
            else:
                matching_sheets.append(sheet_name)
    
    # If no week ending sheets found, try to find sheets with dates
    if not matching_sheets:
        date_pattern = r'(\d{1,2})[-/\s](\d{1,2}|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[-/]?(\d{2,4})?'
        for sheet_name in reversed(xlsx_file.sheet_names):
            if re.search(date_pattern, sheet_name, re.IGNORECASE):
                matching_sheets.append(sheet_name)
    
    if matching_sheets:
        # Try to find the most recent by date
        latest_date = None
        target_sheet = None
        
        for sheet_name in matching_sheets:
            # Try multiple date patterns
            date_match = re.search(r'(\d{1,2})[-/](\d{1,2})(?:[-/](\d{2,4}))?', sheet_name)
            if not date_match:
                # Try pattern with month names like "23 Jul 2026"
                date_match = re.search(r'(\d{1,2})[-/\s]+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[-/]?(\d{2,4})?', sheet_name, re.IGNORECASE)
            
            if date_match:
                day = date_match.group(1)
                month = date_match.group(2)
                year = date_match.group(3) if date_match.group(3) else str(datetime.now().year)
                
                # Convert month name to number if needed
                month_map = {
                    'jan': '1', 'feb': '2', 'mar': '3', 'apr': '4', 'may': '5', 'jun': '6',
                    'jul': '7', 'aug': '8', 'sep': '9', 'oct': '10', 'nov': '11', 'dec': '12'
                }
                if month.lower() in month_map:
                    month = month_map[month.lower()]
                
                # Handle 2-digit year
                if len(year) == 2:
                    year_int = int(year)
                    year = '19' + year if year_int >= 50 else '20' + year
                
                try:
                    sheet_date = datetime.strptime(f"{day}-{month}-{year}", "%d-%m-%Y")
                    if latest_date is None or sheet_date > latest_date:
                        latest_date = sheet_date
                        target_sheet = sheet_name
                except ValueError:
                    pass
        
        return target_sheet or matching_sheets[-1]
    
    return xlsx_file.sheet_names[0] if xlsx_file.sheet_names else None


def get_sheet_summary(file_path: str) -> dict:
    """
    Get a summary of all sheets in an Excel file.
    
    Args:
        file_path: Path to the Excel file
        
    Returns:
        Dictionary with sheet information
    """
    try:
        xlsx_file = pd.ExcelFile(file_path)
        return {
            'file_path': file_path,
            'total_sheets': len(xlsx_file.sheet_names),
            'sheet_names': xlsx_file.sheet_names,
            'week_ending_sheets': [
                name for name in xlsx_file.sheet_names
                if re.search(r'we+ek?\s+endin?g', name, re.IGNORECASE)
            ]
        }
    except Exception as e:
        return {
            'file_path': file_path,
            'error': str(e),
            'total_sheets': 0,
            'sheet_names': [],
            'week_ending_sheets': []
        }


# Common patterns for leave detection
LEAVE_PATTERNS = [
    r'\bleave\b',
    r'\bon leave\b',
    r'\bon planned leave\b',
    r'\bsick leave\b',
    r'\bLEAVE\b',
    r'\bOn Leave\b',
    r'\bOn planned leave\b',
    r'\bSick leave\b'
]


# Day order for week processing
DAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
DAY_ORDER = {day: idx for idx, day in enumerate(DAY_NAMES)}


def get_days_up_to_today() -> Set[str]:
    """
    Get the set of day names that have already passed in the current week.
    
    Returns:
        Set of day names (e.g., {'Monday', 'Tuesday', 'Wednesday'} if today is Thursday)
    """
    today = date.today()
    current_day_name = today.strftime("%A")
    current_day_index = DAY_ORDER.get(current_day_name, 0)
    
    # Include all days up to and including today
    return set(DAY_NAMES[:current_day_index + 1])


def should_include_day(day_name: str) -> bool:
    """
    Check if a given day should be included in data insertion.
    
    Args:
        day_name: Name of the day (e.g., 'Monday', 'Tuesday')
        
    Returns:
        True if the day has already passed or is today, False otherwise
    """
    days_up_to_today = get_days_up_to_today()
    return day_name in days_up_to_today


# Common template headers to remove when checking for meaningful content
TEMPLATE_HEADERS = [
    r'Your Name\s*',
    r'✅\s*(Today\'s Activities|Work Completed Today|Work Completed on \w+)?\s*:?\s*',
    r'🔄\s*Work in Progress\s*:?\s*',
    r'⏳\s*Planned for (Tomorrow|Next Working Day)\s*:?\s*',
    r'🚧\s*Blockers / Support Needed / Impact( of the blocker)?\s*:?\s*',
    r'📝\s*Additional Notes\s*:?\s*',
    r'✅ Work Completed Today\s*:\s*',
    r'🔄 Work in Progress\s*:\s*',
    r'⏳ Planned for Tomorrow\s*:\s*',
    r'🚧 Blockers.*?📝 Additional Notes\s*:\s*',
    r'📝 Additional Notes\s*:\s*',
]


def is_leave_status(text: str) -> bool:
    """
    Check if text indicates a leave status.
    
    Args:
        text: Text to check
        
    Returns:
        True if text indicates leave, False otherwise
    """
    for pattern in LEAVE_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    return False


def remove_template_headers(text: str) -> str:
    """
    Remove template headers from text to check for meaningful content.
    
    Args:
        text: Text to clean
        
    Returns:
        Cleaned text
    """
    cleaned = text
    for pattern in TEMPLATE_HEADERS:
        cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r'[-*•]\s*', '', cleaned)
    return cleaned.strip()


def has_meaningful_content(text: str, min_length: int = 25) -> bool:
    """
    Check if text has meaningful content after removing template headers.
    
    Args:
        text: Text to check
        min_length: Minimum length for meaningful content
        
    Returns:
        True if text has meaningful content, False otherwise
    """
    cleaned = remove_template_headers(text)
    return len(cleaned) >= min_length


# Common header name patterns for column/row detection
NAME_HEADERS = {
    'team member name', 'member name', 'employee name', 'emp name',
    'vlinker', 'vlinkers', 'name', 'emp. name'
}

TL_HEADERS = {
    'team lead', 'tl', 'lead', 'reporting manager', 'manager', 'team lead name'
}

DAY_NAMES = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']


async def store_daily_status(
    user_name: str,
    team_lead: Optional[str],
    sheet_name: str,
    sheet_date: str,
    day_of_week: str,
    status_content: str,
    team_name: Optional[str] = None,
    date: Optional[str] = None
) -> bool:
    """
    Store daily status data for a user in MongoDB.
    Performs upsert operation (update if exists, insert if not).
    
    Args:
        user_name: Name of the user/vlinker
        team_lead: Team lead name
        sheet_name: Name of the sheet
        sheet_date: Date associated with the sheet (from sheet name)
        day_of_week: Day of week (Monday, Tuesday, etc.)
        status_content: The status update content
        team_name: Team name (e.g., Platform, Product, PMI, etc.)
        date: Actual date for this day (optional)
        
    Returns:
        True if successful, False otherwise
    """
    try:
        await MongoDB.connect()
        daily_status_collection = MongoDB.get_collection("daily_status")
        
        # Determine if this is leave status
        is_leave = is_leave_status(status_content)
        
        # Determine if this is filled status
        is_filled = bool(status_content and status_content.strip() and not is_leave)
        if is_filled and not has_meaningful_content(status_content, min_length=15):
            is_filled = False
        
        # Create unique filter for upsert
        filter_query = {
            "user_name": user_name,
            "sheet_name": sheet_name,
            "day_of_week": day_of_week
        }
        
        # Create update document
        update_doc = {
            "$set": {
                "user_name": user_name,
                "team_lead": team_lead,
                "sheet_name": sheet_name,
                "sheet_date": sheet_date,
                "day_of_week": day_of_week,
                "status_content": status_content,
                "is_leave": is_leave,
                "is_filled": is_filled,
                "team_name": team_name,
                "updated_at": datetime.utcnow()
            }
        }
        
        if date:
            update_doc["$set"]["date"] = date
        
        # Perform upsert
        result = await daily_status_collection.update_one(
            filter_query,
            update_doc,
            upsert=True
        )
        
        # await MongoDB.disconnect()
        return result.acknowledged
        
    except Exception as e:
        print(f"Error storing daily status for {user_name}: {e}")
        # await MongoDB.disconnect()
        return False


async def store_daily_status_batch(
    status_records: List[Dict[str, Any]]
) -> int:
    """
    Store multiple daily status records in batch.
    
    Args:
        status_records: List of dictionaries containing status data
        
    Returns:
        Number of successfully stored records
    """
    try:
        await MongoDB.connect()
        daily_status_collection = MongoDB.get_collection("daily_status")
        
        success_count = 0
        for record in status_records:
            try:
                user_name = record.get("user_name")
                team_lead = record.get("team_lead")
                sheet_name = record.get("sheet_name")
                sheet_date = record.get("sheet_date")
                day_of_week = record.get("day_of_week")
                status_content = record.get("status_content")
                team_name = record.get("team_name")
                date = record.get("date")
                
                # Determine if this is leave status
                is_leave = is_leave_status(status_content) if status_content else False
                
                # Determine if this is filled status
                is_filled = bool(status_content and status_content.strip() and not is_leave)
                if is_filled and not has_meaningful_content(status_content, min_length=15):
                    is_filled = False
                
                # Create unique filter for upsert
                filter_query = {
                    "user_name": user_name,
                    "sheet_name": sheet_name,
                    "day_of_week": day_of_week
                }
                
                # Create update document
                update_doc = {
                    "$set": {
                        "user_name": user_name,
                        "team_lead": team_lead,
                        "sheet_name": sheet_name,
                        "sheet_date": sheet_date,
                        "day_of_week": day_of_week,
                        "status_content": status_content,
                        "is_leave": is_leave,
                        "is_filled": is_filled,
                        "team_name": team_name,
                        "updated_at": datetime.utcnow()
                    }
                }
                
                if date:
                    update_doc["$set"]["date"] = date
                
                # Perform upsert
                result = await daily_status_collection.update_one(
                    filter_query,
                    update_doc,
                    upsert=True
                )
                
                if result.acknowledged:
                    success_count += 1
                    
            except Exception as e:
                print(f"Error storing status record for {record.get('user_name')}: {e}")
                continue
        
        # await MongoDB.disconnect()
        return success_count
        
    except Exception as e:
        print(f"Error in batch store daily status: {e}")
        # await MongoDB.disconnect()
        return 0
