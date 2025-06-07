# Code Snippets from toollama/API/api-tools/tools/snippets/core/api/counter.js

File: `toollama/API/api-tools/tools/snippets/core/api/counter.js`  
Language: JavaScript  
Extracted: 2025-06-07 05:21:47  

## Snippet 1
Lines 16-26

```JavaScript
async fetchCount() {
        try {
            const response = await fetch(`${API_CONFIG.getBaseUrl()}/image_counter`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'text/event-stream'
                }
            });
            const data = await response.json();
            return data.count;
```

## Snippet 2
Lines 27-30

```JavaScript
} catch (error) {
            console.error("Error fetching image count:", error);
            return null;
        }
```

## Snippet 3
Lines 41-43

```JavaScript
if (messageElement.textContent === "Loading count...") {
                messageElement.textContent = MessageRotator.messages[0];
            }
```

