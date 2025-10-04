import re
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def debug_scrape():
    """Debug version to see what's actually on the page."""
    
    driver_path = r"C:\edgedriver_win64\msedgedriver.exe"
    service = Service(driver_path)
    
    options = webdriver.EdgeOptions()
    options.add_argument('--headless')
    
    try:
        driver = webdriver.Edge(service=service, options=options)
        driver.get("https://tunniplaan.taltech.ee/#/public")
        
        # Wait for page to load
        time.sleep(5)
        
        # Click on "Teaduskonnad" tab
        try:
            teaduskonnad_tab = driver.find_element(By.XPATH, "//a[contains(text(), 'Teaduskonnad')]")
            teaduskonnad_tab.click()
            time.sleep(3)
        except:
            print("Could not find Teaduskonnad tab")
        
        # Get all text content
        body_text = driver.find_element(By.TAG_NAME, "body").text
        
        # Save full text to file
        with open("full_page_text.txt", "w", encoding="utf-8") as f:
            f.write(body_text)
        
        print("Full page text saved to full_page_text.txt")
        
        # Look for lines with programme patterns
        lines = body_text.split('\n')
        programme_pattern = r'(.+?)\s*\(([A-Z]{4}\d{2})\)'
        
        print("\nLines containing programme patterns:")
        for i, line in enumerate(lines):
            line = line.strip()
            if re.search(programme_pattern, line):
                print(f"Line {i}: '{line}'")
        
        # Look for school names
        valid_schools = [
            "EESTI MEREAKADEEMIA",
            "INFOTEHNOLOOGIA TEADUSKOND", 
            "INSENERITEADUSKOND",
            "LOODUSTEADUSKOND",
            "MAJANDUSTEADUSKOND"
        ]
        
        print("\nLines containing school names:")
        for i, line in enumerate(lines):
            line = line.strip()
            if line in valid_schools:
                print(f"Line {i}: '{line}'")
        
        # Sample some lines around school names
        print("\nContext around school names:")
        for i, line in enumerate(lines):
            line = line.strip()
            if line in valid_schools:
                start = max(0, i-3)
                end = min(len(lines), i+10)
                print(f"\n--- Context around '{line}' (lines {start}-{end}) ---")
                for j in range(start, end):
                    marker = ">>> " if j == i else "    "
                    print(f"{marker}{j}: '{lines[j].strip()}'")
                    
    except Exception as e:
        print(f"Error: {e}")
    finally:
        try:
            driver.quit()
        except:
            pass

if __name__ == "__main__":
    debug_scrape()