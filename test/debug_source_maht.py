#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Quick debug to examine source CSV maht column
"""

import pandas as pd
import os
from pathlib import Path

# Find the newest CSV file
csv_folder = r"C:\Users\siyi.ma\OneDrive - Tallinna Tehnikaülikool\OIS\csv\Otsing_oppekavad"
folder = Path(csv_folder)
csv_files = list(folder.glob('*.csv'))
newest_file = max(csv_files, key=os.path.getmtime)

print(f"Examining: {newest_file}")

# Load with correct encoding
df = pd.read_csv(newest_file, encoding='utf-8-sig', sep=';')

print(f"Shape: {df.shape}")
print(f"Columns: {list(df.columns)}")

# Find maht column
maht_cols = [col for col in df.columns if 'maht' in col.lower()]
print(f"\nColumns with 'maht': {maht_cols}")

# Find EAP column
eap_cols = [col for col in df.columns if 'eap' in col.lower()]
print(f"Columns with 'EAP': {eap_cols}")

# Find the target column
target_col = None
for col in df.columns:
    if 'maht' in col.lower() and 'eap' in col.lower():
        target_col = col
        break

if target_col:
    print(f"\nTarget column: '{target_col}'")
    print(f"Sample values: {df[target_col].head(10).tolist()}")
    print(f"Unique values: {df[target_col].value_counts().head(10)}")
    print(f"Data type: {df[target_col].dtype}")
    
    # Test numeric conversion
    numeric_test = pd.to_numeric(df[target_col], errors='coerce')
    print(f"\nAfter numeric conversion:")
    print(f"Valid numbers: {numeric_test.notna().sum()}")
    print(f"NaN values: {numeric_test.isna().sum()}")
    print(f"Unique numeric values: {numeric_test.value_counts().head(10)}")
else:
    print("\nNo column found with both 'maht' and 'EAP'")
    print("All columns:")
    for i, col in enumerate(df.columns):
        print(f"  {i}: '{col}'")