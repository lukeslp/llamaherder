# Code Snippets from toollama/API/api-tools/tools/snippets/core/ui/interaction/toast.js

File: `toollama/API/api-tools/tools/snippets/core/ui/interaction/toast.js`  
Language: JavaScript  
Extracted: 2025-06-07 05:24:29  

## Snippet 1
Lines 5-7

```JavaScript
export const ToastManager = {
    setupToast(containerId = 'toast', defaultDuration = 3000) {
        const toastElement = document.getElementById(containerId);
```

## Snippet 2
Lines 8-22

```JavaScript
if (!toastElement) return null;

        return {
            show: (message, duration = defaultDuration) => {
                toastElement.textContent = message;
                toastElement.classList.add('show');

                setTimeout(() => {
                    toastElement.classList.remove('show');
                }, duration);
            },
            hide: () => {
                toastElement.classList.remove('show');
            }
        };
```

