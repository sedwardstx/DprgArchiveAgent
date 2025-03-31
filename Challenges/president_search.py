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

# Debug flag - set to True to see detailed output
DEBUG = True

# Target years for our search (as requested by user)
TARGET_YEARS = list(range(1997, 2016))  # 1997-2015

def run_search(query, search_type="hybrid", top_k=150, min_score=0.1):
    """Run a search using the CLI tool and return the results."""
    cmd = ["python", "-m", "src.cli", "search", query, 
           "--type", search_type, "--top-k", str(top_k), "--min-score", str(min_score)]
    
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout

def extract_table_rows(text):
    """Extract table rows from the CLI output."""
    # First, check if we have any results
    if "No results found" in text:
        return []
    
    # Find the part of the output containing the result table
    table_section = re.search(r"Score.*?Title.*?Author.*?Date.*?Excerpt.*?Found \d+ results", text, re.DOTALL)
    if not table_section:
        if DEBUG:
            print("Could not find table section in search results")
        return []
    
    table_text = table_section.group(0)
    
    # Extract rows using line patterns
    # Look for lines with the row format pattern in the CLI output
    rows = []
    
    # Use regex to extract each row by looking for patterns of data between separators
    row_pattern = r'│\s*([\d\.]+)\s*│\s*(.*?)\s*│\s*(.*?)\s*│\s*(.*?)\s*│\s*(.*?)\s*│'
    matches = re.finditer(row_pattern, table_text, re.DOTALL)
    
    for match in matches:
        # Skip header rows
        if "Score" in match.group(1) and "Title" in match.group(2):
            continue
            
        try:
            score = match.group(1).strip()
            title = match.group(2).strip()
            author = match.group(3).strip()
            date = match.group(4).strip()
            excerpt = match.group(5).strip()
            
            # Only include rows with meaningful content
            if score and title and not title.startswith("---"):
                row = {
                    "score": float(score),
                    "title": title,
                    "author": author,
                    "date": date,
                    "excerpt": excerpt
                }
                rows.append(row)
                if DEBUG:
                    print(f"Extracted row: {title} by {author} ({date})")
        except Exception as e:
            if DEBUG:
                print(f"Error parsing row: {str(e)}")
    
    return rows

def extract_year_from_date(date_str):
    """Extract year from a date string."""
    if not date_str:
        return None
        
    # Try to extract YYYY from YYYY-MM-DD format
    year_match = re.search(r'(\d{4})(?:-\d{2}-\d{2})?', date_str)
    if year_match:
        return int(year_match.group(1))
    return None

def extract_presidents_from_text(text):
    """Extract president mentions from text."""
    # Patterns for president mentions
    president_patterns = [
        # Direct president title followed by name
        r'[Pp]resident\s*(?:[-:])?\s*([A-Z][a-zA-Z\.-]+(?:\s+[A-Z][a-zA-Z\.-]+)+)',
        # Name followed by president title
        r'([A-Z][a-zA-Z\.-]+(?:\s+[A-Z][a-zA-Z\.-]+)+)(?:\s*[-,]\s*)[Pp]resident',
        # "X is/as/was president" format
        r'([A-Z][a-zA-Z\.-]+(?:\s+[A-Z][a-zA-Z\.-]+)+)\s+(?:is|as|was|became|elected)\s+(?:the\s+)?[Pp]resident',
        # "elected X as president" format
        r'elected\s+([A-Z][a-zA-Z\.-]+(?:\s+[A-Z][a-zA-Z\.-]+)+)\s+as\s+[Pp]resident',
        # "new president X" format
        r'new\s+[Pp]resident\s+([A-Z][a-zA-Z\.-]+(?:\s+[A-Z][a-zA-Z\.-]+)+)',
        # Election results format
        r'(?:[Ee]lection|[Oo]fficer)s?\s+(?:[Rr]esults?|[Aa]nnouncement)s?:.*?[Pp]resident:?\s+([A-Z][a-zA-Z\.-]+(?:\s+[A-Z][a-zA-Z\.-]+)+)',
    ]
    
    names = []
    for pattern in president_patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE | re.DOTALL)
        for match in matches:
            name = match.group(1).strip()
            # Validate it's a real name (First Last)
            if re.match(r'^[A-Z][a-zA-Z\.-]+(?:\s+[A-Z][a-zA-Z\.-]+)+$', name):
                if DEBUG:
                    print(f"Found president name: {name} in text")
                names.append(name)
    
    return list(set(names))  # Remove duplicates

def search_for_presidents_by_year(year):
    """Search for presidents for a specific year."""
    print(f"\nSearching for presidents in {year}...")
    
    # Create year-specific queries
    year_queries = [
        f"{year} DPRG election results",
        f"{year} DPRG officers",
        f"{year} DPRG president",
        f"{year} election DPRG",
        f"DPRG election {year}"
    ]
    
    search_results = []
    president_mentions = []
    
    for query in year_queries:
        search_output = run_search(query, min_score=0.1)
        rows = extract_table_rows(search_output)
        
        for row in rows:
            # Extract year from the date field
            row_year = extract_year_from_date(row["date"])
            
            # Only include results from the target year or if year can't be determined
            if row_year == year or (row_year is None and year in row["title"] + row["excerpt"]):
                search_results.append(row)
                
                # Look for president mentions
                presidents = extract_presidents_from_text(row["title"] + " " + row["excerpt"])
                for president in presidents:
                    president_mentions.append({
                        "president": president,
                        "year": year,
                        "reference": row
                    })
    
    # Sort results by score
    search_results.sort(key=lambda x: x["score"], reverse=True)
    
    return {
        "top_references": search_results[:5],  # Top 5 references
        "president_mentions": president_mentions
    }

def collect_all_mentions():
    """Collect all president mentions across years."""
    all_mentions = []
    top_references_by_year = {}
    
    for year in TARGET_YEARS:
        results = search_for_presidents_by_year(year)
        all_mentions.extend(results["president_mentions"])
        top_references_by_year[year] = results["top_references"]
        time.sleep(1)  # Avoid rate limiting
    
    # Also search for general officer mentions without year
    general_queries = [
        "DPRG president history",
        "DPRG officers elected",
        "DPRG executive council",
        "DPRG annual meeting officers",
        "DPRG election announcement",
        "new DPRG president"
    ]
    
    for query in general_queries:
        search_output = run_search(query, min_score=0.1)
        rows = extract_table_rows(search_output)
        
        for row in rows:
            # Extract year from the date field
            row_year = extract_year_from_date(row["date"])
            
            # Look for president mentions
            presidents = extract_presidents_from_text(row["title"] + " " + row["excerpt"])
            for president in presidents:
                all_mentions.append({
                    "president": president,
                    "year": row_year,  # Could be None
                    "reference": row
                })
        
        time.sleep(1)  # Avoid rate limiting
    
    return all_mentions, top_references_by_year

def save_results(all_mentions, top_references_by_year):
    """Save results to CSV files."""
    # Create output directory if it doesn't exist
    os.makedirs("output", exist_ok=True)
    
    # 1. Save all president mentions with references
    with open("output/dprg_presidents.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["President", "Year", "Title", "Author", "Date", "Score", "Excerpt"])
        
        for mention in all_mentions:
            writer.writerow([
                mention["president"],
                mention["year"] if mention["year"] else "Unknown",
                mention["reference"]["title"],
                mention["reference"]["author"],
                mention["reference"]["date"],
                mention["reference"]["score"],
                mention["reference"]["excerpt"]
            ])
    
    # 2. Save top 5 references by year
    with open("output/top_references_by_year.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Year", "Rank", "Title", "Author", "Date", "Score", "Excerpt"])
        
        for year in TARGET_YEARS:
            references = top_references_by_year.get(year, [])
            for i, ref in enumerate(references):
                writer.writerow([
                    year,
                    i+1,
                    ref["title"],
                    ref["author"],
                    ref["date"],
                    ref["score"],
                    ref["excerpt"]
                ])
    
    # 3. Create a summary of presidents by year
    presidents_by_year = defaultdict(set)
    for mention in all_mentions:
        year = mention["year"] if mention["year"] else "Unknown"
        presidents_by_year[year].add(mention["president"])
    
    with open("output/presidents_summary.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Year", "Presidents"])
        
        # Sort years to have Unknown at the end
        years = sorted([y for y in presidents_by_year.keys() if y != "Unknown"])
        if "Unknown" in presidents_by_year:
            years.append("Unknown")
            
        for year in years:
            writer.writerow([year, ", ".join(sorted(presidents_by_year[year]))])
    
    # Print summary to console
    print("\nSummary of Presidents by Year:")
    for year in years:
        print(f"{year}: {', '.join(sorted(presidents_by_year[year]))}")
    
    print("\nTop 5 References by Year:")
    for year in TARGET_YEARS:
        references = top_references_by_year.get(year, [])
        if references:
            print(f"\n{year}:")
            for i, ref in enumerate(references):
                print(f"  {i+1}. {ref['title']} by {ref['author']} ({ref['date']})")
        else:
            print(f"\n{year}: No references found")

def main():
    """Main function."""
    print("Starting DPRG President Search...")
    all_mentions, top_references_by_year = collect_all_mentions()
    save_results(all_mentions, top_references_by_year)
    print("\nResults saved to output directory.")

if __name__ == "__main__":
    main() 