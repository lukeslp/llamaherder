# Code Snippets from toollama/API/api-tools/tools/snippets/core/ui/chat/mobile-handler.js

File: `toollama/API/api-tools/tools/snippets/core/ui/chat/mobile-handler.js`  
Language: JavaScript  
Extracted: 2025-06-07 05:24:40  

## Snippet 1
Lines 16-18

```JavaScript
if (window.innerWidth <= 768) {
            // For mobile
            sidePanelsContainer.classList.toggle("active");
```

## Snippet 2
Lines 21-25

```JavaScript
} else {
                setTimeout(() => {
                    inputContainer.style.display = "flex";
                }, 300); // Match the transition duration
            }
```

## Snippet 3
Lines 35-39

```JavaScript
setupMediaQuery() {
        const mediaQuery = window.matchMedia("(max-width: 1050px)");
        mediaQuery.addListener(this.handleMediaQueryChange);
        this.handleMediaQueryChange(mediaQuery);
    }
```

