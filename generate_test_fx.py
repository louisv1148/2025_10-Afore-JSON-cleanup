#!/usr/bin/env python3
"""
Generate Test FX Data
=====================
Temporary script to generate test FX data for pipeline testing
while we resolve the Banxico API access issue.
"""

import pandas as pd
import json
from datetime import datetime
import os

# Generate monthly FX rates from 2019-01 to 2025-08
# Using approximate historical rates
dates = pd.date_range(start="2019-01-01", end="2025-08-31", freq="MS")

records = []
for date in dates:
    # Simulate realistic FX rates (actual rates range from ~18 to ~21 MXN/USD in this period)
    # Adding some variation
    base_rate = 19.5
    year_factor = (date.year - 2019) * 0.3
    month_factor = (date.month / 12) * 0.5
    fx_rate = base_rate + year_factor + month_factor

    records.append({
        "PeriodYear": str(date.year),
        "PeriodMonth": str(date.month).zfill(2),
        "FX_EOM": round(fx_rate, 4)
    })

df = pd.DataFrame(records)

# Save to file
output_path = "/Users/lvc/AI Scripts/2025_10 Afore JSON cleanup/2025_10 files/fx_data.json"
os.makedirs(os.path.dirname(output_path), exist_ok=True)
df.to_json(output_path, orient="records", indent=2)

print(f"✅ Generated {len(df)} test FX records")
print(f"   Range: {df['PeriodYear'].min()}-{df['PeriodMonth'].min()} to {df['PeriodYear'].max()}-{df['PeriodMonth'].max()}")
print(f"   FX range: {df['FX_EOM'].min():.2f} to {df['FX_EOM'].max():.2f} MXN/USD")
print(f"   Saved to: {output_path}")
