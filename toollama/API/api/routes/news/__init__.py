from flask import Blueprint, jsonify

# Create the news blueprint
news_bp = Blueprint('news', __name__)

# Import all routes
from api.routes.news import bbc, nyt, guardian

# Return the blueprint for registration
def get_blueprint():
    return news_bp

@news_bp.route('/schemas', methods=['GET'])
def get_news_schemas():
    """Get all available news API schemas."""
    return jsonify({
        "bbc": {
            "feed": {
                "name": "bbc_news_feed",
                "description": "Get the latest news articles from BBC News",
                "endpoint": "/v2/news/bbc/feed",
                "method": "GET, POST"
            },
            "content": {
                "name": "bbc_news_content",
                "description": "Get the full content of a BBC News article",
                "endpoint": "/v2/news/bbc/content",
                "method": "GET, POST"
            }
        },
        "nyt": {
            "search": {
                "name": "nyt_search",
                "description": "Search for New York Times articles",
                "endpoint": "/v2/news/nyt/search",
                "method": "GET, POST"
            },
            "top": {
                "name": "nyt_top_stories",
                "description": "Get the top stories from the New York Times",
                "endpoint": "/v2/news/nyt/top",
                "method": "GET, POST"
            }
        },
        "guardian": {
            "search": {
                "name": "guardian_search",
                "description": "Search for articles from The Guardian",
                "endpoint": "/v2/news/guardian/search",
                "method": "GET, POST"
            },
            "section": {
                "name": "guardian_section",
                "description": "Get the latest articles from a specific Guardian section",
                "endpoint": "/v2/news/guardian/section/{section_id}",
                "method": "GET, POST"
            },
            "article": {
                "name": "guardian_article",
                "description": "Get the full content of a specific Guardian article",
                "endpoint": "/v2/news/guardian/article/{article_id}",
                "method": "GET, POST"
            }
        }
    }) 