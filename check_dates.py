import json
import pandas as pd

# Load the rebuilt JSON
with open("/Users/lvc/AI Scripts/2025_10 Afore JSON cleanup/consar_siefores_full.json", "r", encoding="utf-8") as f:
    data = json.load(f)

df = pd.DataFrame(data)

# Check date range by Siefore
print("=" * 70)
print("Date Range by Siefore")
print("=" * 70)

for siefore in sorted(df["Siefore"].unique()):
    siefore_df = df[df["Siefore"] == siefore]
    min_date = f"{siefore_df['PeriodYear'].min()}-{siefore_df['PeriodMonth'].min()}"
    max_date = f"{siefore_df['PeriodYear'].max()}-{siefore_df['PeriodMonth'].max()}"
    print(f"{siefore:12} : {min_date} to {max_date}")

# Check the latest dates in detail
print("\n" + "=" * 70)
print("Records from 2025 by Siefore and Month")
print("=" * 70)

df_2025 = df[df["PeriodYear"] == "2025"]
breakdown = df_2025.groupby(["Siefore", "PeriodMonth"]).size().reset_index(name="Count")
breakdown_pivot = breakdown.pivot(index="Siefore", columns="PeriodMonth", values="Count").fillna(0).astype(int)
print(breakdown_pivot)

# Check a sample file to see available columns
print("\n" + "=" * 70)
print("Checking dates in Reporte-18.xlsx (60-64)")
print("=" * 70)

df_test = pd.read_excel("/Users/lvc/AI Scripts/2025_10 Afore JSON cleanup/2025_10 files/Reporte-18.xlsx", header=8)
date_cols = []
for col in df_test.columns[4:]:
    try:
        date = pd.to_datetime(str(col), dayfirst=True, errors="coerce")
        if pd.notna(date):
            date_cols.append((col, date))
    except:
        pass

print(f"Found {len(date_cols)} date columns")
print(f"First 5: {date_cols[:5]}")
print(f"Last 5: {date_cols[-5:]}")
