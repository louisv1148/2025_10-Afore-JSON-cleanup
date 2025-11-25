import json
import pandas as pd

# Load the cleaned JSON
with open("/Users/lvc/AI Scripts/2025_10 Afore JSON cleanup/merged_consar_data_cleaned.json", "r", encoding="utf-8") as f:
    data = json.load(f)

df = pd.DataFrame(data)

# Get unique Siefores
unique_siefores = sorted(df["Siefore"].unique())

print("=" * 60)
print(f"Total Unique Siefores: {len(unique_siefores)}")
print("=" * 60)
for i, siefore in enumerate(unique_siefores, 1):
    count = len(df[df["Siefore"] == siefore])
    print(f"{i:2}. {siefore:30} ({count:,} records)")

print("\n" + "=" * 60)
print("Siefore Value Counts:")
print("=" * 60)
print(df["Siefore"].value_counts().to_string())
