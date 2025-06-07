# AI Image Generator

A web-based interface for generating images using AI models from OpenAI (DALL-E), X.AI (Grok), and Google Gemini.

## Features

- Generate images using multiple AI providers
- Select from different models per provider
- Adjust quality, style, and size settings
- Download generated images
- Regenerate images with the same prompt

## Running the Application

### Method 1: Using the Development Server

The easiest way to run the application is using the provided Flask development server:

1. Install the requirements:
   ```
   pip install flask requests
   ```

2. Run the server:
   ```
   python server.py
   ```

3. Open your browser and navigate to: `http://localhost:8000`

This method automatically handles CORS and proxies API requests to the proper server.

### Method 2: Using a Web Server

If you want to deploy the application on a web server:

1. Copy the contents of the `static` directory to your web server's root or public directory
2. Ensure your server is properly configured for CORS if you're making cross-origin requests
3. Update the `API_BASE_URL` in `app.js` if necessary

## API Server Configuration

The application expects the API server to implement these endpoints:

- `GET /v2` - API information endpoint
- `POST /v2/generate` - Image generation endpoint

## Development

The application includes:

- `static/index.html` - Main HTML structure
- `static/styles.css` - CSS styling
- `static/app.js` - JavaScript for application logic
- `server.py` - Development server and API proxy

## Troubleshooting

### CORS Errors

If you see CORS errors:

1. Make sure you're running the page through a web server (not opening the HTML file directly)
2. Use the provided `server.py` which handles CORS headers automatically
3. Check browser console for specific errors

### API Connectivity Issues

The app will automatically try to connect to:
1. The configured API URL (api.assisted.space)
2. A local server at `http://localhost:8000`
3. A local server at `http://localhost:5000`

If all fail, the application will display an error message.

## License

MIT 