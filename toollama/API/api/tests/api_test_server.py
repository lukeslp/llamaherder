#!/usr/bin/env python
"""
API Test Server

This script serves the API test page and can run tests against the Camina Chat API.
"""

import os
import sys
import json
import argparse
import webbrowser
from http.server import HTTPServer, SimpleHTTPRequestHandler
from functools import partial
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('api_test_server')

# Default port for the test server
DEFAULT_PORT = 8000

# Default API URL
DEFAULT_API_URL = "https://api.assisted.space/v2"

class APITestHandler(SimpleHTTPRequestHandler):
    """Custom HTTP request handler for the API test server."""
    
    def __init__(self, api_url, *args, **kwargs):
        self.api_url = api_url
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        """Handle GET requests."""
        # Serve static files
        if self.path == '/':
            self.path = '/static/apitest.html'
        elif self.path == '/apitest':
            self.path = '/static/apitest.html'
            
        # Find the project root directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)
        
        # Set the directory to serve files from
        os.chdir(project_root)
        
        return SimpleHTTPRequestHandler.do_GET(self)
    
    def log_message(self, format, *args):
        """Override to use our logger."""
        logger.info("%s - %s", self.address_string(), format % args)

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Run the API test server')
    parser.add_argument(
        '--port', 
        type=int, 
        default=DEFAULT_PORT,
        help=f'Port to run the server on (default: {DEFAULT_PORT})'
    )
    parser.add_argument(
        '--api-url',
        type=str,
        default=DEFAULT_API_URL,
        help=f'Base URL for the API (default: {DEFAULT_API_URL})'
    )
    parser.add_argument(
        '--no-browser',
        action='store_true',
        help='Do not open the browser automatically'
    )
    
    return parser.parse_args()

def main():
    """Main function."""
    args = parse_args()
    
    # Create the server
    handler = partial(APITestHandler, args.api_url)
    server = HTTPServer(('localhost', args.port), handler)
    
    # Log server information
    logger.info(f"Starting API test server at http://localhost:{args.port}/")
    logger.info(f"API URL: {args.api_url}")
    logger.info("Press Ctrl+C to quit")
    
    # Open the browser if requested
    if not args.no_browser:
        webbrowser.open(f"http://localhost:{args.port}/")
    
    try:
        # Start the server
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    finally:
        # Clean up
        server.server_close()
        logger.info("Server stopped")
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 