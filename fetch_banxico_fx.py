#!/usr/bin/env python3
"""
Banxico FX Data Scraper
=======================
This script fetches end-of-month USD/MXN exchange rates from Banco de México (Banxico)
and saves them in JSON format for enriching the Afore database.

Data Source:
- Banxico Serie SF43718 (USD/MXN exchange rate)
- API endpoint: https://www.banxico.org.mx/SieInternet/consultaSerieGrafica.do

Output:
- fx_data.json: Monthly end-of-month exchange rates
"""

import requests
import pandas as pd
import json
from datetime import datetime
import os
import time

class BanxicoFXAgent:
    """Agent to scrape and process Banxico FX data."""

    def __init__(self, output_path, token=None, cache_hours=24):
        """
        Initialize the FX agent.

        Args:
            output_path: Path to save the JSON output
            token: Banxico API token (optional, will try without token if not provided)
            cache_hours: Hours to cache data before re-fetching (default 24)
        """
        self.series_id = "SF43718"  # USD/MXN FIX exchange rate
        self.api_url = f"https://www.banxico.org.mx/SieAPIRest/service/v1/series/{self.series_id}/datos"
        self.token = token or os.environ.get("BANXICO_TOKEN")
        self.output_path = output_path
        self.cache_hours = cache_hours

    def should_refresh(self):
        """Check if cached data needs refreshing."""
        if not os.path.exists(self.output_path):
            return True

        file_age_hours = (time.time() - os.path.getmtime(self.output_path)) / 3600
        return file_age_hours > self.cache_hours

    def fetch_data(self):
        """
        Download Banxico FX data from API.

        Returns:
            DataFrame with raw FX data

        Raises:
            ValueError: If API request fails or returns invalid data
        """
        print("Fetching FX data from Banxico SIE API...")

        headers = {
            "Accept": "application/json"
        }

        # Add token to headers if available
        if self.token:
            headers["Bmx-Token"] = self.token
            print("  Using Banxico API token for authentication")
        else:
            print("  ⚠️  No API token provided - API may require authentication")
            print("     Set BANXICO_TOKEN environment variable or use --token parameter")

        try:
            response = requests.get(self.api_url, headers=headers, timeout=30)
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            if response.status_code == 401:
                raise ValueError(
                    "Authentication failed. Banxico API requires a token.\n"
                    "Get your token from: https://www.banxico.org.mx/SieAPIRest/service/v1/token\n"
                    "Then set it using: export BANXICO_TOKEN='your-token' or use --token parameter"
                )
            raise ValueError(f"Error fetching FX data from Banxico: {e}")
        except requests.exceptions.RequestException as e:
            raise ValueError(f"Error fetching FX data from Banxico: {e}")

        try:
            data = response.json()
            series_data = data["bmx"]["series"][0]["datos"]
            print(f"  -> Received {len(series_data)} data points from Banxico")
        except (KeyError, IndexError, json.JSONDecodeError) as e:
            raise ValueError(f"Invalid response format from Banxico API: {e}")

        if not series_data:
            raise ValueError("No data returned from Banxico API")

        return pd.DataFrame(series_data)

    def process_data(self, df):
        """
        Extract last valid FX rate for each month.

        Args:
            df: Raw DataFrame from Banxico API

        Returns:
            DataFrame with PeriodYear, PeriodMonth, and FX_EOM columns
        """
        print("Processing FX data...")

        # Parse dates and convert FX rates to numeric
        df["fecha"] = pd.to_datetime(df["fecha"], format="%d/%m/%Y", errors="coerce")
        df["dato"] = pd.to_numeric(df["dato"], errors="coerce")

        # Drop rows with invalid data
        initial_count = len(df)
        df = df.dropna(subset=["fecha", "dato"])
        dropped = initial_count - len(df)
        if dropped > 0:
            print(f"  -> Dropped {dropped} invalid records")

        # Create period columns
        df["PeriodYear"] = df["fecha"].dt.year.astype(str)
        df["PeriodMonth"] = df["fecha"].dt.month.astype(str).str.zfill(2)

        # Get last (most recent) FX rate for each month
        df_sorted = df.sort_values("fecha")
        df_eom = df_sorted.groupby(["PeriodYear", "PeriodMonth"]).tail(1)

        # Select and rename columns
        df_eom = df_eom[["PeriodYear", "PeriodMonth", "dato"]].rename(columns={"dato": "FX_EOM"})
        df_eom = df_eom.sort_values(["PeriodYear", "PeriodMonth"]).reset_index(drop=True)

        print(f"  -> Extracted {len(df_eom)} monthly FX rates")

        # Display date range
        min_date = f"{df_eom['PeriodYear'].min()}-{df_eom['PeriodMonth'].min()}"
        max_date = f"{df_eom['PeriodYear'].max()}-{df_eom['PeriodMonth'].max()}"
        print(f"  -> Date range: {min_date} to {max_date}")

        return df_eom

    def validate_data(self, df):
        """
        Validate the processed FX data.

        Args:
            df: Processed DataFrame

        Returns:
            bool: True if validation passes

        Raises:
            ValueError: If validation fails
        """
        print("Validating FX data...")

        # Check for required columns
        required_cols = ["PeriodYear", "PeriodMonth", "FX_EOM"]
        missing_cols = set(required_cols) - set(df.columns)
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")

        # Check for null values
        if df["FX_EOM"].isna().any():
            raise ValueError("FX_EOM column contains null values")

        # Check FX rate is in reasonable range (historical data from 1991 onwards)
        # MXN/USD has ranged from ~3 (early 1990s) to ~25 (recent years)
        min_fx = df["FX_EOM"].min()
        max_fx = df["FX_EOM"].max()
        if min_fx < 1 or max_fx > 30:
            raise ValueError(f"FX rates outside expected range: {min_fx:.2f} to {max_fx:.2f}")

        # Check for duplicate months
        duplicates = df.duplicated(subset=["PeriodYear", "PeriodMonth"], keep=False)
        if duplicates.any():
            dup_periods = df[duplicates][["PeriodYear", "PeriodMonth"]].values
            raise ValueError(f"Duplicate periods found: {dup_periods}")

        print(f"  -> Validation passed (FX range: {min_fx:.2f} to {max_fx:.2f} MXN/USD)")
        return True

    def save_json(self, df):
        """
        Save monthly FX data to JSON file.

        Args:
            df: DataFrame with FX data
        """
        # Ensure output directory exists
        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)

        df.to_json(self.output_path, orient="records", indent=2, force_ascii=False)
        file_size = os.path.getsize(self.output_path) / 1024
        print(f"\n✅ FX data saved to: {self.output_path}")
        print(f"   File size: {file_size:.1f} KB")

    def run(self, force_refresh=False):
        """
        Execute the complete FX data scraping pipeline.

        Args:
            force_refresh: If True, ignore cache and fetch fresh data
        """
        print("=" * 70)
        print("Banxico FX Data Scraper")
        print("=" * 70)
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

        # Check cache
        if not force_refresh and not self.should_refresh():
            file_age = (time.time() - os.path.getmtime(self.output_path)) / 3600
            print(f"ℹ️  Using cached data (age: {file_age:.1f} hours)")
            print(f"   File: {self.output_path}")
            print(f"\n   Use force_refresh=True to fetch fresh data")
            return

        try:
            # Fetch raw data
            df = self.fetch_data()

            # Process data
            df_eom = self.process_data(df)

            # Validate data
            self.validate_data(df_eom)

            # Save to JSON
            self.save_json(df_eom)

            print(f"\nCompleted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("=" * 70)

        except Exception as e:
            print(f"\n❌ Error: {e}")
            raise


# === MAIN EXECUTION ===
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Fetch USD/MXN exchange rates from Banxico")
    parser.add_argument("--force", action="store_true", help="Force refresh, ignore cache")
    parser.add_argument("--token", help="Banxico API token (or set BANXICO_TOKEN env var)")
    parser.add_argument("--output", default="/Users/lvc/AI Scripts/2025_10 Afore JSON cleanup/2025_10 files/fx_data.json",
                        help="Output JSON file path")
    parser.add_argument("--cache-hours", type=int, default=24,
                        help="Hours to cache data before re-fetching (default: 24)")

    args = parser.parse_args()

    agent = BanxicoFXAgent(
        output_path=args.output,
        token=args.token,
        cache_hours=args.cache_hours
    )

    agent.run(force_refresh=args.force)
