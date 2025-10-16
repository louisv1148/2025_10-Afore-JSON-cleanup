#!/usr/bin/env python3
"""
Complete Afore Database Pipeline
=================================
This script orchestrates the complete data pipeline:
1. Build base Afore database from Excel files
2. Fetch FX rates from Banxico
3. Enrich database with USD values

Usage:
    python run_full_pipeline.py                    # Run complete pipeline
    python run_full_pipeline.py --skip-rebuild     # Skip step 1 if data exists
    python run_full_pipeline.py --skip-fx          # Skip step 2 if FX data exists
"""

import sys
import os
from datetime import datetime
import argparse

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import our pipeline modules
from cleanup_afore_json import main as rebuild_database
from fetch_banxico_fx import BanxicoFXAgent
from enrich_with_usd import USDEnrichmentAgent


class PipelineOrchestrator:
    """Orchestrates the complete data pipeline."""

    def __init__(self, base_path, skip_rebuild=False, skip_fx=False, force_fx=False):
        """
        Initialize the pipeline orchestrator.

        Args:
            base_path: Base directory path
            skip_rebuild: Skip database rebuild if output exists
            skip_fx: Skip FX fetch if output exists
            force_fx: Force FX refresh even if cached
        """
        self.base_path = base_path
        self.skip_rebuild = skip_rebuild
        self.skip_fx = skip_fx
        self.force_fx = force_fx

        # Define file paths
        self.afore_db_path = os.path.join(base_path, "consar_siefores_full.json")
        self.fx_data_path = os.path.join(base_path, "2025_10 files", "fx_data.json")
        self.enriched_db_path = os.path.join(base_path, "consar_siefores_with_usd.json")

    def print_header(self, title):
        """Print formatted section header."""
        print("\n" + "=" * 70)
        print(f"STEP: {title}")
        print("=" * 70 + "\n")

    def step1_rebuild_database(self):
        """Step 1: Build base Afore database from Excel files."""
        self.print_header("1/3 - Rebuild Afore Database")

        if self.skip_rebuild and os.path.exists(self.afore_db_path):
            print(f"ℹ️  Skipping database rebuild (file exists)")
            print(f"   Using: {self.afore_db_path}")
            file_size = os.path.getsize(self.afore_db_path) / (1024 * 1024)
            print(f"   Size: {file_size:.2f} MB")
            return True

        try:
            print("Running cleanup_afore_json.py...")
            rebuild_database()
            print("\n✅ Step 1 completed: Database rebuilt successfully")
            return True
        except Exception as e:
            print(f"\n❌ Step 1 failed: {e}")
            return False

    def step2_fetch_fx_data(self):
        """Step 2: Fetch FX rates from Banxico."""
        self.print_header("2/3 - Fetch Banxico FX Data")

        if self.skip_fx and os.path.exists(self.fx_data_path) and not self.force_fx:
            print(f"ℹ️  Skipping FX data fetch (file exists)")
            print(f"   Using: {self.fx_data_path}")
            file_size = os.path.getsize(self.fx_data_path) / 1024
            print(f"   Size: {file_size:.1f} KB")
            return True

        try:
            print("Running fetch_banxico_fx.py...")
            agent = BanxicoFXAgent(
                output_path=self.fx_data_path,
                cache_hours=24
            )
            agent.run(force_refresh=self.force_fx)
            print("\n✅ Step 2 completed: FX data fetched successfully")
            return True
        except Exception as e:
            print(f"\n❌ Step 2 failed: {e}")
            return False

    def step3_enrich_with_usd(self):
        """Step 3: Enrich database with USD values."""
        self.print_header("3/3 - Enrich with USD Values")

        try:
            print("Running enrich_with_usd.py...")
            agent = USDEnrichmentAgent(
                afore_data_path=self.afore_db_path,
                fx_data_path=self.fx_data_path,
                output_path=self.enriched_db_path
            )
            agent.run()
            print("\n✅ Step 3 completed: Database enriched successfully")
            return True
        except Exception as e:
            print(f"\n❌ Step 3 failed: {e}")
            return False

    def verify_outputs(self):
        """Verify all expected outputs exist."""
        print("\n" + "=" * 70)
        print("VERIFICATION")
        print("=" * 70 + "\n")

        files_to_check = [
            ("Base Database", self.afore_db_path),
            ("FX Data", self.fx_data_path),
            ("Enriched Database", self.enriched_db_path)
        ]

        all_exist = True
        for name, path in files_to_check:
            if os.path.exists(path):
                size_mb = os.path.getsize(path) / (1024 * 1024)
                print(f"✓ {name:20} : {size_mb:.2f} MB")
            else:
                print(f"✗ {name:20} : NOT FOUND")
                all_exist = False

        return all_exist

    def run(self):
        """Execute the complete pipeline."""
        print("=" * 70)
        print("AFORE DATABASE COMPLETE PIPELINE")
        print("=" * 70)
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Working directory: {self.base_path}\n")

        start_time = datetime.now()

        # Execute pipeline steps
        steps = [
            ("Rebuild Database", self.step1_rebuild_database),
            ("Fetch FX Data", self.step2_fetch_fx_data),
            ("Enrich with USD", self.step3_enrich_with_usd)
        ]

        for i, (name, step_func) in enumerate(steps, 1):
            success = step_func()
            if not success:
                print(f"\n❌ Pipeline failed at step {i}: {name}")
                return False

        # Verify outputs
        if not self.verify_outputs():
            print("\n⚠️  Warning: Some output files are missing")
            return False

        # Success summary
        duration = (datetime.now() - start_time).total_seconds()
        print("\n" + "=" * 70)
        print("✅ PIPELINE COMPLETED SUCCESSFULLY!")
        print("=" * 70)
        print(f"Duration: {duration:.1f} seconds")
        print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"\nFinal output: {self.enriched_db_path}")
        print("=" * 70)

        return True


# === MAIN EXECUTION ===
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run the complete Afore database pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run complete pipeline
  python run_full_pipeline.py

  # Skip database rebuild if it exists
  python run_full_pipeline.py --skip-rebuild

  # Skip FX fetch if it exists
  python run_full_pipeline.py --skip-fx

  # Force fresh FX data
  python run_full_pipeline.py --force-fx

  # Skip both rebuild and FX fetch (only enrich)
  python run_full_pipeline.py --skip-rebuild --skip-fx
        """
    )

    parser.add_argument("--skip-rebuild", action="store_true",
                        help="Skip database rebuild if output file exists")
    parser.add_argument("--skip-fx", action="store_true",
                        help="Skip FX data fetch if output file exists")
    parser.add_argument("--force-fx", action="store_true",
                        help="Force fresh FX data fetch, ignore cache")
    parser.add_argument("--base-path", default="/Users/lvc/AI Scripts/2025_10 Afore JSON cleanup",
                        help="Base directory path (default: current project directory)")

    args = parser.parse_args()

    # Create and run orchestrator
    orchestrator = PipelineOrchestrator(
        base_path=args.base_path,
        skip_rebuild=args.skip_rebuild,
        skip_fx=args.skip_fx,
        force_fx=args.force_fx
    )

    success = orchestrator.run()
    sys.exit(0 if success else 1)
