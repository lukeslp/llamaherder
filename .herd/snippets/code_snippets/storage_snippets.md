# Code Snippets from toollama/API/api-tools/tools/snippets/core/session/storage.js

File: `toollama/API/api-tools/tools/snippets/core/session/storage.js`  
Language: JavaScript  
Extracted: 2025-06-07 05:22:59  

## Snippet 1
Lines 8-11

```JavaScript
export const SessionManager = {
    SESSION_STORAGE_KEY: "chat_session",
    CHAT_HISTORY_KEY: "chatHistory",
```

## Snippet 2
Lines 17-25

```JavaScript
saveSession(messages, currentAssistant) {
        const sessionData = {
            messages,
            currentAssistant,
            timestamp: Date.now()
        };
        localStorage.setItem(this.SESSION_STORAGE_KEY, JSON.stringify(sessionData));
    },
```

## Snippet 3
Lines 61-65

```JavaScript
loadChatHistory() {
        const saved = localStorage.getItem(this.CHAT_HISTORY_KEY);
        return saved ? JSON.parse(saved) : [];
    },
```

## Snippet 4
Lines 70-74

```JavaScript
clearChatHistory() {
        localStorage.removeItem(this.CHAT_HISTORY_KEY);
        return [];
    },
```

## Snippet 5
Lines 79-82

```JavaScript
initializeChatHistory() {
        window.chatHistory = this.loadChatHistory();
        return window.chatHistory;
    }
```

