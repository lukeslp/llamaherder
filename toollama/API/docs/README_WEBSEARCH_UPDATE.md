# Web Search Updates - March 2025

## Overview

The Camina API has been enhanced with several new web search capabilities that complement the existing DuckDuckGo search endpoint. These new endpoints provide a comprehensive suite of tools for web search, content extraction, and page processing.

## New Endpoints

### 1. SearXNG Search (`/web/searxng`)

A meta search engine implementation that combines results from multiple search engines while respecting user privacy, with the added benefit of content scraping. This endpoint not only returns search results but also extracts and cleans the full content from each page.

**Key Features:**
- Aggregates results from multiple search engines
- Extracts and cleans full page content
- Website filtering to exclude unwanted sources
- Control over content length and formatting

### 2. Website Scraper (`/web/website`)

A dedicated endpoint for extracting content from any website. Simply provide a URL and get clean, formatted content back.

**Key Features:**
- Clean content extraction with HTML filtering
- Consistent text formatting
- Customizable word limits
- Brief excerpts for previews

### 3. Reader API (`/web/reader`)

An endpoint that uses the [Reader API](https://r.jina.ai/) to extract content in a clean, readable format. Ideal for news articles, blog posts, and other text-heavy content.

**Key Features:**
- Focused on main content extraction
- Removes ads, navigation, and other distractions
- Cleans and formats text for readability
- Simple URL-to-content conversion

### 4. Search Engine APIs (`/web/search/{engine}`)

A family of endpoints for accessing popular search engines (Google, Bing, Baidu) through a unified interface. These endpoints use the Reader API to extract search results in a clean, readable format.

**Key Features:**
- Support for multiple search engines
- Consistent interface across engines
- Content-focused results
- Clean, readable format

## Use Cases

### Research and Fact-Checking

The new search endpoints are ideal for research and fact-checking:

1. Start with a DuckDuckGo search for initial results
2. Use SearXNG for more comprehensive results from multiple engines
3. Extract full content from the most relevant pages
4. Compare information across sources to verify facts

### Content Aggregation

Create content aggregation applications that gather information from multiple sources:

1. Search for a topic using multiple engines
2. Extract clean content from each result
3. Process and combine the information
4. Present a comprehensive view of the topic

### Data Extraction

Build systems that extract structured data from websites:

1. Search for relevant websites
2. Extract content using the Website Scraper
3. Parse and process the content to extract data points
4. Organize into structured datasets

## Example: Multi-Source Research

```python
import requests

API_URL = "http://localhost:8435/v2"

def research_topic(query, max_results=3):
    """
    Comprehensive research using multiple search methods
    """
    # Search with DuckDuckGo for general web results
    ddg_results = requests.get(
        f"{API_URL}/web/duckduckgo",
        params={"query": query, "max_results": max_results}
    ).json()
    
    # Search with SearXNG for more detailed content
    searxng_results = requests.get(
        f"{API_URL}/web/searxng",
        params={"query": query, "max_results": max_results}
    ).json()
    
    # Get additional focused results from Google
    google_results = requests.get(
        f"{API_URL}/web/search/google",
        params={"query": query}
    ).json()
    
    # Process and combine results
    combined_info = {
        "query": query,
        "sources": {
            "duckduckgo": ddg_results,
            "searxng": searxng_results,
            "google": google_results
        },
        "summary": f"Research results for '{query}' from multiple engines"
    }
    
    return combined_info

# Example usage
results = research_topic("renewable energy technologies")
```

## Documentation

Comprehensive documentation for all web search endpoints is available in:

1. **API_DOCUMENTATION.md**: Detailed endpoint documentation with parameters and examples
2. **Swagger UI**: Interactive documentation accessible through `/v2/docs`
3. **README_WEB_SEARCH.md**: Comprehensive guide to using web search capabilities

## Future Enhancements

Planned future enhancements for the web search tools include:

1. **Image Search**: Add image search capabilities across multiple engines
2. **News Search**: Add specialized news search endpoints
3. **Custom Site Search**: Add the ability to search within specific websites
4. **Advanced Content Analysis**: Add tools for sentiment analysis, entity extraction, and summarization
5. **Integration with Dreamwalker**: Create specialized web research workflows 