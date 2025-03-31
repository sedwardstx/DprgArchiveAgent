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
    # Formal title matches
    r"president:?\s+([A-Z][a-zA-Z\.-]+\s+[A-Z][a-zA-Z\.-]+)",
    r"president\s*[-:=]\s*([A-Z][a-zA-Z\.-]+\s+[A-Z][a-zA-Z\.-]+)",
    r"President[-:]?\s*([A-Z][a-zA-Z\.-]+)",  # Single name mentions
    
    # Contextual mentions
    r"([A-Z][a-zA-Z\.-]+\s+[A-Z][a-zA-Z\.-]+)\s+(?:is|as|was|became|elected)\s+(?:the\s+)?president",
    r"([A-Z][a-zA-Z\.-]+\s+[A-Z][a-zA-Z\.-]+),?\s+president",
    r"new president[,\s]+([A-Z][a-zA-Z\.-]+\s+[A-Z][a-zA-Z\.-]+)",
    r"president[,\s]+([A-Z][a-zA-Z\.-]+\s+[A-Z][a-zA-Z\.-]+)",
    r"for president(?:\s*[-:])?\s*([A-Z][a-zA-Z\.-]+\s+[A-Z][a-zA-Z\.-]+)",
    
    # Specific email formats
    r"president.*?([A-Z][a-zA-Z\.-]+@[a-zA-Z0-9\.-]+\.[a-zA-Z]{2,})\s+\(([A-Z][a-zA-Z\.-]+\s+[A-Z][a-zA-Z\.-]+)\)",
    
    # Name with title
    r"([A-Z][a-zA-Z\.-]+\s+[A-Z][a-zA-Z\.-]+)\s*[-–—]\s*President",
]

# Extract specific patterns for elections results
ELECTION_RESULTS_INDICATORS = [
    r"(?:DPRG|2\d{3}|new|election)\s+(?:officer|election)s?(?:\s+results)?:.*?president:?\s+([A-Z][a-zA-Z\.-]+\s+[A-Z][a-zA-Z\.-]+)",
    r"president\s*[-:=]\s*([A-Z][a-zA-Z\.-]+\s+[A-Z][a-zA-Z\.-]+)",
    r"president\s*[-:=]\s*([A-Z][a-zA-Z\.-]+)",  # Single name
]

def run_search(query, search_type="hybrid", top_k=150, min_score=0.2):
    """Run a search using the CLI tool and return the results."""
    cmd = ["python", "-m", "src.cli", "search", query, 
           "--type", search_type, "--top-k", str(top_k), "--min-score", str(min_score)]
    
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if DEBUG:
        print(f"Command exit code: {result.returncode}")
    return result.stdout

def extract_presidents(text, year=None):
    """Extract president mentions from text."""
    found_presidents = []
    
    # Debug
    if DEBUG:
        print(f"Searching for presidents in text: {text[:100]}...")
    
    # Try election results indicators first (more specific)
    for pattern in ELECTION_RESULTS_INDICATORS:
        matches = re.finditer(pattern, text, re.IGNORECASE | re.DOTALL)
        for match in matches:
            try:
                president_name = match.group(1)
                # Handle single name
                if re.match(r"^[A-Z][a-zA-Z\.-]+$", president_name):
                    # This is just a single name, might want to collect these separately
                    if DEBUG:
                        print(f"Found single name president: {president_name}")
                    continue
                
                # Basic name verification (handle more formats)
                if re.match(r"^[A-Z][a-zA-Z\.-]+\s+[A-Z][a-zA-Z\.-]+$", president_name):
                    found_presidents.append((president_name, year))
                    if DEBUG:
                        print(f"Found president from election pattern: {president_name} ({year})")
            except Exception as e:
                if DEBUG:
                    print(f"Error extracting president: {str(e)}")
    
    # Then try the more general president indicators
    for pattern in PRESIDENT_INDICATORS:
        matches = re.finditer(pattern, text, re.IGNORECASE | re.DOTALL)
        for match in matches:
            try:
                # Some patterns have multiple capture groups for different formats
                if len(match.groups()) > 1 and match.group(2):
                    president_name = match.group(2)  # Email format with name
                else:
                    president_name = match.group(1)
                    
                # Skip if it's just an email address
                if "@" in president_name:
                    continue
                    
                # Handle single name
                if re.match(r"^[A-Z][a-zA-Z\.-]+$", president_name):
                    # This is just a single name, might want to collect these separately
                    if DEBUG:
                        print(f"Found single name president: {president_name}")
                    continue
                    
                # Basic name verification (handle more formats)
                if re.match(r"^[A-Z][a-zA-Z\.-]+\s+[A-Z][a-zA-Z\.-]+$", president_name):
                    found_presidents.append((president_name, year))
                    if DEBUG:
                        print(f"Found president from general pattern: {president_name} ({year})")
            except Exception as e:
                if DEBUG:
                    print(f"Error extracting president: {str(e)}")
    
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
    # First check if we have any search results
    if "No results found" in search_output:
        print("  - No search results returned")
        return [], []
        
    # Print a snippet of the output for debugging
    if DEBUG:
        print(f"  - Search returned content (snippet): {search_output[:200]}...")
    
    # Look for table rows in the output
    # Try to match the CLI table row structure
    result_sections = []
    
    # First try to directly extract from the raw text
    # This handles the case where the CLI tool might not follow a consistent format
    year_pattern = r"\b(20\d\d|19\d\d)\b"
    years = re.findall(year_pattern, search_output)
    if DEBUG and years:
        print(f"  - Found years in text: {years}")
    
    # Directly search for president mentions in the entire text
    presidents_found = extract_presidents(search_output, None)
    if DEBUG:
        print(f"  - Direct text search found {len(presidents_found)} president mentions")
    
    # Also try to extract structured results
    try:
        # Try to split on table boundaries - handle complex CLI output
        table_pattern = r"┃(.+?)┃(.+?)┃(.+?)┃(.+?)┃(.+?)┃"
        rows = re.findall(table_pattern, search_output, re.DOTALL)
        
        if not rows:
            # Fallback to simpler pipe separator
            pipe_pattern = r"\|(.*?)\|(.*?)\|(.*?)\|(.*?)\|(.*?)\|"
            rows = re.findall(pipe_pattern, search_output, re.DOTALL)
        
        if DEBUG:
            print(f"  - Found {len(rows)} table rows")
        
        for row in rows:
            # Skip header row with column names
            if "Score" in row[0] and "Title" in row[1]:
                continue
            
            # Extract data - handle CLI formatting with lots of whitespace
            try:
                score = row[0].strip()
                title = row[1].strip()
                author = row[2].strip()
                date = row[3].strip()
                excerpt = row[4].strip()
                
                # Skip very short/empty rows
                if len(title) < 2 or len(author) < 2:
                    continue
                
                # Construct a section with metadata
                section = f"Title: {title}\nAuthor: {author}\nDate: {date}\nExcerpt: {excerpt}"
                result_sections.append(section)
                
                # Try to extract year from date
                year = None
                if date:
                    date_years = re.findall(year_pattern, date)
                    if date_years:
                        year = int(date_years[0])
                
                # Extract presidents from this section
                section_presidents = extract_presidents(section, year)
                presidents_found.extend(section_presidents)
                
                # Debug info
                if DEBUG:
                    print(f"  - Found result: {title} by {author} ({date})")
                    if section_presidents:
                        print(f"    - Found presidents: {section_presidents}")
            except Exception as e:
                if DEBUG:
                    print(f"  - Error parsing row: {str(e)}")
    except Exception as e:
        if DEBUG:
            print(f"  - Error parsing search results: {str(e)}")
    
    # Create document info
    documents = []
    for president, year in presidents_found:
        # Create a placeholder document info
        doc_info = {
            "title": "Unknown",
            "author": "Unknown",
            "date": str(year) if year else "Unknown",
            "excerpt": f"President mention: {president}",
            "full_text": f"President: {president}, Year: {year}"
        }
        
        documents.append({
            "presidents": [(president, year)],
            "info": doc_info
        })
    
    return presidents_found, documents

def run_president_search():
    """Run searches for president information and process results."""
    all_presidents = []
    all_documents = []
    
    # Add some specific targeted searches that might help
    target_searches = [
        # Direct name searches - add known president names
        "Ron Grant president",
        "David Anderson president",
        "Mike Dodson president",
        "Jim Brown president",
        # Specific elections
        "2006 DPRG election results",
        "2007 DPRG election results",
        "2010 DPRG election results",
        "2015 DPRG election results",
    ]
    
    # Try the target searches first
    for query in target_searches:
        search_output = run_search(query)
        presidents, documents = process_search_results(search_output)
        all_presidents.extend(presidents)
        all_documents.extend(documents)
        print(f"Found {len(presidents)} president mentions in query: {query}")
        # Avoid rate limiting
        time.sleep(1)
    
    # Then do the generic searches
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