#!/usr/bin/env python3
"""Test the updated excel report generator"""

import sys
from pathlib import Path
from datetime import date

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from config import load_config
from excel_reader import ExcelReader
from report_checker import ReportChecker
from excel_report_generator import ExcelReportGenerator, DailyReportData

def main():
    config = load_config()
    reader = ExcelReader(config)
    checker = ReportChecker(config)
    generator = ExcelReportGenerator(config)

    # Get a recent date
    test_date = date.today()
    print(f"Testing report generation for date: {test_date}")
    records, sheet_info = reader.read_employee_records(test_date)
    print(f"Found {len(records)} records")
    print("Sheet info:", sheet_info)

    snapshot = checker.evaluate(records, test_date, "Test")
    print("Generated snapshot")

    daily_data = DailyReportData(
        report_date=snapshot.report_date,
        scheduler_type=snapshot.scheduler_type,
        team_leads=snapshot.team_leads,
        employees_by_tl=snapshot.employees_by_tl,
        completed_count=snapshot.completed_count,
        pending_count=snapshot.pending_count,
        leave_count=snapshot.leave_count,
        skipped_count=snapshot.skipped_count,
        sheet_info=sheet_info
    )

    excel_path = generator.generate_daily_report(daily_data)
    print(f"Generated Excel report at: {excel_path}")

if __name__ == "__main__":
    main()
