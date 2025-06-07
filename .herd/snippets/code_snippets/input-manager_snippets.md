# Code Snippets from toollama/API/api-tools/tools/snippets/core/ui/chat/input-manager.js

File: `toollama/API/api-tools/tools/snippets/core/ui/chat/input-manager.js`  
Language: JavaScript  
Extracted: 2025-06-07 05:24:35  

## Snippet 1
Lines 17-20

```JavaScript
if (event.key === "Enter" && !event.shiftKey) {
                event.preventDefault();
                sendMessageCallback();
            }
```

## Snippet 2
Lines 21-32

```JavaScript
});

        sendButton.addEventListener("click", (event) => {
            event.preventDefault();
            sendMessageCallback();
        });

        // Auto-resize textarea
        messageInput.addEventListener('input', () => {
            messageInput.style.height = 'auto';
            messageInput.style.height = messageInput.scrollHeight + 'px';
        });
```

## Snippet 3
Lines 41-50

```JavaScript
updateInputContainerGeometry(inputContainer, leftPanel, rightPanel) {
        const rightWidth = rightPanel && rightPanel.classList.contains("open")
            ? rightPanel.offsetWidth
            : 0;

        const leftWidth = leftPanel && !leftPanel.classList.contains("closed")
            ? leftPanel.offsetWidth
            : 0;

        requestAnimationFrame(() => {
```

## Snippet 4
Lines 51-55

```JavaScript
if (inputContainer) {
                inputContainer.style.width = `calc(100% - ${leftWidth}px - ${rightWidth}px)`;
                inputContainer.style.right = `${rightWidth}px`;
                inputContainer.style.left = `${leftWidth}px`;
            }
```

