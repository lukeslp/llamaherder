# Code Snippets from toollama/API/--storage/drummer-websearch.html

File: `toollama/API/--storage/drummer-websearch.html`  
Language: HTML  
Extracted: 2025-06-07 05:17:00  

## Snippet 1
Lines 1-119

```HTML
<!-- File: client/drummer_search.html -->
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Drummer Search</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f9f9f9;
        }
        h1 {
            color: #2c3e50;
            text-align: center;
            margin-bottom: 30px;
        }
        .search-container {
            background: white;
            border-radius: 8px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            padding: 20px;
            margin-bottom: 30px;
        }
        .search-form {
            display: flex;
            flex-direction: column;
            gap: 15px;
        }
        .input-row {
            display: flex;
            gap: 15px;
            align-items: center;
        }
        label {
            font-weight: bold;
            min-width: 100px;
        }
        input[type="text"] {
            flex: 1;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 16px;
        }
        select {
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 16px;
            background-color: white;
        }
        button {
            background-color: #2c3e50;
            color: white;
            border: none;
            padding: 12px 24px;
            font-size: 16px;
            border-radius: 4px;
            cursor: pointer;
            transition: background-color 0.3s;
        }
        button:hover {
            background-color: #1a252f;
        }
        .results-container {
            background: white;
            border-radius: 8px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            padding: 20px;
            margin-top: 30px;
        }
        .status-container {
            margin-top: 20px;
            padding: 15px;
            background-color: #f2f2f2;
            border-radius: 4px;
        }
        .progress-bar {
            height: 20px;
            background-color: #e0e0e0;
            border-radius: 10px;
            margin-top: 10px;
            overflow: hidden;
        }
        .progress-fill {
            height: 100%;
            background-color: #3498db;
            width: 0%;
            transition: width 0.5s ease;
        }
        .summary-content {
            margin-top: 20px;
            padding: 20px;
            border: 1px solid #ddd;
            border-radius: 4px;
            background-color: #f9f9f9;
            white-space: pre-wrap;
        }
        .references {
            margin-top: 20px;
            padding: 20px;
            border-top: 1px solid #ddd;
        }
        .loading {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid rgba(0,0,0,.3);
            border-radius: 50%;
            border-top-color: #3498db;
            animation: spin 1s ease-in-out infinite;
            margin-left: 10px;
        }
```

## Snippet 2
Lines 124-165

```HTML
</head>
<body>
    <h1>Drummer Search</h1>

    <div class="search-container">
        <div class="search-form">
            <div class="input-row">
                <label for="query">Search Query:</label>
                <input type="text" id="query" placeholder="Enter your search query...">
            </div>
            <div class="input-row">
                <label for="model-size">Model Size:</label>
                <select id="model-size">
                    <option value="small">Small (3B) - Fastest</option>
                    <option value="medium">Medium (7B) - Balanced</option>
                    <option value="large" selected>Large (24B) - Most Comprehensive</option>
                </select>
            </div>
            <button id="search-button">Search</button>
        </div>
    </div>

    <div class="status-container" id="status-container" style="display: none;">
        <h3>Search Status: <span id="status-text">Initializing...</span></h3>
        <div class="progress-bar">
            <div class="progress-fill" id="progress-fill"></div>
        </div>
        <p id="step-description">Starting search...</p>
    </div>

    <div class="results-container" id="results-container" style="display: none;">
        <h2>Search Results</h2>
        <div class="summary-content" id="summary-content"></div>
    </div>

    <script>
        const API_BASE_URL = 'https://api.assisted.space/v2';
        let workflowId = null;
        let statusCheckInterval = null;

        document.getElementById('search-button').addEventListener('click', startSearch);
```

## Snippet 3
Lines 167-175

```HTML
function createJsonpRequest(url, callback) {
            const callbackName = 'jsonp_callback_' + Math.round(100000 * Math.random());
            window[callbackName] = function(data) {
                delete window[callbackName];
                document.body.removeChild(script);
                callback(data);
            };

            // For POST requests, we'll add the data as URL parameters
```

## Snippet 4
Lines 178-184

```HTML
} else {
                url += '?callback=' + callbackName;
            }

            const script = document.createElement('script');
            script.src = url;
            document.body.appendChild(script);
```

## Snippet 5
Lines 188-195

```HTML
function createProxyIframe() {
            const iframe = document.createElement('iframe');
            iframe.style.display = 'none';
            iframe.id = 'proxy-iframe';
            document.body.appendChild(iframe);
            return iframe;
        }
```

## Snippet 6
Lines 198-232

```HTML
if (!query) {
                alert('Please enter a search query');
                return;
            }

            const modelSize = document.getElementById('model-size').value;
            const searchButton = document.getElementById('search-button');
            const modelValue = `coolhand/drummer-search:${modelSize.replace('small', '3b').replace('medium', '7b').replace('large', '24b')}`;

            // Update UI
            searchButton.disabled = true;
            searchButton.innerHTML = 'Searching...<span class="loading"></span>';
            document.getElementById('status-container').style.display = 'block';
            document.getElementById('results-container').style.display = 'none';
            document.getElementById('status-text').textContent = 'Starting...';
            document.getElementById('progress-fill').style.width = '0%';
            document.getElementById('step-description').textContent = 'Initializing search workflow...';

            try {
                // Prepare request data
                const requestData = {
                    query: query,
                    workflow_type: 'swarm',
                    model: modelValue
                };

                // Make the API request
                const response = await fetch(`${API_BASE_URL}/dreamwalker/search`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(requestData)
                });
```

## Snippet 7
Lines 233-244

```HTML
if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(errorData.error || `HTTP error ${response.status}`);
                }

                const data = await response.json();

                // Update UI with response
                document.getElementById('status-text').textContent = data.status || 'Initialized';
                document.getElementById('progress-fill').style.width = `${data.progress || 0}%`;
                document.getElementById('step-description').textContent = data.step_description || 'Processing request...';
```

## Snippet 8
Lines 248-254

```HTML
// Start polling for status updates
                statusCheckInterval = setInterval(checkWorkflowStatus, 2000);

                // Update button state
                searchButton.disabled = false;
                searchButton.innerHTML = 'Start New Search';
```

## Snippet 9
Lines 255-260

```HTML
} catch (error) {
                handleError(`Error: ${error.message}`);
                console.error(error);
                searchButton.disabled = false;
                searchButton.innerHTML = 'Search';
            }
```

## Snippet 10
Lines 264-268

```HTML
if (!workflowId) return;

            try {
                const response = await fetch(`${API_BASE_URL}/dreamwalker/status/${workflowId}`);
```

## Snippet 11
Lines 269-278

```HTML
if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(errorData.error || `HTTP error ${response.status}`);
                }

                const data = await response.json();

                // Update status display
                updateStatus(data);
```

## Snippet 12
Lines 280-282

```HTML
if (data.status === 'completed') {
                    clearInterval(statusCheckInterval);
                    fetchWorkflowResults();
```

## Snippet 13
Lines 283-286

```HTML
} else if (data.status === 'failed') {
                    clearInterval(statusCheckInterval);
                    handleError(data.error || 'Search failed');
                }
```

## Snippet 14
Lines 287-290

```HTML
} catch (error) {
                handleError(`Error checking status: ${error.message}`);
                clearInterval(statusCheckInterval);
            }
```

## Snippet 15
Lines 293-296

```HTML
async function fetchWorkflowResults() {
            try {
                const response = await fetch(`${API_BASE_URL}/dreamwalker/result/${workflowId}`);
```

## Snippet 16
Lines 297-309

```HTML
if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(errorData.error || `HTTP error ${response.status}`);
                }

                const data = await response.json();

                // Display the results
                displayResults(data);

                // Update button state
                document.getElementById('search-button').disabled = false;
                document.getElementById('search-button').textContent = 'Search';
```

## Snippet 17
Lines 310-312

```HTML
} catch (error) {
                handleError(`Error fetching results: ${error.message}`);
            }
```

## Snippet 18
Lines 315-320

```HTML
function updateStatus(data) {
            document.getElementById('status-text').textContent = data.status;
            document.getElementById('progress-fill').style.width = `${data.progress}%`;
            document.getElementById('step-description').textContent = data.step_description || 'Processing...';
        }
```

## Snippet 19
Lines 321-328

```HTML
function handleError(errorMessage) {
            clearInterval(statusCheckInterval);
            document.getElementById('status-text').textContent = 'Error';
            document.getElementById('step-description').textContent = errorMessage;
            document.getElementById('search-button').disabled = false;
            document.getElementById('search-button').textContent = 'Search';
        }
```

## Snippet 20
Lines 329-344

```HTML
function displayResults(data) {
            const resultsContainer = document.getElementById('results-container');
            const summaryContent = document.getElementById('summary-content');

            resultsContainer.style.display = 'block';

            // Get the summary from the results
            const summary = data.results?.summary || 'No summary available';

            // Convert Markdown to HTML (basic implementation)
            let htmlContent = convertMarkdownToHtml(summary);

            // Display the content
            summaryContent.innerHTML = htmlContent;
        }
```

## Snippet 21
Lines 345-356

```HTML
function convertMarkdownToHtml(markdown) {
            // Very basic Markdown to HTML conversion
            // Headers
            let html = markdown
                .replace(/^### (.*$)/gim, '<h3>$1</h3>')
                .replace(/^## (.*$)/gim, '<h2>$1</h2>')
                .replace(/^# (.*$)/gim, '<h1>$1</h1>');

            // Links
            html = html.replace(/\[([^\]]+)\]\(([^)]+)\)/gim, '<a href="$2" target="_blank">$1</a>');

            // Bold
```

## Snippet 22
Lines 357-359

```HTML
html = html.replace(/\*\*(.*?)\*\*/gim, '<strong>$1</strong>');

            // Italic
```

## Snippet 23
Lines 360-374

```HTML
html = html.replace(/\*(.*?)\*/gim, '<em>$1</em>');

            // Lists
            html = html.replace(/^\s*\- (.*$)/gim, '<li>$1</li>');
            html = html.replace(/<\/li>\n<li>/g, '</li><li>');
            html = html.replace(/(<li>.*<\/li>)/gim, '<ul>$1</ul>');

            // Paragraphs
            html = html.replace(/^\s*(.+)$/gim, '<p>$1</p>');

            // Clean up extra paragraph tags around other elements
            html = html.replace(/<p><(h|ul|ol|li)[1-3]>/gim, '<$1>');
            html = html.replace(/<\/(h|ul|ol|li)[1-3]><\/p>/gim, '</$1>');

            return html;
```

