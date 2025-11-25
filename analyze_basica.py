import json
import pandas as pd

# Load the cleaned JSON
with open("/Users/lvc/AI Scripts/2025_10 Afore JSON cleanup/merged_consar_data_cleaned.json", "r", encoding="utf-8") as f:
    data = json.load(f)

df = pd.DataFrame(data)

# Filter for "Basica" records
basica_df = df[df["Siefore"] == "Basica"]

print("=" * 60)
print(f"Analyzing {len(basica_df)} 'Basica' records")
print("=" * 60)

# Check date range
print(f"\nDate Range:")
print(f"  Earliest: {basica_df['PeriodYear'].min()}-{basica_df['PeriodMonth'].min()}")
print(f"  Latest: {basica_df['PeriodYear'].max()}-{basica_df['PeriodMonth'].max()}")

# Check concepts
print(f"\nConcepts:")
print(basica_df["Concept"].value_counts().to_string())

# Check Afores
print(f"\nAfores:")
print(basica_df["Afore"].value_counts().to_string())

# Sample records
print(f"\nSample records:")
print(basica_df.head(10).to_string(index=False))

# Check specific combinations
print(f"\nBreakdown by Afore-Concept:")
breakdown = basica_df.groupby(["Afore", "Concept"]).size().reset_index(name="Count")
print(breakdown.to_string(index=False))
