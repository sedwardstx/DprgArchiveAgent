#!/usr/bin/env python3
"""
Script to extract DPRG president information from the archive.
"""
import subprocess
import re
import json
from collections import defaultdict
from datetime import datetime
import csv
import os

# Define search queries to find information about presidents
SEARCH_QUERIES = [
    "president elected",
    "new president",
    "officer election results",
    "executive council president",
    "elections president",
    "annual meeting president",
    "officer election announcement",
    "nomination president",
]

# Terms that indicate a person might be a president
PRESIDENT_INDICATORS = [
    r"president:?\s+([A-Z][a-z]+\s+[A-Z][a-z]+)",
    r"([A-Z][a-z]+\s+[A-Z][a-z]+)\s+(?:is|as|was|became|elected)\s+(?:the\s+)?president",
    r"([A-Z][a-z]+\s+[A-Z][a-z]+),?\s+president",
    r"new president[,\s]+([A-Z][a-z]+\s+[A-Z][a-z]+)",
    r"president[,\s]+([A-Z][a-z]+\s+[A-Z][a-z]+)",
]

results = defaultdict(list)

def run_search(query, search_type="hybrid", top_k=100, min_score=0.2):
    """Run a search using the CLI tool and return the results."""
    cmd = ["python", "-m", "src.cli", "search", query, 
           "--type", search_type, "--top-k", str(top_k), "--min-score", str(min_score)]
    
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout

def extract_presidents(text, year=None):
    """Extract president mentions from text."""
    found_presidents = []
    
    for pattern in PRESIDENT_INDICATORS:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            president_name = match.group(1)
            # Verify it looks like a name (avoid false positives)
            if re.match(r"^[A-Z][a-z]+\s+[A-Z][a-z]+$", president_name):
                found_presidents.append((president_name, year))
    
    return found_presidents

def extract_year_from_metadata(text):
    """Extract year from metadata in search results."""
    year_match = re.search(r"Date:\s+(\d{4})", text)
    if year_match:
        return int(year_match.group(1))
    return None

def process_search_results(search_output):
    """Process search results to extract president information."""
    # Split the output into individual results
    result_sections = re.split(r"\n\s*\n", search_output)
    
    presidents_found = []
    for section in result_sections:
        year = extract_year_from_metadata(section)
        presidents = extract_presidents(section, year)
        if presidents:
            presidents_found.extend(presidents)
    
    return presidents_found

def run_president_search():
    """Run searches for president information and process results."""
    all_presidents = []
    
    for query in SEARCH_QUERIES:
        search_output = run_search(query)
        presidents = process_search_results(search_output)
        all_presidents.extend(presidents)
        print(f"Found {len(presidents)} president mentions in query: {query}")
    
    # Deduplicate and organize by year
    presidents_by_year = defaultdict(set)
    for president, year in all_presidents:
        if year:
            presidents_by_year[year].add(president)
    
    # Create directory for output if it doesn't exist
    os.makedirs("output", exist_ok=True)
    
    # Output the results
    output_file = os.path.join("output", "dprg_presidents.csv")
    with open(output_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Year", "President"])
        
        for year in sorted(presidents_by_year.keys()):
            for president in presidents_by_year[year]:
                writer.writerow([year, president])
    
    print(f"\nResults saved to {output_file}")
    print("\nSummary of Presidents by Year:")
    for year in sorted(presidents_by_year.keys()):
        print(f"{year}: {', '.join(presidents_by_year[year])}")

if __name__ == "__main__":
    run_president_search() 