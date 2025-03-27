# Example Usage Scenarios

This guide provides practical examples of using the DprgArchiveAgent in various scenarios. We'll cover both CLI and API examples for different use cases.

## CLI Examples

### Basic Search Examples

#### Simple Semantic Search
```bash
# Find information about robotics competitions
python -m src.cli search "robotics competition in Dallas"
```

This performs a semantic search using the dense vector index, looking for content related to robotics competitions in Dallas, even if those exact words aren't used.

#### Keyword Search
```bash
# Search for specific keywords
python -m src.cli search "YaTu4b robot" --type sparse
```

This performs a keyword search using the sparse vector index, which is better for finding exact matches of specific terms.

#### Hybrid Search
```bash
# Combine semantic and keyword search
python -m src.cli search "autonomous navigation techniques" --type hybrid
```

This combines both search methods, useful for balancing semantic understanding with keyword precision.

### Advanced Filtering Examples

#### Search by Author
```bash
# Find content by a specific author about progress videos
python -m src.cli search "progress video" --author "eric@sssi.com"
```

#### Search with Date Filters
```bash
# Find content from a specific year related to robots
python -m src.cli search "robot" --year 2007

# Find content from a specific month and year
python -m src.cli search "contest" --year 2007 --month 2
```

#### Search with Multiple Filters
```bash
# Combine multiple filters for precise queries
python -m src.cli search "DPRG" --year 2007 --author "eric@sssi.com" --keyword "video"
```

### Metadata-Only Search Examples

#### Find All Content by an Author
```bash
# Get all documents by a specific author
python -m src.cli metadata --author "eric@sssi.com"
```

#### Find Content with Specific Keywords
```bash
# Get all documents that contain specific keywords
python -m src.cli metadata --keyword "dprg" --keyword "yatu4b"
```

#### Combined Metadata Search
```bash
# Find documents from a specific time period with specific keywords
python -m src.cli metadata --year 2007 --month 2 --keyword "progress"
```

### Results Control Examples

#### Limit Result Count
```bash
# Get only the top 3 most relevant results
python -m src.cli search "robotics" --top-k 3
```

#### Set Score Threshold
```bash
# Only show highly relevant results (score >= 0.85)
python -m src.cli search "autonomous robot" --min-score 0.85
```

## API Examples

### Basic API Requests

#### Simple Search
```bash
curl -X GET "http://localhost:8000/search?query=robotics+competition"
```

#### Sparse Search
```bash
curl -X GET "http://localhost:8000/search?query=YaTu4b+robot&search_type=sparse"
```

#### Hybrid Search
```bash
curl -X GET "http://localhost:8000/search?query=autonomous+navigation&search_type=hybrid"
```

### API Requests with Filters

#### Search with Author Filter
```bash
curl -X GET "http://localhost:8000/search?query=progress+video&author=eric@sssi.com"
```

#### Search with Date Filters
```bash
curl -X GET "http://localhost:8000/search?query=robot&year=2007&month=2"
```

#### Search with Multiple Filters
```bash
curl -X GET "http://localhost:8000/search?query=DPRG&year=2007&keywords=video,progress"
```

### Metadata API Requests

#### Find by Author
```bash
curl -X GET "http://localhost:8000/metadata?author=eric@sssi.com"
```

#### Find by Keywords
```bash
curl -X GET "http://localhost:8000/metadata?keywords=dprg,yatu4b"
```

#### Find by Combined Metadata
```bash
curl -X GET "http://localhost:8000/metadata?year=2007&month=2&keywords=progress"
```

### Python Code Examples

#### Basic Search with Python
```python
import requests
import json

# Basic search
response = requests.get(
    "http://localhost:8000/search",
    params={"query": "robotics competition"}
)

# Print results nicely
results = response.json()
print(f"Found {results['total']} results in {results['elapsed_time']:.2f}s")
for doc in results["results"]:
    print(f"Score: {doc['score']:.2f} - {doc['metadata']['title']}")
    print(f"Author: {doc['metadata']['author']}")
    print(f"Date: {doc['metadata']['date']}")
    print(f"Excerpt: {doc['text_excerpt'][:100]}...")
    print("-" * 40)
```

#### Advanced Search with Python
```python
import requests

# Search with multiple parameters
params = {
    "query": "progress video",
    "author": "eric@sssi.com",
    "year": 2007,
    "search_type": "hybrid",
    "top_k": 5,
    "min_score": 0.75
}

response = requests.get("http://localhost:8000/search", params=params)
results = response.json()

# Process results
for idx, doc in enumerate(results["results"], 1):
    print(f"Result {idx}: {doc['metadata']['title']} (Score: {doc['score']:.2f})")
```

#### Using Metadata Search
```python
import requests

# Metadata search
params = {
    "year": 2007,
    "keywords": "dprg,progress,video",
    "top_k": 10
}

response = requests.get("http://localhost:8000/metadata", params=params)
results = response.json()

# Check if we got results
if results["total"] > 0:
    print(f"Found {results['total']} matching documents")
    for doc in results["results"]:
        print(f"- {doc['metadata']['title']} ({doc['metadata']['date']})")
else:
    print("No matching documents found")
```

### JavaScript/Node.js Examples

#### Basic Search with JavaScript
```javascript
// Basic search using fetch
fetch('http://localhost:8000/search?query=robotics+competition')
  .then(response => response.json())
  .then(data => {
    console.log(`Found ${data.total} results in ${data.elapsed_time.toFixed(2)}s`);
    data.results.forEach(doc => {
      console.log(`Score: ${doc.score.toFixed(2)} - ${doc.metadata.title}`);
      console.log(`Author: ${doc.metadata.author}`);
      console.log(`Date: ${doc.metadata.date}`);
      console.log(`Excerpt: ${doc.text_excerpt.substring(0, 100)}...`);
      console.log('-'.repeat(40));
    });
  })
  .catch(error => console.error('Error:', error));
```

#### Advanced Search with JavaScript
```javascript
// Search with multiple parameters
const params = new URLSearchParams({
  query: 'progress video',
  author: 'eric@sssi.com',
  year: 2007,
  search_type: 'hybrid',
  top_k: 5,
  min_score: 0.75
});

fetch(`http://localhost:8000/search?${params.toString()}`)
  .then(response => response.json())
  .then(data => {
    console.log(`Search query: "${data.query}" (${data.search_type} search)`);
    console.log(`Found ${data.total} results`);
    
    data.results.forEach((doc, idx) => {
      console.log(`Result ${idx+1}: ${doc.metadata.title} (Score: ${doc.score.toFixed(2)})`);
    });
  })
  .catch(error => console.error('Error:', error));
```

## Real-World Use Cases

### Use Case 1: Finding Historical Information

**Scenario**: A DPRG member wants to find information about past robotics competitions.

**CLI Approach**:
```bash
python -m src.cli search "robotics competition history" --type hybrid
```

**API Approach**:
```bash
curl -X GET "http://localhost:8000/search?query=robotics+competition+history&search_type=hybrid"
```

### Use Case 2: Finding a Specific Author's Content on a Topic

**Scenario**: Looking for progress updates on a specific project by a particular author.

**CLI Approach**:
```bash
python -m src.cli search "YaTu4b progress" --author "eric@sssi.com" --type hybrid
```

**API Approach**:
```bash
curl -X GET "http://localhost:8000/search?query=YaTu4b+progress&author=eric@sssi.com&search_type=hybrid"
```

### Use Case 3: Finding Content from a Specific Time Period

**Scenario**: Researching DPRG activities from February 2007.

**CLI Approach**:
```bash
python -m src.cli metadata --year 2007 --month 2
```

**API Approach**:
```bash
curl -X GET "http://localhost:8000/metadata?year=2007&month=2"
```

### Use Case 4: Integration into a Web Application

**Scenario**: Building a web interface to search the DPRG archive.

**Frontend JavaScript**:
```javascript
// Search form handler
document.getElementById('search-form').addEventListener('submit', function(e) {
  e.preventDefault();
  
  const query = document.getElementById('query').value;
  const author = document.getElementById('author').value;
  const year = document.getElementById('year').value;
  const searchType = document.querySelector('input[name="search-type"]:checked').value;
  
  const params = new URLSearchParams();
  params.append('query', query);
  if (author) params.append('author', author);
  if (year) params.append('year', year);
  params.append('search_type', searchType);
  
  fetch(`http://localhost:8000/search?${params.toString()}`)
    .then(response => response.json())
    .then(data => {
      const resultsDiv = document.getElementById('results');
      resultsDiv.innerHTML = ''; // Clear previous results
      
      if (data.total === 0) {
        resultsDiv.innerHTML = '<p>No results found.</p>';
        return;
      }
      
      data.results.forEach(doc => {
        const resultCard = document.createElement('div');
        resultCard.className = 'result-card';
        resultCard.innerHTML = `
          <h3>${doc.metadata.title || 'Untitled'}</h3>
          <p class="meta">
            <span>Author: ${doc.metadata.author || 'Unknown'}</span>
            <span>Date: ${doc.metadata.date || 'Unknown'}</span>
            <span>Score: ${doc.score.toFixed(2)}</span>
          </p>
          <p class="excerpt">${doc.text_excerpt}</p>
          <p class="keywords">Keywords: ${doc.metadata.keywords?.join(', ') || 'None'}</p>
        `;
        resultsDiv.appendChild(resultCard);
      });
    })
    .catch(error => {
      console.error('Error:', error);
      document.getElementById('results').innerHTML = 
        '<p class="error">An error occurred while searching. Please try again.</p>';
    });
}); 