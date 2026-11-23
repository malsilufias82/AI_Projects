import pandas as pd


# function which takes list of sheet names and find the latest sheet with latest date
def get_latest_sheet_name(sheet_names: list):
    """
    Find the latest sheet name from a list by extracting and comparing dates.
    
    Args:
        sheet_names: List of sheet names
        
    Returns:
        The sheet name with the latest date, or None if no valid dates found
    """
    import re
    from datetime import datetime
    
    if not sheet_names:
        return None
    
    # Patterns to remove from sheet names before date extraction
    cleanup_patterns = [
        r'week\s*ending',
        r'we\s*ending',
        r'w/e',
        r'w\.e\.',
        r'standup\s*status',
        r'team\s*status',
        r'daily\s*tracker',
        r'data\s*team',
        r'_',
    ]
    
    def clean_sheet_name(name: str) -> str:
        """Remove non-date text from sheet name."""
        cleaned = name
        for pattern in cleanup_patterns:
            cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE)
        return cleaned.strip()
    
    def extract_date(sheet_name: str):
        """Extract date from sheet name, return (datetime, original_name) or (None, None)."""
        # Try multiple date patterns
        patterns = [
            # Pattern: 23 Jul 2026, 23-Jul-2026, 23 Jul 26
            r'(\d{1,2})[-/\s]+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[-/\s]+(\d{2,4})',
            # Pattern: 23-7-26, 23-07-2026, 23/7/26
            r'(\d{1,2})[-/](\d{1,2})(?:[-/](\d{2,4}))?',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, sheet_name, re.IGNORECASE)
            if match:
                day = match.group(1)
                month = match.group(2)
                year = match.group(3) if match.group(3) else str(datetime.now().year)
                
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
                    date_obj = datetime.strptime(f"{day}-{month}-{year}", "%d-%m-%Y")
                    return (date_obj, sheet_name)
                except ValueError:
                    continue
        
        return (None, None)
    
    # Process all sheet names - try extraction directly first, then with cleaning
    valid_sheets = []
    for sheet_name in sheet_names:
        print(f"Processing sheet: {sheet_name}")
        # Try direct extraction first
        date_obj, original_name = extract_date(sheet_name)
        if date_obj:
            print(f"  Direct extraction succeeded: {date_obj}")
            valid_sheets.append((date_obj, sheet_name))
        else:
            # If direct extraction fails, try with cleaning
            cleaned_name = clean_sheet_name(sheet_name)
            print(f"  Direct extraction failed, cleaned name: {cleaned_name}")
            date_obj, original_name = extract_date(cleaned_name)
            if date_obj:
                print(f"  Cleaned extraction succeeded: {date_obj}")
                valid_sheets.append((date_obj, sheet_name))
            else:
                print(f"  Could not extract date from: {sheet_name}")
    
    print(f"Valid sheets found: {len(valid_sheets)}")
    if valid_sheets:
        valid_sheets.sort(key=lambda x: x[0], reverse=True)
        print(f"Latest sheet: {valid_sheets[0][1]} with date {valid_sheets[0][0]}")
        return valid_sheets[0][1]
    
    print("No valid sheets with dates found")
    return None


# read excel
# get name of latest sheet
# use the latest sheet to read names and updates based on the ruleset for each day and create DF with one big sheet
# convert it to dict array and return
def process_sheet(file_name: str):
    df = pd.read_excel(file_name)
    latest_sheet_name = get_latest_sheet_name(df.sheet_names)
    df_latest_sheet = df[latest_sheet_name]
    
    pass