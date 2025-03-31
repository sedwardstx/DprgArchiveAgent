#!/usr/bin/env python3
"""
Script to find DPRG officer election results and officer announcements.
Uses targeted search terms and focuses on December/January timeframes when elections typically occurred.
"""
import subprocess
import re
import csv
import os
import time
from collections import defaultdict

# Target years for our search
#TARGET_YEARS = list(range(1997, 2016))  # 1997-2015
TARGET_YEARS = list(range(2006, 2007))  # 1997-2015

def run_search(query, search_type="hybrid", top_k=30, min_score=0.1):
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

def extract_month_from_date(date_str):
    """Extract month from a date string."""
    if not date_str:
        return None
        
    # Try to extract MM from YYYY-MM-DD format
    month_match = re.search(r'\d{4}-(\d{2})-\d{2}', date_str)
    if month_match:
        return int(month_match.group(1))
    return None

def is_election_period_date(date_str):
    """Check if the date is in the election period (December or January)."""
    month = extract_month_from_date(date_str)
    if month in [12, 1]:  # December or January
        return True
    return False

def get_officer_election_references(year):
    """Get references for officer elections for a specific year."""
    print(f"\nSearching for officer elections in {year}...")
    
    # Create specific queries focused on elections and officers
    # Include the user-suggested terms that have shown good results
    election_queries = [
        # January election queries for the target year
        f"DPRG officer election {year} January",
        f"DPRG officers elected {year} January",
        f"DPRG voting results {year} January",
        
        # December election queries for the previous year (since elections often happen in Dec for next year)
        f"DPRG officer election {year-1} December",
        f"DPRG officers elected {year-1} December",
        f"DPRG voting results {year-1} December",
        
        # User-suggested specific terms
        f"{year} voting REQUEST DPRG",
        f"{year} Officers Election DPRG",
        f"{year} proxy vote DPRG",
        f"{year} nominate DPRG officers",
        f"{year} \"President:\" DPRG",
        f"{year} \"Vice President:\" DPRG",
        f"{year} club officers DPRG",
        
        # Additional targeted queries for election results
        f"{year} election results DPRG",
        f"{year} DPRG officer announcement",
        f"{year} DPRG annual meeting minutes officers",
    ]
    
    all_results = []
    
    for query in election_queries:
        print(f"  Query: {query}")
        search_output = run_search(query, min_score=0.1)
        rows = extract_table_rows(search_output)
        
        # Prioritize rows that contain officer-related keywords in the title or excerpt
        for row in rows:
            # Extract year from the date field
            row_year = extract_year_from_date(row["date"])
            
            # Calculate relevance score boost based on content
            full_text = (row["title"] + " " + row["excerpt"]).lower()
            relevance_boost = 0
            
            # Boost score based on presence of key terms in content
            officer_terms = [
                "president", "vice president", "secretary", "treasurer", 
                "elected", "election results", "officer", "voting results",
                "proxy vote", "nominate", "annual meeting", "executive committee"
            ]
            
            for term in officer_terms:
                if term in full_text:
                    relevance_boost += 0.05
            
            # Extra boost for specific officer position mentions
            specific_officer_patterns = [
                r"president:?\s*([A-Z][a-zA-Z\.-]+(?:\s+[A-Z][a-zA-Z\.-]+)+)",
                r"vice president:?\s*([A-Z][a-zA-Z\.-]+(?:\s+[A-Z][a-zA-Z\.-]+)+)",
                r"secretary:?\s*([A-Z][a-zA-Z\.-]+(?:\s+[A-Z][a-zA-Z\.-]+)+)",
                r"treasurer:?\s*([A-Z][a-zA-Z\.-]+(?:\s+[A-Z][a-zA-Z\.-]+)+)"
            ]
            
            for pattern in specific_officer_patterns:
                if re.search(pattern, full_text, re.IGNORECASE):
                    relevance_boost += 0.1
            
            # Boost if in election period (December or January)
            if is_election_period_date(row["date"]):
                relevance_boost += 0.1
                
            # Only include results that are relevant to the year or have year in content
            if (row_year == year or row_year == year-1 or str(year) in full_text):
                # Apply the relevance boost
                row["score"] += relevance_boost
                row["adjusted"] = True  # Mark that we've adjusted the score
                
                # Extract potential officer positions mentioned
                row["positions"] = extract_officer_positions(full_text)
                
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
    
    # Take top results
    return filtered_results[:5]

def extract_officer_positions(text):
    """Extract officer positions and names from text."""
    positions = {}
    
    # Check for various positions
    position_patterns = {
        "President": [
            r"[Pp]resident:?\s*([A-Z][a-zA-Z\.-]+(?:\s+[A-Z][a-zA-Z\.-]+)+)",
            r"([A-Z][a-zA-Z\.-]+(?:\s+[A-Z][a-zA-Z\.-]+)+)(?:\s*[-,]\s*)[Pp]resident",
            r"([A-Z][a-zA-Z\.-]+(?:\s+[A-Z][a-zA-Z\.-]+)+)\s+(?:is|as|was|became|elected)\s+(?:the\s+)?[Pp]resident",
            r"elected\s+([A-Z][a-zA-Z\.-]+(?:\s+[A-Z][a-zA-Z\.-]+)+)\s+as\s+[Pp]resident",
            r"new\s+[Pp]resident\s+([A-Z][a-zA-Z\.-]+(?:\s+[A-Z][a-zA-Z\.-]+)+)",
        ],
        "Vice President": [
            r"[Vv]ice\s*[Pp]resident:?\s*([A-Z][a-zA-Z\.-]+(?:\s+[A-Z][a-zA-Z\.-]+)+)",
            r"([A-Z][a-zA-Z\.-]+(?:\s+[A-Z][a-zA-Z\.-]+)+)(?:\s*[-,]\s*)[Vv]ice\s*[Pp]resident",
        ],
        "Secretary": [
            r"[Ss]ecretary:?\s*([A-Z][a-zA-Z\.-]+(?:\s+[A-Z][a-zA-Z\.-]+)+)",
            r"([A-Z][a-zA-Z\.-]+(?:\s+[A-Z][a-zA-Z\.-]+)+)(?:\s*[-,]\s*)[Ss]ecretary",
        ],
        "Treasurer": [
            r"[Tt]reasurer:?\s*([A-Z][a-zA-Z\.-]+(?:\s+[A-Z][a-zA-Z\.-]+)+)",
            r"([A-Z][a-zA-Z\.-]+(?:\s+[A-Z][a-zA-Z\.-]+)+)(?:\s*[-,]\s*)[Tt]reasurer",
        ],
    }
    
    for position, patterns in position_patterns.items():
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.DOTALL)
            for match in matches:
                name = match.group(1).strip()
                # Basic name verification
                if re.match(r"^[A-Z][a-zA-Z\.-]+(?:\s+[A-Z][a-zA-Z\.-]+)+$", name):
                    positions[position] = name
                    break  # Found one name for this position, move to next position
    
    return positions

def search_across_all_years():
    """Run general searches for officer elections and announcements."""
    print("\nRunning general officer election searches...")
    general_queries = [
        # Generic election queries not tied to specific years
        "DPRG election results",
        "DPRG officers elected",
        "DPRG annual meeting minutes officers",
        "DPRG president announcement",
        "DPRG executive committee members",
        "DPRG club officers announcement",
        "DPRG voting results",
        "DPRG officer nomination results",
        "President: DPRG",
        "Vice President: DPRG",
    ]
    
    all_results = []
    
    for query in general_queries:
        print(f"  Query: {query}")
        search_output = run_search(query, min_score=0.1, top_k=50)
        rows = extract_table_rows(search_output)
        
        # Process each row to check if it contains officer information
        for row in rows:
            # Extract year from the date field
            row_year = extract_year_from_date(row["date"])
            
            # Calculate relevance score boost based on content
            full_text = (row["title"] + " " + row["excerpt"]).lower()
            relevance_boost = 0
            
            # Boost score based on presence of key terms in content
            officer_terms = [
                "president", "vice president", "secretary", "treasurer", 
                "elected", "election results", "officer", "voting results",
                "proxy vote", "nominate", "annual meeting", "executive committee"
            ]
            
            for term in officer_terms:
                if term in full_text:
                    relevance_boost += 0.05
            
            # Extra boost for specific officer position mentions
            specific_officer_patterns = [
                r"president:?\s*([A-Z][a-zA-Z\.-]+(?:\s+[A-Z][a-zA-Z\.-]+)+)",
                r"vice president:?\s*([A-Z][a-zA-Z\.-]+(?:\s+[A-Z][a-zA-Z\.-]+)+)",
                r"secretary:?\s*([A-Z][a-zA-Z\.-]+(?:\s+[A-Z][a-zA-Z\.-]+)+)",
                r"treasurer:?\s*([A-Z][a-zA-Z\.-]+(?:\s+[A-Z][a-zA-Z\.-]+)+)"
            ]
            
            for pattern in specific_officer_patterns:
                if re.search(pattern, full_text, re.IGNORECASE):
                    relevance_boost += 0.1
            
            # Apply the relevance boost
            row["score"] += relevance_boost
            row["adjusted"] = True  # Mark that we've adjusted the score
            
            # Extract potential officer positions mentioned
            row["positions"] = extract_officer_positions(full_text)
            
            # Only include rows that actually have officer position mentions
            if row["positions"]:
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
    
    # Take top results
    return filtered_results[:50]

def main():
    """Main function."""
    print("Starting DPRG Officer Search...")
    
    # Create output directory if it doesn't exist
    os.makedirs("output", exist_ok=True)
    
    # First run searches across all years to find general officer mentions
    general_results = search_across_all_years()
    
    # If we found general results, save them
    if general_results:
        with open("output/general_officer_results.csv", "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Title", "Author", "Date", "Score", "President", "Vice President", "Secretary", "Treasurer", "Excerpt"])
            
            for result in general_results:
                positions = result["positions"]
                writer.writerow([
                    result["title"],
                    result["author"],
                    result["date"],
                    result["score"],
                    positions.get("President", ""),
                    positions.get("Vice President", ""),
                    positions.get("Secretary", ""),
                    positions.get("Treasurer", ""),
                    result["excerpt"]
                ])
                
        print(f"\nSaved {len(general_results)} general officer mentions to output/general_officer_results.csv")
    
    # Store officer references by year
    officer_refs_by_year = {}
    presidents_by_year = {}
    
    # Process each year
    for year in TARGET_YEARS:
        references = get_officer_election_references(year)
        officer_refs_by_year[year] = references
        
        # Extract presidents for this year
        for ref in references:
            if "positions" in ref and "President" in ref["positions"]:
                if year not in presidents_by_year:
                    presidents_by_year[year] = []
                presidents_by_year[year].append({
                    "name": ref["positions"]["President"],
                    "reference": ref
                })
        
        # Save year-specific references
        if references:
            with open(f"output/years/{year}_officer_references.csv", "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["Rank", "Title", "Author", "Date", "Score", "President", "Vice President", "Secretary", "Treasurer", "Excerpt"])
                
                for i, ref in enumerate(references):
                    positions = ref.get("positions", {})
                    writer.writerow([
                        i+1,
                        ref["title"],
                        ref["author"],
                        ref["date"],
                        ref["score"],
                        positions.get("President", ""),
                        positions.get("Vice President", ""),
                        positions.get("Secretary", ""),
                        positions.get("Treasurer", ""),
                        ref["excerpt"]
                    ])
    
    # Save top references by year to CSV
    with open("output/officer_references_by_year.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Year", "Rank", "Title", "Author", "Date", "Score", "President", "Vice President", "Secretary", "Treasurer", "Excerpt"])
        
        for year in sorted(officer_refs_by_year.keys()):
            references = officer_refs_by_year[year]
            for i, ref in enumerate(references):
                positions = ref.get("positions", {})
                writer.writerow([
                    year,
                    i+1,
                    ref["title"],
                    ref["author"],
                    ref["date"],
                    ref["score"],
                    positions.get("President", ""),
                    positions.get("Vice President", ""),
                    positions.get("Secretary", ""),
                    positions.get("Treasurer", ""),
                    ref["excerpt"]
                ])
    
    # Save presidents by year summary
    with open("output/presidents_by_year.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Year", "President", "Source Title", "Source Date", "Source Author"])
        
        for year in sorted(presidents_by_year.keys()):
            president_refs = presidents_by_year[year]
            for president_ref in president_refs:
                ref = president_ref["reference"]
                writer.writerow([
                    year,
                    president_ref["name"],
                    ref["title"],
                    ref["date"],
                    ref["author"]
                ])
    
    # Print summary to console
    print("\nOfficer References by Year (showing up to 5 per year):")
    for year in sorted(TARGET_YEARS):
        references = officer_refs_by_year.get(year, [])
        if references:
            print(f"\n{year}:")
            for i, ref in enumerate(references):
                positions = ref.get("positions", {})
                president = positions.get("President", "")
                vice_president = positions.get("Vice President", "")
                
                position_str = ""
                if president:
                    position_str += f"President: {president}"
                if vice_president:
                    if position_str:
                        position_str += ", "
                    position_str += f"VP: {vice_president}"
                
                print(f"  {i+1}. {ref['title']} by {ref['author']} ({ref['date']}) - {position_str}")
        else:
            print(f"\n{year}: No officer references found")
            
    print("\nResults saved to output/officer_references_by_year.csv")
    print("President summary saved to output/presidents_by_year.csv")

if __name__ == "__main__":
    main() 