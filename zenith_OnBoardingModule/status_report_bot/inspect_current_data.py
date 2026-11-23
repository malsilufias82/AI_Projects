
#!/usr/bin/env python3
"""Inspect current Excel files and records"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from config import load_config
from excel_reader import ExcelReader
from datetime import date

def main():
    config = load_config()
    reader = ExcelReader(config)
    
    # Read records for today's week or latest
    records, sheet_info = reader.read_employee_records()
    print(f"Sheet info: {sheet_info}")
    print(f"Total records: {len(records)}")
    
    # Print each record with details
    print("\n--- Employee Records ---")
    for rec in records:
        status_str = f"Status: {rec.status}"
        leave_str = f"Is Leave: {rec.is_leave}"
        print(f"• {rec.employee_name} (Team: {rec.team}, TL: {rec.team_lead}) - {status_str}, {leave_str}")
    
    # Look for specific employees mentioned: Aashita Jain and Yuvraj Kaushik
    print("\n--- Specific Employees ---")
    target_names = ["Aashita Jain", "Yuvraj Kaushik"]
    for rec in records:
        if rec.employee_name in target_names:
            print(f"✓ Found {rec.employee_name}:")
            print(f"  - Status: {rec.status}")
            print(f"  - Is Leave: {rec.is_leave}")
            print(f"  - Team: {rec.team}")
            print(f"  - Team Lead: {rec.team_lead}")

if __name__ == "__main__":
    main()
