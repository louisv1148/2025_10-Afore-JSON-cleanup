import pandas as pd

# === CONFIGURATION ===
file_path = "/Users/lvc/AI Scripts/2025_10 Afore JSON cleanup/2025_10 files/Reporte-16.xlsx"
header_row = 8

# === READ FILE ===
df = pd.read_excel(file_path, header=header_row)
df.columns = [str(c).strip() for c in df.columns]

# Look at column 1 (index 1) which contains the concept names
concepts_col = df.iloc[:, 1].astype(str).str.strip()

# Filter for potential concept rows (not NaN, not empty, looks like a concept)
potential_concepts = concepts_col[
    (concepts_col != "nan") &
    (concepts_col != "") &
    (~concepts_col.str.startswith("Unnamed"))
].unique()

print("=" * 60)
print("All unique entries in column 1 (potential concepts):")
print("=" * 60)
for i, concept in enumerate(potential_concepts[:50], 1):  # Show first 50
    print(f"{i}. {concept}")

# Search specifically for investment-related concepts
print("\n" + "=" * 60)
print("Investment-related concepts:")
print("=" * 60)
investment_concepts = [c for c in potential_concepts if any(keyword in c.lower() for keyword in ["invers", "activo", "fondo", "fiduc", "tercer"])]
for concept in investment_concepts:
    print(f"  • {concept}")
