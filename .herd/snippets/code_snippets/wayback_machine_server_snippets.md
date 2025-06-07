# Code Snippets from toollama/API/api-tools/wayback_machine_server.py

File: `toollama/API/api-tools/wayback_machine_server.py`  
Language: Python  
Extracted: 2025-06-07 05:16:29  

## Snippet 1
Lines 1-5

```Python
from flask import Flask, request, redirect, render_template_string
from waybackpy.cdx_api import CDXApi as WaybackMachineCDXServerAPI

app = Flask(__name__)
```

## Snippet 2
Lines 6-29

```Python
# HTML template for the index page
INDEX_HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Wayback Machine Redirector</title>
</head>
<body>
    <h1>Wayback Machine Redirector</h1>
    <p>Enter a URL to find its most recent archived version:</p>
    <form action="/search" method="post">
        <input type="url" name="url" placeholder="https://example.com" required style="width:300px; padding:5px;">
        <button type="submit" style="padding:5px 10px;">Find Archive</button>
    </form>
</body>
</html>
"""

# Define a User-Agent string to mimic a real browser.
USER_AGENT = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
              "AppleWebKit/537.36 (KHTML, like Gecko) "
              "Chrome/90.0.4430.93 Safari/537.36")
```

## Snippet 3
Lines 37-40

```Python
if not target_url:
        return "Error: No URL provided", 400

    try:
```

## Snippet 4
Lines 41-45

```Python
# Create a WaybackMachineCDXServerAPI instance for the target URL.
        wayback = WaybackMachineCDXServerAPI(target_url, USER_AGENT)
        # Retrieve the most recent snapshot.
        snapshot = wayback.newest()
        archive_url = snapshot.archive_url  # This property holds the archived URL.
```

## Snippet 5
Lines 49-51

```Python
if archive_url:
        return redirect(archive_url)
    else:
```

