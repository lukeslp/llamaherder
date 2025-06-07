# Web Search Tools Documentation

## Overview

The Camina API provides a comprehensive suite of web search tools that enable you to search the web, extract content from websites, and process search results through a unified interface. These tools can be used for research, content aggregation, fact-checking, and data extraction.

## Available Search Tools

### 1. DuckDuckGo Search

DuckDuckGo search provides privacy-focused web search capabilities with minimal tracking. It's ideal for general web search queries.

**Key Features:**
- Privacy-focused search results
- Region-specific searching
- SafeSearch content filtering
- Time-limited results

### 2. SearXNG Search with Content Scraping

SearXNG is a meta search engine that combines results from multiple search engines while respecting user privacy. Our implementation adds content scraping to provide full-text content from the search results.

**Key Features:**
- Meta search engine aggregating multiple sources
- Content scraping for comprehensive results
- Website filtering to exclude unwanted sources
- Control over content length and detail

### 3. Website Content Scraper

Extract and format the content from any website URL. The scraper handles cleaning the content, removing unwanted elements, and providing both full content and a brief excerpt.

**Key Features:**
- Clean content extraction
- HTML filtering and text formatting
- Control over content length
- Error handling for sites that block scraping

### 4. Reader API

Access clean, readable content from any URL using the Reader API. This tool is ideal for extracting the main article content from news sites, blogs, and other content-heavy pages.

**Key Features:**
- Clean content extraction
- Removal of ads, navigation, and other distractions
- Focus on the main content
- Formatted for readability

### 5. Search Engine APIs

Access Google, Bing, and Baidu search results through a unified interface. These endpoints use the Reader API to access search results and provide them in a clean, readable format.

**Key Features:**
- Multiple search engines (Google, Bing, Baidu)
- Uniform interface across engines
- Content-focused results
- Readable format

## Common Use Cases

### Research and Fact-Checking

Combine multiple search tools to verify information across different sources:

1. Start with a DuckDuckGo search for initial results
2. Use SearXNG to get more comprehensive results from multiple engines
3. Use the Website Scraper to extract full content from the most relevant pages
4. Compare information across sources to verify facts

### Content Aggregation

Gather content from multiple sources on a specific topic:

1. Search for a topic using multiple search engines
2. Extract content from the most relevant pages
3. Combine and summarize the information
4. Generate a comprehensive overview of the topic

### Data Extraction

Extract structured data from websites:

1. Search for relevant websites using DuckDuckGo or SearXNG
2. Use the Website Scraper to extract content
3. Process the content to extract specific data points
4. Organize the data into a structured format

## Implementation Examples

### Python Example - Multi-Source Research

```python
import requests
import json

API_URL = "http://localhost:8435/v2"

def multi_source_research(query, max_results=3):
    """
    Conduct multi-source research on a topic
    
    Args:
        query: The research query
        max_results: Maximum number of results per source
        
    Returns:
        Combined research results
    """
    results = {
        "query": query,
        "sources": {}
    }
    
    # 1. Search with DuckDuckGo
    duckduckgo_response = requests.get(
        f"{API_URL}/web/duckduckgo",
        params={"query": query, "max_results": max_results}
    )
    
    if duckduckgo_response.status_code == 200:
        results["sources"]["duckduckgo"] = duckduckgo_response.json()
    
    # 2. Search with SearXNG
    searxng_response = requests.get(
        f"{API_URL}/web/searxng",
        params={"query": query, "max_results": max_results}
    )
    
    if searxng_response.status_code == 200:
        results["sources"]["searxng"] = searxng_response.json()
    
    # 3. Extract content from top results
    top_urls = []
    
    # Add DuckDuckGo URLs
    if "duckduckgo" in results["sources"]:
        for result in results["sources"]["duckduckgo"]["results"]:
            top_urls.append(result["href"])
    
    # Add SearXNG URLs
    if "searxng" in results["sources"]:
        for result in results["sources"]["searxng"]["results"]:
            if result["url"] not in top_urls:  # Avoid duplicates
                top_urls.append(result["url"])
    
    # Limit to top 3 unique URLs
    top_urls = top_urls[:3]
    
    # Extract content from each URL
    results["detailed_content"] = []
    
    for url in top_urls:
        reader_response = requests.get(
            f"{API_URL}/web/reader",
            params={"url": url}
        )
        
        if reader_response.status_code == 200:
            content = reader_response.json()
            results["detailed_content"].append({
                "url": url,
                "content": content
            })
    
    return results

# Example usage
research_results = multi_source_research("climate change solutions")
print(f"Found {len(research_results['sources'])} sources and {len(research_results['detailed_content'])} detailed content items")
```

### JavaScript Example - Website Content Extraction

```javascript
const API_URL = "http://localhost:8435/v2";

async function extractWebsiteContent(url, maxWords = 2000) {
  try {
    const response = await fetch(`${API_URL}/web/website?url=${encodeURIComponent(url)}&max_words=${maxWords}`);
    
    if (!response.ok) {
      throw new Error(`Error: ${response.status} - ${await response.text()}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error("Extraction error:", error);
    return { error: error.message };
  }
}

// Example usage
async function displayWebsiteContent() {
  const url = "https://example.com";
  const result = await extractWebsiteContent(url);
  
  if (result.error) {
    console.error(`Failed to extract content: ${result.error}`);
    return;
  }
  
  console.log(`Title: ${result.result.title}`);
  console.log(`Excerpt: ${result.result.excerpt}`);
  console.log(`Content length: ${result.result.content.length} characters`);
  
  // Display the content in a div
  document.getElementById('content').innerHTML = `
    <h1>${result.result.title}</h1>
    <p><em>Source: <a href="${result.result.url}" target="_blank">${result.result.url}</a></em></p>
    <div class="excerpt">
      <strong>Excerpt:</strong> ${result.result.excerpt}
    </div>
    <div class="content">
      ${result.result.content}
    </div>
  `;
}
```

## Combining with Other API Features

### Combining with Academic Research

Use web search tools alongside academic research tools for comprehensive research:

```python
# Search both web and academic sources
web_results = requests.get(
    f"{API_URL}/web/duckduckgo",
    params={"query": "machine learning applications", "max_results": 5}
).json()

academic_results = requests.get(
    f"{API_URL}/research/semantic-scholar",
    params={"query": "machine learning applications", "limit": 5}
).json()

# Combine results for a comprehensive view
combined_results = {
    "query": "machine learning applications",
    "web_sources": web_results["results"],
    "academic_sources": academic_results["results"]
}
```

### Combining with AI Chat

Use web search to provide up-to-date information for AI chat applications:

```python
# Get web content first
search_results = requests.get(
    f"{API_URL}/web/duckduckgo",
    params={"query": "latest AI advancements", "max_results": 3}
).json()

# Format search results as context
context = "Here's some recent information about AI advancements:\n\n"
for result in search_results["results"]:
    context += f"- {result['title']}: {result['body']}\n"
context += "\nPlease use this information in your response."

# Send to AI chat endpoint with the search results as context
chat_response = requests.post(
    f"{API_URL}/chat/completions",
    json={
        "provider": "anthropic",
        "model": "claude-3-opus-20240229",
        "prompt": f"{context}\n\nWhat are the most significant recent advancements in AI?"
    }
).json()
```

## Best Practices

1. **Rate Limiting**: Respect the rate limits of the underlying search engines and APIs
2. **Content Caching**: Cache search results and extracted content to reduce redundant requests
3. **Error Handling**: Implement robust error handling for scraping failures and API errors
4. **Fallback Sources**: Use multiple search engines and fallback to alternatives when one fails
5. **Content Validation**: Validate and clean extracted content before processing
6. **Respect Websites**: Avoid aggressive scraping that could burden websites or violate their terms of service

## Performance Considerations

- SearXNG with content scraping is slower than standard search due to the additional scraping step
- The Reader API depends on third-party service availability
- Website scraping may encounter rate limiting or blocking from certain websites
- Consider implementing request queuing for multiple simultaneous searches or scraping operations

## Future Enhancements

Planned future enhancements for the web search tools include:

1. **Image Search**: Add image search capabilities
2. **News Search**: Add specialized news search endpoints
3. **Custom Site Search**: Add the ability to search within specific websites
4. **Advanced Content Analysis**: Add tools for sentiment analysis, entity extraction, and summarization of web content
5. **Integration with Dreamwalker**: Create specialized web research workflows

## Support

For issues, feature requests, or questions about the web search tools, please contact:
- Email: api@assisted.space
- GitHub: [Submit an issue](https://github.com/coolhand/camina-chat/issues) 