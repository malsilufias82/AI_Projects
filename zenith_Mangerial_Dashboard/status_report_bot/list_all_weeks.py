
#!/usr/bin/env python3
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from config import load_config
from generate_team_lead_report import get_all_available_weeks

def main():
    config = load_config()
    all_weeks = get_all_available_weeks(config)
    print("Available weeks (chronological order):")
    for week in all_weeks:
        print(f"  {week.strftime('%d-%m-%Y')}")

if __name__ == "__main__":
    main()
