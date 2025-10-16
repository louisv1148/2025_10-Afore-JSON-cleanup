# Afore JSON Data Cleanup Project

This project consolidates and cleans Afore holdings data from multiple sources to create a unified, standardized JSON database.

## Purpose

The script addresses data quality issues in the Afore holdings database by:

1. Combining data from the main JSON file with additional XLS reports
2. Standardizing Siefore naming conventions (removing "Basica" prefixes)
3. Adding missing Pensiones and Inicial Siefore data
4. Generating a summary report of the cleanup process

## Data Sources

- **Main JSON**: `merged_consar_data_2019_2025.json` - Primary database
- **Reporte-16.xls**: Pensiones Siefore data
- **Reporte-17.xls**: Inicial Siefore data

## Output Files

- **merged_consar_data_cleaned.json**: Cleaned and consolidated data
- **cleanup_summary.csv**: Summary statistics of the cleanup process

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

- **Age-based**: 0-24, 25-29, 30-34, 35-39, 40-44, 45-49, 50-54, 55-59, 60-64, 65-69, 70+
- **Special**: Pensiones, Inicial

## Concept Types

- **Total de Activo**: Total assets under management
- **Inversiones Tercerizadas**: Outsourced investments
- **Inversión en títulos Fiduciarios**: Fiduciary title investments
- **Inversión en Fondos Mutuos**: Mutual fund investments

## Notes

- Values in XLS files are stored in thousands and are converted to actual values (multiplied by 1000)
- Date parsing is flexible to handle various date formats in XLS files
- The script checks for any remaining "Basica" labels that may need manual review

## Project Structure

```
2025_10 Afore JSON cleanup/
├── cleanup_afore_json.py       # Main cleanup script
├── README.md                    # This file
├── requirements.txt             # Python dependencies
├── merged_consar_data_cleaned.json  # Output (generated)
└── cleanup_summary.csv          # Summary report (generated)
```

## Troubleshooting

### File Not Found Errors

Ensure all source files are in the correct locations:
- Main JSON: `/Users/lvc/Downloads/merged_consar_data_2019_2025.json`
- XLS files: `/Users/lvc/Downloads/Reporte-16.xls` and `/Users/lvc/Downloads/Reporte-17.xls`

### Missing Dependencies

If you encounter import errors, ensure you've installed all requirements:
```bash
pip install -r requirements.txt
```

### Excel Reading Issues

If you encounter issues reading XLS files, try:
```bash
pip install --upgrade pandas openpyxl xlrd
```

## License

Internal project for Afore Holdings analysis.
