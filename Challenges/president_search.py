#!/usr/bin/env python3
"""
Script to extract DPRG president information from the archive.
"""
import subprocess
import re
import json
from collections import defaultdict
import csv
import os
import time

# Define search queries to find information about presidents
SEARCH_QUERIES = [
    "election results",
    "DPRG election",
    "officer election results",
    "Results of elections",
    "president elected",
    "executive council",
    "executive officers", 
    "new officers",
    "annual meeting officers",
    "DPRG Elections",
    "voting procedure officers",
]

# Terms that indicate a person might be a president
PRESIDENT_INDICATORS = [
    r"president:?\s+([A-Z][a-zA-Z\.-]+\s+[A-Z][a-zA-Z\.-]+)",
    r"([A-Z][a-zA-Z\.-]+\s+[A-Z][a-zA-Z\.-]+)\s+(?:is|as|was|became|elected)\s+(?:the\s+)?president",
    r"([A-Z][a-zA-Z\.-]+\s+[A-Z][a-zA-Z\.-]+),?\s+president",
    r"new president[,\s]+([A-Z][a-zA-Z\.-]+\s+[A-Z][a-zA-Z\.-]+)",
    r"president[,\s]+([A-Z][a-zA-Z\.-]+\s+[A-Z][a-zA-Z\.-]+)",
    r"president\s*[-:]?\s*([A-Z][a-zA-Z\.-]+\s+[A-Z][a-zA-Z\.-]+)",
    r"for president(?:\s*[-:])?\s*([A-Z][a-zA-Z\.-]+\s+[A-Z][a-zA-Z\.-]+)",
    r"president.*?([A-Z][a-zA-Z\.-]+\s+[A-Z][a-zA-Z\.-]+)",
    # Match email format with name (common in DPRG posts)
    r"President.*?([A-Z][a-zA-Z\.-]+@[a-zA-Z0-9\.-]+\.[a-zA-Z]{2,})\s+\(([A-Z][a-zA-Z\.-]+\s+[A-Z][a-zA-Z\.-]+)\)",
    # Match "Name - President" format
    r"([A-Z][a-zA-Z\.-]+\s+[A-Z][a-zA-Z\.-]+)\s*[-–—]\s*President",
]

# Extract specific patterns for elections results
ELECTION_RESULTS_INDICATORS = [
    r"(?:DPRG|2\d{3}|new|election)\s+(?:officer|election)s?(?:\s+results)?:.*?president:?\s+([A-Z][a-zA-Z\.-]+\s+[A-Z][a-zA-Z\.-]+)",
    r"president\s*[-:=]\s*([A-Z][a-zA-Z\.-]+\s+[A-Z][a-zA-Z\.-]+)",
]

def run_search(query, search_type="hybrid", top_k=150, min_score=0.2):
    """Run a search using the CLI tool and return the results."""
    cmd = ["python", "-m", "src.cli", "search", query, 
           "--type", search_type, "--top-k", str(top_k), "--min-score", str(min_score)]
    
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout

def extract_presidents(text, year=None):
    """Extract president mentions from text."""
    found_presidents = []
    
    # Try election results indicators first (more specific)
    for pattern in ELECTION_RESULTS_INDICATORS:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            president_name = match.group(1)
            # Basic name verification (handle more formats)
            if re.match(r"^[A-Z][a-zA-Z\.-]+\s+[A-Z][a-zA-Z\.-]+$", president_name):
                found_presidents.append((president_name, year))
    
    # Then try the more general president indicators
    for pattern in PRESIDENT_INDICATORS:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            # Some patterns have multiple capture groups for different formats
            if len(match.groups()) > 1 and match.group(2):
                president_name = match.group(2)  # Email format with name
            else:
                president_name = match.group(1)
                
            # Basic name verification (handle more formats)
            if re.match(r"^[A-Z][a-zA-Z\.-]+\s+[A-Z][a-zA-Z\.-]+$", president_name):
                found_presidents.append((president_name, year))
    
    return found_presidents

def extract_year_from_metadata(text):
    """Extract year from metadata in search results."""
    # Try to find Date field in the format YYYY-MM-DD or just YYYY
    year_match = re.search(r"Date:\s+(\d{4})(?:-\d{2}-\d{2})?", text)
    if year_match:
        return int(year_match.group(1))
    
    # Try alternative format with just the year
    year_match = re.search(r"Date:\s+(\d{4})", text)
    if year_match:
        return int(year_match.group(1))
        
    # Try to find year in email subjects or headers
    year_match = re.search(r"(?:Subject|From).*?(?:election|results|officers).*?(?:for|in)\s+(\d{4})", text)
    if year_match:
        return int(year_match.group(1))
    
    return None

def extract_document_info(section):
    """Extract title, author, date, and text from a search result section."""
    title_match = re.search(r"Title:\s+(.+)$", section, re.MULTILINE)
    author_match = re.search(r"Author:\s+(.+)$", section, re.MULTILINE)
    date_match = re.search(r"Date:\s+(.+)$", section, re.MULTILINE)
    excerpt_match = re.search(r"Excerpt:\s+(.+)$", section, re.MULTILINE)
    
    title = title_match.group(1) if title_match else ""
    author = author_match.group(1) if author_match else ""
    date = date_match.group(1) if date_match else ""
    excerpt = excerpt_match.group(1) if excerpt_match else section
    
    return {
        "title": title.strip(),
        "author": author.strip(),
        "date": date.strip(),
        "excerpt": excerpt.strip(),
        "full_text": section
    }

def process_search_results(search_output):
    """Process search results to extract president information."""
    # Split the output into individual results
    result_sections = re.split(r"│\s+\d+\.\d+\s+│", search_output)
    
    presidents_found = []
    documents = []
    
    for section in result_sections:
        if not section.strip() or "Score" in section and "Title" in section:
            continue  # Skip header or empty sections
            
        year = extract_year_from_metadata(section)
        presidents = extract_presidents(section, year)
        
        if presidents:
            presidents_found.extend(presidents)
            doc_info = extract_document_info(section)
            documents.append({
                "presidents": presidents,
                "info": doc_info
            })
    
    return presidents_found, documents

def run_president_search():
    """Run searches for president information and process results."""
    all_presidents = []
    all_documents = []
    
    for query in SEARCH_QUERIES:
        search_output = run_search(query)
        presidents, documents = process_search_results(search_output)
        all_presidents.extend(presidents)
        all_documents.extend(documents)
        print(f"Found {len(presidents)} president mentions in query: {query}")
        # Avoid rate limiting
        time.sleep(1)
    
    # Deduplicate and organize by year
    presidents_by_year = defaultdict(set)
    for president, year in all_presidents:
        if year:
            presidents_by_year[year].add(president)
        else:
            # If year is unknown, add to "Unknown" category
            presidents_by_year["Unknown"].add(president)
    
    # Count mentions for confidence
    president_mentions = defaultdict(int)
    for president, _ in all_presidents:
        president_mentions[president] += 1
    
    # Create directory for output if it doesn't exist
    os.makedirs("output", exist_ok=True)
    
    # Output the results
    output_file = os.path.join("output", "dprg_presidents.csv")
    with open(output_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Year", "President", "Mentions"])
        
        # Sort years with Unknown at the end
        years = sorted([y for y in presidents_by_year.keys() if y != "Unknown"])
        if "Unknown" in presidents_by_year:
            years.append("Unknown")
            
        for year in years:
            for president in sorted(presidents_by_year[year]):
                writer.writerow([year, president, president_mentions[president]])
    
    # Also save detailed information
    details_file = os.path.join("output", "dprg_president_details.csv")
    with open(details_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["President", "Year", "Title", "Date", "Author", "Excerpt"])
        
        for doc in all_documents:
            for president, year in doc["presidents"]:
                writer.writerow([
                    president,
                    year if year else "Unknown",
                    doc["info"]["title"],
                    doc["info"]["date"],
                    doc["info"]["author"],
                    doc["info"]["excerpt"][:100] + "..." if len(doc["info"]["excerpt"]) > 100 else doc["info"]["excerpt"]
                ])
    
    print(f"\nResults saved to {output_file}")
    print(f"Detailed information saved to {details_file}")
    print("\nSummary of Presidents by Year:")
    
    for year in years:
        presidents_list = sorted(presidents_by_year[year])
        president_info = [f"{p} ({president_mentions[p]} mentions)" for p in presidents_list]
        year_str = year if year != "Unknown" else "Unknown Year"
        print(f"{year_str}: {', '.join(president_info)}")

if __name__ == "__main__":
    run_president_search() 