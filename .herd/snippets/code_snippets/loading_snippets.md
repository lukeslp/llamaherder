# Code Snippets from toollama/API/api-tools/tools/snippets/core/progress/loading.js

File: `toollama/API/api-tools/tools/snippets/core/progress/loading.js`  
Language: JavaScript  
Extracted: 2025-06-07 05:22:27  

## Snippet 1
Lines 16-19

```JavaScript
if (isLoading) {
            button.classList.add("loading");
            button.innerHTML = `<i class="fas fa-spinner fa-spin"></i> ${loadingText}`;
            button.disabled = true;
```

## Snippet 2
Lines 33-38

```JavaScript
async withLoadingState(button, operation, loadingText = 'Processing...') {
        const originalButtonText = button.innerHTML;
        this.setLoadingState(button, true, loadingText);

        try {
            await operation();
```

