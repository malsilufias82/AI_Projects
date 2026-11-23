# Excel Sheet Processing Helper

This module provides generic utility functions for processing weekly status Excel sheets. Each Excel file type should have its own dedicated processing module that imports these helpers as needed.

## Features

- **Text normalization**: Clean and normalize text values
- **Offboarded vlinker loading**: Load offboarded team members from DU.xlsx
- **Sheet finding**: Find sheets by date or latest "Week Ending" pattern
- **Leave pattern detection**: Recognize various leave patterns
- **Template header removal**: Clean status templates with emoji headers
- **Meaningful content checking**: Determine if text has actual content vs templates

## Helper Functions

### Text Processing

```python
from app.engine.sheets.helper import normalize_text

# Normalize text by removing special characters
clean_text = normalize_text("John_Doe@Company")  # "john doe company"
```

### Offboarded Vlinkers

```python
from app.engine.sheets.helper import load_offboarded_vlinkers

# Load offboarded vlinkers from DU.xlsx
offboarded = load_offboarded_vlinkers("DU.xlsx")
```

### Sheet Finding

```python
from app.engine.sheets.helper import find_sheet_by_date, find_latest_week_ending_sheet
import pandas as pd

xlsx_file = pd.ExcelFile("PlateformTeam.xlsx")

# Find sheet by specific date
sheet = find_sheet_by_date(xlsx_file, "19-07-2026")

# Find latest Week Ending sheet (any day)
sheet = find_latest_week_ending_sheet(xlsx_file)

# Find latest Week Ending sheet for specific day (e.g., Friday)
sheet = find_latest_week_ending_sheet(xlsx_file, week_ending_day="Friday")

# Find latest Week Ending sheet for Sunday
sheet = find_latest_week_ending_sheet(xlsx_file, week_ending_day="Sunday")

# Custom week ending pattern
sheet = find_latest_week_ending_sheet(
    xlsx_file,
    week_ending_pattern=r'week\s+ending',
    week_ending_day="Friday"
)
```

### Sheet Summary

```python
from app.engine.sheets.helper import get_sheet_summary

# Get information about sheets in a file
summary = get_sheet_summary("PlateformTeam.xlsx")
# Returns: {'total_sheets': 5, 'sheet_names': [...], 'week_ending_sheets': [...]}
```

### Leave Detection

```python
from app.engine.sheets.helper import is_leave_status, LEAVE_PATTERNS

# Check if text indicates leave
if is_leave_status("On planned leave"):
    print("Person is on leave")

# Access leave patterns directly
print(LEAVE_PATTERNS)
```

### Template Cleaning

```python
from app.engine.sheets.helper import remove_template_headers, has_meaningful_content

# Remove template headers
clean = remove_template_headers("✅ Work Completed Today: Task A")
# Returns: "Task A"

# Check for meaningful content
if has_meaningful_content("✅ Work Completed Today: Task A"):
    print("Has actual content")
```

### Common Constants

```python
from app.engine.sheets.helper import NAME_HEADERS, TL_HEADERS, DAY_NAMES, TEMPLATE_HEADERS

# Header name patterns for column/row detection
print(NAME_HEADERS)  # {'team member name', 'vlinker', 'name', ...}
print(TL_HEADERS)    # {'team lead', 'tl', 'lead', ...}
print(DAY_NAMES)      # ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
print(TEMPLATE_HEADERS)  # List of template header patterns
```

## File-Specific Processing

Each Excel file type should have its own processing module. For example:

### Example: PlateformTeam Processing Module (Friday week ending)

```python
# plateformteam_processor.py
import pandas as pd
from app.engine.sheets.helper import (
    load_offboarded_vlinkers,
    find_latest_week_ending_sheet,
    normalize_text,
    is_leave_status,
    has_meaningful_content,
    NAME_HEADERS,
    TL_HEADERS,
    DAY_NAMES
)

def process_file(file_path: str, du_file_path: str = "DU.xlsx", **kwargs):
    """Process PlateformTeam.xlsx file (Friday week ending)"""
    xlsx_file = pd.ExcelFile(file_path)
    
    # Find latest Friday week ending sheet
    sheet_name = find_latest_week_ending_sheet(
        xlsx_file,
        week_ending_day="Friday"
    )
    
    offboarded = load_offboarded_vlinkers(du_file_path)
    
    # File-specific processing logic here
    df = pd.read_excel(file_path, sheet_name=sheet_name, header=None)
    
    # Use helper functions as needed
    # ...
    
    return results
```

### Example: PMITeam Processing Module (Sunday week ending)

```python
# pmiteam_processor.py
import pandas as pd
from app.engine.sheets.helper import (
    load_offboarded_vlinkers,
    find_latest_week_ending_sheet,
    normalize_text,
    is_leave_status,
    has_meaningful_content,
    DAY_NAMES
)

def process_file(file_path: str, du_file_path: str = "DU.xlsx", **kwargs):
    """Process PMITeam.xlsx file (Sunday week ending)"""
    xlsx_file = pd.ExcelFile(file_path)
    
    # Find latest Sunday week ending sheet
    sheet_name = find_latest_week_ending_sheet(
        xlsx_file,
        week_ending_day="Sunday"
    )
    
    offboarded = load_offboarded_vlinkers(du_file_path)
    
    # File-specific processing logic here
    df = pd.read_excel(file_path, sheet_name=sheet_name, header=None)
    
    # Use helper functions as needed
    # ...
    
    return results
```

## Available Helper Functions

### Text Utilities
- `normalize_text(val)` - Clean and normalize text values
- `is_leave_status(text)` - Check if text indicates leave
- `remove_template_headers(text)` - Remove template headers from text
- `has_meaningful_content(text, min_length)` - Check for meaningful content

### Data Loading
- `load_offboarded_vlinkers(du_file_path)` - Load offboarded team members from DU.xlsx

### Sheet Finding
- `find_sheet_by_date(xlsx_file, target_date)` - Find sheet by specific date
- `find_latest_week_ending_sheet(xlsx_file)` - Find latest Week Ending sheet
- `get_sheet_summary(file_path)` - Get sheet information

### Constants
- `LEAVE_PATTERNS` - List of leave detection patterns
- `TEMPLATE_HEADERS` - List of template header patterns
- `NAME_HEADERS` - Common name column headers
- `TL_HEADERS` - Common team lead column headers
- `DAY_NAMES` - Standard day names (Monday-Friday)

## Dependencies

- pandas >= 2.0.0
- openpyxl >= 3.0.0

## Notes

- File paths should be absolute or relative to the working directory
- DU.xlsx must contain a "VLink Team Details" sheet with "Status" column
- Date format expected: DD-MM-YYYY
- Helper functions are case-insensitive for sheet name matching
