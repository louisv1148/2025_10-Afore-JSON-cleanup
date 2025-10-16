#!/usr/bin/env python3
"""
Afore JSON Data Complete Rebuild Script
========================================
This script rebuilds the complete Afore holdings database from all Siefore Excel files.
It processes all 11 Siefores and extracts 4 key concepts from each.

Data Sources:
- Reporte-16.xlsx → Pensiones
- Reporte-17.xlsx → Inicial
- Reporte-18.xlsx → 55-59
- Reporte-19.xlsx → 60-64
- Reporte-20.xlsx → 65-69
- Reporte-21.xlsx → 70-74
- Reporte-22.xlsx → 75-79
- Reporte-23.xlsx → 80-84
- Reporte-24.xlsx → 85-89
- Reporte-25.xlsx → 90-94
- Reporte-26.xlsx → 95-99

Concepts Extracted:
1. Total de Activo
2. Inversiones Tercerizadas
3. Inversión en títulos Fiduciarios
4. Inversión en Fondos Mutuos
"""

import pandas as pd
import json
import os
from datetime import datetime

# === CONFIGURATION ===
BASE_PATH = "/Users/lvc/AI Scripts/2025_10 Afore JSON cleanup/2025_10 files"
OUTPUT_JSON_PATH = "/Users/lvc/AI Scripts/2025_10 Afore JSON cleanup/consar_siefores_full.json"
SUMMARY_REPORT_PATH = "/Users/lvc/AI Scripts/2025_10 Afore JSON cleanup/rebuild_summary.csv"

# Files are numbered 16–26 (inclusive)
SIEFORE_MAP = {
    16: "Pensiones",
    17: "Inicial",
    18: "55-59",
    19: "60-64",
    20: "65-69",
    21: "70-74",
    22: "75-79",
    23: "80-84",
    24: "85-89",
    25: "90-94",
    26: "95-99"
}

CONCEPTS = [
    "Total de Activo",
    "Inversiones Tercerizadas",
    "Inversion en Titulos Fiduciarios",
    "Inversion en Fondos Mutuos"
]

# Excel file structure configuration
HEADER_ROW = 8        # Dates start at row 8
FIRST_VALUE_COL = 4   # Column E = index 4
NUM_AFORES = 10       # 10 Afores per concept


def extract_siefore_data(file_path, siefore_name):
    """
    Extracts all four concepts from a single Siefore Excel file.

    Args:
        file_path: Path to the Excel file
        siefore_name: Name of the Siefore (e.g., "Pensiones", "60-64")

    Returns:
        DataFrame with extracted records
    """
    try:
        df = pd.read_excel(file_path, header=HEADER_ROW)
    except Exception as e:
        print(f"    ❌ Error reading {file_path}: {e}")
        return pd.DataFrame()

    df.columns = [str(c).strip() for c in df.columns]
    all_records = []

    for concept in CONCEPTS:
        # Find row containing the concept (case-insensitive, partial match for encoding issues)
        # Use different search terms for concepts with encoding issues
        if "Fiduciarios" in concept:
            concept_search = "Fiduciarios"
        elif "Fondos Mutuos" in concept:
            concept_search = "Fondos Mutuos"
        elif "Tercerizadas" in concept:
            concept_search = "Tercerizadas"
        else:
            concept_search = concept

        concept_idx = df[df.iloc[:, 1].astype(str).str.contains(concept_search, case=False, na=False)]

        if concept_idx.empty:
            print(f"    ⚠️  Concept '{concept}' not found in {siefore_name}. Skipping...")
            continue

        concept_row = concept_idx.index[0]
        afore_block = df.iloc[concept_row + 1 : concept_row + 1 + NUM_AFORES, :]
        afore_names = afore_block.iloc[:, 1].fillna("").str.strip()

        # Loop through all Afores and months
        for i, afore in enumerate(afore_names):
            if not afore or afore == "nan":
                continue

            row = afore_block.iloc[i, FIRST_VALUE_COL:]

            for col, val in row.items():
                # Parse date - handles multiple formats:
                # 1. Pandas Timestamp objects (already parsed)
                # 2. Spanish month abbreviations like "Ago-2025", "Ene-2024"
                # 3. Standard datetime strings
                if isinstance(col, pd.Timestamp):
                    date = col
                else:
                    col_str = str(col).strip()

                    # Handle Spanish month abbreviations
                    spanish_months = {
                        "Ene": "01", "Feb": "02", "Mar": "03", "Abr": "04",
                        "May": "05", "Jun": "06", "Jul": "07", "Ago": "08",
                        "Sep": "09", "Oct": "10", "Nov": "11", "Dic": "12"
                    }

                    # Check if it's in format "Ago-2025"
                    if "-" in col_str and len(col_str.split("-")) == 2:
                        parts = col_str.split("-")
                        if parts[0] in spanish_months and len(parts[1]) == 4:
                            month = spanish_months[parts[0]]
                            year = parts[1]
                            date = pd.Timestamp(f"{year}-{month}-01")
                        else:
                            date = pd.to_datetime(col_str, errors="coerce")
                    else:
                        date = pd.to_datetime(col_str, errors="coerce")

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
                        "PeriodYear": str(date.year),
                        "PeriodMonth": str(date.month).zfill(2),
                        "valueMXN": value_mxn
                    })

    return pd.DataFrame(all_records)


def main():
    """Main execution function to rebuild the complete database."""
    print("=" * 70)
    print("Afore JSON Complete Database Rebuild")
    print("=" * 70)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    # === MAIN LOOP: PROCESS ALL FILES ===
    all_dataframes = []
    file_summary = []

    for report_num, siefore_name in sorted(SIEFORE_MAP.items()):
        file_path = os.path.join(BASE_PATH, f"Reporte-{report_num}.xlsx")

        if not os.path.exists(file_path):
            print(f"⚠️  File not found: {file_path}")
            file_summary.append({
                "Report_Number": report_num,
                "Siefore": siefore_name,
                "Status": "File Not Found",
                "Records_Extracted": 0
            })
            continue

        print(f"🔹 Processing {siefore_name:12} from Reporte-{report_num}.xlsx...")
        df_siefore = extract_siefore_data(file_path, siefore_name)
        records_count = len(df_siefore)
        print(f"   ➜ {records_count:,} records extracted.")

        all_dataframes.append(df_siefore)
        file_summary.append({
            "Report_Number": report_num,
            "Siefore": siefore_name,
            "Status": "Success",
            "Records_Extracted": records_count
        })

    # === COMBINE ALL INTO ONE MASTER DATAFRAME ===
    if not all_dataframes:
        print("\n❌ No data extracted — check file paths or structure.")
        return

    print("\n" + "=" * 70)
    print("Combining all data sources...")
    print("=" * 70)

    full_df = pd.concat(all_dataframes, ignore_index=True)

    # === SAVE OUTPUT ===
    print(f"\nSaving complete database to: {OUTPUT_JSON_PATH}")
    full_df.to_json(OUTPUT_JSON_PATH, orient="records", indent=2, force_ascii=False)
    print("  ✓ JSON saved successfully")

    # === GENERATE SUMMARY ===
    summary_df = pd.DataFrame(file_summary)
    summary_df.to_csv(SUMMARY_REPORT_PATH, index=False)
    print(f"\nSaving summary report to: {SUMMARY_REPORT_PATH}")
    print("  ✓ Summary saved successfully")

    # === FINAL STATISTICS ===
    print("\n" + "=" * 70)
    print("REBUILD COMPLETE!")
    print("=" * 70)
    print(f"Total Records:        {len(full_df):,}")
    print(f"Unique Afores:        {full_df['Afore'].nunique()}")
    print(f"Unique Siefores:      {full_df['Siefore'].nunique()}")
    print(f"Unique Concepts:      {full_df['Concept'].nunique()}")
    print(f"Date Range:           {full_df['PeriodYear'].min()}-{full_df['PeriodMonth'].min()} to {full_df['PeriodYear'].max()}-{full_df['PeriodMonth'].max()}")

    print("\nSiefores included:")
    for siefore in sorted(full_df["Siefore"].unique()):
        count = len(full_df[full_df["Siefore"] == siefore])
        print(f"  • {siefore:12} : {count:,} records")

    print("\nConcepts included:")
    for concept in sorted(full_df["Concept"].unique()):
        count = len(full_df[full_df["Concept"] == concept])
        print(f"  • {concept:40} : {count:,} records")

    print(f"\nCompleted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)


if __name__ == "__main__":
    main()
