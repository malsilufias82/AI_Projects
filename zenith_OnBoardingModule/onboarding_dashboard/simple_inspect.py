
import pandas as pd

# Read the Resource List sheet
df = pd.read_excel("data/BLK Onboarding Tracker.xlsx", sheet_name="Resource List", header=1)
print("=== Columns ===")
print(df.columns.tolist())
print("\n=== First 10 Rows ===")
print(df.head(10))
print("\n=== Team Lead Unique Values ===")
if "Team Lead" in df.columns:
    print(df["Team Lead"].value_counts())
else:
    print("Team Lead column not found")
