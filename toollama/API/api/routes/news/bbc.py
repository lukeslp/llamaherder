#!/usr/bin/env python
from flask import request, jsonify
import requests
import logging
import xml.etree.ElementTree as ElementTree
from bs4 import BeautifulSoup
import re
from typing import Dict, List, Any, Optional

from api.routes.news import news_bp

# Logger for this module
logger = logging.getLogger(__name__)

# Default user agent to use for BBC News API requests
DEFAULT_USER_AGENT = "CaminaChat API/1.0"

# BBC News categories and their RSS feed endpoints
BBC_CATEGORIES = {
    "top_stories": "",
    "world": "world",
    "uk": "uk",
    "business": "business",
    "politics": "politics",
    "health": "health",
    "education": "education",
    "science_and_environment": "science_and_environment",
    "technology": "technology",
    "entertainment_and_arts": "entertainment_and_arts",
    "africa": "world/africa",
    "asia": "world/asia",
    "australia": "world/australia",
    "europe": "world/europe",
    "latin_america": "world/latin_america",
    "middle_east": "world/middle_east",
    "us_and_canada": "world/us_and_canada"
}

# Regex to match a BBC News article URI
BBC_URI_REGEX = re.compile(
    r"^(https?:\/\/)(www\.)?bbc\.(com|co\.uk)\/news\/(articles|videos)\/\w+$"
)

def get_feed_url(category: str) -> str:
    """Get the RSS feed URL for a given BBC News category."""
    if category not in BBC_CATEGORIES:
        raise ValueError(f"Invalid category: {category}")
        
    category_path = BBC_CATEGORIES[category]
    
    return (
        f"https://feeds.bbci.co.uk/news/{category_path}/rss.xml"
        if category != "top_stories"
        else "https://feeds.bbci.co.uk/news/rss.xml"
    )

def parse_bbc_feed(xml_content: str) -> List[Dict[str, Any]]:
    """Parse a BBC News RSS feed into a structured format."""
    try:
        # Parse the XML
        root = ElementTree.fromstring(xml_content)
        
        # Find all item elements
        items = root.findall('.//item')
        
        articles = []
        for item in items:
            # Extract article details
            title = item.find('title').text if item.find('title') is not None else ""
            description = item.find('description').text if item.find('description') is not None else ""
            link = item.find('link').text if item.find('link') is not None else ""
            pub_date = item.find('pubDate').text if item.find('pubDate') is not None else ""
            
            # Extract media content if available
            media = item.find('.//{http://search.yahoo.com/mrss/}thumbnail')
            media_url = media.get('url') if media is not None else None
            
            articles.append({
                "title": title,
                "description": description,
                "link": link,
                "published_at": pub_date,
                "image_url": media_url
            })
            
        return articles
        
    except Exception as e:
        logger.error(f"Error parsing BBC feed: {str(e)}")
        return []

def extract_article_content(html_content: str) -> Dict[str, Any]:
    """Extract article content from BBC News HTML."""
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Extract article title
        title_tag = soup.find('h1')
        title = title_tag.text.strip() if title_tag else ""
        
        # Extract article content
        content_blocks = []
        
        # Look for article body
        article = soup.find('article')
        if article:
            # Get all paragraphs
            paragraphs = article.find_all('p')
            for p in paragraphs:
                # Skip if paragraph is in a figure caption or summary
                if p.parent.name in ['figcaption', 'summary']:
                    continue
                    
                # Add paragraph text
                text = p.text.strip()
                if text:
                    content_blocks.append({"type": "paragraph", "content": text})
            
            # Get all headings
            headings = article.find_all(['h2', 'h3'])
            for h in headings:
                text = h.text.strip()
                if text:
                    content_blocks.append({"type": "heading", "content": text})
            
            # Get all images
            images = article.find_all('img')
            for img in images:
                if img.get('src') and not img.get('src').startswith('data:'):
                    content_blocks.append({
                        "type": "image", 
                        "content": img.get('src'),
                        "alt": img.get('alt', '')
                    })
        
        # Sort content blocks based on their position in the document
        sorted_blocks = sorted(
            content_blocks,
            key=lambda block: soup.prettify().find(block["content"]) if block["type"] != "image" else float('inf')
        )
        
        return {
            "title": title,
            "content": sorted_blocks
        }
        
    except Exception as e:
        logger.error(f"Error extracting article content: {str(e)}")
        return {"title": "", "content": []}

@news_bp.route('/bbc/feed', methods=['GET', 'POST'])
def get_bbc_news_feed():
    """
    Get the latest news articles from BBC News.
    
    Required parameters:
    - category: The news category to retrieve (default: top_stories)
      Valid categories: top_stories, world, uk, business, politics, health, 
      education, science_and_environment, technology, entertainment_and_arts,
      africa, asia, australia, europe, latin_america, middle_east, us_and_canada
    
    Optional parameters:
    - user_agent: User agent to use for the request (default: system value)
    """
    # Get parameters from either URL query or JSON body
    if request.method == 'POST':
        data = request.json or {}
    else:
        data = request.args.to_dict()
    
    # Get required parameters
    category = data.get('category', 'top_stories')
    
    # Validate category
    if category not in BBC_CATEGORIES:
        return jsonify({
            "success": False,
            "error": f"Invalid category: {category}. Valid categories are: {', '.join(BBC_CATEGORIES.keys())}"
        }), 400
    
    # Get optional parameters
    user_agent = data.get('user_agent', DEFAULT_USER_AGENT)
    
    # Get the RSS feed URL
    try:
        feed_url = get_feed_url(category)
        
        # Make the request to BBC News API
        headers = {'User-Agent': user_agent}
        response = requests.get(feed_url, headers=headers)
        response.raise_for_status()
        
        # Parse the response
        articles = parse_bbc_feed(response.content)
        
        # Format the category name for display
        display_category = category.replace('_', ' ').title()
        
        return jsonify({
            "success": True,
            "category": category,
            "display_category": display_category,
            "count": len(articles),
            "articles": articles
        })
        
    except Exception as e:
        logger.error(f"Error fetching BBC News feed: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e),
            "category": category
        }), 500

@news_bp.route('/bbc/content', methods=['GET', 'POST'])
def get_bbc_news_content():
    """
    Get the full content of a BBC News article.
    
    Required parameters:
    - url: The URL of the BBC News article
    
    Optional parameters:
    - user_agent: User agent to use for the request (default: system value)
    """
    # Get parameters from either URL query or JSON body
    if request.method == 'POST':
        data = request.json or {}
    else:
        data = request.args.to_dict()
    
    # Get required parameters
    url = data.get('url')
    
    if not url:
        return jsonify({"error": "URL parameter is required"}), 400
    
    # Validate URL
    if not BBC_URI_REGEX.match(url) and not url.startswith('https://www.bbc.com/news/') and not url.startswith('https://www.bbc.co.uk/news/'):
        return jsonify({"error": "Invalid BBC News URL"}), 400
    
    # Get optional parameters
    user_agent = data.get('user_agent', DEFAULT_USER_AGENT)
    
    # Make the request to BBC News
    try:
        headers = {'User-Agent': user_agent}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        # Extract article content
        article = extract_article_content(response.content)
        
        return jsonify({
            "success": True,
            "url": url,
            "title": article.get("title", ""),
            "content": article.get("content", [])
        })
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching BBC News article: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e),
            "url": url
        }), 500

@news_bp.route('/bbc/schema/feed', methods=['GET'])
def get_bbc_feed_schema():
    """Get the JSON schema for the BBC News feed tool."""
    schema = {
        "type": "function",
        "function": {
            "name": "get_bbc_news_feed",
            "description": "Get the latest news articles from BBC News by category",
            "parameters": {
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "enum": list(BBC_CATEGORIES.keys()),
                        "description": "The news category to retrieve",
                        "default": "top_stories"
                    }
                }
            }
        }
    }
    
    return jsonify(schema)

@news_bp.route('/bbc/schema/content', methods=['GET'])
def get_bbc_content_schema():
    """Get the JSON schema for the BBC News content tool."""
    schema = {
        "type": "function",
        "function": {
            "name": "get_bbc_news_content",
            "description": "Get the full content of a BBC News article by URL",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "The URL of the BBC News article"
                    }
                },
                "required": ["url"]
            }
        }
    }
    
    return jsonify(schema) 