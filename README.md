# Afore JSON Database Pipeline

Complete data pipeline for Afore holdings database: rebuilds from Excel files, fetches USD/MXN exchange rates from Banxico, and calculates USD values for all holdings.

## Purpose

This pipeline provides a complete, automated workflow:

1. **Database Rebuild**: Process all 11 Siefore Excel files (Reporte-16 through Reporte-26)
2. **FX Data Scraping**: Fetch end-of-month USD/MXN exchange rates from Banco de México
3. **USD Enrichment**: Calculate USD values for all holdings using FX rates
4. **Data Validation**: Comprehensive validation and error checking throughout
5. **Summary Statistics**: Detailed reports at each stage

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

**FX Data Source:**
- Banco de México (Banxico) Serie SF43718: USD/MXN exchange rate
- API endpoint: https://www.banxico.org.mx/SieInternet/

## Output Files

**Intermediate Files:**
- `consar_siefores_full.json`: Base database with MXN values (32,280 records)
- `2025_10 files/fx_data.json`: Monthly end-of-month FX rates
- `rebuild_summary.csv`: Database rebuild statistics

**Final Output:**
- `consar_siefores_with_usd.json`: Complete enriched database with FX_EOM and valueUSD fields

## Installation

### Prerequisites

- Python 3.7 or higher
- pip package manager
- Internet connection (for Banxico API)
- **Banxico API Token** (required for FX data fetching)

### Setup

1. Install required dependencies:

```bash
pip install -r requirements.txt
```

2. **Get a Banxico API Token** (required for Step 2 - FX data):
   - Visit: https://www.banxico.org.mx/SieAPIRest/service/v1/token
   - Request a free API token
   - Set it as an environment variable:
     ```bash
     export BANXICO_TOKEN='your-token-here'
     ```
   - Or pass it directly to the script: `--token your-token-here`

**Note:** For testing without a token, you can use `generate_test_fx.py` to create sample FX data.

## Usage

### Option 1: Run Complete Pipeline (Recommended)

Run all three steps automatically:

```bash
python run_full_pipeline.py
```

**Pipeline options:**
```bash
# Skip database rebuild if it already exists
python run_full_pipeline.py --skip-rebuild

# Skip FX fetch if data is cached (default: 24 hours)
python run_full_pipeline.py --skip-fx

# Force fresh FX data from Banxico
python run_full_pipeline.py --force-fx

# Run only the USD enrichment step
python run_full_pipeline.py --skip-rebuild --skip-fx
```

### Option 2: Run Individual Steps

**Step 1: Rebuild Database**
```bash
python cleanup_afore_json.py
```
Processes all Excel files and generates `consar_siefores_full.json`

**Step 2: Fetch FX Data**
```bash
python fetch_banxico_fx.py
```
Scrapes Banxico for USD/MXN rates and generates `fx_data.json`

Options:
- `--force`: Ignore cache, fetch fresh data
- `--cache-hours N`: Set cache duration (default: 24)

**Step 3: Enrich with USD**
```bash
python enrich_with_usd.py
```
Merges FX data and calculates USD values, generates `consar_siefores_with_usd.json`

## Data Structure

### Base Database Fields
- **Afore**: Name of the Afore (pension fund administrator)
- **Siefore**: Investment fund category (age-based or Pensiones/Inicial)
- **Concept**: Type of investment
- **PeriodYear**: Year of the data point (string)
- **PeriodMonth**: Month of the data point (zero-padded string, e.g., "01", "12")
- **valueMXN**: Value in Mexican Pesos (float)

### Enriched Database Fields (adds to above)
- **FX_EOM**: End-of-month USD/MXN exchange rate (float)
- **valueUSD**: Value in US Dollars (float, calculated as valueMXN / FX_EOM)

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
├── 2025_10 files/                     # Data directory
│   ├── Reporte-16.xlsx through Reporte-26.xlsx  # Source Excel files
│   └── fx_data.json                   # FX rates (generated)
│
├── cleanup_afore_json.py              # Step 1: Database rebuild
├── fetch_banxico_fx.py                # Step 2: FX data scraper
├── enrich_with_usd.py                 # Step 3: USD enrichment
├── run_full_pipeline.py               # Pipeline orchestrator
│
├── consar_siefores_full.json          # Base database (generated)
├── consar_siefores_with_usd.json      # Final enriched database (generated)
├── rebuild_summary.csv                # Rebuild statistics (generated)
│
├── README.md                           # This file
├── requirements.txt                    # Python dependencies
└── .gitignore                          # Git ignore rules
```

## Pipeline Results

**Step 1 - Database Rebuild:**
- 32,280 total records
- 11 unique Siefores (correctly mapped)
- 11 unique Afores (pension fund administrators)
- 4 investment concepts fully extracted
- Coverage: 2019-01 to 2025-08

**Step 2 - FX Data:**
- Monthly end-of-month exchange rates
- Full historical coverage matching database dates
- Cached for 24 hours to reduce API calls

**Step 3 - Final Enriched Database:**
- All 32,280 records with FX_EOM field
- All records with calculated valueUSD field
- Ready for analysis in both MXN and USD

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
