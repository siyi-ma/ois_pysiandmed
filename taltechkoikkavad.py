import pandas as pd
import os
import re
from pathlib import Path
try:
    import pyarrow as pa
    import pyarrow.parquet as pq
    PARQUET_AVAILABLE = True
except ImportError:
    PARQUET_AVAILABLE = False
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
import time
import warnings

# Suppress pandas SettingWithCopyWarning
warnings.filterwarnings('ignore', category=pd.errors.SettingWithCopyWarning)

def scrape_study_programmes():
    """Scrape study programmes and their schools from TalTech timetable."""
    
    driver_path = r"C:\edgedriver_win64\msedgedriver.exe"
    if not os.path.exists(driver_path):
        warnings.warn(f"EdgeDriver not found at {driver_path}. Please download latest version.")
        return {}
    
    service = Service(driver_path)
    
    options = webdriver.EdgeOptions()
    options.add_argument('--headless')  # Run in background
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-logging')  # Suppress logs
    options.add_argument('--log-level=3')  # Only fatal errors
    options.add_argument('--disable-extensions')
    options.add_argument('--disable-gpu')
    
    programme_school_map = {}
    
    # Define the exact 5 schools
    valid_schools = [
        "EESTI MEREAKADEEMIA",
        "INFOTEHNOLOOGIA TEADUSKOND", 
        "INSENERITEADUSKOND",
        "LOODUSTEADUSKOND",
        "MAJANDUSTEADUSKOND"
    ]
    
    try:
        driver = webdriver.Edge(service=service, options=options)
        driver.get("https://tunniplaan.taltech.ee/#/public")
        
        # Wait for page to load
        wait = WebDriverWait(driver, 15)
        time.sleep(5)  # Allow dynamic content to load
        
        current_school = "Teaduskond määramata"
        
        # Get page source and split by lines for sequential processing
        page_source = driver.page_source
        
        # Get all text elements in order
        all_elements = driver.find_elements(By.XPATH, "//*[text()]")
        
        for element in all_elements:
            try:
                text = element.text.strip()
                
                # Skip empty text
                if not text:
                    continue
                    
                # Check if this is one of the 5 valid schools (exact match)
                if text in valid_schools:
                    current_school = text
                    print(f"Found school: {current_school}")
                    continue
                
                # Check if this is a study programme with valid format
                # Programme format: "Programme Name (ABCD12):" - note the colon at the end
                programme_pattern = r'^(.+?)\s*\(([A-Z]{4}\d{2})\):?.*$'
                match = re.match(programme_pattern, text)
                
                if match:
                    programme_name = match.group(1).strip()
                    full_code = match.group(2)
                    
                    # Skip if programme name is too short or is a school name
                    if (len(programme_name) < 3 or 
                        programme_name in valid_schools or
                        programme_name.upper() in [s.upper() for s in valid_schools]):
                        continue
                    
                    # Skip if element is a link (pink text)
                    try:
                        if (element.tag_name == 'a' or 
                            element.find_element(By.XPATH, "./ancestor::a") or
                            'color' in element.get_attribute('style') and 'rgb(233, 30, 99)' in element.get_attribute('style')):
                            continue
                    except:
                        pass
                    
                    # Only add if we have a valid current school
                    if current_school != "Teaduskond määramata":
                        # Use full code as key to avoid overwriting programmes with same 4-char prefix
                        programme_school_map[full_code] = {
                            'full_code': full_code,
                            'programme_name': programme_name,
                            'school': current_school
                        }
                        
                        # Only print during scraping, not when loading from JSON
                        if not hasattr(scrape_study_programmes, '_quiet_mode'):
                            print(f"  Programme: {programme_name} ({full_code}) -> {current_school}")
                        
            except Exception as e:
                continue
        
        # If no programmes found, try alternative approach with more flexible parsing
        if not programme_school_map:
            print("Trying alternative parsing method...")
            
            # Get all text content and process line by line
            body_text = driver.find_element(By.TAG_NAME, "body").text
            lines = body_text.split('\n')
            
            current_school = "Teaduskond määramata"
            
            for line in lines:
                line = line.strip()
                
                # Check for school names
                if line in valid_schools:
                    current_school = line
                    print(f"Found school: {current_school}")
                    continue
                
                # Check for programme pattern - updated to handle colon
                programme_pattern = r'^(.+?)\s*\(([A-Z]{4}\d{2})\):?.*$'
                match = re.match(programme_pattern, line)
                
                if match and current_school != "Teaduskond määramata":
                    programme_name = match.group(1).strip()
                    full_code = match.group(2)
                    
                    if (len(programme_name) >= 3 and 
                        programme_name not in valid_schools):
                        
                        # Use full code as key to avoid overwriting programmes with same 4-char prefix
                        programme_school_map[full_code] = {
                            'full_code': full_code,
                            'programme_name': programme_name,
                            'school': current_school
                        }
                        
                        if not hasattr(scrape_study_programmes, '_quiet_mode'):
                            print(f"  Programme: {programme_name} ({full_code}) -> {current_school}")
                    
    except WebDriverException as e:
        error_msg = str(e).lower()
        if any(keyword in error_msg for keyword in ['version', 'chrome', 'browser', 'driver']):
            print("\nWARNING: EdgeDriver version mismatch detected!")
            print("   Your Edge browser may have updated but EdgeDriver hasn't.")
            print("   Please download the latest EdgeDriver from:")
            print("   https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/")
            print(f"   Install it to: C:\\edgedriver_win64\\msedgedriver.exe\n")
        else:
            print(f"WebDriver error: {e}")
        
    except Exception as e:
        print(f"Error during web scraping: {e}")
        
    finally:
        try:
            driver.quit()
        except:
            pass
    
    print(f"Scraped {len(programme_school_map)} study programmes")
    
    # Show summary by school
    school_counts = {}
    for code, info in programme_school_map.items():
        school = info['school']
        school_counts[school] = school_counts.get(school, 0) + 1
    
    for school, count in school_counts.items():
        print(f"  {school}: {count} programmes")
    
    return programme_school_map

def determine_school_from_programme(programme_name, code):
    """Fallback function - not used when scraping actual school names."""
    return 'Teaduskond määramata'

def find_newest_csv(folder_path):
    """Find the newest CSV file in the folder by creation date."""
    folder = Path(folder_path)
    csv_files = list(folder.glob("*.csv"))
    
    if not csv_files:
        raise FileNotFoundError(f"No CSV files found in {folder_path}")
    
    # Sort by creation time (newest first)
    newest_file = max(csv_files, key=lambda f: f.stat().st_ctime)
    return newest_file

def process_taltechkoikkavad():
    """Replicate Power Query ETL steps to generate taltechkoikkavad.csv."""
    
    # Input and output paths
    input_folder = r"C:\Users\siyi.ma\OneDrive - Tallinna Tehnikaülikool\OIS\csv\Otsing_oppekavad"
    output_folder = r"C:\Users\siyi.ma\OneDrive - Tallinna Tehnikaülikool\OIS\pysiandmed"
    output_file = Path(output_folder) / "taltechkoikkavad.csv"
    
    # Ensure output folder exists
    Path(output_folder).mkdir(parents=True, exist_ok=True)
    
    # NEW: Scrape study programmes and schools
    print("Scraping study programmes from TalTech timetable...")
    programme_school_map = scrape_study_programmes()
    
    # Step 1: Find newest CSV file (equivalent to sorted rows by date created)
    newest_csv = find_newest_csv(input_folder)
    print(f"Processing file: {newest_csv}")
    
    # Step 2: Read CSV with specific encoding and delimiter
    # Try multiple encodings for Baltic characters
    encodings = ['utf-8-sig', 'windows-1257', 'iso-8859-4', 'utf-8', 'cp1252']
    df = None
    
    for encoding in encodings:
        try:
            df = pd.read_csv(newest_csv, 
                           delimiter=';', 
                           encoding=encoding,
                           header=1,  # Skip first row, use second row as header
                           skipinitialspace=True)
            print(f"Successfully read with encoding: {encoding}")
            break
        except (UnicodeDecodeError, pd.errors.EmptyDataError):
            continue
    
    if df is None:
        raise ValueError("Could not read CSV with any supported encoding")
    
    # Handle BOM and clean column names
    df.columns = df.columns.str.strip().str.replace('\ufeff', '')
    
    # Drop any columns with blank/NaN/BOM-only names
    df = df.loc[:, ~df.columns.isin(['', ' ', '\ufeff']) & df.columns.notna()]
    
    # Debug: Print available columns
    print("Available columns:")
    for i, col in enumerate(df.columns):
        print(f"{i}: '{col}'")
    
    # Map expected columns to actual columns (handle variations)
    column_mapping = {}
    for col in df.columns:
        col_lower = col.lower().strip()
        if 'õppekava kood' in col_lower and 'taltech' in col_lower:
            column_mapping['TalTechi õppekava kood'] = col
        elif 'maht' in col_lower and 'eap' in col_lower:
            column_mapping['maht (EAP)'] = col
        elif 'õppekavaversiooni kood' in col_lower:
            column_mapping['õppekavaversiooni kood'] = col
        elif 'nimetus e.k' in col_lower:
            column_mapping['nimetus e.k.'] = col
        elif 'nimetus i.k' in col_lower:
            column_mapping['nimetus i.k.'] = col
        elif 'õppetase' in col_lower:
            column_mapping['õppetase'] = col
        elif 'nominaalne õppeaeg' in col_lower:
            column_mapping['nominaalne õppeaeg (semestrites)'] = col
        elif 'programmijuhi nimi' in col_lower or 'õppekava juhi' in col_lower:
            column_mapping['õppekava juhi/programmijuhi nimi'] = col
        elif 'peakeel' in col_lower:
            column_mapping['peakeel'] = col
        elif 'õppevaldkond' in col_lower:
            column_mapping['õppevaldkond'] = col
    
    # Check if required columns are found
    required_columns = ['TalTechi õppekava kood', 'maht (EAP)', 'õppekavaversiooni kood']
    missing_columns = [col for col in required_columns if col not in column_mapping]
    
    if missing_columns:
        print(f"Missing required columns: {missing_columns}")
        print("Available columns for manual mapping:")
        for col in df.columns:
            print(f"  '{col}'")
        return None
    
    # Step 3: Clean data - remove rows where "maht (EAP)" is empty
    maht_col = column_mapping['maht (EAP)']
    df_clean = df[df[maht_col].notna() & (df[maht_col] != '')]
    
    # Step 4: Group by full TalTechi õppekava kood, sort by version descending, take first
    # This ensures we get the latest version of each programme
    kava_col = column_mapping['TalTechi õppekava kood']
    version_col = column_mapping['õppekavaversiooni kood']
    df_sorted = df_clean.sort_values(version_col, ascending=False)
    df_grouped = df_sorted.groupby(kava_col).first().reset_index()
    
    # Step 5: Select and rename columns using mapped column names
    output_columns = {
        'kavakood': column_mapping.get('TalTechi õppekava kood'),
        'nimetusek': column_mapping.get('nimetus e.k.'),
        'nimetusik': column_mapping.get('nimetus i.k.'),
        'tase': column_mapping.get('õppetase'),
        'maht': column_mapping.get('maht (EAP)'),
        'nominaalne_oppeaeg': column_mapping.get('nominaalne õppeaeg (semestrites)'),
        'programmijuht': column_mapping.get('õppekava juhi/programmijuhi nimi'),
        'peakeel': column_mapping.get('peakeel'),
        'oppevaldkond': column_mapping.get('õppevaldkond')
    }
    
    # Filter out columns that weren't found
    available_columns = {k: v for k, v in output_columns.items() if v is not None}
    
    # Select available columns and rename
    df_final = df_grouped[list(available_columns.values())].copy()
    df_final.columns = list(available_columns.keys())
    
    # Step 7: Transform data types and uppercase "tase"
    if 'kavakood' in df_final.columns:
        df_final['kavakood'] = df_final['kavakood'].astype(str)
    if 'nimetusek' in df_final.columns:
        df_final['nimetusek'] = df_final['nimetusek'].astype(str)
    if 'nimetusik' in df_final.columns:
        df_final['nimetusik'] = df_final['nimetusik'].astype(str)
    if 'tase' in df_final.columns:
        df_final['tase'] = df_final['tase'].astype(str).str.upper()
    if 'maht' in df_final.columns:
        # Handle European decimal format (comma) and convert to numeric
        df_final['maht'] = df_final['maht'].astype(str).str.replace(',', '.', regex=False)
        df_final['maht'] = pd.to_numeric(df_final['maht'], errors='coerce')
        df_final['maht'] = df_final['maht'].fillna(0).astype(int)
    if 'nominaalne_oppeaeg' in df_final.columns:
        df_final['nominaalne_oppeaeg'] = pd.to_numeric(df_final['nominaalne_oppeaeg'], errors='coerce')
        df_final['nominaalne_oppeaeg'] = df_final['nominaalne_oppeaeg'].fillna(0).astype(int)
    if 'programmijuht' in df_final.columns:
        df_final['programmijuht'] = df_final['programmijuht'].astype(str)
    if 'peakeel' in df_final.columns:
        df_final['peakeel'] = df_final['peakeel'].astype(str)
    if 'oppevaldkond' in df_final.columns:
        df_final['oppevaldkond'] = df_final['oppevaldkond'].astype(str)
    
    # Step 7.5: Add teaduskond mapping
    if 'kavakood' in df_final.columns:
        # Create a lookup dictionary from full_code to school
        code_to_school = {}
        for full_code, info in programme_school_map.items():
            school = info['school']
            code_to_school[full_code] = school
        
        # First pass: direct mapping from scraped data
        df_final['teaduskond'] = df_final['kavakood'].map(
            lambda x: code_to_school.get(x, 'Teaduskond määramata')
        )
        
        # Add mapping source column
        df_final['teaduskond_allikas'] = df_final['kavakood'].map(
            lambda x: 'Scraped' if x in code_to_school else 'Unmapped'
        )
        
        mapped_count = sum(df_final['teaduskond'] != 'Teaduskond määramata')
        unmapped_count = sum(df_final['teaduskond'] == 'Teaduskond määramata')
        print(f"Mapped {mapped_count} programmes to schools (from {len(programme_school_map)} scraped programmes)")
        print(f"Unmapped programmes: {unmapped_count}")
        
        # Debug: Show which programmes were mapped
        mapped_programmes = df_final[df_final['teaduskond_allikas'] == 'Scraped']['kavakood'].tolist()
        print(f"Scraped programmes found in CSV: {len(mapped_programmes)}")
        if len(mapped_programmes) < len(programme_school_map):
            scraped_codes = set(programme_school_map.keys())
            csv_codes = set(df_final['kavakood'].tolist())
            missing_in_csv = scraped_codes - csv_codes
            print(f"Scraped codes not found in CSV ({len(missing_in_csv)}): {sorted(missing_in_csv)}")
        
        # Second pass: educated guessing for unmapped programmes
        if unmapped_count > 0:
            print("Making educated guesses for unmapped programmes based on study fields...")
            
            def guess_teaduskond(row):
                if row['teaduskond'] != 'Teaduskond määramata':
                    return row['teaduskond'], row['teaduskond_allikas']
                
                # Get study field and group for guessing
                oppevaldkond = str(row.get('oppevaldkond', '')).lower() if 'oppevaldkond' in row else ''
                
                # Educated guessing based on study field patterns
                if any(word in oppevaldkond for word in ['informaatika', 'infotehnoloogia', 'arvutiteadus', 'küberturve', 'it']):
                    return 'INFOTEHNOLOOGIA TEADUSKOND', 'Guessed'
                elif any(word in oppevaldkond for word in ['ehitus', 'arhitektuur', 'insener', 'tehnika', 'tehnoloogia', 'energia', 'elektro', 'masina', 'material']):
                    return 'INSENERITEADUSKOND', 'Guessed'
                elif any(word in oppevaldkond for word in ['loodus', 'füüsika', 'matemaatika', 'keemia', 'bio', 'geo', 'öko']):
                    return 'LOODUSTEADUSKOND', 'Guessed'
                elif any(word in oppevaldkond for word in ['majandus', 'äri', 'juht', 'õigus', 'avalik', 'poliitika', 'sotsiaal']):
                    return 'MAJANDUSTEADUSKOND', 'Guessed'
                elif any(word in oppevaldkond for word in ['mere', 'laev', 'vesi', 'sadama']):
                    return 'EESTI MEREAKADEEMIA', 'Guessed'
                else:
                    # Look at programme code patterns as last resort
                    kavakood = str(row.get('kavakood', ''))
                    if kavakood.startswith(('I', 'V')):  # Common IT/CS prefixes
                        return 'INFOTEHNOLOOGIA TEADUSKOND', 'Guessed'
                    elif kavakood.startswith(('E', 'M', 'R')):  # Common engineering prefixes
                        return 'INSENERITEADUSKOND', 'Guessed'
                    elif kavakood.startswith(('L', 'Y', 'K')):  # Common natural sciences prefixes
                        return 'LOODUSTEADUSKOND', 'Guessed'
                    elif kavakood.startswith(('T', 'H')):  # Common business/social prefixes
                        return 'MAJANDUSTEADUSKOND', 'Guessed'
                    elif kavakood.startswith('V') and 'meer' in oppevaldkond:  # Marine
                        return 'EESTI MEREAKADEEMIA', 'Guessed'
                    else:
                        return 'Teaduskond määramata', 'Unmapped'
            
            # Apply guessing function
            guessing_results = df_final.apply(guess_teaduskond, axis=1, result_type='expand')
            df_final['teaduskond'] = guessing_results[0]
            df_final['teaduskond_allikas'] = guessing_results[1]
            
            # Report guessing results
            final_unmapped = sum(df_final['teaduskond'] == 'Teaduskond määramata')
            guessed_count = sum(df_final['teaduskond_allikas'] == 'Guessed')
            print(f"Guessed {guessed_count} additional programmes")
            print(f"Still unmapped: {final_unmapped}")
            
            # Show breakdown by source
            source_counts = df_final['teaduskond_allikas'].value_counts()
            print("\nMapping source breakdown:")
            for source, count in source_counts.items():
                print(f"  {source}: {count}")
    
    # Step 8: Save to CSV
    df_final.to_csv(output_file, index=False, encoding='utf-8')
    
    # Save parquet version to output folder
    if PARQUET_AVAILABLE:
        output_dir = Path('output')
        output_dir.mkdir(exist_ok=True)
        parquet_file = output_dir / f"{Path(output_file).stem}.parquet"
        df_final.to_parquet(parquet_file, index=False)
        print(f"Generated {output_file}")
        print(f"Generated {parquet_file}")
    else:
        print(f"Generated {output_file}")
        print("Note: Install pyarrow for parquet format support")
    print(f"Processed {len(df_final)} records")
    return df_final

def main():
    """CLI interface for the ETL script using command-line arguments."""
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(description='TalTech Study Programmes ETL Tool')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--full', action='store_true', 
                      help='Run full ETL (scraping + CSV processing + mapping)')
    group.add_argument('--scrapeonly', action='store_true',
                      help='Scraping only (save programmes to file)')
    group.add_argument('--csvetlonly', action='store_true',
                      help='CSV processing only (without scraping)')
    
    args = parser.parse_args()
    
    try:
        if args.full:
            print("=== Running Full ETL ===")
            result = process_taltechkoikkavad()
            if result is not None:
                print("Full ETL completed successfully")
            else:
                print("ETL failed")
                
        elif args.scrapeonly:
            print("=== Scraping Only ===")
            programme_map = scrape_study_programmes()
            
            # Save to JSON file for later use
            import json
            output_file = "scraped_programmes.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(programme_map, f, ensure_ascii=False, indent=2)
            print(f"Scraped {len(programme_map)} programmes saved to {output_file}")
            
        elif args.csvetlonly:
            print("=== CSV Processing Only ===")
            print("Loading previously scraped programmes...")
            
            # Try to load scraped programmes
            import json
            try:
                with open("scraped_programmes.json", 'r', encoding='utf-8') as f:
                    programme_map = json.load(f)
                print(f"Loaded {len(programme_map)} scraped programmes")
            except FileNotFoundError:
                print("No scraped programmes found. Running scraping first...")
                # Set quiet mode for scraping
                scrape_study_programmes._quiet_mode = True
                programme_map = scrape_study_programmes()
                # Save for future use
                with open("scraped_programmes.json", 'w', encoding='utf-8') as f:
                    json.dump(programme_map, f, ensure_ascii=False, indent=2)
            
            # Run CSV processing with loaded data
            result = process_csv_with_mapping(programme_map)
            if result is not None:
                print("CSV processing completed successfully")
            else:
                print("CSV processing failed")
                
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

def process_csv_with_mapping(programme_school_map):
    """Process CSV with pre-loaded programme mapping."""
    # Input and output paths
    input_folder = r"C:\Users\siyi.ma\OneDrive - Tallinna Tehnikaülikool\OIS\csv\Otsing_oppekavad"
    output_folder = r"C:\Users\siyi.ma\OneDrive - Tallinna Tehnikaülikool\OIS\pysiandmed"
    output_file = Path(output_folder) / "taltechkoikkavad.csv"
    
    # Ensure output folder exists
    Path(output_folder).mkdir(parents=True, exist_ok=True)
    
    # Step 1: Find newest CSV file
    newest_csv = find_newest_csv(input_folder)
    print(f"Processing file: {newest_csv}")
    
    # Step 2: Read CSV with specific encoding and delimiter
    # Try multiple encodings for Baltic characters
    encodings = ['utf-8-sig', 'windows-1257', 'iso-8859-4', 'utf-8', 'cp1252']
    df = None
    
    for encoding in encodings:
        try:
            df = pd.read_csv(newest_csv, 
                           delimiter=';', 
                           encoding=encoding,
                           header=1,  # Skip first row, use second row as header
                           skipinitialspace=True)
            print(f"Successfully read with encoding: {encoding}")
            break
        except (UnicodeDecodeError, pd.errors.EmptyDataError):
            continue
    
    if df is None:
        raise ValueError("Could not read CSV with any supported encoding")
    
    # Handle BOM and clean column names
    df.columns = df.columns.str.strip().str.replace('\ufeff', '')
    
    # Drop any columns with blank/NaN/BOM-only names
    df = df.loc[:, ~df.columns.isin(['', ' ', '\ufeff']) & df.columns.notna()]
    
    # Map expected columns to actual columns (handle variations)
    column_mapping = {}
    for col in df.columns:
        col_lower = col.lower().strip()
        if 'õppekava kood' in col_lower and 'taltech' in col_lower:
            column_mapping['TalTechi õppekava kood'] = col
        elif 'maht' in col_lower and 'eap' in col_lower:
            column_mapping['maht (EAP)'] = col
        elif 'õppekavaversiooni kood' in col_lower:
            column_mapping['õppekavaversiooni kood'] = col
        elif 'nimetus e.k' in col_lower:
            column_mapping['nimetus e.k.'] = col
        elif 'nimetus i.k' in col_lower:
            column_mapping['nimetus i.k.'] = col
        elif 'õppetase' in col_lower:
            column_mapping['õppetase'] = col
        elif 'nominaalne õppeaeg' in col_lower:
            column_mapping['nominaalne õppeaeg (semestrites)'] = col
        elif 'programmijuhi nimi' in col_lower or 'õppekava juhi' in col_lower:
            column_mapping['õppekava juhi/programmijuhi nimi'] = col
        elif 'peakeel' in col_lower:
            column_mapping['peakeel'] = col
        elif 'õppevaldkond' in col_lower:
            column_mapping['õppevaldkond'] = col
    
    # Check if required columns are found
    required_columns = ['TalTechi õppekava kood', 'maht (EAP)', 'õppekavaversiooni kood']
    missing_columns = [col for col in required_columns if col not in column_mapping]
    
    if missing_columns:
        print(f"Missing required columns: {missing_columns}")
        print("Available columns for manual mapping:")
        for col in df.columns:
            print(f"  '{col}'")
        return None
    
    # Step 3: Clean data - remove rows where "maht (EAP)" is empty
    maht_col = column_mapping['maht (EAP)']
    df_clean = df[df[maht_col].notna() & (df[maht_col] != '')]
    
    # Step 4: Group by full TalTechi õppekava kood, sort by version descending, take first
    # This ensures we get the latest version of each programme
    kava_col = column_mapping['TalTechi õppekava kood']
    version_col = column_mapping['õppekavaversiooni kood']
    df_sorted = df_clean.sort_values(version_col, ascending=False)
    df_grouped = df_sorted.groupby(kava_col).first().reset_index()
    
    # Step 5: Select and rename columns using mapped column names
    output_columns = {
        'kavakood': column_mapping.get('TalTechi õppekava kood'),
        'nimetusek': column_mapping.get('nimetus e.k.'),
        'nimetusik': column_mapping.get('nimetus i.k.'),
        'tase': column_mapping.get('õppetase'),
        'maht': column_mapping.get('maht (EAP)'),
        'nominaalne_oppeaeg': column_mapping.get('nominaalne õppeaeg (semestrites)'),
        'programmijuht': column_mapping.get('õppekava juhi/programmijuhi nimi'),
        'peakeel': column_mapping.get('peakeel'),
        'oppevaldkond': column_mapping.get('õppevaldkond')
    }
    
    # Filter out columns that weren't found
    available_columns = {k: v for k, v in output_columns.items() if v is not None}
    
    # Select available columns and rename
    df_final = df_grouped[list(available_columns.values())].copy()
    df_final.columns = list(available_columns.keys())
    
    # Step 7: Transform data types and uppercase "tase"
    if 'kavakood' in df_final.columns:
        df_final['kavakood'] = df_final['kavakood'].astype(str)
    if 'nimetusek' in df_final.columns:
        df_final['nimetusek'] = df_final['nimetusek'].astype(str)
    if 'nimetusik' in df_final.columns:
        df_final['nimetusik'] = df_final['nimetusik'].astype(str)
    if 'tase' in df_final.columns:
        df_final['tase'] = df_final['tase'].astype(str).str.upper()
    if 'maht' in df_final.columns:
        # Handle European decimal format (comma) and convert to numeric
        df_final['maht'] = df_final['maht'].astype(str).str.replace(',', '.', regex=False)
        df_final['maht'] = pd.to_numeric(df_final['maht'], errors='coerce')
        df_final['maht'] = df_final['maht'].fillna(0).astype(int)
    if 'nominaalne_oppeaeg' in df_final.columns:
        df_final['nominaalne_oppeaeg'] = pd.to_numeric(df_final['nominaalne_oppeaeg'], errors='coerce')
        df_final['nominaalne_oppeaeg'] = df_final['nominaalne_oppeaeg'].fillna(0).astype(int)
    if 'programmijuht' in df_final.columns:
        df_final['programmijuht'] = df_final['programmijuht'].astype(str)
    if 'peakeel' in df_final.columns:
        df_final['peakeel'] = df_final['peakeel'].astype(str)
    if 'oppevaldkond' in df_final.columns:
        df_final['oppevaldkond'] = df_final['oppevaldkond'].astype(str)
    
    # Step 7.5: Add teaduskond mapping using provided mapping
    if 'kavakood' in df_final.columns:
        # Create a lookup dictionary from full_code to school
        code_to_school = {}
        for full_code, info in programme_school_map.items():
            school = info['school']
            code_to_school[full_code] = school
        
        # First pass: direct mapping from scraped data
        df_final['teaduskond'] = df_final['kavakood'].map(
            lambda x: code_to_school.get(x, 'Teaduskond määramata')
        )
        
        # Add mapping source column
        df_final['teaduskond_allikas'] = df_final['kavakood'].map(
            lambda x: 'Scraped' if x in code_to_school else 'Unmapped'
        )
        
        mapped_count = sum(df_final['teaduskond'] != 'Teaduskond määramata')
        unmapped_count = sum(df_final['teaduskond'] == 'Teaduskond määramata')
        print(f"Mapped {mapped_count} programmes to schools (from {len(programme_school_map)} scraped programmes)")
        print(f"Unmapped programmes: {unmapped_count}")
        
        # Debug: Show which programmes were mapped
        mapped_programmes = df_final[df_final['teaduskond_allikas'] == 'Scraped']['kavakood'].tolist()
        print(f"Scraped programmes found in CSV: {len(mapped_programmes)}")
        if len(mapped_programmes) < len(programme_school_map):
            scraped_codes = set(programme_school_map.keys())
            csv_codes = set(df_final['kavakood'].tolist())
            missing_in_csv = scraped_codes - csv_codes
            print(f"Scraped codes not found in CSV ({len(missing_in_csv)}): {sorted(missing_in_csv)}")
        
        # Apply educated guessing for unmapped programmes
        if unmapped_count > 0:
            print("Making educated guesses for unmapped programmes based on study fields...")
            
            def guess_teaduskond(row):
                if row['teaduskond'] != 'Teaduskond määramata':
                    return row['teaduskond'], row['teaduskond_allikas']
                
                # Get study field for guessing
                oppevaldkond = str(row.get('oppevaldkond', '')).lower() if 'oppevaldkond' in row else ''
                
                # Educated guessing based on study field patterns
                if any(word in oppevaldkond for word in ['informaatika', 'infotehnoloogia', 'arvutiteadus', 'küberturve', 'it']):
                    return 'INFOTEHNOLOOGIA TEADUSKOND', 'Guessed'
                elif any(word in oppevaldkond for word in ['ehitus', 'arhitektuur', 'insener', 'tehnika', 'tehnoloogia', 'energia', 'elektro', 'masina', 'material']):
                    return 'INSENERITEADUSKOND', 'Guessed'
                elif any(word in oppevaldkond for word in ['loodus', 'füüsika', 'matemaatika', 'keemia', 'bio', 'geo', 'öko']):
                    return 'LOODUSTEADUSKOND', 'Guessed'
                elif any(word in oppevaldkond for word in ['majandus', 'äri', 'juht', 'õigus', 'avalik', 'poliitika', 'sotsiaal']):
                    return 'MAJANDUSTEADUSKOND', 'Guessed'
                elif any(word in oppevaldkond for word in ['mere', 'laev', 'vesi', 'sadama']):
                    return 'EESTI MEREAKADEEMIA', 'Guessed'
                else:
                    # Look at programme code patterns as last resort
                    kavakood = str(row.get('kavakood', ''))
                    if kavakood.startswith(('I', 'V')):  # Common IT/CS prefixes
                        return 'INFOTEHNOLOOGIA TEADUSKOND', 'Guessed'
                    elif kavakood.startswith(('E', 'M', 'R')):  # Common engineering prefixes
                        return 'INSENERITEADUSKOND', 'Guessed'
                    elif kavakood.startswith(('L', 'Y', 'K')):  # Common natural sciences prefixes
                        return 'LOODUSTEADUSKOND', 'Guessed'
                    elif kavakood.startswith(('T', 'H')):  # Common business/social prefixes
                        return 'MAJANDUSTEADUSKOND', 'Guessed'
                    elif kavakood.startswith('V') and 'meer' in oppevaldkond:  # Marine
                        return 'EESTI MEREAKADEEMIA', 'Guessed'
                    else:
                        return 'Teaduskond määramata', 'Unmapped'
            
            # Apply guessing function
            guessed_results = df_final.apply(guess_teaduskond, axis=1, result_type='expand')
            df_final['teaduskond'] = guessed_results[0]
            df_final['teaduskond_allikas'] = guessed_results[1]
            
            # Count final results
            final_mapped = sum(df_final['teaduskond_allikas'] == 'Scraped')
            final_guessed = sum(df_final['teaduskond_allikas'] == 'Guessed')
            final_unmapped = sum(df_final['teaduskond_allikas'] == 'Unmapped')
            
            print(f"Final mapping: {final_mapped} scraped, {final_guessed} guessed, {final_unmapped} unmapped")
    
    # Step 8: Save to CSV with Excel-compatible format
    # Sort by kavakood for consistent output
    if 'kavakood' in df_final.columns:
        df_final = df_final.sort_values('kavakood')
    
    df_final.to_csv(output_file, index=False, encoding='utf-8-sig', sep=';')
    
    # Save parquet version to output folder
    if PARQUET_AVAILABLE:
        output_dir = Path('output')
        output_dir.mkdir(exist_ok=True)
        parquet_file = output_dir / f"{Path(output_file).stem}.parquet"
        df_final.to_parquet(parquet_file, index=False)
        print(f"Output saved to: {output_file}")
        print(f"Parquet saved to: {parquet_file}")
    else:
        print(f"Output saved to: {output_file}")
        print("Note: Install pyarrow for parquet format support")
    print(f"Total programmes: {len(df_final)}")
    
    return df_final

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")