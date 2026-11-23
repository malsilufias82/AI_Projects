#!/usr/bin/env python3
"""Create 4 sample status report Excel files."""

from datetime import datetime
import pandas as pd
import os

# Sample data for 4 files
sample_datasets = [
    {
        "file": "data/status_report1.xlsx",
        "data": {
            "Employee Name": ["Amit Sharma", "Neha Patel"],
            "Employee ID": ["EMP001", "EMP002"],
            "Team": ["Frontend", "Backend"],
            "Team Lead": ["Rohit", "Rohit"],
            "Project": ["Website Redesign", "API V2"],
            "Status": ["Done", "Pending"],
            "Last Updated": [datetime(2026, 6, 27, 10, 30), None]
        }
    },
    {
        "file": "data/status_report2.xlsx",
        "data": {
            "Employee Name": ["Rahul Singh", "Priya Mehta"],
            "Employee ID": ["EMP003", "EMP004"],
            "Team": ["Frontend", "DevOps"],
            "Team Lead": ["Anjali", "Anjali"],
            "Project": ["Dashboard", "Infrastructure"],
            "Status": ["Done", "Pending"],
            "Last Updated": [datetime(2026, 6, 28, 14, 15), None]
        }
    },
    {
        "file": "data/status_report3.xlsx",
        "data": {
            "Employee Name": ["Karan Joshi", "Pooja Gupta"],
            "Employee ID": ["EMP005", "EMP006"],
            "Team": ["Backend", "QA"],
            "Team Lead": ["Rohit", "Vikram"],
            "Project": ["API V2", "Testing"],
            "Status": ["Pending", "Done"],
            "Last Updated": [None, datetime(2026, 6, 29, 9, 45)]
        }
    },
    {
        "file": "data/status_report4.xlsx",
        "data": {
            "Employee Name": ["Riya Verma", "Arjun Kumar"],
            "Employee ID": ["EMP007", "EMP008"],
            "Team": ["Design", "Design"],
            "Team Lead": ["Vikram", "Vikram"],
            "Project": ["UI/UX", "Branding"],
            "Status": ["Pending", "Pending"],
            "Last Updated": [None, None]
        }
    }
]

# Create data directory if it doesn't exist
os.makedirs("data", exist_ok=True)

# Write each Excel file
for dataset in sample_datasets:
    df = pd.DataFrame(dataset["data"])
    df.to_excel(dataset["file"], sheet_name="Weekly Status", index=False, engine="openpyxl")
    print(f"✅ Created {dataset['file']}")

print("\nAll sample files created successfully!")