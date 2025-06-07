#!/usr/bin/env python
from flask import request, jsonify
import requests
import logging
import os
from typing import Dict, List, Any, Optional
from datetime import datetime

from api.routes.news import news_bp
from api.config.api_keys import ADDITIONAL_API_KEYS

# Logger for this module
logger = logging.getLogger(__name__)

# Default user agent to use for Guardian API requests
DEFAULT_USER_AGENT = "CaminaChat API/1.0"

# Guardian API key from app.py
GUARDIAN_API_KEY = ADDITIONAL_API_KEYS.get('guardian', '')

# Guardian sections for filtering
GUARDIAN_SECTIONS = [
    'world', 'politics', 'uk-news', 'us-news', 'business', 'technology', 
    'science', 'environment', 'media', 'education', 'society', 'law', 
    'sport', 'football', 'culture', 'film', 'music', 'books', 'travel', 
    'lifestyle', 'fashion', 'food', 'money', 'opinion', 'art', 'stage'
]

@news_bp.route('/guardian/search', methods=['GET', 'POST'])
def search_guardian_articles():
    """
    Search for Guardian articles.
    
    Required parameters:
    - query: The search query
    
    Optional parameters:
    - api_key: The Guardian API key (if not provided, uses environment variable)
    - page: The page number (default: 1)
    - page_size: The number of results per page (default: 10, max: 50)
    - section: Filter by section (e.g., politics, technology, etc.)
    - from_date: Filter by date (YYYY-MM-DD format)
    - to_date: Filter by date (YYYY-MM-DD format)
    - order_by: Sort order (newest, oldest, relevance - default: newest)
    - tag: Filter by tag
    - show_fields: Comma-separated list of fields to include (e.g., headline,byline,thumbnail)
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
    api_key = data.get('api_key', GUARDIAN_API_KEY)
    page = int(data.get('page', 1))
    page_size = min(int(data.get('page_size', 10)), 50)  # Guardian API max is 50
    section = data.get('section')
    from_date = data.get('from_date')
    to_date = data.get('to_date')
    order_by = data.get('order_by', 'newest')
    tag = data.get('tag')
    show_fields = data.get('show_fields', 'headline,byline,trailText,thumbnail,publication,shortUrl,wordcount,body')
    
    if not api_key:
        return jsonify({"error": "Guardian API key is required. Please provide it via api_key parameter."}), 400
    
    # Validate parameters
    if order_by not in ['newest', 'oldest', 'relevance']:
        return jsonify({"error": "order_by must be one of: newest, oldest, relevance"}), 400
        
    if section and section not in GUARDIAN_SECTIONS:
        return jsonify({"error": f"Invalid section. Valid sections are: {', '.join(GUARDIAN_SECTIONS)}"}), 400
    
    # Construct the request parameters
    params = {
        "q": query,
        "api-key": api_key,
        "page": page,
        "page-size": page_size,
        "order-by": order_by,
        "show-fields": show_fields
    }
    
    # Add optional filters if provided
    if section:
        params["section"] = section
        
    if from_date:
        params["from-date"] = from_date
        
    if to_date:
        params["to-date"] = to_date
        
    if tag:
        params["tag"] = tag
    
    # Make the request to Guardian API
    try:
        url = "https://content.guardianapis.com/search"
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        # Parse the response
        data = response.json()
        response_data = data.get("response", {})
        articles = response_data.get("results", [])
        
        # Extract relevant information
        formatted_articles = []
        for article in articles:
            # Extract basic article data
            article_id = article.get("id", "")
            web_url = article.get("webUrl", "")
            api_url = article.get("apiUrl", "")
            section_id = article.get("sectionId", "")
            section_name = article.get("sectionName", "")
            publication_date = article.get("webPublicationDate", "")
            
            # Extract fields if available
            fields = article.get("fields", {})
            headline = fields.get("headline", article.get("webTitle", "No Title"))
            byline = fields.get("byline", "")
            trail_text = fields.get("trailText", "")
            thumbnail = fields.get("thumbnail", "")
            body = fields.get("body", "")
            
            formatted_articles.append({
                "id": article_id,
                "title": headline,
                "byline": byline,
                "description": trail_text,
                "url": web_url,
                "api_url": api_url,
                "section_id": section_id,
                "section_name": section_name,
                "published_at": publication_date,
                "thumbnail": thumbnail,
                "body": body if "body" in fields else None
            })
        
        # Get pagination data
        current_page = response_data.get("currentPage", 1)
        page_size = response_data.get("pageSize", 10)
        pages = response_data.get("pages", 1)
        total_results = response_data.get("total", 0)
        
        return jsonify({
            "success": True,
            "query": query,
            "page": current_page,
            "page_size": page_size,
            "total_pages": pages,
            "total_results": total_results,
            "count": len(formatted_articles),
            "articles": formatted_articles
        })
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Error searching Guardian articles: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e),
            "query": query
        }), 500

@news_bp.route('/guardian/section/<section_id>', methods=['GET', 'POST'])
def get_guardian_section(section_id):
    """
    Get the latest articles from a specific Guardian section.
    
    Path parameter:
    - section_id: The section ID to retrieve (e.g., politics, technology)
    
    Optional parameters:
    - api_key: The Guardian API key (if not provided, uses environment variable)
    - page: The page number (default: 1)
    - page_size: The number of results per page (default: 10, max: 50)
    - show_fields: Comma-separated list of fields to include (default: headline,byline,trailText,thumbnail)
    """
    # Validate section ID
    if section_id not in GUARDIAN_SECTIONS:
        return jsonify({
            "success": False,
            "error": f"Invalid section: {section_id}. Valid sections are: {', '.join(GUARDIAN_SECTIONS)}"
        }), 400
    
    # Get parameters from either URL query or JSON body
    if request.method == 'POST':
        data = request.json or {}
    else:
        data = request.args.to_dict()
    
    # Get optional parameters
    api_key = data.get('api_key', GUARDIAN_API_KEY)
    page = int(data.get('page', 1))
    page_size = min(int(data.get('page_size', 10)), 50)  # Guardian API max is 50
    show_fields = data.get('show_fields', 'headline,byline,trailText,thumbnail,publication,shortUrl')
    
    if not api_key:
        return jsonify({"error": "Guardian API key is required. Please provide it via api_key parameter."}), 400
    
    # Construct the request parameters
    params = {
        "section": section_id,
        "api-key": api_key,
        "page": page,
        "page-size": page_size,
        "show-fields": show_fields
    }
    
    # Make the request to Guardian API
    try:
        url = "https://content.guardianapis.com/search"
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        # Parse the response
        data = response.json()
        response_data = data.get("response", {})
        articles = response_data.get("results", [])
        
        # Extract relevant information
        formatted_articles = []
        for article in articles:
            # Extract basic article data
            article_id = article.get("id", "")
            web_url = article.get("webUrl", "")
            api_url = article.get("apiUrl", "")
            section_name = article.get("sectionName", "")
            publication_date = article.get("webPublicationDate", "")
            
            # Extract fields if available
            fields = article.get("fields", {})
            headline = fields.get("headline", article.get("webTitle", "No Title"))
            byline = fields.get("byline", "")
            trail_text = fields.get("trailText", "")
            thumbnail = fields.get("thumbnail", "")
            
            formatted_articles.append({
                "id": article_id,
                "title": headline,
                "byline": byline,
                "description": trail_text,
                "url": web_url,
                "api_url": api_url,
                "section_name": section_name,
                "published_at": publication_date,
                "thumbnail": thumbnail
            })
        
        # Get pagination data
        current_page = response_data.get("currentPage", 1)
        page_size = response_data.get("pageSize", 10)
        pages = response_data.get("pages", 1)
        total_results = response_data.get("total", 0)
        
        return jsonify({
            "success": True,
            "section": section_id,
            "section_name": articles[0].get("sectionName", section_id.capitalize()) if articles else section_id.capitalize(),
            "page": current_page,
            "page_size": page_size,
            "total_pages": pages,
            "total_results": total_results,
            "count": len(formatted_articles),
            "articles": formatted_articles
        })
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching Guardian section: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e),
            "section": section_id
        }), 500

@news_bp.route('/guardian/article/<path:article_id>', methods=['GET', 'POST'])
def get_guardian_article(article_id):
    """
    Get the full content of a specific Guardian article.
    
    Path parameter:
    - article_id: The article ID from the Guardian API
    
    Optional parameters:
    - api_key: The Guardian API key (if not provided, uses environment variable)
    - show_fields: Comma-separated list of fields to include
    """
    # Get parameters from either URL query or JSON body
    if request.method == 'POST':
        data = request.json or {}
    else:
        data = request.args.to_dict()
    
    # Get optional parameters
    api_key = data.get('api_key', GUARDIAN_API_KEY)
    show_fields = data.get('show_fields', 'headline,byline,trailText,thumbnail,body,publication,shortUrl,wordcount')
    
    if not api_key:
        return jsonify({"error": "Guardian API key is required. Please provide it via api_key parameter."}), 400
    
    # Construct the request parameters
    params = {
        "api-key": api_key,
        "show-fields": show_fields
    }
    
    # Make the request to Guardian API
    try:
        url = f"https://content.guardianapis.com/{article_id}"
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        # Parse the response
        data = response.json()
        content = data.get("response", {}).get("content", {})
        
        if not content:
            return jsonify({
                "success": False,
                "error": "Article not found",
                "article_id": article_id
            }), 404
        
        # Extract basic article data
        web_url = content.get("webUrl", "")
        api_url = content.get("apiUrl", "")
        section_id = content.get("sectionId", "")
        section_name = content.get("sectionName", "")
        publication_date = content.get("webPublicationDate", "")
        
        # Extract fields if available
        fields = content.get("fields", {})
        headline = fields.get("headline", content.get("webTitle", "No Title"))
        byline = fields.get("byline", "")
        trail_text = fields.get("trailText", "")
        thumbnail = fields.get("thumbnail", "")
        body = fields.get("body", "")
        wordcount = fields.get("wordcount", 0)
        
        return jsonify({
            "success": True,
            "id": article_id,
            "title": headline,
            "byline": byline,
            "description": trail_text,
            "url": web_url,
            "api_url": api_url,
            "section_id": section_id,
            "section_name": section_name,
            "published_at": publication_date,
            "thumbnail": thumbnail,
            "body": body,
            "wordcount": wordcount
        })
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching Guardian article: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e),
            "article_id": article_id
        }), 500

@news_bp.route('/guardian/schema/search', methods=['GET'])
def get_guardian_search_schema():
    """Get the JSON schema for Guardian search endpoint."""
    return jsonify({
        "name": "guardian_search",
        "description": "Search for articles from The Guardian news source",
        "parameters": {
            "type": "object",
            "required": ["query"],
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query term or phrase"
                },
                "api_key": {
                    "type": "string",
                    "description": "API key for The Guardian (optional if set in environment)"
                },
                "page": {
                    "type": "integer",
                    "description": "Page number for paginated results",
                    "default": 1
                },
                "page_size": {
                    "type": "integer",
                    "description": "Number of results per page (max 50)",
                    "default": 10,
                    "maximum": 50
                },
                "section": {
                    "type": "string",
                    "description": "Filter by section",
                    "enum": GUARDIAN_SECTIONS
                },
                "from_date": {
                    "type": "string",
                    "description": "Filter by date (YYYY-MM-DD format)",
                    "pattern": "^\\d{4}-\\d{2}-\\d{2}$"
                },
                "to_date": {
                    "type": "string",
                    "description": "Filter by date (YYYY-MM-DD format)",
                    "pattern": "^\\d{4}-\\d{2}-\\d{2}$"
                },
                "order_by": {
                    "type": "string",
                    "description": "Sort order",
                    "enum": ["newest", "oldest", "relevance"],
                    "default": "newest"
                }
            }
        }
    })

@news_bp.route('/guardian/schema/section', methods=['GET'])
def get_guardian_section_schema():
    """Get the JSON schema for Guardian section endpoint."""
    return jsonify({
        "name": "guardian_section",
        "description": "Get the latest articles from a specific Guardian section",
        "parameters": {
            "type": "object",
            "required": ["section_id"],
            "properties": {
                "section_id": {
                    "type": "string",
                    "description": "The section ID to retrieve",
                    "enum": GUARDIAN_SECTIONS
                },
                "api_key": {
                    "type": "string",
                    "description": "API key for The Guardian (optional if set in environment)"
                },
                "page": {
                    "type": "integer",
                    "description": "Page number for paginated results",
                    "default": 1
                },
                "page_size": {
                    "type": "integer",
                    "description": "Number of results per page (max 50)",
                    "default": 10,
                    "maximum": 50
                }
            }
        }
    })

@news_bp.route('/guardian/schema/article', methods=['GET'])
def get_guardian_article_schema():
    """Get the JSON schema for Guardian article endpoint."""
    return jsonify({
        "name": "guardian_article",
        "description": "Get the full content of a specific Guardian article",
        "parameters": {
            "type": "object",
            "required": ["article_id"],
            "properties": {
                "article_id": {
                    "type": "string",
                    "description": "The article ID from the Guardian API"
                },
                "api_key": {
                    "type": "string",
                    "description": "API key for The Guardian (optional if set in environment)"
                }
            }
        }
    }) 