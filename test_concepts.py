import pandas as pd

# === CONFIGURATION ===
file_path = "/Users/lvc/AI Scripts/2025_10 Afore JSON cleanup/2025_10 files/Reporte-16.xlsx"
siefore_name = "Pensiones"

concepts_to_test = [
    "Inversiones Tercerizadas",
    "Fiduciarios",  # Partial match due to encoding issues
    "Fondos Mutuos"  # Partial match due to encoding issues
]

header_row = 8        # Dates on row 8 (0-based)
num_afores = 10       # 10 Afores per concept
first_value_col = 4   # Column E (numeric data starts here)
num_preview_cols = 5  # Only show first few months for inspection

# === READ FILE ===
df = pd.read_excel(file_path, header=header_row)
df.columns = [str(c).strip() for c in df.columns]

date_cols = df.columns[first_value_col : first_value_col + num_preview_cols]
all_records = []

for concept in concepts_to_test:
    concept_idx = df[df.iloc[:, 1].astype(str).str.contains(concept, case=False, na=False)]
    if concept_idx.empty:
        print(f"⚠️ Concept '{concept}' not found in {siefore_name}. Skipping...")
        continue

    concept_row = concept_idx.index[0]
    afore_block = df.iloc[concept_row + 1 : concept_row + 1 + num_afores, :]
    afore_names = afore_block.iloc[:, 1].fillna("").str.strip()

    for i, afore in enumerate(afore_names):
        row = afore_block.iloc[i, first_value_col : first_value_col + num_preview_cols]
        for col, val in row.items():
            date = pd.to_datetime(col, dayfirst=True, errors="coerce")
            if pd.notna(date):
                val_str = str(val).replace(",", "").strip()
                try:
                    value_mxn = float(val_str) * 1000 if val_str not in ["N/A", "-", "", "nan", "None"] else 0.0
                except Exception:
                    value_mxn = 0.0

                all_records.append({
                    "Afore": afore,
                    "Siefore": siefore_name,
                    "Concept": concept,
                    "PeriodYear": date.year,
                    "PeriodMonth": str(date.month).zfill(2),
                    "valueMXN": value_mxn
                })

# === OUTPUT PREVIEW ===
preview_df = pd.DataFrame(all_records)
print("✅ Extraction test complete.")
print(f"Concepts extracted: {preview_df['Concept'].unique().tolist()}")
print(f"Rows extracted: {len(preview_df)}")
print("\nPreview:")
print(preview_df.head(20))
