# Code Snippets from toollama/API/api-tools/tools/snippets/core/ui/chat/display-manager.js

File: `toollama/API/api-tools/tools/snippets/core/ui/chat/display-manager.js`  
Language: JavaScript  
Extracted: 2025-06-07 05:24:34  

## Snippet 1
Lines 17-20

```JavaScript
if (!messagesList) return;

        messagesList.innerHTML = "";
```

## Snippet 2
Lines 21-31

```JavaScript
if (Array.isArray(chatHistory)) {
            chatHistory.forEach((message) => {
                MessageManager.createMessageItem(
                    message.content,
                    message.type,
                    messagesList
                );
            });
        }

        MessageManager.autoScroll();
```

## Snippet 3
Lines 40-43

```JavaScript
if (messagesList) {
            MessageManager.createMessageItem(content, "system-message", messagesList);
            MessageManager.autoScroll();
        }
```

## Snippet 4
Lines 53-62

```JavaScript
if (!toast) return;

        toast.textContent = message;
        toast.setAttribute('aria-hidden', 'false');
        toast.classList.add('show');

        setTimeout(() => {
            toast.classList.remove('show');
            toast.setAttribute('aria-hidden', 'true');
        }, duration);
```

