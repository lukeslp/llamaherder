# Code Snippets from toollama/API/api-tools/tools/snippets/core/ui/interaction/scroll.js

File: `toollama/API/api-tools/tools/snippets/core/ui/interaction/scroll.js`  
Language: JavaScript  
Extracted: 2025-06-07 05:23:57  

## Snippet 1
Lines 7-23

```JavaScript
if (!container) return;

        // Auto-scroll on content change
        const autoScroll = () => {
            container.scrollTop = container.scrollHeight;
        };

        // Smooth scroll to bottom
        const smoothScrollToBottom = () => {
            container.scrollTo({
                top: container.scrollHeight,
                behavior: 'smooth'
            });
        };

        // Handle scroll events
        container.addEventListener('scroll', () => {
```

## Snippet 2
Lines 24-26

```JavaScript
if (container.scrollTop + container.clientHeight >= container.scrollHeight - 10) {
                // User has scrolled to bottom
                container.dataset.autoScroll = 'true';
```

## Snippet 3
Lines 31-37

```JavaScript
});

        return {
            autoScroll,
            smoothScrollToBottom,
            isAtBottom: () => container.dataset.autoScroll === 'true'
        };
```

