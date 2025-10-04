#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Debug script to examine maht column data
"""

import pandas as pd
import os
from pathlib import Path

def find_newest_csv(folder_path):
    """Find the newest CSV file in the given folder."""
    folder = Path(folder_path)
    if not folder.exists():
        return None
    
    csv_files = list(folder.glob('*.csv'))
    if not csv_files:
        return None
    
    # Get the newest file by modification time
    newest_file = max(csv_files, key=os.path.getmtime)
    return newest_file

def examine_maht_column():
    """Examine the maht column data to understand why values are 0."""
    
    # Find the newest CSV file
    csv_folder = r"C:\Users\siyi.ma\OneDrive - Tallinna Tehnikaülikool\OIS\csv\Otsing_oppekavad"
    csv_file = find_newest_csv(csv_folder)
    
    if not csv_file:
        print("No CSV file found!")
        return
    
    print(f"Examining file: {csv_file}")
    
    # Try different encodings
    encodings = ['utf-8-sig', 'windows-1257', 'iso-8859-4', 'utf-8', 'cp1252']
    df = None
    
    for encoding in encodings:
        try:
            df = pd.read_csv(csv_file, encoding=encoding, sep=';')
            print(f"Successfully loaded with encoding: {encoding}")
            break
        except:
            continue
    
    if df is None:
        print("Could not load CSV file with any encoding")
        return
    
    print(f"\nDataFrame shape: {df.shape}")
    print(f"Columns: {list(df.columns)}")
    
    # Find maht-related columns
    maht_columns = [col for col in df.columns if 'maht' in col.lower()]
    print(f"\nColumns containing 'maht': {maht_columns}")
    
    # Look for columns with EAP
    eap_columns = [col for col in df.columns if 'eap' in col.lower()]
    print(f"Columns containing 'eap': {eap_columns}")
    
    # Find the specific column we're looking for
    target_column = None
    for col in df.columns:
        if 'maht' in col.lower() and 'eap' in col.lower():
            target_column = col
            break
    
    if target_column:
        print(f"\nTarget column found: '{target_column}'")
        print(f"Data type: {df[target_column].dtype}")
        print(f"Unique values (first 20): {df[target_column].value_counts().head(20)}")
        print(f"Sample values: {df[target_column].head(10).tolist()}")
        print(f"Non-null count: {df[target_column].notna().sum()}")
        print(f"Null count: {df[target_column].isna().sum()}")
        
        # Try to convert to numeric and see what happens
        numeric_series = pd.to_numeric(df[target_column], errors='coerce')
        print(f"\nAfter pd.to_numeric conversion:")
        print(f"Non-null count: {numeric_series.notna().sum()}")
        print(f"Null count: {numeric_series.isna().sum()}")
        print(f"Unique numeric values: {numeric_series.value_counts().head(10)}")
        
    else:
        print("\nNo column found with both 'maht' and 'eap'")
        print("Available columns:")
        for i, col in enumerate(df.columns):
            print(f"  {i}: '{col}'")

if __name__ == "__main__":
    examine_maht_column()