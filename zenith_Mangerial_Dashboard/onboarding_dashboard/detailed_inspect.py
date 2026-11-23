
import pandas as pd

print("=== Phase1 - Machine Setup sheet ===")
df_phase1 = pd.read_excel("data/BLK Onboarding Tracker.xlsx", sheet_name="Phase1 - Machine Setup", header=None)
# Print first 20 rows and 15 columns
print(df_phase1.iloc[:20, :15])

print("\n=== Resource List sheet (BLK Credentials column) ===")
df_resources = pd.read_excel("data/BLK Onboarding Tracker.xlsx", sheet_name="Resource List", header=1)
print(df_resources[["Vlinker", "BLK Credentials Rcvd"]].head(20))
