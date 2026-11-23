
#!/usr/bin/env python3
import json
from pathlib import Path

history_file = Path(__file__).parent / "data" / "skipped_employees.json"
with open(history_file, "r", encoding="utf-8") as f:
    data = json.load(f)

for emp_key in data["employees"]:
    # Reset is_skipped to False for everyone
    data["employees"][emp_key]["is_skipped"] = False

# Save
with open(history_file, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2)

print("✅ Reset all skipped employees flags!")
