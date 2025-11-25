import pandas as pd

files_to_check = [
    ("/Users/lvc/AI Scripts/2025_10 Afore JSON cleanup/2025_10 files/Reporte-16.xlsx", "Reporte-16"),
    ("/Users/lvc/AI Scripts/2025_10 Afore JSON cleanup/2025_10 files/Reporte-17.xlsx", "Reporte-17")
]

for file_path, file_name in files_to_check:
    print("=" * 60)
    print(f"File: {file_name}")
    print("=" * 60)

    # Read first few rows without header to see structure
    df_raw = pd.read_excel(file_path, header=None)

    # Print first 15 rows, first 3 columns
    print("\nFirst 15 rows (raw):")
    print(df_raw.iloc[:15, :3].to_string())

    # Now try with header row 8
    df = pd.read_excel(file_path, header=8)

    # Look for indicators in the file
    # Check if there's a title or description in early rows
    print("\n" + "-" * 60)
    print("Looking for Siefore type indicators...")
    print("-" * 60)

    # Search for keywords in all cells
    for i in range(min(10, len(df_raw))):
        for j in range(min(5, len(df_raw.columns))):
            cell_value = str(df_raw.iloc[i, j]).lower()
            if any(keyword in cell_value for keyword in ["pensiones", "pensión", "pension", "inicial", "básica inicial", "básica pensiones"]):
                print(f"Row {i}, Col {j}: {df_raw.iloc[i, j]}")

    print("\n")
