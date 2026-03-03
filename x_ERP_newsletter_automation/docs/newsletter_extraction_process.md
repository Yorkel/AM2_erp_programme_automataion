# NEWSLETTER EXTRACTION PROCESS  
**ERP Weekly Education Newsletter**  
---

## 1. PROJECT OVERVIEW  
The goal of this process was to extract structured data from 87 archived ERP Weekly Education Newsletters, each stored as Word-generated HTML files.

Each newsletter issue contains around 12 news items, following this consistent structure:
- **Theme** – table with dark blue background  
- **Subtheme** – table with grey or light blue background  
- **Title** – usually bold text  
- **Description** – follows the title  
- **Link** – contained within the description  

The aim was to create a structured dataset where each row corresponds to one news item, with the following columns:

`ID`, `newsletter_number`, `issue_date`, `theme`, `subtheme`, `title`, `description`, `link`.


---

## 2. PROCESS SUMMARY  

### Step 1: Organize Files  
- Gathered all 87 newsletter HTML files into one folder:  
  `/data_raw/newsletters_15.10.2025/`
- Renamed them consistently using a short Python script:  
  `newsletter_01.html`, `newsletter_02.html`, … `newsletter_87.html`
- The renaming script used the “Newsletter ##” pattern found at the end of each filename to extract the correct issue number.

### Step 2: Parse HTML Structure  
- Used **BeautifulSoup** to parse the Word-generated HTML files.  
- Identified key visual and formatting cues:  
  - Tables with **dark blue backgrounds** represent **Themes**  
  - Tables with **grey or light blue backgrounds** represent **Subthemes**  
  - Paragraphs with **bold or strong formatting** are **Titles**  
  - Following paragraphs contain **Descriptions** and **Links**

### Step 3: Implement Extraction Logic  
- Built a Python script (`extract_newsletters.py`) that:  
  1. Iterates through all newsletters  
  2. Extracts **themes, subthemes, titles, descriptions, and links**  
  3. Writes all items into a structured CSV file:  
     `/data_processed/newsletter_items.csv`


---

## 3. KEY ISSUES AND FIXES  

### Issue 1: Inconsistent File Names  
**Problem:** Original filenames had inconsistent prefixes (e.g., “ERP Weekly Newsletter”, “Education Policy Newsletter”).  
**Fix:** Used a regular expression to detect “Newsletter ##” at the end of filenames and rename them consistently (`newsletter_01.html`, `newsletter_02.html`, etc.).  

---

### Issue 2: Missing Data for Later Newsletters (#24–#87)  
**Problem:** The script reported “No rows parsed” for newsletters 24 onward.  
**Cause:** Later newsletters used slightly different colour shades for theme/subtheme tables (e.g. `#042854`, `#A5DAE9`, `#D9E2F3`, `#DAE3F3`).  
**Fix:** Added the new colours to the theme and subtheme colour lists:  
- **DARK_BLUE_BG:** `#002060`, `#1F3864`, `#203864`, `#00205B`, `#042854`  
- **GREY_BG:** `#DEEAF6`, `#E7E6E6`, `#D9D9D9`, `#A5DAE9`, `#D9E2F3`, `#DAE3F3`

---

### Issue 3: Newsletter #86 Returned No Items  
**Problem:** Issue #86 contained no bold or strong text — all item titles were plain paragraphs.  
**Fix:** Added a fallback parser (`fallback_parse_by_link`) that:
- Detects items by the **presence of links** instead of bold formatting  
- Groups paragraphs under the same **theme or subtheme**  
- Uses the **first paragraph as the title** and the following as descriptions  
- Creates an item when a **link** is encountered  
This fallback activates automatically when the main parser finds zero rows.

---

### Issue 4: Mixed Colour Formats (RGB vs HEX)  
**Problem:** Some newsletters used CSS colour values in `rgb()` format instead of hexadecimal.  
**Fix:** Added a conversion step to translate `rgb()` values to `#RRGGBB` format before matching.

---

## 4. FINAL RESULTS  
- Successfully parsed **1,523 news items** from **87 newsletters**  
- Only `newsletter_86.html` required the fallback parser  
- Output saved as:  
  `/data_processed/newsletter_items.csv`


---

## 5. RECOMMENDATIONS FOR FUTURE AUTOMATION  

### 1. Standardize Newsletter Formatting  
- Keep consistent theme/subtheme colours  
- Always use bold text for titles  
- Maintain a uniform date and issue number format  
- Consider defining a simple HTML or Markdown template  

### 2. Include Metadata in Each Newsletter  
- Add structured headers (e.g., JSON or YAML front matter) with issue number and date  
- This will make parsing and indexing easier  

### 3. Automate Ingestion  
- Create a scheduled script (e.g., using **cron** or **GitHub Actions**) that:  
  - Detects new HTML files  
  - Runs the extraction automatically  
  - Appends new rows to the master CSV or a database  

### 4. Add Automated Validation  
- Detect missing themes, duplicate titles, or empty links  
- Report inconsistencies for manual review  

### 5. Extend Functionality  
- Convert extracted data into a **searchable database** (e.g., SQLite or PostgreSQL)  
- Use **NLP** to classify topics, detect entities, and analyze trends  
- Build an **interactive dashboard** (e.g., with Streamlit) to visualize newsletter content over time  


---

## 6. SUMMARY  

| Stage                       | Description                                    | Outcome      |
|------------------------------|------------------------------------------------|---------------|
| File Organization            | Renamed and structured 87 newsletters          | ✅ Success |
| HTML Parsing                 | Built BeautifulSoup parser                     | ✅ Success |
| Colour Variations            | Added extra HEX/RGB colours                    | ✅ Success |
| Non-Bold Titles (Issue #86)  | Added fallback parser by link detection        | ✅ Success |
| Output Validation            | Generated 1,523 rows in CSV                    | ✅ Success |
| Future-Proofing              | Standardization and automation recommended     | 🔜 Next Step |

---

**Author:** Yorkel  
**Date:** 17 October 2025  
**Project:** ERP Newsletter Extraction and Automation  
---
