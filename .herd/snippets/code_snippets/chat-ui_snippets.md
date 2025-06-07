# Code Snippets from toollama/API/api-tools/tools/snippets/processed/chat-ui.js

File: `toollama/API/api-tools/tools/snippets/processed/chat-ui.js`  
Language: JavaScript  
Extracted: 2025-06-07 05:21:32  

## Snippet 1
Lines 6-24

```JavaScript
// Message Creation and Management
export const MessageManager = {
    createMessageItem(content, type, messagesList) {
        const li = document.createElement("li");
        li.className = `message ${type}`;
        li.innerHTML = this.processMessageContent(content);
        messagesList.appendChild(li);
        return li;
    },

    createMessageElement(content, type) {
        const container = document.createElement('div');
        container.className = `message-container ${type}-container`;
        container.setAttribute('role', 'listitem');

        const message = document.createElement('div');
        message.className = `message ${type}`;
        message.innerHTML = content;
```

## Snippet 2
Lines 27-32

```JavaScript
} else {
            message.setAttribute('aria-label', 'Your message');
        }

        container.appendChild(message);
        return container;
```

## Snippet 3
Lines 33-41

```JavaScript
},

    processMessageContent(content) {
        // Process markdown, links, code blocks, etc.
        return typeof content === 'string' ? content : JSON.stringify(content);
    },

    autoScroll() {
        const messagesList = document.getElementById("messages");
```

## Snippet 4
Lines 42-44

```JavaScript
if (messagesList) {
            messagesList.scrollTop = messagesList.scrollHeight;
        }
```

## Snippet 5
Lines 46-51

```JavaScript
};

// Input Container Management
export const InputManager = {
    setupEventListeners(messageInput, sendButton, sendMessageCallback) {
        messageInput.addEventListener("keypress", (event) => {
```

## Snippet 6
Lines 52-55

```JavaScript
if (event.key === "Enter" && !event.shiftKey) {
                event.preventDefault();
                sendMessageCallback();
            }
```

## Snippet 7
Lines 56-67

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

## Snippet 8
Lines 68-79

```JavaScript
},

    updateInputContainerGeometry(inputContainer, leftPanel, rightPanel) {
        const rightWidth = rightPanel && rightPanel.classList.contains("open")
            ? rightPanel.offsetWidth
            : 0;

        const leftWidth = leftPanel && !leftPanel.classList.contains("closed")
            ? leftPanel.offsetWidth
            : 0;

        requestAnimationFrame(() => {
```

## Snippet 9
Lines 80-84

```JavaScript
if (inputContainer) {
                inputContainer.style.width = `calc(100% - ${leftWidth}px - ${rightWidth}px)`;
                inputContainer.style.right = `${rightWidth}px`;
                inputContainer.style.left = `${leftWidth}px`;
            }
```

## Snippet 10
Lines 87-91

```JavaScript
};

// Mobile Responsiveness
export const MobileHandler = {
    handleMobilePanel(panelId, sidePanelsContainer, inputContainer) {
```

## Snippet 11
Lines 92-94

```JavaScript
if (window.innerWidth <= 768) {
            // For mobile
            sidePanelsContainer.classList.toggle("active");
```

## Snippet 12
Lines 97-101

```JavaScript
} else {
                setTimeout(() => {
                    inputContainer.style.display = "flex";
                }, 300); // Match the transition duration
            }
```

## Snippet 13
Lines 106-112

```JavaScript
},

    setupMediaQuery() {
        const mediaQuery = window.matchMedia("(max-width: 1050px)");
        mediaQuery.addListener(this.handleMediaQueryChange);
        this.handleMediaQueryChange(mediaQuery);
    }
```

## Snippet 14
Lines 113-118

```JavaScript
};

// Chat Display Updates
export const ChatDisplayManager = {
    updateChatDisplay(chatHistory = []) {
        const messagesList = document.getElementById("messages");
```

## Snippet 15
Lines 119-122

```JavaScript
if (!messagesList) return;

        messagesList.innerHTML = "";
```

## Snippet 16
Lines 123-133

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

## Snippet 17
Lines 134-137

```JavaScript
},

    addSystemMessage(content) {
        const messagesList = document.getElementById("messages");
```

## Snippet 18
Lines 138-141

```JavaScript
if (messagesList) {
            MessageManager.createMessageItem(content, "system-message", messagesList);
            MessageManager.autoScroll();
        }
```

## Snippet 19
Lines 142-145

```JavaScript
},

    showToast(message, duration = 3000) {
        const toast = document.getElementById('toast');
```

## Snippet 20
Lines 146-155

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

