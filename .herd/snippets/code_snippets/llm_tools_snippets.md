# Code Snippets from toollama/API/api-tools/tools/Untitled/llm_tools.py

File: `toollama/API/api-tools/tools/Untitled/llm_tools.py`  
Language: Python  
Extracted: 2025-06-07 05:19:58  

## Snippet 1
Lines 1-6

```Python
from typing import Dict, Optional, List, Union
import requests
import json
import os
from datetime import datetime
```

## Snippet 2
Lines 13-24

```Python
async def fetch_citation(self, doi: str) -> Dict:
        """
        Fetch citation data from CrossRef API.
        Referenced from from_markdown.js lines 96-105
        """
        try:
            response = await requests.get(f"https://api.crossref.org/works/{doi}")
            return response.json()["message"]
        except Exception as e:
            print(f"Citation fetch failed: {e}")
            return None
```

## Snippet 3
Lines 25-38

```Python
def process_file_embed(self, file: Dict, file_url: str) -> str:
        """
        Generate appropriate embed HTML based on file type.
        Referenced from from_utils.js lines 1388-1415
        """
        file_ext = file["name"].split(".")[-1].lower()

        # Code files
        code_extensions = {
            'js', 'jsx', 'ts', 'tsx', 'py', 'java', 'cpp', 'c', 'cs',
            'php', 'rb', 'go', 'rs', 'swift', 'kt', 'dart', 'sql',
            'html', 'css', 'scss', 'less', 'json', 'xml', 'yaml', 'yml', 'toml'
        }
```

## Snippet 4
Lines 39-42

```Python
if file_ext in code_extensions:
            return f"```{file_ext}\n{file['name']}\n```"

        # Markdown files
```

## Snippet 5
Lines 43-46

```Python
if file_ext in ['md', 'markdown']:
            return f"[View Markdown: {file['name']}]({file_url})"

        # Text files
```

## Snippet 6
Lines 47-58

```Python
if file["type"] == "text/plain" or file_ext in ['txt', 'log', 'csv', 'tsv']:
            return f'<div class="text-embed-container" data-file-url="{file_url}">\n' \
                   f'    <pre class="text-content">Loading text content...</pre>\n' \
                   f'</div>'

        # Default fallback
        return f'<div class="file-embed-container">\n' \
               f'    <a href="{file_url}" target="_blank" rel="noopener noreferrer">\n' \
               f'        <i class="fas fa-file"></i> {file["name"]}\n' \
               f'    </a>\n' \
               f'</div>'
```

## Snippet 7
Lines 61-84

```Python
Get list of supported MIME types for file processing.
        Referenced from from_simple_alt_text.js lines 140-185
        """
        return [
            # Image Formats
            'image/jpeg', 'image/jpg', 'image/png', 'image/gif',
            'image/webp', 'image/heic', 'image/heif', 'image/avif',
            'image/tiff', 'image/bmp', 'image/x-icon',
            'image/vnd.microsoft.icon', 'image/svg+xml',
            'image/vnd.adobe.photoshop', 'image/x-adobe-dng',
            'image/x-canon-cr2', 'image/x-nikon-nef',
            'image/x-sony-arw', 'image/x-fuji-raf',
            'image/x-olympus-orf', 'image/x-panasonic-rw2',
            'image/x-rgb', 'image/x-portable-pixmap',
            'image/x-portable-graymap', 'image/x-portable-bitmap',
            # Video Formats
            'video/mp4', 'video/quicktime', 'video/webm',
            'video/x-msvideo', 'video/x-flv', 'video/x-ms-wmv',
            'video/x-matroska', 'video/3gpp', 'video/x-m4v',
            'video/x-ms-asf', 'video/x-mpegURL', 'video/x-ms-vob',
            'video/x-ms-tmp', 'video/x-mpeg', 'video/mp2t',
            'application/octet-stream'
        ]
```

## Snippet 8
Lines 85-107

```Python
def initialize_markdown(self, html: bool = True, breaks: bool = True) -> Dict:
        """
        Initialize markdown parser configuration.
        Referenced from from_markdown.js lines 2-43
        """
        return {
            "html": html,
            "breaks": breaks,
            "linkify": True,
            "typographer": True,
            "highlight": True,
            "plugins": [
                "markdownit-task-lists",
                "markdownit-footnote",
                "markdownit-sub",
                "markdownit-sup",
                "markdownit-deflist",
                "markdownit-abbr",
                "markdownit-mark",
                "markdownit-multimd-table",
                "markdownit-katex"
            ]
        }
```

