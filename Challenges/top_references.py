#!/usr/bin/env python3
"""
Script to identify top DPRG archive references related to officer elections by year.
This script focuses on finding references to club officer elections, particularly
presidents and other officers, with emphasis on election periods (Dec-Feb).
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

def run_search(query, search_type="hybrid", top_k=20, min_score=0.1, year=None, month=None):
    """Run a search using the CLI tool and return the results.
    
    Args:
        query (str): The search query text
        search_type (str): Type of search (dense, sparse, or hybrid)
        top_k (int): Number of results to return
        min_score (float): Minimum similarity score threshold
        year (int): Optional year to filter results
        month (int): Optional month to filter results (1-12)
    """
    cmd = ["python", "-m", "src.cli", "search", query, 
           "--type", search_type, "--top-k", str(top_k), "--min-score", str(min_score)]
    
    # Add metadata filters if provided
    if year is not None:
        cmd.extend(["--year", str(year)])
    if month is not None:
        cmd.extend(["--month", str(month)])
    
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout

def extract_table_rows(output_text):
    """Extract table rows from the CLI output.
    
    This function parses the search results table, preserving exact titles and dates
    for cross-referencing with the DPRG website. It handles multiple table formats
    and cleans up the data while maintaining accuracy.
    
    Args:
        output_text (str): Raw output from the CLI search command
        
    Returns:
        list: List of dictionaries containing parsed row data
    """
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
    
    # Different possible row patterns to handle various table formats
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
                
                # Clean up title - preserve exact title but ensure [DPRG] prefix
                title = re.sub(r'\s+', ' ', title).strip()
                if not title.startswith('[DPRG]'):
                    title = f"[DPRG] {title}"
                
                # Clean up author email - remove truncated characters
                author = re.sub(r'[^\w@\.-]', '', author)
                
                # Clean up date - ensure proper format and extract from either date field or excerpt
                date_match = re.search(r'(\d{4})-(\d{2})-(\d{2})', date)
                if date_match:
                    date = f"{date_match.group(1)}-{date_match.group(2)}-{date_match.group(3)}"
                else:
                    # Try to extract date from excerpt if not in standard format
                    excerpt_date_match = re.search(r'(\d{4})-(\d{2})-(\d{2})', excerpt)
                    if excerpt_date_match:
                        date = f"{excerpt_date_match.group(1)}-{excerpt_date_match.group(2)}-{excerpt_date_match.group(3)}"
                
                # Extract just the numeric score value
                score_match = re.search(r"([\d\.]+)", score)
                if score_match:
                    score = score_match.group(1)
                
                # Create row object with cleaned data
                row = {
                    "score": float(score),
                    "title": title,
                    "author": author,
                    "date": date,
                    "excerpt": excerpt
                }
                rows.append(row)
                print(f"  Extracted: {title} by {author} ({date})")
            except Exception as e:
                print(f"  Error parsing row: {str(e)}")
    
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

def is_election_period_date(date_str):
    """Check if the date falls within election period (Dec-Feb)."""
    if not date_str:
        return False
        
    # Try to extract month from YYYY-MM-DD format
    month_match = re.search(r'\d{4}-(\d{2})-\d{2}', date_str)
    if month_match:
        month = int(month_match.group(1))
        return month in [12, 1, 2]  # December, January, February
    return False

def get_election_references_for_year(year):
    """Get top references for officer elections in a specific year.
    
    This function searches for officer election references across a three-month period:
    - December of the previous year
    - January of the target year
    - February of the target year
    
    The search is designed to find election-related content while preserving exact titles
    and dates for cross-referencing with the DPRG website.
    
    Args:
        year (int): The target year to search for election references
        
    Returns:
        list: Top 10 most relevant election references, sorted by score
    """
    print(f"\nSearching for officer election references in {year}...")
    
    # Simplified queries focusing on officer positions (without redundant DPRG prefix)
    election_queries = [
        # Core officer position queries
        "President",
        "Vice President",
        "Secretary",
        "Treasurer",
        "Librarian",
        
        # Election-specific variations
        "President election",
        "Vice President election",
        "Secretary election",
        "Treasurer election",
        "Librarian election",
        
        # Results variations
        "President elected",
        "Vice President elected",
        "Secretary elected",
        "Treasurer elected",
        "Librarian elected"
    ]
    
    all_results = []
    
    # Search for each query in each relevant month
    for query in election_queries:
        # Search December of previous year
        print(f"  Query: {query} (December {year-1})")
        search_output = run_search(query, min_score=0.1, year=year-1, month=12)
        rows = extract_table_rows(search_output)
        all_results.extend(rows)
        
        # Search January of target year
        print(f"  Query: {query} (January {year})")
        search_output = run_search(query, min_score=0.1, year=year, month=1)
        rows = extract_table_rows(search_output)
        all_results.extend(rows)
        
        # Search February of target year
        print(f"  Query: {query} (February {year})")
        search_output = run_search(query, min_score=0.1, year=year, month=2)
        rows = extract_table_rows(search_output)
        all_results.extend(rows)
        
        # Rate limiting to avoid overwhelming the server
        time.sleep(0.5)
    
    # Calculate relevance boost for each result
    for row in all_results:
        # Calculate relevance boost based on content
        full_text = (row["title"] + " " + row["excerpt"]).lower()
        relevance_boost = 0
        
        # Boost score based on presence of key election terms
        election_terms = [
            "president", "vice president", "secretary", "treasurer", "librarian",
            "elected", "election results", "officer", "voting results",
            "proxy vote", "nominate", "annual meeting", "executive committee"
        ]
        
        for term in election_terms:
            if term in full_text:
                relevance_boost += 0.05
        
        # Extra boost for specific officer position mentions with names
        specific_officer_patterns = [
            r"president:?\s*([A-Z][a-zA-Z\.-]+(?:\s+[A-Z][a-zA-Z\.-]+)+)",
            r"vice president:?\s*([A-Z][a-zA-Z\.-]+(?:\s+[A-Z][a-zA-Z\.-]+)+)",
            r"secretary:?\s*([A-Z][a-zA-Z\.-]+(?:\s+[A-Z][a-zA-Z\.-]+)+)",
            r"treasurer:?\s*([A-Z][a-zA-Z\.-]+(?:\s+[A-Z][a-zA-Z\.-]+)+)",
            r"librarian:?\s*([A-Z][a-zA-Z\.-]+(?:\s+[A-Z][a-zA-Z\.-]+)+)"
        ]
        
        for pattern in specific_officer_patterns:
            if re.search(pattern, full_text, re.IGNORECASE):
                relevance_boost += 0.1
        
        # Apply the relevance boost
        row["score"] += relevance_boost
    
    # Remove duplicates while keeping the highest scoring version of each unique post
    unique_results = {}
    for row in all_results:
        key = f"{row['title']}|{row['author']}"
        if key not in unique_results or row['score'] > unique_results[key]['score']:
            unique_results[key] = row
    
    # Sort by score and take top 10
    filtered_results = list(unique_results.values())
    filtered_results.sort(key=lambda x: x["score"], reverse=True)
    return filtered_results[:10]

def analyze_officer_positions(top_references_by_year):
    """Analyze election results to determine officer positions by year.
    
    This function examines the top references for each year and attempts to determine
    who held each officer position based on election results and announcements.
    
    Args:
        top_references_by_year (dict): Dictionary of top references by year
    """
    # Officer positions to track
    positions = ["President", "Vice President", "Secretary", "Treasurer", "Librarian"]
    
    # Create a summary file
    with open("output/officer_positions_by_year.md", "w") as f:
        f.write("# DPRG Officer Positions by Year\n\n")
        
        for year in sorted(top_references_by_year.keys()):
            f.write(f"## {year}\n\n")
            f.write("| Position | Name | Source | Date |\n")
            f.write("|----------|------|---------|------|\n")
            
            # Get all references for this year
            references = top_references_by_year.get(year, [])
            
            # Track found positions to avoid duplicates
            found_positions = set()
            
            # First pass: Look for explicit election results
            for ref in references:
                full_text = (ref["title"] + " " + ref["excerpt"]).lower()
                
                # Look for patterns like "President: John Smith" or "John Smith elected President"
                for position in positions:
                    if position.lower() in full_text:
                        # Try to find the name after the position
                        name_patterns = [
                            rf"{position.lower()}:?\s*([A-Z][a-zA-Z\.-]+(?:\s+[A-Z][a-zA-Z\.-]+)+)",
                            rf"([A-Z][a-zA-Z\.-]+(?:\s+[A-Z][a-zA-Z\.-]+)+)\s+elected\s+{position.lower()}"
                        ]
                        
                        for pattern in name_patterns:
                            match = re.search(pattern, full_text, re.IGNORECASE)
                            if match and position not in found_positions:
                                name = match.group(1).strip()
                                f.write(f"| {position} | {name} | {ref['title']} | {ref['date']} |\n")
                                found_positions.add(position)
                                break
            
            # Second pass: Look for announcements or mentions if we still have missing positions
            for ref in references:
                full_text = (ref["title"] + " " + ref["excerpt"]).lower()
                
                for position in positions:
                    if position not in found_positions and position.lower() in full_text:
                        # Try to find any name near the position mention
                        name_pattern = r"([A-Z][a-zA-Z\.-]+(?:\s+[A-Z][a-zA-Z\.-]+)+)"
                        matches = re.finditer(name_pattern, full_text)
                        
                        # Look for names that appear near the position mention
                        for match in matches:
                            name = match.group(1).strip()
                            # Skip common words or partial names
                            if len(name.split()) > 1 and not any(word in name.lower() for word in ["president", "vice", "secretary", "treasurer", "librarian"]):
                                f.write(f"| {position} | {name} | {ref['title']} | {ref['date']} |\n")
                                found_positions.add(position)
                                break
            
            # Mark any unfound positions
            for position in positions:
                if position not in found_positions:
                    f.write(f"| {position} | Unknown | - | - |\n")
            
            f.write("\n")
    
    print("\nOfficer positions summary saved to output/officer_positions_by_year.md")

def main():
    """Main function."""
    print("Starting DPRG Officer Election References Search...")
    
    # Create output directory if it doesn't exist
    os.makedirs("output", exist_ok=True)
    
    # Store all top references by year
    top_references_by_year = {}
    
    # Process each year
    for year in TARGET_YEARS:
        top_references = get_election_references_for_year(year)
        top_references_by_year[year] = top_references
        
        # Save after each year in case of interruption
        save_year_references(year, top_references)
    
    # Save top 10 references by year to CSV
    save_all_references(top_references_by_year)
    
    # Analyze and save officer positions
    analyze_officer_positions(top_references_by_year)
    
    # Print summary to console
    print("\nTop 10 Officer Election References by Year:")
    for year in sorted(top_references_by_year.keys()):
        references = top_references_by_year.get(year, [])
        if references:
            print(f"\n{year}:")
            for i, ref in enumerate(references):
                print(f"  {i+1}. {ref['title']} by {ref['author']} ({ref['date']})")
        else:
            print(f"\n{year}: No election references found")
            
    print("\nResults saved to output/top_references_by_year.csv")
    print("Officer positions summary saved to output/officer_positions_by_year.md")

def save_year_references(year, references):
    """Save references for a specific year."""
    os.makedirs("output/years", exist_ok=True)
    with open(f"output/years/{year}_election_references.csv", "w", newline="") as f:
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