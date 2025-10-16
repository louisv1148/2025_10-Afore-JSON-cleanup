# Afore JSON Database Rebuild Project

This project rebuilds the complete Afore holdings database from all 11 Siefore Excel files, generating a clean, unified JSON database with comprehensive coverage from 2019 to August 2025.

## Purpose

The script completely rebuilds the Afore holdings database by:

1. Processing all 11 Siefore Excel files (Reporte-16 through Reporte-26)
2. Extracting 4 key investment concepts from each Siefore
3. Handling Spanish date formats and encoding issues
4. Generating a unified database with 32,280+ records
5. Producing detailed summary statistics

## Data Sources

**Excel Files (all in `2025_10 files/` directory):**
- **Reporte-16.xlsx** → Pensiones
- **Reporte-17.xlsx** → Inicial
- **Reporte-18.xlsx** → 55-59 years
- **Reporte-19.xlsx** → 60-64 years
- **Reporte-20.xlsx** → 65-69 years
- **Reporte-21.xlsx** → 70-74 years
- **Reporte-22.xlsx** → 75-79 years
- **Reporte-23.xlsx** → 80-84 years
- **Reporte-24.xlsx** → 85-89 years
- **Reporte-25.xlsx** → 90-94 years
- **Reporte-26.xlsx** → 95-99 years

## Output Files

- **consar_siefores_full.json**: Complete rebuilt database (32,280 records)
- **rebuild_summary.csv**: Detailed summary statistics by Siefore

## Installation

### Prerequisites

- Python 3.7 or higher
- pip package manager

### Setup

1. Install required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

Run the cleanup script:

```bash
python cleanup_afore_json.py
```

The script will:
1. Load the main JSON database
2. Extract data from both XLS reports
3. Combine all sources
4. Standardize Siefore names
5. Save the cleaned data and summary report

## Data Structure

Each record in the JSON contains:

- **Afore**: Name of the Afore (pension fund administrator)
- **Siefore**: Investment fund category (age-based or Pensiones/Inicial)
- **Concept**: Type of investment (e.g., "Total de Activo", "Inversiones Tercerizadas")
- **PeriodYear**: Year of the data point
- **PeriodMonth**: Month of the data point (zero-padded)
- **valueMXN**: Value in Mexican Pesos
- **FX_EOM**: End of month exchange rate (if applicable)

## Siefore Categories

All 11 Siefores are included:
- **Age-based**: 55-59, 60-64, 65-69, 70-74, 75-79, 80-84, 85-89, 90-94, 95-99
- **Special**: Pensiones, Inicial

## Concept Types

- **Total de Activo**: Total assets under management
- **Inversiones Tercerizadas**: Outsourced investments
- **Inversión en títulos Fiduciarios**: Fiduciary title investments
- **Inversión en Fondos Mutuos**: Mutual fund investments

## Notes

- Values in Excel files are stored in thousands and are converted to actual values (multiplied by 1000)
- Script handles Spanish month abbreviations (Ene, Ago, Dic, etc.) for complete date coverage
- Date range: January 2019 to August 2025 for most Siefores
- All concepts are extracted with proper encoding handling

## Project Structure

```
2025_10 Afore JSON cleanup/
├── 2025_10 files/              # Excel source files (Reporte-16 through Reporte-26)
├── cleanup_afore_json.py       # Main rebuild script
├── README.md                    # This file
├── requirements.txt             # Python dependencies
├── consar_siefores_full.json   # Output database (generated)
└── rebuild_summary.csv          # Summary report (generated)
```

## Results

The script generates a complete database with:
- **32,280 total records**
- **11 unique Siefores** (correctly mapped)
- **11 unique Afores** (pension fund administrators)
- **4 investment concepts** fully extracted
- **Coverage:** 2019-01 to 2025-08

## Troubleshooting

### File Not Found Errors

Ensure all Excel files (Reporte-16.xlsx through Reporte-26.xlsx) are in the `2025_10 files/` subdirectory.

### Missing Dependencies

If you encounter import errors, ensure you've installed all requirements:
```bash
pip install -r requirements.txt
```

### Excel Reading Issues

If you encounter issues reading Excel files, try:
```bash
pip install --upgrade pandas openpyxl xlrd
```

## License

Internal project for Afore Holdings analysis.
