#!/usr/bin/env python
from flask import request, jsonify
import requests
import json
import os
import logging
from typing import Dict, Any, List, Optional

from api.routes.social import social_bp

# Logger for this module
logger = logging.getLogger(__name__)

# Default user agent to use for Reddit API requests
DEFAULT_USER_AGENT = "CaminaChat API/1.0"

def parse_reddit_data(response_content):
    """Parse raw Reddit API response into a structured format."""
    try:
        data = json.loads(response_content)
        output = []
        
        if "data" not in data:
            return output
            
        if "children" not in data["data"]:
            return output
            
        for item in data["data"]["children"]:
            output.append(item)
            
        return output
    except Exception as e:
        logger.error(f"Error parsing Reddit data: {str(e)}")
        return []

def parse_reddit_posts(data):
    """Parse Reddit posts into a structured format."""
    posts = []
    
    for item in data:
        if item["kind"] != "t3":
            continue
            
        item_data = item["data"]
        
        # Create a structured post object
        post = {
            "id": item_data.get("name", ""),
            "title": item_data.get("title", ""),
            "text": item_data.get("selftext", ""),
            "link": item_data.get("url", ""),
            "permalink": f"https://www.reddit.com{item_data.get('permalink', '')}",
            
            "author": {
                "username": item_data.get("author", ""),
                "id": item_data.get("author_fullname", "")
            },
            
            "subreddit": {
                "name": item_data.get("subreddit", ""),
                "id": item_data.get("subreddit_id", ""),
                "subscribers": item_data.get("subreddit_subscribers", 0)
            },
            
            "statistics": {
                "score": item_data.get("score", 0),
                "upvotes": item_data.get("ups", 0),
                "downvotes": item_data.get("downs", 0),
                "upvote_ratio": item_data.get("upvote_ratio", 0),
                "comments": item_data.get("num_comments", 0),
                "crossposts": item_data.get("num_crossposts", 0),
                "awards": item_data.get("total_awards_received", 0)
            },
            
            "flags": {
                "is_pinned": item_data.get("pinned", False),
                "is_self": item_data.get("is_self", False),
                "is_video": item_data.get("is_video", False),
                "is_nsfw": item_data.get("over_18", False),
                "is_spoiler": item_data.get("spoiler", False),
                "is_stickied": item_data.get("stickied", False)
            },
            
            "timestamp": item_data.get("created_utc", 0)
        }
        
        # Add media information if available
        if "media" in item_data and item_data["media"]:
            post["media"] = {
                "type": "reddit_video" if "reddit_video" in item_data["media"] else "external",
                "url": (item_data["media"].get("reddit_video", {}).get("fallback_url", "")
                        if "reddit_video" in item_data["media"] else item_data.get("url", ""))
            }
        elif "preview" in item_data and "images" in item_data["preview"]:
            post["media"] = {
                "type": "image",
                "url": item_data["preview"]["images"][0]["source"].get("url", "")
            }
            
        posts.append(post)
    
    return posts

@social_bp.route('/reddit/subreddit', methods=['GET', 'POST'])
def get_subreddit_feed():
    """
    Get the latest posts from a subreddit.
    
    Required parameters:
    - subreddit: Name of the subreddit
    
    Optional parameters:
    - limit: Number of posts to retrieve (default: 10)
    - sort: Sort method (hot, new, top, rising - default: hot)
    - timeframe: Timeframe for 'top' sort (hour, day, week, month, year, all - default: day)
    - user_agent: User agent to use for the request (default: system value)
    """
    # Get parameters from either URL query or JSON body
    if request.method == 'POST':
        data = request.json or {}
    else:
        data = request.args.to_dict()
    
    # Get required parameters
    subreddit = data.get('subreddit')
    
    if not subreddit:
        return jsonify({"error": "Subreddit parameter is required"}), 400
        
    # Get optional parameters
    limit = int(data.get('limit', 10))
    sort = data.get('sort', 'hot')
    timeframe = data.get('timeframe', 'day')
    user_agent = data.get('user_agent', DEFAULT_USER_AGENT)
    
    # Validate parameters
    if limit < 1 or limit > 100:
        return jsonify({"error": "Limit must be between 1 and 100"}), 400
        
    if sort not in ['hot', 'new', 'top', 'rising']:
        return jsonify({"error": "Sort must be one of: hot, new, top, rising"}), 400
        
    if sort == 'top' and timeframe not in ['hour', 'day', 'week', 'month', 'year', 'all']:
        return jsonify({"error": "Timeframe must be one of: hour, day, week, month, year, all"}), 400
    
    # Construct the Reddit API URL
    url = f"https://www.reddit.com/r/{subreddit}/{sort}.json"
    
    # Add parameters
    params = {'limit': limit}
    
    if sort == 'top':
        params['t'] = timeframe
    
    # Make the request to Reddit API
    try:
        headers = {'User-Agent': user_agent}
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        
        # Parse the response
        raw_data = parse_reddit_data(response.content)
        posts = parse_reddit_posts(raw_data)
        
        return jsonify({
            "success": True,
            "subreddit": subreddit,
            "sort": sort,
            "count": len(posts),
            "posts": posts
        })
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching Reddit data: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e),
            "subreddit": subreddit
        }), 500

@social_bp.route('/reddit/user', methods=['GET', 'POST'])
def get_user_feed():
    """
    Get the latest posts from a Reddit user.
    
    Required parameters:
    - username: Reddit username
    
    Optional parameters:
    - limit: Number of posts to retrieve (default: 10)
    - sort: Sort method (hot, new, top, controversial - default: new)
    - timeframe: Timeframe for 'top' sort (hour, day, week, month, year, all - default: all)
    - user_agent: User agent to use for the request (default: system value)
    """
    # Get parameters from either URL query or JSON body
    if request.method == 'POST':
        data = request.json or {}
    else:
        data = request.args.to_dict()
    
    # Get required parameters
    username = data.get('username')
    
    if not username:
        return jsonify({"error": "Username parameter is required"}), 400
        
    # Get optional parameters
    limit = int(data.get('limit', 10))
    sort = data.get('sort', 'new')
    timeframe = data.get('timeframe', 'all')
    user_agent = data.get('user_agent', DEFAULT_USER_AGENT)
    
    # Validate parameters
    if limit < 1 or limit > 100:
        return jsonify({"error": "Limit must be between 1 and 100"}), 400
        
    if sort not in ['hot', 'new', 'top', 'controversial']:
        return jsonify({"error": "Sort must be one of: hot, new, top, controversial"}), 400
        
    if sort in ['top', 'controversial'] and timeframe not in ['hour', 'day', 'week', 'month', 'year', 'all']:
        return jsonify({"error": "Timeframe must be one of: hour, day, week, month, year, all"}), 400
    
    # Construct the Reddit API URL
    url = f"https://www.reddit.com/user/{username}/submitted/{sort}.json"
    
    # Add parameters
    params = {'limit': limit}
    
    if sort in ['top', 'controversial']:
        params['t'] = timeframe
    
    # Make the request to Reddit API
    try:
        headers = {'User-Agent': user_agent}
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        
        # Parse the response
        raw_data = parse_reddit_data(response.content)
        posts = parse_reddit_posts(raw_data)
        
        return jsonify({
            "success": True,
            "username": username,
            "sort": sort,
            "count": len(posts),
            "posts": posts
        })
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching Reddit user data: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e),
            "username": username
        }), 500

@social_bp.route('/reddit/schema/subreddit', methods=['GET'])
def get_reddit_subreddit_schema():
    """Get the JSON schema for the Reddit subreddit feed tool."""
    schema = {
        "type": "function",
        "function": {
            "name": "get_reddit_subreddit",
            "description": "Get the latest posts from a specific subreddit on Reddit",
            "parameters": {
                "type": "object",
                "properties": {
                    "subreddit": {
                        "type": "string",
                        "description": "The name of the subreddit (without r/ prefix)"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Number of posts to retrieve (1-100)",
                        "default": 10
                    },
                    "sort": {
                        "type": "string",
                        "enum": ["hot", "new", "top", "rising"],
                        "description": "Sort method for posts",
                        "default": "hot"
                    },
                    "timeframe": {
                        "type": "string",
                        "enum": ["hour", "day", "week", "month", "year", "all"],
                        "description": "Timeframe for 'top' sort",
                        "default": "day"
                    }
                },
                "required": ["subreddit"]
            }
        }
    }
    
    return jsonify(schema)

@social_bp.route('/reddit/schema/user', methods=['GET'])
def get_reddit_user_schema():
    """Get the JSON schema for the Reddit user feed tool."""
    schema = {
        "type": "function",
        "function": {
            "name": "get_reddit_user",
            "description": "Get the latest posts from a specific user on Reddit",
            "parameters": {
                "type": "object",
                "properties": {
                    "username": {
                        "type": "string",
                        "description": "The Reddit username (without u/ prefix)"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Number of posts to retrieve (1-100)",
                        "default": 10
                    },
                    "sort": {
                        "type": "string",
                        "enum": ["hot", "new", "top", "controversial"],
                        "description": "Sort method for posts",
                        "default": "new"
                    },
                    "timeframe": {
                        "type": "string",
                        "enum": ["hour", "day", "week", "month", "year", "all"],
                        "description": "Timeframe for 'top' and 'controversial' sorts",
                        "default": "all"
                    }
                },
                "required": ["username"]
            }
        }
    }
    
    return jsonify(schema) 