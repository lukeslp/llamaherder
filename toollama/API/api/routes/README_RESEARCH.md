# Academic Research Endpoints

This module provides access to various scholarly databases and academic search engines, allowing users to search for scientific papers, academic articles, and research publications through a unified API.

## Overview

The research module implements the following endpoints:

- **Semantic Scholar**: Search for academic papers with detailed metadata
- **arXiv**: Access preprints across multiple scientific domains
- **PubMed**: Search for biomedical and life sciences literature
- **Google Scholar**: Search academic papers (implemented via Semantic Scholar as a proxy)

All endpoints follow a consistent response format and support both GET and POST request methods for flexibility.

## Endpoint Details

### 1. Semantic Scholar

Provides access to academic papers using the Semantic Scholar API.

**Endpoint:** `/research/semantic-scholar`

**Parameters:**
- `query` (required): The search term to look up
- `limit` (optional): Maximum number of results to return (default: 10)
- `fields` (optional): Fields to include in response (comma-separated, default: "url,abstract,authors,title,venue,year,publicationTypes,tldr")
- `fieldsOfStudy` (optional): Filter by specific field(s)
- `year` (optional): Filter by publication year

**Example Response:**
```json
{
  "query": "machine learning",
  "results": [
    {
      "paperId": "a1b2c3d4e5f6",
      "title": "Advances in Machine Learning: A 2023 Perspective",
      "abstract": "This paper provides an overview of recent advances...",
      "authors": [
        {
          "authorId": "123456789",
          "name": "Jane Smith"
        }
      ],
      "venue": "Journal of Machine Learning Research",
      "year": 2023,
      "url": "https://example.org/papers/advances-ml-2023"
    }
  ],
  "count": 1,
  "total": 15783,
  "next_offset": 1,
  "offset": 0
}
```

### 2. arXiv

Provides access to preprints from arXiv.org, a major repository of electronic preprints.

**Endpoint:** `/research/arxiv`

**Parameters:**
- `query` (required): The search term to look up
- `max_results` (optional): Maximum number of results to return (default: 10)
- `sort_by` (optional): Sorting criteria (default: "relevance")
- `sort_order` (optional): Sorting order (default: "descending")
- `category` (optional): Filter by arXiv category (e.g., "cs.AI", "physics.optics")

**Example Response:**
```json
{
  "query": "quantum computing",
  "results": [
    {
      "id": "2304.12345",
      "title": "Advances in Quantum Computing Algorithms",
      "summary": "This paper describes recent advances in quantum computing algorithms...",
      "authors": ["John Doe", "Jane Smith"],
      "published": "2023-04-15T12:00:00Z",
      "updated": "2023-04-20T12:00:00Z",
      "categories": ["quant-ph", "cs.ET"],
      "pdf_url": "https://arxiv.org/pdf/2304.12345.pdf"
    }
  ],
  "count": 1,
  "total_results": 5672
}
```

### 3. PubMed

Provides access to biomedical literature from MEDLINE, life science journals, and online books.

**Endpoint:** `/research/pubmed`

**Parameters:**
- `query` (required): The search term to look up
- `max_results` (optional): Maximum number of results to return (default: 10)
- `sort` (optional): Sort by relevance or publication date (default: "relevance")
- `date_range` (optional): Filter by date range (e.g., "2020/01/01:2023/01/01")
- `journal` (optional): Filter by journal name

**Example Response:**
```json
{
  "query": "covid vaccination",
  "results": [
    {
      "id": "34567890",
      "title": "Efficacy of COVID-19 Vaccination in High-Risk Populations",
      "abstract": "This study examines the efficacy of COVID-19 vaccination...",
      "authors": ["Robert Johnson", "Sarah Williams"],
      "journal": "The New England Journal of Medicine",
      "publication_date": "2022-06-15",
      "publication_types": ["Journal Article", "Research Support"],
      "pmid": "34567890",
      "source": "PubMed",
      "url": "https://pubmed.ncbi.nlm.nih.gov/34567890/"
    }
  ],
  "count": 1,
  "total": 12345
}
```

### 4. Google Scholar

Provides academic paper search capabilities through Google Scholar, implemented via Semantic Scholar as a proxy (since Google Scholar doesn't offer an official API).

**Endpoint:** `/research/google-scholar`

**Parameters:**
- `query` (required): The search term to look up
- `max_results` (optional): Maximum number of results to return (default: 10)

**Example Response:**
```json
{
  "query": "natural language processing",
  "results": [
    {
      "title": "Attention Is All You Need",
      "abstract": "This paper introduces the Transformer...",
      "authors": ["Ashish Vaswani", "Noam Shazeer", "Niki Parmar"],
      "venue": "Advances in Neural Information Processing Systems",
      "year": 2017,
      "citations": 45000,
      "influential_citations": 8500,
      "url": "https://example.org/papers/transformer",
      "source": "Google Scholar (via Semantic Scholar)"
    }
  ],
  "count": 1,
  "note": "Google Scholar results are approximated via Semantic Scholar as Google Scholar has no official API."
}
```

## Implementation Details

### Dependencies

The research module relies on the following external libraries:
- `requests`: For making HTTP requests to the various APIs
- `urllib.parse`: For URL encoding of query parameters
- `xml.etree.ElementTree`: For parsing XML responses (used by arXiv API)
- `lxml`: Used by the DuckDuckGo search library (required for Google Scholar functionality)

### Error Handling

All endpoints implement robust error handling for:
- Missing required parameters
- Invalid parameter values
- API connection errors
- Rate limiting
- Malformed responses

Errors are returned as JSON objects with descriptive messages and appropriate HTTP status codes.

## Usage Examples

### cURL Examples

#### Semantic Scholar (GET)
```bash
curl "http://localhost:8435/v2/research/semantic-scholar?query=machine%20learning&limit=3&year=2023"
```

#### Semantic Scholar (POST)
```bash
curl -X POST "http://localhost:8435/v2/research/semantic-scholar" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "machine learning",
    "limit": 3,
    "fields": "url,abstract,authors,title,venue,year",
    "fieldsOfStudy": "Computer Science",
    "year": "2023"
  }'
```

#### arXiv (GET)
```bash
curl "http://localhost:8435/v2/research/arxiv?query=quantum%20computing&max_results=2&category=quant-ph"
```

#### PubMed (POST)
```bash
curl -X POST "http://localhost:8435/v2/research/pubmed" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "covid vaccination",
    "max_results": 2,
    "sort": "relevance",
    "date_range": "2022/01/01:2023/01/01"
  }'
```

### Python Example

```python
import requests
import json

API_URL = "http://localhost:8435/v2"

def search_semantic_scholar(query, limit=10, year=None, fields=None):
    """
    Search academic papers using Semantic Scholar.
    
    Args:
        query: Search term
        limit: Maximum number of results to return
        year: Filter by publication year
        fields: Fields to include in response (comma-separated)
        
    Returns:
        Search results as a Python dictionary
    """
    params = {
        "query": query,
        "limit": limit
    }
    
    if year:
        params["year"] = year
        
    if fields:
        params["fields"] = fields
        
    response = requests.get(f"{API_URL}/research/semantic-scholar", params=params)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None

# Example usage
results = search_semantic_scholar("machine learning", limit=3, year=2023)
if results:
    print(f"Found {results['count']} results out of {results['total']} total matches")
    for i, paper in enumerate(results['results']):
        print(f"\n{i+1}. {paper['title']} ({paper.get('year', 'N/A')})")
        print(f"   Authors: {', '.join([a['name'] for a in paper.get('authors', [])])}")
        if 'abstract' in paper:
            print(f"   Abstract: {paper['abstract'][:200]}...")
        print(f"   URL: {paper.get('url', 'N/A')}")
```

## Future Enhancements

Planned future enhancements for the research endpoints include:

1. **Citation Graph Visualization**: Implement tools to visualize citation networks and relationships between papers
2. **Author-Focused Searches**: Add specialized endpoints for searching by author and exploring collaboration networks
3. **Full-Text Retrieval**: Add capabilities to retrieve and process full text where available
4. **Research Summarization**: Generate summaries of research papers and literature reviews on specific topics
5. **Integration with Dreamwalker**: Create specialized research workflows for comprehensive literature reviews

## Error Codes

Common error codes returned by the research endpoints:

| Status Code | Description                        | Common Causes                               |
|-------------|------------------------------------|---------------------------------------------|
| 400         | Bad Request                        | Missing required parameters, invalid values |
| 429         | Too Many Requests                  | Rate limit exceeded                         |
| 500         | Internal Server Error              | API connectivity issues, parsing errors     |
| 502         | Bad Gateway                        | Upstream API unavailable                    |
| 504         | Gateway Timeout                    | Timeout communicating with upstream API     | 