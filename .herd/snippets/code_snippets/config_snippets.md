# Code Snippets from toollama/API/api-tools/tools/snippets/core/api/config.js

File: `toollama/API/api-tools/tools/snippets/core/api/config.js`  
Language: JavaScript  
Extracted: 2025-06-07 05:21:49  

## Snippet 1
Lines 13-17

```JavaScript
getBaseUrl() {
        return window.location.hostname === "localhost"
            ? "http://localhost:5002"
            : "https://ai.assisted.space";
    }
```

