# Code Snippets from toollama/API/api-tools/tools/snippets/core/ui/chat/message-manager.js

File: `toollama/API/api-tools/tools/snippets/core/ui/chat/message-manager.js`  
Language: JavaScript  
Extracted: 2025-06-07 05:24:37  

## Snippet 1
Lines 16-23

```JavaScript
createMessageItem(content, type, messagesList) {
        const li = document.createElement("li");
        li.className = `message ${type}`;
        li.innerHTML = this.processMessageContent(content);
        messagesList.appendChild(li);
        return li;
    },
```

## Snippet 2
Lines 30-38

```JavaScript
createMessageElement(content, type) {
        const container = document.createElement('div');
        container.className = `message-container ${type}-container`;
        container.setAttribute('role', 'listitem');

        const message = document.createElement('div');
        message.className = `message ${type}`;
        message.innerHTML = content;
```

## Snippet 3
Lines 41-46

```JavaScript
} else {
            message.setAttribute('aria-label', 'Your message');
        }

        container.appendChild(message);
        return container;
```

## Snippet 4
Lines 54-58

```JavaScript
processMessageContent(content) {
        // Process markdown, links, code blocks, etc.
        return typeof content === 'string' ? content : JSON.stringify(content);
    },
```

## Snippet 5
Lines 64-66

```JavaScript
if (messagesList) {
            messagesList.scrollTop = messagesList.scrollHeight;
        }
```

