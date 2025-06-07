"""
Blueprint for Web search routes.
"""

from flask import Blueprint, jsonify, request
from flask_cors import cross_origin
import logging
import json
import os
import requests
from typing import Dict, Any, List, Optional
from duckduckgo_search import DDGS
from bs4 import BeautifulSoup
import concurrent.futures
import unicodedata
import re
from urllib.parse import urlparse, urljoin
import asyncio
from functools import wraps

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create blueprint
web_bp = Blueprint('web', __name__)

# Default configuration for search tools
DEFAULT_CONFIG = {
    "SEARXNG_ENGINE_API_BASE_URL": "https://paulgo.io/search",
    "IGNORED_WEBSITES": "",
    "RETURNED_SCRAPPED_PAGES_NO": 3,
    "SCRAPPED_PAGES_NO": 5,
    "PAGE_CONTENT_WORDS_LIMIT": 5000,
    "TIMEOUT": 30,
    "READER_API": "https://r.jina.ai/"
}

# Helper function to run async function in sync context
def run_async(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        return asyncio.run(f(*args, **kwargs))
    return wrapper

# Helper functions for web search
class HelpFunctions:
    def __init__(self):
        pass

    def get_base_url(self, url):
        parsed_url = urlparse(url)
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
        return base_url

    def generate_excerpt(self, content, max_length=200):
        return content[:max_length] + "..." if len(content) > max_length else content

    def format_text(self, original_text):
        soup = BeautifulSoup(original_text, "html.parser")
        formatted_text = soup.get_text(separator=" ", strip=True)
        formatted_text = unicodedata.normalize("NFKC", formatted_text)
        formatted_text = re.sub(r"\s+", " ", formatted_text)
        formatted_text = formatted_text.strip()
        formatted_text = self.remove_emojis(formatted_text)
        return formatted_text

    def remove_emojis(self, text):
        return "".join(c for c in text if not unicodedata.category(c).startswith("So"))

    def process_search_result(self, result, config):
        title_site = self.remove_emojis(result["title"])
        url_site = result["url"]
        snippet = result.get("content", "")

        # Check if the website is in the ignored list, but only if IGNORED_WEBSITES is not empty
        if config["IGNORED_WEBSITES"]:
            base_url = self.get_base_url(url_site)
            if any(
                ignored_site.strip() in base_url
                for ignored_site in config["IGNORED_WEBSITES"].split(",")
            ):
                return None

        try:
            response_site = requests.get(url_site, timeout=20)
            response_site.raise_for_status()
            html_content = response_site.text

            soup = BeautifulSoup(html_content, "html.parser")
            content_site = self.format_text(soup.get_text(separator=" ", strip=True))

            truncated_content = self.truncate_to_n_words(
                content_site, config["PAGE_CONTENT_WORDS_LIMIT"]
            )

            return {
                "title": title_site,
                "url": url_site,
                "content": truncated_content,
                "snippet": self.remove_emojis(snippet),
            }

        except requests.exceptions.RequestException as e:
            return None

    def truncate_to_n_words(self, text, token_limit):
        tokens = text.split()
        truncated_tokens = tokens[:token_limit]
        return " ".join(truncated_tokens)

# DuckDuckGo search endpoint (existing)
@web_bp.route('/duckduckgo', methods=["GET", "OPTIONS", "POST"])
@cross_origin()
def duckduckgo_search():
    """
    Perform a search using DuckDuckGo Search.
    
    Query parameters (GET) or JSON body (POST):
    - query: The search term to look up (required)
    - region: Region for the search (default: 'wt-wt')
    - safesearch: SafeSearch setting (default: 'moderate')
    - timelimit: Time limit for results (default: None)
    - max_results: Maximum number of results to return (default: 10)
    """
    # Handle OPTIONS request for CORS preflight
    if request.method == "OPTIONS":
        response = jsonify({"allowed_methods": ["GET", "POST", "OPTIONS"]})
        return response
    
    try:
        # Get parameters from either query string (GET) or JSON body (POST)
        if request.method == "GET":
            query = request.args.get("query")
            region = request.args.get("region", "wt-wt")
            safesearch = request.args.get("safesearch", "moderate")
            timelimit = request.args.get("timelimit")
            max_results = int(request.args.get("max_results", "10"))
        else:  # POST
            data = request.get_json() or {}
            query = data.get("query")
            region = data.get("region", "wt-wt")
            safesearch = data.get("safesearch", "moderate")
            timelimit = data.get("timelimit")
            max_results = int(data.get("max_results", 10))
        
        # Validate required parameters
        if not query:
            logger.error("Missing required parameter: query")
            return jsonify({"error": "Missing required parameter: query"}), 400
        
        logger.info(f"DuckDuckGo search: query={query}, region={region}, max_results={max_results}")
        
        # Perform the search
        with DDGS() as ddgs:
            results = list(ddgs.text(
                query, 
                region=region, 
                safesearch=safesearch,
                timelimit=timelimit,
                max_results=max_results
            ))
        
        logger.info(f"Found {len(results)} results for query: {query}")
        
        # Return the results
        return jsonify({
            "query": query,
            "results": results,
            "count": len(results)
        })
        
    except ValueError as ve:
        logger.error(f"Value error in duckduckgo_search: {str(ve)}")
        return jsonify({"error": f"Invalid parameter value: {str(ve)}"}), 400
    except Exception as e:
        logger.error(f"Error in duckduckgo_search: {str(e)}")
        return jsonify({"error": str(e)}), 500

# SearXNG web search endpoint
@web_bp.route('/searxng', methods=["GET", "OPTIONS", "POST"])
@cross_origin()
@run_async
async def searxng_search():
    """
    Perform a search using SearXNG and scrape the first N pages of results.
    
    Query parameters (GET) or JSON body (POST):
    - query: The search term to look up (required)
    - max_results: Maximum number of results to return (default: 3)
    - api_url: SearXNG API URL (default: from configuration)
    - ignored_websites: Comma-separated list of websites to ignore (default: from configuration)
    - max_words_per_page: Maximum number of words to include per page (default: 5000)
    """
    # Handle OPTIONS request for CORS preflight
    if request.method == "OPTIONS":
        response = jsonify({"allowed_methods": ["GET", "POST", "OPTIONS"]})
        return response
    
    try:
        # Get parameters from either query string (GET) or JSON body (POST)
        if request.method == "GET":
            query = request.args.get("query")
            max_results = int(request.args.get("max_results", DEFAULT_CONFIG["RETURNED_SCRAPPED_PAGES_NO"]))
            api_url = request.args.get("api_url", DEFAULT_CONFIG["SEARXNG_ENGINE_API_BASE_URL"])
            ignored_websites = request.args.get("ignored_websites", DEFAULT_CONFIG["IGNORED_WEBSITES"])
            max_words = int(request.args.get("max_words_per_page", DEFAULT_CONFIG["PAGE_CONTENT_WORDS_LIMIT"]))
        else:  # POST
            data = request.get_json() or {}
            query = data.get("query")
            max_results = int(data.get("max_results", DEFAULT_CONFIG["RETURNED_SCRAPPED_PAGES_NO"]))
            api_url = data.get("api_url", DEFAULT_CONFIG["SEARXNG_ENGINE_API_BASE_URL"])
            ignored_websites = data.get("ignored_websites", DEFAULT_CONFIG["IGNORED_WEBSITES"])
            max_words = int(data.get("max_words_per_page", DEFAULT_CONFIG["PAGE_CONTENT_WORDS_LIMIT"]))
        
        # Validate required parameters
        if not query:
            logger.error("Missing required parameter: query")
            return jsonify({"error": "Missing required parameter: query"}), 400
        
        logger.info(f"SearXNG search: query={query}, max_results={max_results}")
        
        # Configure search parameters
        config = DEFAULT_CONFIG.copy()
        config.update({
            "SEARXNG_ENGINE_API_BASE_URL": api_url,
            "IGNORED_WEBSITES": ignored_websites,
            "RETURNED_SCRAPPED_PAGES_NO": max_results,
            "SCRAPPED_PAGES_NO": max(max_results + 2, 5),  # Get a few extra in case some fail
            "PAGE_CONTENT_WORDS_LIMIT": max_words
        })
        
        # Prepare search parameters
        search_engine_url = config["SEARXNG_ENGINE_API_BASE_URL"]
        params = {
            "q": query,
            "format": "json",
            "number_of_results": config["RETURNED_SCRAPPED_PAGES_NO"]
        }
        
        # Send request to search engine
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
        }
        
        resp = requests.get(search_engine_url, params=params, headers=headers, timeout=config["TIMEOUT"])
        resp.raise_for_status()
        data = resp.json()
        
        results = data.get("results", [])
        limited_results = results[:config["SCRAPPED_PAGES_NO"]]
        
        logger.info(f"Retrieved {len(limited_results)} SearXNG search results for query: {query}")
        
        # Process search results
        functions = HelpFunctions()
        results_json = []
        
        if limited_results:
            with concurrent.futures.ThreadPoolExecutor() as executor:
                futures = [
                    executor.submit(functions.process_search_result, result, config)
                    for result in limited_results
                ]
                for future in concurrent.futures.as_completed(futures):
                    result_json = future.result()
                    if result_json:
                        results_json.append(result_json)
                    if len(results_json) >= config["RETURNED_SCRAPPED_PAGES_NO"]:
                        break
            
            results_json = results_json[:config["RETURNED_SCRAPPED_PAGES_NO"]]
        
        logger.info(f"Successfully processed {len(results_json)} pages for query: {query}")
        
        # Return the results
        return jsonify({
            "query": query,
            "results": results_json,
            "count": len(results_json)
        })
        
    except ValueError as ve:
        logger.error(f"Value error in searxng_search: {str(ve)}")
        return jsonify({"error": f"Invalid parameter value: {str(ve)}"}), 400
    except requests.exceptions.RequestException as re:
        logger.error(f"Request error in searxng_search: {str(re)}")
        return jsonify({"error": f"Search engine request failed: {str(re)}"}), 502
    except Exception as e:
        logger.error(f"Error in searxng_search: {str(e)}")
        return jsonify({"error": str(e)}), 500

# Website scraper endpoint
@web_bp.route('/website', methods=["GET", "OPTIONS", "POST"])
@cross_origin()
@run_async
async def scrape_website():
    """
    Scrape content from a specified website URL.
    
    Query parameters (GET) or JSON body (POST):
    - url: The URL of the website to scrape (required)
    - max_words: Maximum number of words to include (default: 5000)
    """
    # Handle OPTIONS request for CORS preflight
    if request.method == "OPTIONS":
        response = jsonify({"allowed_methods": ["GET", "POST", "OPTIONS"]})
        return response
    
    try:
        # Get parameters from either query string (GET) or JSON body (POST)
        if request.method == "GET":
            url = request.args.get("url")
            max_words = int(request.args.get("max_words", DEFAULT_CONFIG["PAGE_CONTENT_WORDS_LIMIT"]))
        else:  # POST
            data = request.get_json() or {}
            url = data.get("url")
            max_words = int(data.get("max_words", DEFAULT_CONFIG["PAGE_CONTENT_WORDS_LIMIT"]))
        
        # Validate required parameters
        if not url:
            logger.error("Missing required parameter: url")
            return jsonify({"error": "Missing required parameter: url"}), 400
        
        logger.info(f"Scraping website: url={url}")
        
        # Configure scraper
        config = DEFAULT_CONFIG.copy()
        config["PAGE_CONTENT_WORDS_LIMIT"] = max_words
        
        functions = HelpFunctions()
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
        }
        
        # Fetch the website content
        response_site = requests.get(url, headers=headers, timeout=config["TIMEOUT"])
        response_site.raise_for_status()
        html_content = response_site.text
        
        # Parse website content
        soup = BeautifulSoup(html_content, "html.parser")
        
        page_title = soup.title.string if soup.title else "No title found"
        page_title = unicodedata.normalize("NFKC", page_title.strip())
        page_title = functions.remove_emojis(page_title)
        
        content_site = functions.format_text(soup.get_text(separator=" ", strip=True))
        truncated_content = functions.truncate_to_n_words(content_site, config["PAGE_CONTENT_WORDS_LIMIT"])
        
        result = {
            "title": page_title,
            "url": url,
            "content": truncated_content,
            "excerpt": functions.generate_excerpt(content_site)
        }
        
        logger.info(f"Successfully scraped website: {url}")
        
        # Return the result
        return jsonify({
            "url": url,
            "result": result
        })
        
    except ValueError as ve:
        logger.error(f"Value error in scrape_website: {str(ve)}")
        return jsonify({"error": f"Invalid parameter value: {str(ve)}"}), 400
    except requests.exceptions.RequestException as re:
        logger.error(f"Request error in scrape_website: {str(re)}")
        return jsonify({"error": f"Website request failed: {str(re)}"}), 502
    except Exception as e:
        logger.error(f"Error in scrape_website: {str(e)}")
        return jsonify({"error": str(e)}), 500

# Reader API endpoint
@web_bp.route('/reader', methods=["GET", "OPTIONS", "POST"])
@cross_origin()
def reader_api():
    """
    Use the Reader API to extract content from a URL in readable format.
    
    Query parameters (GET) or JSON body (POST):
    - url: The URL to read from (required)
    """
    # Handle OPTIONS request for CORS preflight
    if request.method == "OPTIONS":
        response = jsonify({"allowed_methods": ["GET", "POST", "OPTIONS"]})
        return response
    
    try:
        # Get parameters from either query string (GET) or JSON body (POST)
        if request.method == "GET":
            url = request.args.get("url")
        else:  # POST
            data = request.get_json() or {}
            url = data.get("url")
        
        # Validate required parameters
        if not url:
            logger.error("Missing required parameter: url")
            return jsonify({"error": "Missing required parameter: url"}), 400
        
        logger.info(f"Reader API request for URL: {url}")
        
        # Send request to Reader API
        reader_api_url = DEFAULT_CONFIG["READER_API"]
        response = requests.post(reader_api_url, data={"url": url}, timeout=DEFAULT_CONFIG["TIMEOUT"])
        response.raise_for_status()
        content = response.text
        
        # Create a title from the URL
        parsed_url = urlparse(url)
        domain = parsed_url.netloc
        title = f"Content from {domain}"
        
        logger.info(f"Successfully retrieved content from Reader API for URL: {url}")
        
        # Return the result
        return jsonify({
            "url": url,
            "title": title,
            "content": content
        })
        
    except ValueError as ve:
        logger.error(f"Value error in reader_api: {str(ve)}")
        return jsonify({"error": f"Invalid parameter value: {str(ve)}"}), 400
    except requests.exceptions.RequestException as re:
        logger.error(f"Request error in reader_api: {str(re)}")
        return jsonify({"error": f"Reader API request failed: {str(re)}"}), 502
    except Exception as e:
        logger.error(f"Error in reader_api: {str(e)}")
        return jsonify({"error": str(e)}), 500

# Search engine endpoints using Reader API
@web_bp.route('/search/<engine>', methods=["GET", "OPTIONS", "POST"])
@cross_origin()
def search_engine(engine):
    """
    Perform a search using various search engines through the Reader API.
    
    Path parameter:
    - engine: Search engine to use ('google', 'bing', or 'baidu')
    
    Query parameters (GET) or JSON body (POST):
    - query: The search term to look up (required)
    """
    # Handle OPTIONS request for CORS preflight
    if request.method == "OPTIONS":
        response = jsonify({"allowed_methods": ["GET", "POST", "OPTIONS"]})
        return response
    
    try:
        # Validate engine parameter
        if engine not in ['google', 'bing', 'baidu']:
            logger.error(f"Invalid search engine: {engine}")
            return jsonify({"error": f"Invalid search engine. Must be one of: google, bing, baidu"}), 400
        
        # Get parameters from either query string (GET) or JSON body (POST)
        if request.method == "GET":
            query = request.args.get("query")
        else:  # POST
            data = request.get_json() or {}
            query = data.get("query")
        
        # Validate required parameters
        if not query:
            logger.error("Missing required parameter: query")
            return jsonify({"error": "Missing required parameter: query"}), 400
        
        logger.info(f"Search request: engine={engine}, query={query}")
        
        # Prepare the search request
        reader_api_url = DEFAULT_CONFIG["READER_API"]
        
        if engine == "baidu":
            url = f"{reader_api_url}{DEFAULT_CONFIG['SEARXNG_ENGINE_API_BASE_URL']}?wd={query}"
            headers = {"X-Target-Selector": "#content_left"}
        else:
            prefix = "!go" if engine == "google" else "!bi"
            url = f"{reader_api_url}{DEFAULT_CONFIG['SEARXNG_ENGINE_API_BASE_URL']}?q={prefix} {query}"
            headers = {"X-Target-Selector": "#urls"}
        
        # Send request to Reader API
        response = requests.get(url, headers=headers, timeout=DEFAULT_CONFIG["TIMEOUT"])
        response.raise_for_status()
        content = response.text
        
        logger.info(f"Successfully retrieved search results from {engine} for query: {query}")
        
        # Return the results
        return jsonify({
            "engine": engine,
            "query": query,
            "content": content
        })
        
    except ValueError as ve:
        logger.error(f"Value error in search_engine: {str(ve)}")
        return jsonify({"error": f"Invalid parameter value: {str(ve)}"}), 400
    except requests.exceptions.RequestException as re:
        logger.error(f"Request error in search_engine: {str(re)}")
        return jsonify({"error": f"Search engine request failed: {str(re)}"}), 502
    except Exception as e:
        logger.error(f"Error in search_engine: {str(e)}")
        return jsonify({"error": str(e)}), 500 