
import sys
from pathlib import Path
from datetime import date

sys.path.insert(0, str(Path(__file__).parent / "src"))

from config import load_config
from generate_team_lead_report import get_all_available_weeks

config = load_config()
all_weeks = get_all_available_weeks(config)
print("Available weeks in chronological order:")
for wk in all_weeks:
    print(f"  - {wk.strftime('%d-%m-%Y')}")
