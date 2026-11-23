"""
Import employees and tasks from existing Excel file into the database
"""
from pathlib import Path

from db import import_from_excel


def main():
    excel_path = Path(__file__).resolve().parent / "data" / "BLK Onboarding Tracker.xlsx"
    print(f"Importing data from {excel_path}...")
    import_from_excel(excel_path)
    print("Import complete!")


if __name__ == "__main__":
    main()
