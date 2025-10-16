#!/usr/bin/env python3
"""
USD Value Enrichment Script
============================
This script merges the Afore holdings database with Banxico FX data and calculates
USD values for all holdings.

Inputs:
- consar_siefores_full.json: Base Afore database (MXN values)
- fx_data.json: Monthly end-of-month USD/MXN exchange rates

Output:
- consar_siefores_with_usd.json: Enriched database with FX_EOM and valueUSD fields
"""

import pandas as pd
import json
import os
from datetime import datetime

class USDEnrichmentAgent:
    """Agent to enrich Afore data with USD values."""

    def __init__(self, afore_data_path, fx_data_path, output_path):
        """
        Initialize the enrichment agent.

        Args:
            afore_data_path: Path to the base Afore JSON database
            fx_data_path: Path to the FX rates JSON file
            output_path: Path to save the enriched database
        """
        self.afore_data_path = afore_data_path
        self.fx_data_path = fx_data_path
        self.output_path = output_path

    def load_data(self):
        """
        Load both Afore and FX data.

        Returns:
            Tuple of (afore_df, fx_df)

        Raises:
            FileNotFoundError: If input files don't exist
            ValueError: If data format is invalid
        """
        print("Loading data files...")

        # Load Afore database
        if not os.path.exists(self.afore_data_path):
            raise FileNotFoundError(f"Afore database not found: {self.afore_data_path}")

        with open(self.afore_data_path, "r", encoding="utf-8") as f:
            afore_data = json.load(f)
        afore_df = pd.DataFrame(afore_data)
        print(f"  -> Loaded {len(afore_df):,} Afore records")

        # Load FX data
        if not os.path.exists(self.fx_data_path):
            raise FileNotFoundError(f"FX data not found: {self.fx_data_path}")

        with open(self.fx_data_path, "r", encoding="utf-8") as f:
            fx_data = json.load(f)
        fx_df = pd.DataFrame(fx_data)
        print(f"  -> Loaded {len(fx_df):,} FX rates")

        # Validate required columns
        required_afore_cols = ["PeriodYear", "PeriodMonth", "valueMXN"]
        missing_cols = set(required_afore_cols) - set(afore_df.columns)
        if missing_cols:
            raise ValueError(f"Missing required columns in Afore data: {missing_cols}")

        required_fx_cols = ["PeriodYear", "PeriodMonth", "FX_EOM"]
        missing_cols = set(required_fx_cols) - set(fx_df.columns)
        if missing_cols:
            raise ValueError(f"Missing required columns in FX data: {missing_cols}")

        return afore_df, fx_df

    def merge_fx_data(self, afore_df, fx_df):
        """
        Merge FX rates with Afore data.

        Args:
            afore_df: DataFrame with Afore holdings
            fx_df: DataFrame with FX rates

        Returns:
            Merged DataFrame
        """
        print("\nMerging FX data with Afore database...")

        initial_count = len(afore_df)

        # Merge on PeriodYear and PeriodMonth
        merged_df = afore_df.merge(
            fx_df,
            on=["PeriodYear", "PeriodMonth"],
            how="left"
        )

        # Check for records without FX data
        missing_fx = merged_df["FX_EOM"].isna().sum()
        if missing_fx > 0:
            print(f"  ⚠️  Warning: {missing_fx:,} records missing FX data")

            # Show which periods are missing
            missing_periods = merged_df[merged_df["FX_EOM"].isna()][["PeriodYear", "PeriodMonth"]].drop_duplicates()
            print(f"     Missing FX for {len(missing_periods)} periods:")
            for _, row in missing_periods.head(10).iterrows():
                print(f"       - {row['PeriodYear']}-{row['PeriodMonth']}")
            if len(missing_periods) > 10:
                print(f"       ... and {len(missing_periods) - 10} more")

        print(f"  -> Successfully merged {len(merged_df) - missing_fx:,} records with FX data")

        return merged_df

    def calculate_usd_values(self, df):
        """
        Calculate USD values from MXN values and FX rates.

        Args:
            df: DataFrame with valueMXN and FX_EOM columns

        Returns:
            DataFrame with added valueUSD column
        """
        print("\nCalculating USD values...")

        # Calculate USD values (valueUSD = valueMXN / FX_EOM)
        df["valueUSD"] = df["valueMXN"] / df["FX_EOM"]

        # Count valid calculations
        valid_usd = df["valueUSD"].notna().sum()
        print(f"  -> Calculated USD values for {valid_usd:,} records")

        # Show some statistics
        if valid_usd > 0:
            total_mxn = df["valueMXN"].sum()
            avg_fx = df["FX_EOM"].mean()
            total_usd = df["valueUSD"].sum()

            print(f"\nSummary Statistics:")
            print(f"  Total valueMXN: ${total_mxn:,.0f}")
            print(f"  Average FX Rate: {avg_fx:.2f} MXN/USD")
            print(f"  Total valueUSD: ${total_usd:,.0f}")

        return df

    def reorder_columns(self, df):
        """
        Reorder columns for better readability.

        Args:
            df: DataFrame to reorder

        Returns:
            DataFrame with reordered columns
        """
        # Preferred column order
        priority_cols = [
            "Afore", "Siefore", "Concept",
            "PeriodYear", "PeriodMonth",
            "valueMXN", "FX_EOM", "valueUSD"
        ]

        # Get remaining columns
        remaining_cols = [col for col in df.columns if col not in priority_cols]

        # Combine: priority columns first, then any others
        ordered_cols = [col for col in priority_cols if col in df.columns] + remaining_cols

        return df[ordered_cols]

    def save_enriched_data(self, df):
        """
        Save enriched data to JSON file.

        Args:
            df: DataFrame with enriched data
        """
        print(f"\nSaving enriched database to: {self.output_path}")

        # Ensure output directory exists
        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)

        # Save to JSON
        df.to_json(self.output_path, orient="records", indent=2, force_ascii=False)

        file_size = os.path.getsize(self.output_path) / (1024 * 1024)
        print(f"  ✓ Saved {len(df):,} records")
        print(f"  ✓ File size: {file_size:.2f} MB")

    def generate_summary_report(self, df):
        """
        Generate summary statistics report.

        Args:
            df: Enriched DataFrame
        """
        print("\n" + "=" * 70)
        print("ENRICHMENT SUMMARY")
        print("=" * 70)

        # Overall stats
        print(f"\nTotal Records: {len(df):,}")
        print(f"Records with FX data: {df['FX_EOM'].notna().sum():,}")
        print(f"Records with USD values: {df['valueUSD'].notna().sum():,}")

        # Date range
        min_date = f"{df['PeriodYear'].min()}-{df['PeriodMonth'].min()}"
        max_date = f"{df['PeriodYear'].max()}-{df['PeriodMonth'].max()}"
        print(f"\nDate Range: {min_date} to {max_date}")

        # By Siefore
        print(f"\nRecords by Siefore:")
        siefore_counts = df.groupby("Siefore").size().sort_values(ascending=False)
        for siefore, count in siefore_counts.items():
            print(f"  • {siefore:12} : {count:,} records")

        # FX rate statistics
        if df["FX_EOM"].notna().any():
            print(f"\nFX Rate Statistics:")
            print(f"  Min: {df['FX_EOM'].min():.4f} MXN/USD")
            print(f"  Max: {df['FX_EOM'].max():.4f} MXN/USD")
            print(f"  Mean: {df['FX_EOM'].mean():.4f} MXN/USD")
            print(f"  Median: {df['FX_EOM'].median():.4f} MXN/USD")

    def run(self):
        """Execute the complete USD enrichment pipeline."""
        print("=" * 70)
        print("USD Value Enrichment Pipeline")
        print("=" * 70)
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

        try:
            # Load data
            afore_df, fx_df = self.load_data()

            # Merge FX data
            merged_df = self.merge_fx_data(afore_df, fx_df)

            # Calculate USD values
            enriched_df = self.calculate_usd_values(merged_df)

            # Reorder columns
            enriched_df = self.reorder_columns(enriched_df)

            # Save enriched data
            self.save_enriched_data(enriched_df)

            # Generate summary
            self.generate_summary_report(enriched_df)

            print(f"\nCompleted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("=" * 70)

        except Exception as e:
            print(f"\n❌ Error: {e}")
            raise


# === MAIN EXECUTION ===
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Enrich Afore database with USD values")
    parser.add_argument("--afore-data", default="/Users/lvc/AI Scripts/2025_10 Afore JSON cleanup/consar_siefores_full.json",
                        help="Path to base Afore JSON database")
    parser.add_argument("--fx-data", default="/Users/lvc/AI Scripts/2025_10 Afore JSON cleanup/2025_10 files/fx_data.json",
                        help="Path to FX rates JSON file")
    parser.add_argument("--output", default="/Users/lvc/AI Scripts/2025_10 Afore JSON cleanup/consar_siefores_with_usd.json",
                        help="Output path for enriched database")

    args = parser.parse_args()

    agent = USDEnrichmentAgent(
        afore_data_path=args.afore_data,
        fx_data_path=args.fx_data,
        output_path=args.output
    )

    agent.run()
