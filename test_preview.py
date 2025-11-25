import pandas as pd

# === CONFIGURATION ===
file_path = "/Users/lvc/AI Scripts/2025_10 Afore JSON cleanup/2025_10 files/Reporte-16.xlsx"
siefore_name = "Pensiones"
concept_target = "Total de Activo"
header_row = 8          # Dates in row 8 (0-based)
concept_row = 9         # Concept row in row 9
num_afores = 10         # 10 Afores under each concept
first_value_col = 4     # Column E = index 4
start_date = pd.Timestamp("2024-08-01")

# === READ FILE ===
df = pd.read_excel(file_path, header=header_row)
df.columns = [str(c).strip() for c in df.columns]

# Identify "Total de Activo"
concept_idx = df[df.iloc[:, 1].astype(str).str.contains(concept_target, case=False, na=False)].index[0]
afore_block = df.iloc[concept_idx + 1 : concept_idx + 1 + num_afores, :]

# Get Afore names
afore_names = afore_block.iloc[:, 1].fillna("").str.strip()

# Identify numeric/date columns
date_cols = df.columns[first_value_col:]

# === PARSE VALUES ===
records = []
for i, afore in enumerate(afore_names):
    row = afore_block.iloc[i, first_value_col:]
    for col, val in row.items():
        date = pd.to_datetime(col, dayfirst=True, errors="coerce")
        if pd.notna(date) and date >= start_date:
            # Convert N/A or missing to 0
            try:
                val_clean = str(val).replace(",", "").strip()
                value_mxn = float(val_clean) * 1000 if val_clean not in ["N/A", "-", "", "nan", "None"] else 0.0
            except Exception:
                value_mxn = 0.0

            records.append({
                "Afore": afore,
                "Siefore": siefore_name,
                "Concept": concept_target,
                "PeriodYear": date.year,
                "PeriodMonth": str(date.month).zfill(2),
                "valueMXN": value_mxn
            })

# === OUTPUT PREVIEW ===
preview_df = pd.DataFrame(records)
print(preview_df.head(20))
