#!/usr/bin/env python
from flask import request, jsonify
import requests
import logging
import os
from typing import Dict, List, Any, Optional

from api.routes.news import news_bp
from api.config.api_keys import ADDITIONAL_API_KEYS

# Logger for this module
logger = logging.getLogger(__name__)

# Configuration for API keys
API_KEYS = {
    'nyt': ADDITIONAL_API_KEYS.get('nyt', os.environ.get('NYT_API_KEY', ''))
}

@news_bp.route('/nyt/search', methods=['GET', 'POST'])
def search_nyt_articles():
    """
    Search for New York Times articles.
    
    Required parameters:
    - query: The search query
    
    Optional parameters:
    - api_key: The NYT API key (if not provided, uses environment variable)
    - page: The page number for paginated results (default: 0)
    - sort: Sort order (newest, oldest, relevance - default: newest)
    - begin_date: Filter by begin date (YYYYMMDD format)
    - end_date: Filter by end date (YYYYMMDD format)
    - filter_query: Filter query using NYT search syntax
    """
    # Get parameters from either URL query or JSON body
    if request.method == 'POST':
        data = request.json or {}
    else:
        data = request.args.to_dict()
    
    # Get required parameters
    query = data.get('query')
    
    if not query:
        return jsonify({"error": "Query parameter is required"}), 400
    
    # Get optional parameters
    api_key = data.get('api_key', API_KEYS['nyt'])
    page = int(data.get('page', 0))
    sort = data.get('sort', 'newest')
    begin_date = data.get('begin_date')
    end_date = data.get('end_date')
    filter_query = data.get('filter_query')
    
    if not api_key:
        return jsonify({"error": "NYT API key is required. Please provide it via api_key parameter or set the NYT_API_KEY environment variable."}), 400
    
    # Validate parameters
    if sort not in ['newest', 'oldest', 'relevance']:
        return jsonify({"error": "Sort must be one of: newest, oldest, relevance"}), 400
        
    if page < 0 or page > 100:
        return jsonify({"error": "Page must be between 0 and 100"}), 400
    
    # Construct the request parameters
    params = {
        "q": query,
        "api-key": api_key,
        "sort": sort,
        "page": page
    }
    
    # Add optional filters if provided
    if begin_date:
        params["begin_date"] = begin_date
        
    if end_date:
        params["end_date"] = end_date
        
    if filter_query:
        params["fq"] = filter_query
    
    # Make the request to NYT API
    try:
        url = "https://api.nytimes.com/svc/search/v2/articlesearch.json"
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        # Parse the response
        data = response.json()
        articles = data.get("response", {}).get("docs", [])
        
        # Extract relevant information
        formatted_articles = []
        for article in articles:
            # Extract headline
            headline = article.get("headline", {}).get("main", "No Title")
            
            # Extract snippet
            snippet = article.get("snippet", "")
            
            # Extract publication date
            pub_date = article.get("pub_date", "Unknown Date")
            
            # Extract URL
            url = article.get("web_url", "")
            
            # Extract author
            byline = article.get("byline", {}).get("original", "")
            
            # Extract section and type
            section = article.get("section_name", "")
            doc_type = article.get("document_type", "")
            
            # Extract keywords
            keywords = []
            for keyword in article.get("keywords", []):
                keywords.append({
                    "name": keyword.get("name", ""),
                    "value": keyword.get("value", "")
                })
            
            # Extract multimedia (images)
            multimedia = []
            for media in article.get("multimedia", []):
                if media.get("type") == "image":
                    multimedia.append({
                        "url": f"https://www.nytimes.com/{media.get('url')}",
                        "type": media.get("type", ""),
                        "width": media.get("width", 0),
                        "height": media.get("height", 0),
                        "caption": media.get("caption", "")
                    })
            
            formatted_articles.append({
                "title": headline,
                "snippet": snippet,
                "url": url,
                "published_at": pub_date,
                "byline": byline,
                "section": section,
                "type": doc_type,
                "keywords": keywords,
                "multimedia": multimedia
            })
        
        # Get metadata
        meta = data.get("response", {}).get("meta", {})
        hits = meta.get("hits", 0)
        offset = meta.get("offset", 0)
        
        return jsonify({
            "success": True,
            "query": query,
            "page": page,
            "total_hits": hits,
            "offset": offset,
            "count": len(formatted_articles),
            "articles": formatted_articles
        })
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Error searching NYT articles: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e),
            "query": query
        }), 500

@news_bp.route('/nyt/top', methods=['GET', 'POST'])
def get_nyt_top_stories():
    """
    Get the top stories from the New York Times.
    
    Optional parameters:
    - api_key: The NYT API key (if not provided, uses environment variable)
    - section: The section to retrieve (home, world, science, etc. - default: home)
    """
    # Get parameters from either URL query or JSON body
    if request.method == 'POST':
        data = request.json or {}
    else:
        data = request.args.to_dict()
    
    # Get optional parameters
    api_key = data.get('api_key', API_KEYS['nyt'])
    section = data.get('section', 'home')
    
    if not api_key:
        return jsonify({"error": "NYT API key is required. Please provide it via api_key parameter or set the NYT_API_KEY environment variable."}), 400
    
    # Valid sections
    valid_sections = [
        'arts', 'automobiles', 'books', 'business', 'fashion', 'food',
        'health', 'home', 'insider', 'magazine', 'movies', 'nyregion',
        'obituaries', 'opinion', 'politics', 'realestate', 'science',
        'sports', 'sundayreview', 'technology', 'theater', 'travel',
        'upshot', 'us', 'world'
    ]
    
    # Validate section
    if section not in valid_sections:
        return jsonify({
            "success": False,
            "error": f"Invalid section: {section}. Valid sections are: {', '.join(valid_sections)}"
        }), 400
    
    # Make the request to NYT API
    try:
        url = f"https://api.nytimes.com/svc/topstories/v2/{section}.json"
        params = {"api-key": api_key}
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        # Parse the response
        data = response.json()
        articles = data.get("results", [])
        
        # Extract relevant information
        formatted_articles = []
        for article in articles:
            # Extract title
            title = article.get("title", "No Title")
            
            # Extract abstract
            abstract = article.get("abstract", "")
            
            # Extract publication date
            pub_date = article.get("published_date", "Unknown Date")
            
            # Extract URL
            url = article.get("url", "")
            
            # Extract section and subsection
            section = article.get("section", "")
            subsection = article.get("subsection", "")
            
            # Extract byline
            byline = article.get("byline", "")
            
            # Extract thumbnail
            thumbnail = None
            for media in article.get("multimedia", []):
                if media.get("format") == "thumbLarge":
                    thumbnail = media.get("url", "")
                    break
            
            formatted_articles.append({
                "title": title,
                "abstract": abstract,
                "url": url,
                "published_at": pub_date,
                "byline": byline,
                "section": section,
                "subsection": subsection,
                "thumbnail": thumbnail
            })
        
        return jsonify({
            "success": True,
            "section": section,
            "count": len(formatted_articles),
            "articles": formatted_articles
        })
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching NYT top stories: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e),
            "section": section
        }), 500

@news_bp.route('/nyt/schema/search', methods=['GET'])
def get_nyt_search_schema():
    """Get the JSON schema for the NYT article search tool."""
    schema = {
        "type": "function",
        "function": {
            "name": "search_nyt_articles",
            "description": "Search for New York Times articles by keyword or topic",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query"
                    },
                    "page": {
                        "type": "integer",
                        "description": "The page number for paginated results (0-100)",
                        "default": 0
                    },
                    "sort": {
                        "type": "string",
                        "enum": ["newest", "oldest", "relevance"],
                        "description": "Sort order for search results",
                        "default": "newest"
                    },
                    "begin_date": {
                        "type": "string",
                        "description": "Filter by begin date in YYYYMMDD format"
                    },
                    "end_date": {
                        "type": "string",
                        "description": "Filter by end date in YYYYMMDD format"
                    }
                },
                "required": ["query"]
            }
        }
    }
    
    return jsonify(schema)

@news_bp.route('/nyt/schema/top', methods=['GET'])
def get_nyt_top_schema():
    """Get the JSON schema for the NYT top stories tool."""
    # Valid sections
    valid_sections = [
        'arts', 'automobiles', 'books', 'business', 'fashion', 'food',
        'health', 'home', 'insider', 'magazine', 'movies', 'nyregion',
        'obituaries', 'opinion', 'politics', 'realestate', 'science',
        'sports', 'sundayreview', 'technology', 'theater', 'travel',
        'upshot', 'us', 'world'
    ]
    
    schema = {
        "type": "function",
        "function": {
            "name": "get_nyt_top_stories",
            "description": "Get the top stories from the New York Times by section",
            "parameters": {
                "type": "object",
                "properties": {
                    "section": {
                        "type": "string",
                        "enum": valid_sections,
                        "description": "The section to retrieve top stories from",
                        "default": "home"
                    }
                }
            }
        }
    }
    
    return jsonify(schema) 