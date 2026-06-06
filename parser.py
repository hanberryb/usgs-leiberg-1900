import csv
import os
import re

# Define output file paths
STAND_CSV = "stand_data.csv"
COMP_CSV = "composition_data.csv"

def initialize_csv_files():
    """Creates the CSV files with headers if they do not exist."""
    if not os.path.exists(STAND_CSV):
        with open(STAND_CSV, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Township", "Category", "Species", "Metric", "Value"])

    if not os.path.exists(COMP_CSV):
        with open(COMP_CSV, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Township", "Species", "Diameter Classification", "Percentage"])

def parse_document_text(raw_text):
    """Scans text block and parses sections sequentially by matching Townships."""
    initialize_csv_files()

    # Find and split sections by Township identifiers (e.g., TOWNSHIP 28 SOUTH, RANGE 6 EAST)
    township_matches = list(re.finditer(r"TOWNSHIP\s+\d+\s+SOUTH,\s+RANGE\s+\d+½?\s+EAST", raw_text, re.IGNORECASE))

    if not township_matches:
        print("No township headers detected. Check text formatting.")
        return

    for i in range(len(township_matches)):
        start_idx = township_matches[i].start()
        end_idx = township_matches[i+1].start() if i + 1 < len(township_matches) else len(raw_text)
        
        township_name = township_matches[i].group().strip().upper()
        block = raw_text[start_idx:end_idx]
        
        print(f"Processing: {township_name}...")
        extract_metrics(township_name, block)

def extract_metrics(township, text_block):
    """Extracts specific tables from a township block using regular expressions."""
    
    # 1. Parse Land Area Metrics
    area_patterns = {
        "Forested area": r"Forested area\s*(?:\.+\s*)*([\d,]+|None)",
        "Badly burned area": r"Badly burned area\s*(?:\.+\s*)*([\d,]+|None)",
        "Logged area": r"Logged area\s*(?:\.+\s*)*([\d,]+|None)",
        "Nonforested area": r"Nonforested area\s*(?:\.+\s*)*([\d,]+|None)"
    }
    
    with open(STAND_CSV, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        for metric_name, pattern in area_patterns.items():
            match = re.search(pattern, text_block, re.IGNORECASE)
            if match:
                val = match.group(1).replace(",", "")
                val = 0 if val.lower() == 'none' else int(val)
                writer.writerow([township, "Area Metrics", "All", metric_name, val])

    # 2. Parse Composition Percentages (4 inches and upward)
    comp_section = re.search(r"Composition of forest.*?\n(.*?)(?=TOWNSHIP|Forested and other|$)", text_block, re.DOTALL | re.IGNORECASE)
    if comp_section:
        lines = comp_section.group(1).strip().split('\n')
        with open(COMP_CSV, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            for line in lines:
                match = re.search(r"([A-Za-z\s]+?)\s*(?:\.+\s*)*(\.?\d+)\s*$", line)
                if match:
                    species = match.group(1).strip()
                    percentage = float(match.group(2))
                    writer.writerow([township, species, "4 inches and upward", percentage])

# Wrapper for processing local files
if __name__ == "__main__":
    # To run this script locally, place a file named text_dump.txt 
    # with your extracted document text in the same folder.
    input_filename = "text_dump.txt"
    if os.path.exists(input_filename):
        with open(input_filename, "r", encoding="utf-8") as file:
            data = file.read()
        parse_document_text(data)
        print("Extraction complete! Output saved to stand_data.csv and composition_data.csv")
    else:
        print(f"Please create a '{input_filename}' file containing your document text to run the script.")
