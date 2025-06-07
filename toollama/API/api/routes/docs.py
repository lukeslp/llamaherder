from flask import Blueprint, jsonify, send_from_directory, current_app
from flask_cors import cross_origin
from flask_swagger_ui import get_swaggerui_blueprint
import os
import json
from ruamel.yaml import YAML

# Create a blueprint for docs
docs_bp = Blueprint('docs', __name__)

# Define Swagger UI blueprint
SWAGGER_URL = '/docs'  # URL for exposing Swagger UI
API_URL = '/static/swagger/swagger.json'  # Where to find the Swagger definition

# Register Swagger UI blueprint
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Camina Chat API Documentation"
    }
)

@docs_bp.route('/swagger.json')
def swagger_json():
    """Serve the Swagger JSON file."""
    swagger_path = os.path.join(current_app.root_path, 'static', 'swagger', 'swagger.yaml')
    yaml = YAML(typ='safe')
    with open(swagger_path, 'r') as file:
        swagger_data = yaml.load(file)
    return jsonify(swagger_data)

@docs_bp.route('/')
def docs_index():
    """Redirect to the Swagger UI."""
    return current_app.send_static_file('swagger/index.html')

@docs_bp.route('/dreamwalker')
@cross_origin()
def dreamwalker_docs():
    """Serve the Dreamwalker documentation."""
    return jsonify({
        "title": "Dreamwalker Framework",
        "description": "Advanced multi-step AI workflows for complex tasks",
        "version": "1.0.0",
        "workflows": [
            {
                "name": "SwarmDreamwalker",
                "description": "Query expansion and parallel search workflow",
                "endpoints": [
                    {
                        "path": "/dreamwalker/search",
                        "method": "POST",
                        "description": "Start a new search workflow",
                        "parameters": [
                            {
                                "name": "query",
                                "type": "string",
                                "description": "The query to process",
                                "required": True
                            },
                            {
                                "name": "workflow_type",
                                "type": "string",
                                "description": "Type of workflow to execute",
                                "default": "swarm",
                                "required": False
                            },
                            {
                                "name": "model",
                                "type": "string",
                                "description": "Model to use for the workflow",
                                "default": "coolhand/camina-search:24b",
                                "required": False
                            }
                        ]
                    },
                    {
                        "path": "/dreamwalker/status/{workflow_id}",
                        "method": "GET",
                        "description": "Get the status of a workflow",
                        "parameters": [
                            {
                                "name": "workflow_id",
                                "type": "string",
                                "description": "Unique identifier for the workflow",
                                "required": True
                            }
                        ]
                    },
                    {
                        "path": "/dreamwalker/result/{workflow_id}",
                        "method": "GET",
                        "description": "Get the result of a completed workflow",
                        "parameters": [
                            {
                                "name": "workflow_id",
                                "type": "string",
                                "description": "Unique identifier for the workflow",
                                "required": True
                            }
                        ]
                    },
                    {
                        "path": "/dreamwalker/cancel/{workflow_id}",
                        "method": "DELETE",
                        "description": "Cancel a running workflow",
                        "parameters": [
                            {
                                "name": "workflow_id",
                                "type": "string",
                                "description": "Unique identifier for the workflow",
                                "required": True
                            }
                        ]
                    },
                    {
                        "path": "/dreamwalker/list",
                        "method": "GET",
                        "description": "List active workflows",
                        "parameters": [
                            {
                                "name": "status",
                                "type": "string",
                                "description": "Filter workflows by status",
                                "required": False
                            },
                            {
                                "name": "limit",
                                "type": "integer",
                                "description": "Maximum number of workflows to return",
                                "default": 10,
                                "required": False
                            }
                        ]
                    },
                    {
                        "path": "/dreamwalker/cleanup",
                        "method": "DELETE",
                        "description": "Clean up old workflows",
                        "parameters": [
                            {
                                "name": "status",
                                "type": "string",
                                "description": "Status of workflows to clean up",
                                "default": "completed",
                                "required": False
                            },
                            {
                                "name": "age_hours",
                                "type": "integer",
                                "description": "Age in hours of workflows to clean up",
                                "default": 24,
                                "required": False
                            }
                        ]
                    }
                ]
            }
        ]
    })

@docs_bp.route('/research')
@cross_origin()
def research_docs():
    """Serve the Research Search documentation."""
    return jsonify({
        "title": "Academic Research API",
        "description": "Search academic papers and research across multiple scholarly databases",
        "version": "1.0.0",
        "status": {
            "semantic_scholar": {
                "status": "active",
                "features": ["paper search", "citation data", "author information"],
                "implementation_date": "February 2025"
            },
            "arxiv": {
                "status": "active",
                "features": ["preprint search", "PDF access", "category filtering"],
                "implementation_date": "February 2025"
            },
            "pubmed": {
                "status": "active",
                "features": ["medical literature", "journal filtering", "date ranges"],
                "implementation_date": "February 2025"
            },
            "google_scholar": {
                "status": "active",
                "features": ["academic search", "citation counts"],
                "implementation_date": "February 2025",
                "notes": "Implemented via Semantic Scholar as a proxy since Google Scholar has no official API"
            }
        },
        "endpoints": [
            {
                "path": "/research/semantic-scholar",
                "method": "GET/POST",
                "description": "Search academic papers using Semantic Scholar",
                "parameters": [
                    {
                        "name": "query",
                        "type": "string",
                        "description": "The search term to look up",
                        "required": True
                    },
                    {
                        "name": "limit",
                        "type": "integer",
                        "description": "Maximum number of results to return",
                        "default": 10,
                        "required": False
                    },
                    {
                        "name": "fields",
                        "type": "string",
                        "description": "Fields to include in response (comma-separated)",
                        "default": "url,abstract,authors,title,venue,year,publicationTypes,tldr",
                        "required": False
                    },
                    {
                        "name": "fieldsOfStudy",
                        "type": "string",
                        "description": "Filter by specific field(s)",
                        "required": False
                    },
                    {
                        "name": "year",
                        "type": "string",
                        "description": "Filter by publication year",
                        "required": False
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Successful search result",
                        "content_type": "application/json"
                    },
                    "400": {
                        "description": "Bad request - missing or invalid parameters",
                        "content_type": "application/json"
                    },
                    "500": {
                        "description": "Internal server error or API error",
                        "content_type": "application/json"
                    }
                }
            },
            {
                "path": "/research/arxiv",
                "method": "GET/POST",
                "description": "Search academic papers on arXiv",
                "parameters": [
                    {
                        "name": "query",
                        "type": "string",
                        "description": "The search term to look up",
                        "required": True
                    },
                    {
                        "name": "max_results",
                        "type": "integer",
                        "description": "Maximum number of results to return",
                        "default": 10,
                        "required": False
                    },
                    {
                        "name": "sort_by",
                        "type": "string",
                        "description": "Sorting criteria",
                        "default": "relevance",
                        "required": False
                    },
                    {
                        "name": "sort_order",
                        "type": "string",
                        "description": "Sorting order",
                        "default": "descending",
                        "required": False
                    },
                    {
                        "name": "category",
                        "type": "string",
                        "description": "Filter by arXiv category",
                        "required": False
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Successful search result",
                        "content_type": "application/json"
                    },
                    "400": {
                        "description": "Bad request - missing or invalid parameters",
                        "content_type": "application/json"
                    },
                    "500": {
                        "description": "Internal server error or API error",
                        "content_type": "application/json"
                    }
                }
            },
            {
                "path": "/research/pubmed",
                "method": "GET/POST",
                "description": "Search medical literature on PubMed",
                "parameters": [
                    {
                        "name": "query",
                        "type": "string",
                        "description": "The search term to look up",
                        "required": True
                    },
                    {
                        "name": "max_results",
                        "type": "integer",
                        "description": "Maximum number of results to return",
                        "default": 10,
                        "required": False
                    },
                    {
                        "name": "sort",
                        "type": "string",
                        "description": "Sort by relevance or publication date",
                        "default": "relevance",
                        "required": False
                    },
                    {
                        "name": "date_range",
                        "type": "string",
                        "description": "Filter by date range (e.g., '2020/01/01:2023/01/01')",
                        "required": False
                    },
                    {
                        "name": "journal",
                        "type": "string",
                        "description": "Filter by journal name",
                        "required": False
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Successful search result",
                        "content_type": "application/json"
                    },
                    "400": {
                        "description": "Bad request - missing or invalid parameters",
                        "content_type": "application/json"
                    },
                    "500": {
                        "description": "Internal server error or API error",
                        "content_type": "application/json"
                    }
                }
            },
            {
                "path": "/research/google-scholar",
                "method": "GET/POST",
                "description": "Search academic papers using Google Scholar (via Semantic Scholar)",
                "parameters": [
                    {
                        "name": "query",
                        "type": "string",
                        "description": "The search term to look up",
                        "required": True
                    },
                    {
                        "name": "max_results",
                        "type": "integer",
                        "description": "Maximum number of results to return",
                        "default": 10,
                        "required": False
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Successful search result",
                        "content_type": "application/json"
                    },
                    "400": {
                        "description": "Bad request - missing or invalid parameters",
                        "content_type": "application/json"
                    },
                    "500": {
                        "description": "Internal server error or API error",
                        "content_type": "application/json"
                    }
                },
                "notes": [
                    "This endpoint uses Semantic Scholar as a proxy since Google Scholar doesn't provide an official API"
                ]
            }
        ]
    })

@docs_bp.route('/web')
@cross_origin()
def web_docs():
    """Serve the Web Search documentation."""
    return jsonify({
        "title": "Web Search API",
        "description": "Search the web using various search engines",
        "version": "1.0.0",
        "status": {
            "duckduckgo": {
                "status": "active",
                "features": ["web search", "instant answers"],
                "implementation_date": "February 2025"
            },
            "searxng": {
                "status": "active",
                "features": ["meta search", "content scraping"],
                "implementation_date": "March 2025"
            },
            "website": {
                "status": "active",
                "features": ["content extraction", "text formatting"],
                "implementation_date": "March 2025"
            },
            "reader": {
                "status": "active",
                "features": ["clean content extraction"],
                "implementation_date": "March 2025"
            },
            "search_engines": {
                "status": "active",
                "features": ["google", "bing", "baidu"],
                "implementation_date": "March 2025"
            },
            "google": {
                "status": "planned",
                "features": ["web search", "news search", "custom site search"],
                "planned_date": "Q3 2025"
            },
            "bing": {
                "status": "planned",
                "features": ["web search", "image search", "video search"],
                "planned_date": "Q4 2025"
            }
        },
        "endpoints": [
            {
                "name": "DuckDuckGo Search",
                "route": "/web/duckduckgo",
                "methods": ["GET", "POST", "OPTIONS"],
                "description": "Search the web using DuckDuckGo Search",
                "parameters": [
                    {
                        "name": "query",
                        "required": True,
                        "description": "The search term to look up",
                        "type": "string"
                    },
                    {
                        "name": "region",
                        "required": False,
                        "description": "Region for the search (e.g., 'us-en')",
                        "type": "string",
                        "default": "wt-wt"
                    },
                    {
                        "name": "safesearch",
                        "required": False,
                        "description": "SafeSearch setting ('on', 'moderate', 'off')",
                        "type": "string",
                        "default": "moderate"
                    },
                    {
                        "name": "timelimit",
                        "required": False,
                        "description": "Time limit for results ('d', 'w', 'm', 'y' for day, week, month, year)",
                        "type": "string",
                        "default": None
                    },
                    {
                        "name": "max_results",
                        "required": False,
                        "description": "Maximum number of results to return",
                        "type": "integer",
                        "default": 10
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Successful search result",
                        "content_type": "application/json",
                        "schema": {
                            "type": "object",
                            "properties": {
                                "count": {
                                    "type": "integer",
                                    "description": "Number of results returned"
                                },
                                "query": {
                                    "type": "string",
                                    "description": "The original search query"
                                },
                                "results": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "title": {
                                                "type": "string",
                                                "description": "Title of the search result"
                                            },
                                            "href": {
                                                "type": "string",
                                                "description": "URL of the search result"
                                            },
                                            "body": {
                                                "type": "string",
                                                "description": "Snippet or description of the search result"
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    },
                    "400": {
                        "description": "Bad request - missing or invalid parameters",
                        "content_type": "application/json"
                    },
                    "500": {
                        "description": "Internal server error",
                        "content_type": "application/json"
                    }
                },
                "example_request": {
                    "query": "accessibility design",
                    "max_results": 3,
                    "region": "us-en",
                    "safesearch": "moderate"
                },
                "example_response": {
                    "count": 3,
                    "query": "accessibility design",
                    "results": [
                        {
                            "title": "Designing for Web Accessibility - Tips for Getting Started",
                            "href": "https://www.w3.org/WAI/tips/designing/",
                            "body": "These tips introduce some basic considerations to help you get started with accessible web design."
                        },
                        {
                            "title": "Web Accessibility Guidelines and Standards",
                            "href": "https://www.example.com/accessibility",
                            "body": "Sample description for accessibility standards and guidelines."
                        },
                        {
                            "title": "Accessible Design Principles",
                            "href": "https://www.example.com/design-principles",
                            "body": "Sample principles for creating accessible designs."
                        }
                    ]
                },
                "notes": [
                    "The DuckDuckGo search API has rate limits which may cause 429 errors if exceeded",
                    "SafeSearch settings control content filtering (on, moderate, off)",
                    "Region settings affect localization of search results"
                ]
            },
            {
                "name": "SearXNG Search",
                "route": "/web/searxng",
                "methods": ["GET", "POST", "OPTIONS"],
                "description": "Search the web using SearXNG meta search engine and scrape the first N pages of results",
                "parameters": [
                    {
                        "name": "query",
                        "required": True,
                        "description": "The search term to look up",
                        "type": "string"
                    },
                    {
                        "name": "max_results",
                        "required": False,
                        "description": "Maximum number of results to return",
                        "type": "integer",
                        "default": 3
                    },
                    {
                        "name": "api_url",
                        "required": False,
                        "description": "SearXNG API URL",
                        "type": "string",
                        "default": "https://paulgo.io/search"
                    },
                    {
                        "name": "ignored_websites",
                        "required": False,
                        "description": "Comma-separated list of websites to ignore",
                        "type": "string",
                        "default": ""
                    },
                    {
                        "name": "max_words_per_page",
                        "required": False,
                        "description": "Maximum number of words to include per page",
                        "type": "integer",
                        "default": 5000
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Successful search result",
                        "content_type": "application/json",
                        "schema": {
                            "type": "object",
                            "properties": {
                                "count": {
                                    "type": "integer",
                                    "description": "Number of results returned"
                                },
                                "query": {
                                    "type": "string",
                                    "description": "The original search query"
                                },
                                "results": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "title": {
                                                "type": "string",
                                                "description": "Title of the search result"
                                            },
                                            "url": {
                                                "type": "string",
                                                "description": "URL of the search result"
                                            },
                                            "content": {
                                                "type": "string",
                                                "description": "Extracted and formatted content from the page"
                                            },
                                            "snippet": {
                                                "type": "string",
                                                "description": "Brief excerpt or summary of the content"
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    },
                    "400": {
                        "description": "Bad request - missing or invalid parameters",
                        "content_type": "application/json"
                    },
                    "502": {
                        "description": "Bad gateway - search engine request failed",
                        "content_type": "application/json"
                    },
                    "500": {
                        "description": "Internal server error",
                        "content_type": "application/json"
                    }
                },
                "example_request": {
                    "query": "machine learning",
                    "max_results": 2,
                    "ignored_websites": "wikipedia.org,youtube.com"
                },
                "example_response": {
                    "count": 2,
                    "query": "machine learning",
                    "results": [
                        {
                            "title": "What is Machine Learning? | IBM",
                            "url": "https://www.ibm.com/topics/machine-learning",
                            "content": "Machine learning is a branch of artificial intelligence (AI) and computer science...",
                            "snippet": "Machine learning is a branch of artificial intelligence..."
                        },
                        {
                            "title": "Machine Learning | Stanford Online",
                            "url": "https://online.stanford.edu/courses/machine-learning",
                            "content": "This course provides a broad introduction to machine learning...",
                            "snippet": "This course provides a broad introduction to machine learning..."
                        }
                    ]
                },
                "notes": [
                    "This endpoint combines search with content scraping for more comprehensive results",
                    "Results may take longer to return than standard search APIs due to scraping",
                    "Some websites may block scraping attempts, resulting in fewer actual results"
                ]
            },
            {
                "name": "Website Scraper",
                "route": "/web/website",
                "methods": ["GET", "POST", "OPTIONS"],
                "description": "Scrape content from a specified website URL",
                "parameters": [
                    {
                        "name": "url",
                        "required": True,
                        "description": "The URL of the website to scrape",
                        "type": "string"
                    },
                    {
                        "name": "max_words",
                        "required": False,
                        "description": "Maximum number of words to include",
                        "type": "integer",
                        "default": 5000
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Successfully scraped website content",
                        "content_type": "application/json",
                        "schema": {
                            "type": "object",
                            "properties": {
                                "url": {
                                    "type": "string",
                                    "description": "The URL that was scraped"
                                },
                                "result": {
                                    "type": "object",
                                    "properties": {
                                        "title": {
                                            "type": "string",
                                            "description": "Title of the webpage"
                                        },
                                        "url": {
                                            "type": "string",
                                            "description": "URL of the webpage"
                                        },
                                        "content": {
                                            "type": "string",
                                            "description": "Extracted and formatted content from the page"
                                        },
                                        "excerpt": {
                                            "type": "string",
                                            "description": "Brief excerpt from the content"
                                        }
                                    }
                                }
                            }
                        }
                    },
                    "400": {
                        "description": "Bad request - missing or invalid parameters",
                        "content_type": "application/json"
                    },
                    "502": {
                        "description": "Bad gateway - website request failed",
                        "content_type": "application/json"
                    },
                    "500": {
                        "description": "Internal server error",
                        "content_type": "application/json"
                    }
                },
                "example_request": {
                    "url": "https://example.com",
                    "max_words": 1000
                },
                "example_response": {
                    "url": "https://example.com",
                    "result": {
                        "title": "Example Domain",
                        "url": "https://example.com",
                        "content": "This domain is for use in illustrative examples in documents...",
                        "excerpt": "This domain is for use in illustrative examples in documents..."
                    }
                },
                "notes": [
                    "Some websites may block scraping attempts, resulting in errors",
                    "Content is cleaned and formatted to remove unnecessary elements",
                    "Large pages may be truncated based on the max_words parameter"
                ]
            },
            {
                "name": "Reader API",
                "route": "/web/reader",
                "methods": ["GET", "POST", "OPTIONS"],
                "description": "Use the Reader API to extract content from a URL in readable format",
                "parameters": [
                    {
                        "name": "url",
                        "required": True,
                        "description": "The URL to read from",
                        "type": "string"
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Successfully extracted content",
                        "content_type": "application/json",
                        "schema": {
                            "type": "object",
                            "properties": {
                                "url": {
                                    "type": "string",
                                    "description": "The URL that was read"
                                },
                                "title": {
                                    "type": "string",
                                    "description": "Title derived from the URL"
                                },
                                "content": {
                                    "type": "string",
                                    "description": "Extracted content in clean, readable format"
                                }
                            }
                        }
                    },
                    "400": {
                        "description": "Bad request - missing or invalid parameters",
                        "content_type": "application/json"
                    },
                    "502": {
                        "description": "Bad gateway - Reader API request failed",
                        "content_type": "application/json"
                    },
                    "500": {
                        "description": "Internal server error",
                        "content_type": "application/json"
                    }
                },
                "example_request": {
                    "url": "https://news.ycombinator.com"
                },
                "example_response": {
                    "url": "https://news.ycombinator.com",
                    "title": "Content from news.ycombinator.com",
                    "content": "Hacker News new | past | comments | ask | show | jobs | submit..."
                },
                "notes": [
                    "Uses a third-party Reader API (r.jina.ai) to extract clean, readable content",
                    "Focuses on the main content and removes ads, navigation, etc.",
                    "Performance depends on the third-party API's availability"
                ]
            },
            {
                "name": "Search Engine APIs",
                "route": "/web/search/<engine>",
                "methods": ["GET", "POST", "OPTIONS"],
                "description": "Perform a search using various search engines through the Reader API",
                "parameters": [
                    {
                        "name": "engine",
                        "required": True,
                        "description": "Search engine to use ('google', 'bing', or 'baidu')",
                        "type": "string",
                        "in": "path"
                    },
                    {
                        "name": "query",
                        "required": True,
                        "description": "The search term to look up",
                        "type": "string"
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Successful search result",
                        "content_type": "application/json",
                        "schema": {
                            "type": "object",
                            "properties": {
                                "engine": {
                                    "type": "string",
                                    "description": "The search engine used"
                                },
                                "query": {
                                    "type": "string",
                                    "description": "The original search query"
                                },
                                "content": {
                                    "type": "string",
                                    "description": "Extracted search results in a readable format"
                                }
                            }
                        }
                    },
                    "400": {
                        "description": "Bad request - missing or invalid parameters",
                        "content_type": "application/json"
                    },
                    "502": {
                        "description": "Bad gateway - search engine request failed",
                        "content_type": "application/json"
                    },
                    "500": {
                        "description": "Internal server error",
                        "content_type": "application/json"
                    }
                },
                "example_request": {
                    "query": "artificial intelligence news"
                },
                "example_response": {
                    "engine": "google",
                    "query": "artificial intelligence news",
                    "content": "[Extracted search results from Google in a readable format]..."
                },
                "notes": [
                    "Uses a third-party Reader API to access search engines indirectly",
                    "Content is returned in a clean, readable format rather than structured JSON",
                    "Performance depends on the third-party API's availability"
                ]
            }
        ]
    })

def register_docs_routes(app):
    """Register the docs blueprint with the Flask app."""
    # Register the Swagger UI blueprint
    app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)
    
    # Register the docs blueprint for additional endpoints
    app.register_blueprint(docs_bp, url_prefix='/api/docs')
    
    # Ensure the static/swagger directory exists
    swagger_dir = os.path.join(app.root_path, 'static', 'swagger')
    os.makedirs(swagger_dir, exist_ok=True) 