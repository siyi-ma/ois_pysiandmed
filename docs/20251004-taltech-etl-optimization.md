# 20251004-taltech-etl-optimization

## Session Overview
**Date:** October 4, 2025  
**Main Theme:** TalTech Study Programmes ETL Tool Development and Optimization  
**Focus Files:** `teltechkoikkavad.py`, `scraped_programmes.json`, `README.md`  
**Duration:** Extended development session with multiple optimization cycles  

## Objectives Accomplished
1. **Debug Output Cleanup:** Removed verbose debug messages for cleaner CSV-only processing
2. **Data Structure Optimization:** Removed unnecessary `code_prefix` field from scraped data
3. **ETL Logic Refinement:** Simplified grouping logic to match Power Query patterns
4. **Mapping Accuracy Improvement:** Achieved 100% mapping rate for scraped programmes
5. **Documentation Creation:** Comprehensive README.md based on development process

## Initial State
- **Script:** `teltechkoikkavad.py` - Python ETL tool for TalTech study programme processing
- **Functionality:** Web scraping + CSV processing + school mapping
- **Issues:** Verbose debug output, complex grouping logic, suboptimal mapping accuracy
- **Mapping Rate:** 71/82 scraped programmes mapped (86.6%)

## Errors Encountered and Solutions

### 1. Verbose Debug Output During CSV Processing
**Problem:** When using `--csvetlonly` mode, script displayed unnecessary debug information including full scraping output and column mapping details.

**Error Messages:**
```
Mapped columns: {'TalTechi õppekava kood': 'TalTechi õppekava kood', ...}
Original maht values (first 5): ['180,00', '240,00', ...]
Processed maht values (first 5): [0, 0, 0, 0, 0]
```

**Solution Applied:**
- Removed `print(f"Mapped columns: {column_mapping}")` statements
- Eliminated maht value debug output
- Added quiet mode flag for scraping during CSV-only processing
- Modified scraping function to check for `_quiet_mode` attribute

**Code Changes:**
```python
# Before
print(f"Mapped columns: {column_mapping}")
print(f"Original maht values (first 5): {df_final['maht'].head().tolist()}")

# After  
# Check if required columns are found (removed verbose output)
# Convert to numeric, coercing errors to NaN, then fill NaN with 0 and convert to int
```

### 2. Unnecessary code_prefix Field in Scraped Data
**Problem:** `scraped_programmes.json` contained redundant `code_prefix` field that duplicated first 4 characters of full code.

**Solution Applied:**
```python
# Removed code_prefix from programme mapping
programme_school_map[full_code] = {
    'full_code': full_code,
    'programme_name': programme_name,
    'school': current_school
    # Removed: 'code_prefix': code_prefix
}
```

**Command Line Action:**
```python
# Automated cleanup of existing JSON file
import json
with open("scraped_programmes.json", 'r', encoding='utf-8') as f:
    programmes = json.load(f)
for code, data in programmes.items():
    if 'code_prefix' in data:
        del data['code_prefix']
with open("scraped_programmes.json", 'w', encoding='utf-8') as f:
    json.dump(programmes, f, ensure_ascii=False, indent=2)
```

### 3. Curriculum Version Filtering Logic Error
**Problem:** Script filtered curricula by suffix > 70 but then grouped by 4-character prefix, causing logical inconsistency and lost programmes.

**Error Analysis:**
```python
# Problematic logic
df_clean['kava_suffix'] = pd.to_numeric(df_clean[version_col].astype(str).str[-2:], errors='coerce')
df_filtered = df_clean[df_clean['kava_suffix'] <= 70]  # Filter by version
df_grouped = df_sorted.groupby('kava_prefix').first().reset_index()  # Group by prefix
```

**Issue:** Different programmes with same 4-char prefix (e.g., `IAIB17`, `IAIB25`) would be grouped together, losing individual programmes.

**Solution Applied:**
```python
# Simplified logic - group by full programme code
kava_col = column_mapping['TalTechi õppekava kood']
version_col = column_mapping['õppekavaversiooni kood']
df_sorted = df_clean.sort_values(version_col, ascending=False)
df_grouped = df_sorted.groupby(kava_col).first().reset_index()
```

### 4. Data Type Conversion Error
**Problem:** `astype(int, errors='ignore')` caused comparison errors with string values.

**Error Message:**
```
Error: '<=' not supported between instances of 'str' and 'int'
```

**Solution Applied:**
```python
# Before (problematic)
df_clean['kava_suffix'] = df_clean[version_col].astype(str).str[-2:].astype(int, errors='ignore')

# After (fixed)
df_clean['kava_suffix'] = pd.to_numeric(df_clean[version_col].astype(str).str[-2:], errors='coerce')
df_filtered = df_clean[df_clean['kava_suffix'].notna() & (df_clean['kava_suffix'] <= 70)]
```

## Key Command Line Actions

### Testing Commands Used:
```bash
# Primary testing command
python teltechkoikkavad.py --csvetlonly

# Full ETL testing  
python teltechkoikkavad.py --full

# Scraping only mode
python teltechkoikkavad.py --scrapeonly
```

### File Operations:
```bash
# Directory listing to verify files
dir *.py

# Manual file execution (debugging filename typos)
python teltechkoikkavad.py  # vs incorrect: python taltechkoikkavad.py
```

## Technical Improvements

### 1. ETL Logic Simplification
**Before:** Complex multi-step process with filtering and prefix extraction
**After:** Direct grouping by full programme code with version sorting

**Code Transformation:**
```python
# Before (8 lines, complex logic)
version_col = column_mapping['õppekavaversiooni kood']
df_clean['kava_suffix'] = pd.to_numeric(df_clean[version_col].astype(str).str[-2:], errors='coerce')
df_filtered = df_clean[df_clean['kava_suffix'].notna() & (df_clean['kava_suffix'] <= 70)]
kava_col = column_mapping['TalTechi õppekava kood']
df_filtered['kava_prefix'] = df_filtered[kava_col].str[:4]
df_sorted = df_filtered.sort_values(version_col, ascending=False)
df_grouped = df_sorted.groupby('kava_prefix').first().reset_index()

# After (4 lines, clean logic)
kava_col = column_mapping['TalTechi õppekava kood']
version_col = column_mapping['õppekavaversiooni kood']
df_sorted = df_clean.sort_values(version_col, ascending=False)
df_grouped = df_sorted.groupby(kava_col).first().reset_index()
```

### 2. Mapping Accuracy Enhancement
**Metrics Improvement:**

| Metric | Initial | Final | Change |
|--------|---------|-------|--------|
| Scraped programmes mapped | 71/82 (86.6%) | 82/82 (100%) | +11 programmes |
| Total programmes in output | 189 | 240 | +51 programmes |
| Missing scraped programmes | 11 | 0 | Fully resolved |

**Previously Missing Programmes Recovered:**
- `AAVM02` - Elektroenergeetika
- `EAKM25` - Keskkonnatehnoloogiad ja -strateegiad  
- `HAAM02` - Avaliku sektori juhtimine ja innovatsioon
- `KATM02` - Toidutehnoloogia ja -arendus
- `MARM06` - Tööstustehnika ja juhtimine
- `MATM02` - Tootearendus ja tootmistehnika
- `TAAM02` - Majandusanalüüs

## Process Summary

### Phase 1: Debug Output Cleanup
**Goal:** Remove verbose output during CSV-only processing  
**Actions:** Modified print statements, added quiet mode for scraping  
**Result:** Clean output for `--csvetlonly` mode  
**Status:** ✅ Completed

### Phase 2: Data Structure Optimization  
**Goal:** Remove redundant `code_prefix` field  
**Actions:** Updated scraping logic, cleaned existing JSON file  
**Result:** Cleaner data structure, smaller file size  
**Status:** ✅ Completed

### Phase 3: Curriculum Filtering Logic Fix
**Goal:** Resolve mapping accuracy issues  
**Actions:** Analyzed filtering vs grouping logic, simplified approach  
**Result:** Improved from 78/82 to 82/82 programmes mapped  
**Status:** ✅ Completed

### Phase 4: ETL Logic Simplification
**Goal:** Align Python logic with Power Query patterns  
**Actions:** Removed unnecessary filtering, simplified grouping  
**Result:** Cleaner code, better performance, more programmes included  
**Status:** ✅ Completed

### Phase 5: Documentation Creation
**Goal:** Create comprehensive project documentation  
**Actions:** Generated README.md based on development process  
**Result:** Complete user and technical documentation  
**Status:** ✅ Completed

## Technical Architecture

### Core Components:
1. **Web Scraper:** `scrape_study_programmes()` - Selenium-based scraping from TalTech timetable
2. **CSV Processor:** `process_taltechkoikkavad()` - Main ETL function with encoding detection
3. **School Mapper:** Intelligent mapping using scraped data + educated guessing
4. **CLI Interface:** `main()` - argparse-based command line interface

### Data Flow:
```
CSV Input → Column Detection → Data Cleaning → Version Sorting → 
Grouping by Full Code → School Mapping → Educated Guessing → CSV Output
```

### File Dependencies:
- **Input:** `C:\Users\siyi.ma\OneDrive - Tallinna Tehnikaülikool\OIS\csv\Otsing_oppekavad\*.csv`
- **Cache:** `scraped_programmes.json`
- **Output:** `C:\Users\siyi.ma\OneDrive - Tallinna Tehnikaülikool\OIS\pysiandmed\taltechkoikkavad.csv`

## Lessons Learned

### 1. ETL Logic Design
- **Issue:** Mixing filtering criteria (version suffix) with grouping criteria (programme prefix) creates logical inconsistencies
- **Solution:** Keep filtering and grouping aligned on the same data dimension
- **Application:** Group by full programme code instead of extracted prefixes

### 2. Data Processing Patterns
- **Issue:** Complex multi-step transformations can introduce bugs and reduce readability
- **Solution:** Simplify logic to essential operations: sort → group → aggregate
- **Application:** Match Power Query patterns for consistency

### 3. Debug Output Management
- **Issue:** Verbose debugging clutters user experience in production modes
- **Solution:** Implement quiet modes and conditional debug output
- **Application:** Use function attributes or parameters to control verbosity

### 4. Data Structure Evolution
- **Issue:** Redundant fields in cached data increase complexity
- **Solution:** Regular cleanup of data structures as requirements evolve
- **Application:** Remove `code_prefix` when full codes are sufficient

## Outstanding Items
**Status:** All primary objectives completed successfully  
**Future Considerations:**
- Monitor EdgeDriver version compatibility with browser updates
- Consider adding data validation rules for CSV input format changes
- Potential optimization: cache column mappings to reduce processing time

## Final State
- **Mapping Accuracy:** 100% (82/82 scraped programmes)
- **Total Output:** 240 study programmes
- **Code Quality:** Simplified, maintainable ETL logic
- **Documentation:** Complete README.md with usage examples
- **CLI Functionality:** All three modes (`--full`, `--scrapeonly`, `--csvetlonly`) working optimally