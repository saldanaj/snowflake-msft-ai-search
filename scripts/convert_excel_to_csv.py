#!/usr/bin/env python3
"""
Convert Excel sample data to CSV for analysis.
"""

import pandas as pd
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def convert_excel_to_csv():
    """Convert Excel file to CSV."""
    excel_path = project_root / "data" / "prep" / "sample_data.xlsx"
    csv_path = project_root / "data" / "prep" / "sample_data.csv"

    print(f"Reading Excel file: {excel_path}")

    try:
        # Read Excel file - try openpyxl engine first for .xlsx files
        try:
            df = pd.read_excel(excel_path, engine='openpyxl')
        except Exception as e1:
            print(f"  Trying alternate engine due to: {e1}")
            # Fall back to default engine
            df = pd.read_excel(excel_path)

        print(f"\nFound {len(df)} rows and {len(df.columns)} columns")
        print(f"\nColumns: {list(df.columns)}")
        print(f"\nData types:\n{df.dtypes}")
        print(f"\nFirst few rows:\n{df.head()}")

        # Save to CSV
        df.to_csv(csv_path, index=False)
        print(f"\nSaved to CSV: {csv_path}")

        # Print sample of data
        print(f"\n{'='*80}")
        print("Sample Data Preview:")
        print(f"{'='*80}")
        for idx, row in df.head(3).iterrows():
            print(f"\nRow {idx + 1}:")
            for col in df.columns:
                print(f"  {col}: {row[col]}")

        return df

    except Exception as e:
        print(f"Error reading Excel file: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    convert_excel_to_csv()
