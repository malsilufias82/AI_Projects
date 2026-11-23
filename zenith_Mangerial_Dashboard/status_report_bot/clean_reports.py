
from pathlib import Path

reports_dir = Path(__file__).parent / "reports"
for f in reports_dir.glob("*.xlsx"):
    try:
        f.unlink()
        print(f"Deleted {f.name}")
    except Exception as e:
        print(f"Error deleting {f.name}: {e}")
for f in reports_dir.glob("~$*.xlsx"):
    try:
        f.unlink()
    except:
        pass
