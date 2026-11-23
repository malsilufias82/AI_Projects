
from openpyxl import load_workbook
import pandas as pd

wb = load_workbook("data/BLK Onboarding Tracker.xlsx", data_only=True)
ws = wb["Resource List"]

# Read all data
headers = [cell.value for cell in ws[2]]
data = []
for row in ws.iter_rows(min_row=3, values_only=True):
    if any(row):
        data.append(row)

df = pd.DataFrame(data, columns=headers)
df = df.dropna(axis=1, how="all")

print("Columns available:", list(df.columns))
print("\nFirst 20 rows (Vlinker & Team Lead):")
for idx, row in df.head(20).iterrows():
    print(f"Vlinker: {row.get('Vlinker')}, Team Lead: {row.get('Team Lead')}")
