import pandas as pd

# Check Reporte-19 which should have the most recent data
file_path = "/Users/lvc/AI Scripts/2025_10 Afore JSON cleanup/2025_10 files/Reporte-19.xlsx"

df = pd.read_excel(file_path, header=8)
print("=" * 70)
print("Column headers from Reporte-19.xlsx (60-64)")
print("=" * 70)

# Get all columns from position 4 onwards
date_columns = df.columns[4:]
print(f"\nTotal columns from position 4: {len(date_columns)}")
print("\nAll date columns:")
for i, col in enumerate(date_columns):
    print(f"{i+1:3}. {col}")
