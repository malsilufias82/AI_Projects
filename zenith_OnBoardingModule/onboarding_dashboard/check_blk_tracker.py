
import pandas as pd

print("Reading BLK Onboarding Tracker...")
df_blk = pd.read_excel("data/BLK Onboarding Tracker.xlsx")

print(f"\n✅ Success! Found {len(df_blk)} rows, {len(df_blk.columns)} columns.\n")

print("📊 Column names:")
for col in df_blk.columns:
    print(f"  - {col}")

print("\n🔍 First 5 rows (preview):")
print(df_blk.head())
