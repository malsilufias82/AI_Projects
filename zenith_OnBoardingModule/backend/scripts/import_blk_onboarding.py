import argparse
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.services.blk_onboarding_import import import_blk_workbook, parse_blk_workbook


def main() -> None:
    parser = argparse.ArgumentParser(description="Import the BLK onboarding tracker into MongoDB.")
    parser.add_argument(
        "--workbook",
        type=Path,
        default=Path(__file__).resolve().parents[2] / "onboarding_dashboard" / "data" / "BLK Onboarding Tracker.xlsx",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Write new employee, onboarding, and activity records to the configured MongoDB.",
    )
    args = parser.parse_args()

    employees, onboarding, activities = parse_blk_workbook(args.workbook)
    print(
        f"Parsed {len(employees)} unique employees, {len(onboarding)} onboarding records, "
        f"and {len(activities)} Week0/Day0-Day5 activities from {args.workbook}."
    )
    if not args.apply:
        print("Dry run only; use --apply to import into MongoDB.")
        return

    result = asyncio.run(import_blk_workbook(args.workbook))
    print("Import complete: " + ", ".join(f"{key}={value}" for key, value in result.items()))


if __name__ == "__main__":
    main()
