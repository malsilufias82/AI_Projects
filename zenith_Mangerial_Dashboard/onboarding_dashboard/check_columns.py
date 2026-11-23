
from app import load_all_blk_data

df_resources, activities, employee_names, _, _, _ = load_all_blk_data()

print("df_resources.columns:")
for col in df_resources.columns:
    print(f"  - {col}")

print("\nFirst 10 values of 'VLinker' column:")
if "VLinker" in df_resources.columns:
    print(df_resources["VLinker"].head(10).to_string())

print("\nFirst 10 values of 'Skill set' column:")
if "Skill set" in df_resources.columns:
    print(df_resources["Skill set"].head(10).to_string())

print("\nemployee_names (from Phase1):")
print(employee_names[:10])
