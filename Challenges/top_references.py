#!/usr/bin/env python3
"""
Script to identify top DPRG archive references by year.
This script focuses solely on finding high-quality references for each year
without attempting to extract president information.
"""
import subprocess
import re
import csv
import os
import time
from collections import defaultdict

# Run for all years
TEST_MODE = True
TARGET_YEARS = [2006, 2007] if TEST_MODE else list(range(1997, 2016))

def run_search(query, search_type="hybrid", top_k=20, min_score=0.1):
    """Run a search using the CLI tool and return the results."""
    cmd = ["python", "-m", "src.cli", "search", query, 
           "--type", search_type, "--top-k", str(top_k), "--min-score", str(min_score)]
    
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout

def extract_table_rows(output_text):
    """Extract table rows from the CLI output."""
    # First, check if we have any results
    if "No results found" in output_text:
        print("  No results found")
        return []
    
    # Save the output for debugging
    if not os.path.exists("debug"):
        os.makedirs("debug")
    with open(f"debug/last_search_output.txt", "w") as f:
        f.write(output_text)
    
    # Find all lines that look like table rows
    rows = []
    
    # Different possible row patterns
    patterns = [
        r'│\s*([\d\.]+)\s*│\s*(.*?)\s*│\s*(.*?)\s*│\s*(.*?)\s*│\s*(.*?)\s*│',  # Standard table format
        r'\|\s*([\d\.]+)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|',  # Alternative format
    ]
    
    # Try different patterns
    for pattern in patterns:
        matches = re.finditer(pattern, output_text, re.DOTALL)
        
        for match in matches:
            try:
                # Skip header rows
                if "Score" in match.group(1) and "Title" in match.group(2):
                    continue
                
                # Extract data
                score = match.group(1).strip()
                title = match.group(2).strip()
                author = match.group(3).strip()
                date = match.group(4).strip()
                excerpt = match.group(5).strip()
                
                # Skip rows with unusable data
                if not score or not title or any(x in title for x in ["-----", "=====", "Score", "Title"]):
                    continue
                
                # Sometimes the scores might have extra text, so extract just the number
                score_match = re.search(r"([\d\.]+)", score)
                if score_match:
                    score = score_match.group(1)
                
                # Create row object
                row = {
                    "score": float(score),
                    "title": title,
                    "author": author,
                    "date": date,
                    "excerpt": excerpt
                }
                rows.append(row)
                print(f"  Extracted: {title[:50]}... by {author} ({date})")
            except Exception as e:
                print(f"  Error parsing row: {str(e)}")
    
    # If we didn't extract any rows, try a simpler approach - look for lines with 5 pipe-separated sections
    if not rows:
        print("  Trying simpler extraction...")
        # Split output by lines and look for lines with pipes
        lines = output_text.split('\n')
        for line in lines:
            if line.count('|') >= 5 or line.count('│') >= 5:
                parts = re.split(r'[|│]', line)
                if len(parts) >= 6:  # There's an empty part at the beginning and end
                    try:
                        # Skip header rows
                        if "Score" in parts[1] and "Title" in parts[2]:
                            continue
                        
                        score = parts[1].strip()
                        title = parts[2].strip() 
                        author = parts[3].strip()
                        date = parts[4].strip()
                        excerpt = parts[5].strip()
                        
                        # Skip rows with unusable data
                        if not score or not title or any(x in title for x in ["-----", "=====", "Score", "Title"]):
                            continue
                        
                        # Sometimes the scores might have extra text, so extract just the number
                        score_match = re.search(r"([\d\.]+)", score)
                        if score_match:
                            score = score_match.group(1)
                        
                        # Create row object  
                        row = {
                            "score": float(score),
                            "title": title,
                            "author": author,
                            "date": date,
                            "excerpt": excerpt
                        }
                        rows.append(row)
                        print(f"  Extracted: {title[:50]}... by {author} ({date})")
                    except Exception as e:
                        print(f"  Error parsing line: {str(e)}")
    
    print(f"  Found {len(rows)} total results")
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

def get_references_for_year(year):
    """Get top references for a specific year."""
    print(f"\nSearching for references in {year}...")
    
    # Create year-specific queries - we'll focus on general DPRG content for the year
    year_queries = [
        # General year searches
        f"{year} DPRG",
        
        # Specifically looking for annual content
        f"{year} DPRG annual meeting",
        
        # Specifically looking for president/officer content
        f"{year} DPRG officers",
        f"{year} DPRG president",
        f"{year} DPRG election",
        
        # Specifically look for meeting minutes
        f"{year} DPRG minutes",
    ]
    
    all_results = []
    
    for query in year_queries:
        print(f"  Query: {query}")
        search_output = run_search(query, min_score=0.1)
        rows = extract_table_rows(search_output)
        
        for row in rows:
            # Extract year from the date field
            row_year = extract_year_from_date(row["date"])
            
            # Only include results from the target year or if year can't be determined
            # but the title/excerpt contains the year
            if row_year == year or (row_year is None and str(year) in row["title"] + row["excerpt"]):
                all_results.append(row)
                
        # Avoid hammering the server
        time.sleep(0.5)
    
    # Remove duplicates (based on title and author)
    unique_results = {}
    for row in all_results:
        key = f"{row['title']}|{row['author']}"
        if key not in unique_results or row['score'] > unique_results[key]['score']:
            unique_results[key] = row
    
    # Convert back to list and sort by score
    filtered_results = list(unique_results.values())
    filtered_results.sort(key=lambda x: x["score"], reverse=True)
    
    # Take top 5
    return filtered_results[:5]

def search_for_presidents():
    """Run specific searches to find president mentions."""
    print("\nRunning specific president-focused searches...")
    president_queries = [
        "DPRG president history",
        "DPRG election results",
        "DPRG officer announcement",
        "DPRG new president",
        "DPRG annual meeting minutes",
        "DPRG executive committee",
    ]
    
    president_results = []
    
    for query in president_queries:
        print(f"  Query: {query}")
        search_output = run_search(query, min_score=0.1, top_k=50)
        rows = extract_table_rows(search_output)
        president_results.extend(rows)
        
        # Avoid hammering the server
        time.sleep(0.5)
    
    # Remove duplicates (based on title and author)
    unique_results = {}
    for row in president_results:
        key = f"{row['title']}|{row['author']}"
        if key not in unique_results or row['score'] > unique_results[key]['score']:
            unique_results[key] = row
    
    # Convert back to list and sort by score
    filtered_results = list(unique_results.values())
    filtered_results.sort(key=lambda x: x["score"], reverse=True)
    
    # Save president-focused results
    if filtered_results:
        os.makedirs("output", exist_ok=True)
        with open("output/president_focused_results.csv", "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Title", "Author", "Date", "Score", "Excerpt"])
            
            for result in filtered_results:
                writer.writerow([
                    result["title"],
                    result["author"],
                    result["date"],
                    result["score"],
                    result["excerpt"]
                ])
        
        print(f"\nSaved {len(filtered_results)} president-focused search results to output/president_focused_results.csv")
    else:
        print("\nNo president-focused results found.")

def main():
    """Main function."""
    print("Starting DPRG Top References Search...")
    
    # Create output directory if it doesn't exist
    os.makedirs("output", exist_ok=True)
    
    # First run president-specific searches
    search_for_presidents()
    
    # Store all top references by year
    top_references_by_year = {}
    
    # Process each year
    for year in TARGET_YEARS:
        top_references = get_references_for_year(year)
        top_references_by_year[year] = top_references
        
        # Save after each year in case of interruption
        save_year_references(year, top_references)
    
    # Save top 5 references by year to CSV
    save_all_references(top_references_by_year)
    
    # Print summary to console
    print("\nTop 5 References by Year:")
    for year in sorted(top_references_by_year.keys()):
        references = top_references_by_year.get(year, [])
        if references:
            print(f"\n{year}:")
            for i, ref in enumerate(references):
                print(f"  {i+1}. {ref['title']} by {ref['author']} ({ref['date']})")
        else:
            print(f"\n{year}: No references found")
            
    print("\nResults saved to output/top_references_by_year.csv")

def save_year_references(year, references):
    """Save references for a specific year."""
    os.makedirs("output/years", exist_ok=True)
    with open(f"output/years/{year}_references.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Rank", "Title", "Author", "Date", "Score", "Excerpt"])
        
        for i, ref in enumerate(references):
            writer.writerow([
                i+1,
                ref["title"],
                ref["author"],
                ref["date"],
                ref["score"],
                ref["excerpt"]
            ])

def save_all_references(top_references_by_year):
    """Save all references to a single CSV file."""
    with open("output/top_references_by_year.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Year", "Rank", "Title", "Author", "Date", "Score", "Excerpt"])
        
        for year in sorted(top_references_by_year.keys()):
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

if __name__ == "__main__":
    main() 