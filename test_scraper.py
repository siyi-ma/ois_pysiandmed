import pandas as pd
import os
import re
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
import time
import warnings

def simple_scrape_test():
    """Simple test of scraping logic."""
    
    # Test with the saved text file
    if os.path.exists("full_page_text.txt"):
        print("Using saved page text for testing...")
        with open("full_page_text.txt", "r", encoding="utf-8") as f:
            body_text = f.read()
        
        lines = body_text.split('\n')
        
        valid_schools = [
            "EESTI MEREAKADEEMIA",
            "INFOTEHNOLOOGIA TEADUSKOND", 
            "INSENERITEADUSKOND",
            "LOODUSTEADUSKOND",
            "MAJANDUSTEADUSKOND"
        ]
        
        programme_school_map = {}
        current_school = "Teaduskond määramata"
        
        for i, line in enumerate(lines):
            line = line.strip()
            
            if not line:
                continue
                
            # Check for school names
            if line in valid_schools:
                current_school = line
                print(f"Found school at line {i}: {current_school}")
                continue
            
            # Check for programme pattern with colon
            programme_pattern = r'^(.+?)\s*\(([A-Z]{4}\d{2})\):?.*$'
            match = re.match(programme_pattern, line)
            
            if match and current_school != "Teaduskond määramata":
                programme_name = match.group(1).strip()
                full_code = match.group(2)
                code_prefix = full_code[:4]
                
                if (len(programme_name) >= 3 and 
                    programme_name not in valid_schools):
                    
                    # Use full code as key to avoid overwriting programmes with same 4-char prefix
                    programme_school_map[full_code] = {
                        'full_code': full_code,
                        'programme_name': programme_name,
                        'school': current_school,
                        'code_prefix': code_prefix
                    }
                    
                    print(f"  Programme: {programme_name} ({full_code}) -> {current_school}")
        
        print(f"\nTotal scraped: {len(programme_school_map)} programmes")
        
        # Show summary by school
        school_counts = {}
        for full_code, info in programme_school_map.items():
            school = info['school']
            school_counts[school] = school_counts.get(school, 0) + 1
        
        for school, count in school_counts.items():
            print(f"  {school}: {count} programmes")
        
        # Show details for INFOTEHNOLOOGIA TEADUSKOND
        print(f"\nINFOTEHNOLOOGIA TEADUSKOND programmes:")
        it_programmes = [(code, info) for code, info in programme_school_map.items() 
                        if info['school'] == 'INFOTEHNOLOOGIA TEADUSKOND']
        for i, (code, info) in enumerate(sorted(it_programmes), 1):
            print(f"  {i:2d}. {info['programme_name']} ({code})")
            
        return programme_school_map
    else:
        print("No saved page text found. Run debug_scraper.py first.")
        return {}

if __name__ == "__main__":
    simple_scrape_test()