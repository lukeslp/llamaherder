# Code Snippets from toollama/API/api-tools/tools/snippets/core/ui/panel/observer.js

File: `toollama/API/api-tools/tools/snippets/core/ui/panel/observer.js`  
Language: JavaScript  
Extracted: 2025-06-07 05:24:43  

## Snippet 1
Lines 12-14

```JavaScript
setupMutationObservers(leftPanelContainer, updateCallback) {
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
```

## Snippet 2
Lines 15-17

```JavaScript
if (mutation.attributeName === "class") {
                    requestAnimationFrame(updateCallback);
                }
```

## Snippet 3
Lines 19-25

```JavaScript
});

        observer.observe(leftPanelContainer, {
            attributes: true,
        });

        return observer;
```

