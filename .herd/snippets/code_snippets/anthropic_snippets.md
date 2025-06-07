# Code Snippets from toollama/API/api-tools/tools/llm/anthropic/anthropic.html

File: `toollama/API/api-tools/tools/llm/anthropic/anthropic.html`  
Language: HTML  
Extracted: 2025-06-07 05:20:46  

## Snippet 1
Lines 1-34

```HTML
<!DOCTYPE html>
<html lang="en">
  <head>
    <link rel="icon" href="/assets/favicons/fav_spiral_light.ico" type="image/x-icon">
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Anthropic - Claude AI Assistant</title>

    <!-- Primary Meta Tags -->
    <meta name="title" content="Anthropic">
    <meta name="description" content="Anthropic - Claude AI Assistant">
    <meta name="keywords" content="Anthropic, Claude, AI, Assistant, Language Model, Accessibility">

    <!-- Open Graph / Facebook -->
    <meta property="og:type" content="website">
    <meta property="og:url" content="https://clean.luke.studio/anthropic/">
    <meta property="og:title" content="Anthropic">
    <meta property="og:description" content="Anthropic - Claude AI Assistant">
    <meta property="og:image" content="https://i.imgur.com/YeAwK6f.gif">

    <!-- Twitter -->
    <meta property="twitter:card" content="summary_large_image">
    <meta property="twitter:url" content="https://clean.luke.studio/anthropic/">
    <meta property="twitter:title" content="Anthropic">
    <meta property="twitter:description" content="Anthropic - Claude AI Assistant">
    <meta property="twitter:image" content="https://i.imgur.com/YeAwK6f.gif">

    <!-- Accessibility -->
    <meta name="theme-color" content="#2c1810">

    <!-- Markdown Libraries -->
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.7.0/highlight.min.js"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.7.0/styles/github.min.css">
```

## Snippet 2
Lines 35-38

```HTML
<!-- DOMPurify for sanitizing HTML -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/dompurify/3.0.9/purify.min.js"></script>

    <style>
```

## Snippet 3
Lines 39-51

```HTML
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;1,400&display=swap');

      :root {
        --primary-color: #2c1810;
        --secondary-color: #1a0f0a;
        --background-color: #f4f1ea;
        --message-bg: #fff;
        --user-message-bg: #f9f7f3;
        --border-color: #e0d9c8;
        --text-color: #333;
        --metadata-color: #94a3b8;
      }
```

## Snippet 4
Lines 53-65

```HTML
@media (prefers-color-scheme: dark) {
        :root {
          --primary-color: #5e493f;
          --secondary-color: #3b2a20;
          --background-color: #1a1a1a;
          --message-bg: #2a2a2a;
          --user-message-bg: #333333;
          --border-color: #444444;
          --text-color: #e0e0e0;
          --metadata-color: #a0a0a0;
        }
      }
```

## Snippet 5
Lines 66-83

```HTML
/* Focus styles for accessibility */
      *:focus {
        outline: 3px solid #4d90fe;
        outline-offset: 2px;
      }

      body {
        display: flex;
        flex-direction: column;
        height: 100vh;
        margin: 0;
        font-family: 'Playfair Display', serif;
        background: var(--background-color);
        padding: 20px;
        color: var(--text-color);
        transition: background-color 0.3s, color 0.3s;
      }
```

## Snippet 6
Lines 84-164

```HTML
/* Toast Notifications */
      .toast-container {
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 1000;
        display: flex;
        flex-direction: column;
        gap: 10px;
        max-width: 350px;
      }

      .toast {
        display: flex;
        align-items: center;
        padding: 12px 16px;
        background-color: var(--message-bg);
        color: var(--text-color);
        border-radius: 4px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        opacity: 0;
        transform: translateY(-20px);
        transition: opacity 0.3s, transform 0.3s;
        margin-bottom: 10px;
      }

      .toast.show {
        opacity: 1;
        transform: translateY(0);
      }

      .toast svg {
        width: 20px;
        height: 20px;
        margin-right: 12px;
        flex-shrink: 0;
      }

      .toast .message {
        flex: 1;
        font-size: 14px;
      }

      .toast .close-button {
        background: none;
        border: none;
        padding: 4px;
        cursor: pointer;
        opacity: 0.6;
        transition: opacity 0.2s;
        color: var(--text-color);
      }

      .toast .close-button:hover {
        opacity: 1;
      }

      .toast.success {
        border-left: 4px solid #10b981;
      }

      .toast.success svg {
        color: #10b981;
      }

      .toast.error {
        border-left: 4px solid #ef4444;
      }

      .toast.error svg {
        color: #ef4444;
      }

      .toast.info {
        border-left: 4px solid #3b82f6;
      }

      .toast.info svg {
        color: #3b82f6;
      }
```

## Snippet 7
Lines 165-187

```HTML
/* Loading spinner */
      .loading-spinner {
        display: none;
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-color: rgba(0, 0, 0, 0.1);
        z-index: 999;
        justify-content: center;
        align-items: center;
      }

      .spinner {
        width: 40px;
        height: 40px;
        border: 4px solid rgba(255, 255, 255, 0.5);
        border-radius: 50%;
        border-top-color: var(--primary-color);
        animation: spin 1s linear infinite;
      }
```

## Snippet 8
Lines 193-350

```HTML
/* Loading state for send button */
      #sendButton.loading {
        background-color: var(--secondary-color);
        cursor: not-allowed;
        opacity: 0.7;
      }

      .chat-container {
        flex: 1;
        display: flex;
        flex-direction: column;
        background: var(--message-bg);
        padding: 40px;
        overflow-y: auto;
        box-shadow: 0 0 10px rgba(0,0,0,0.1);
        border: 1px solid var(--border-color);
        max-width: 800px;
        margin: 0 auto;
        width: 100%;
        box-sizing: border-box;
        transition: background-color 0.3s, border-color 0.3s;
      }

      .message-container {
        flex: 1;
        overflow-y: auto;
        display: flex;
        flex-direction: column;
        gap: 20px;
      }

      .message-wrapper {
        display: flex;
        flex-direction: column;
        gap: 8px;
        position: relative;
      }

      .message-actions {
        position: absolute;
        top: 0;
        right: 0;
        display: none;
        gap: 8px;
        padding: 5px;
      }

      .message-wrapper:hover .message-actions {
        display: flex;
      }

      .copy-btn {
        background: transparent;
        border: none;
        cursor: pointer;
        color: var(--metadata-color);
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 4px;
        border-radius: 4px;
        transition: background-color 0.2s;
      }

      .copy-btn:hover {
        background-color: rgba(0, 0, 0, 0.05);
        color: var(--primary-color);
      }

      .copy-btn svg {
        width: 16px;
        height: 16px;
      }

      .message {
        padding: 12px;
        border-radius: 0;
        word-wrap: break-word;
        font-size: 17px;
        line-height: 1.8;
        border-bottom: 1px solid var(--border-color);
        transition: background-color 0.3s, border-color 0.3s;
      }

      .user-message {
        background-color: var(--user-message-bg);
        font-style: italic;
        text-align: right;
      }

      .bot-message {
        text-align: justify;
        letter-spacing: 0.3px;
        text-indent: 20px;
        font-weight: 400;
      }

      .message-metadata {
        display: flex;
        justify-content: flex-end;
        gap: 10px;
        font-size: 0.8em;
        color: var(--metadata-color);
      }

      .input-container {
        padding: 20px;
        background-color: var(--background-color);
        border-top: 1px solid var(--border-color);
        max-width: 800px;
        margin: 0 auto;
        width: 100%;
        box-sizing: border-box;
        display: flex;
        gap: 10px;
        transition: background-color 0.3s, border-color 0.3s;
      }

      #messageInput {
        flex: 1;
        padding: 12px;
        border: 1px solid var(--border-color);
        border-radius: 2px;
        background-color: var(--message-bg);
        color: var(--text-color);
        font-family: 'Playfair Display', serif;
        font-size: 16px;
        resize: none;
        min-height: 20px;
        max-height: 150px;
        overflow-y: auto;
        line-height: 1.5;
        transition: background-color 0.3s, border-color 0.3s, color 0.3s;
      }

      #sendButton {
        padding: 12px 24px;
        background-color: var(--primary-color);
        color: white;
        border: none;
        border-radius: 2px;
        cursor: pointer;
        font-family: 'Playfair Display', serif;
        text-transform: uppercase;
        letter-spacing: 1px;
        transition: background-color 0.2s ease;
      }

      #sendButton:hover {
        background-color: var(--secondary-color);
      }

      .error-message {
        color: #e53e3e;
        background-color: var(--message-bg);
        border: 1px solid #fc8181;
      }
```

## Snippet 9
Lines 351-386

```HTML
/* Theme toggle and clear button */
      .theme-toggle, .clear-button {
        position: fixed;
        background: var(--primary-color);
        color: white;
        border: none;
        border-radius: 50%;
        width: 40px;
        height: 40px;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 100;
        transition: background-color 0.2s, transform 0.2s;
      }

      .theme-toggle {
        top: 20px;
        right: 20px;
      }

      .clear-button {
        top: 20px;
        right: 70px;
      }

      .theme-toggle:hover, .clear-button:hover {
        background-color: var(--secondary-color);
        transform: scale(1.05);
      }

      .theme-toggle:active, .clear-button:active {
        transform: scale(0.95);
      }
```

## Snippet 10
Lines 387-399

```HTML
/* Code block styling */
      pre {
        background-color: #f6f8fa;
        padding: 16px;
        border-radius: 6px;
        overflow-x: auto;
      }

      code {
        font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
        font-size: 14px;
      }
```

## Snippet 11
Lines 400-417

```HTML
@media (prefers-color-scheme: dark) {
        pre {
          background-color: #2d333b;
        }
      }

      .sr-only {
        position: absolute;
        width: 1px;
        height: 1px;
        padding: 0;
        margin: -1px;
        overflow: hidden;
        clip: rect(0, 0, 0, 0);
        white-space: nowrap;
        border-width: 0;
      }
```

## Snippet 12
Lines 418-438

```HTML
@media (max-width: 768px) {
        body {
          padding: 10px;
        }

        .chat-container {
          padding: 20px;
        }

        .input-container {
          padding: 10px;
        }

        #messageInput {
          font-size: 14px;
        }

        #sendButton {
          padding: 8px 16px;
        }
      }
```

## Snippet 13
Lines 440-475

```HTML
</head>
  <body>
    <div id="toast" class="toast"></div>
    <div class="loading-spinner" id="loadingSpinner" aria-live="polite" aria-atomic="true">
      <div class="spinner" aria-label="Loading, please wait"></div>
    </div>

    <button id="themeToggle" class="theme-toggle" aria-label="Toggle dark mode">
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M12 16C14.2091 16 16 14.2091 16 12C16 9.79086 14.2091 8 12 8C9.79086 8 8 9.79086 8 12C8 14.2091 9.79086 16 12 16Z" stroke="currentColor" stroke-width="1.5"/>
        <path d="M12 3V5M12 19V21M3 12H5M19 12H21M5.63604 5.63604L7.05025 7.05025M16.9497 16.9497L18.364 18.364M5.63604 18.364L7.05025 16.9497M16.9497 7.05025L18.364 5.63604" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
      </svg>
    </button>

    <button id="clearConversation" class="clear-button" aria-label="Clear conversation">
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M3 6h18"></path>
        <path d="M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2"></path>
        <line x1="10" y1="11" x2="10" y2="17"></line>
        <line x1="14" y1="11" x2="14" y2="17"></line>
      </svg>
    </button>

    <div style="text-align: center; padding: 20px; max-width: 800px; margin: 0 auto; border-bottom: none;">
      <h1 style="font-size: 42px; margin: 0; font-weight: 700; letter-spacing: -1px;">Anthropic</h1>
      <h2 style="font-size: 24px; margin: 0; font-weight: 700; letter-spacing: -1px;">actuallyusefulai.com</h2>
      <p style="margin-top: 10px; font-size: 16px; color: var(--metadata-color);">Accessible, ethical, actually useful AI</p>
    </div>

    <div class="chat-container" aria-label="Chat with Claude">
      <div class="message-container" aria-live="polite"></div>
    </div>

    <div class="input-container">
      <textarea
        id="messageInput"
```

## Snippet 14
Lines 482-486

```HTML
</div>

    <script>
      console.log('Anthropic interface loaded');
```

## Snippet 15
Lines 487-499

```HTML
// Constants for API configuration
      const MAX_TOKENS = 4096;
      const API_ENDPOINT = 'https://api.assisted.space/v2/chat/anthropic';

      // Store conversation history
      let conversationHistory = [
        {
          role: 'system',
          content: 'You are Claude, a helpful AI assistant created by Anthropic. You provide thoughtful, accurate, and accessible responses.'
        }
      ];

      // Theme toggle functionality
```

## Snippet 16
Lines 500-503

```HTML
function setupThemeToggle() {
        const themeToggle = document.getElementById('themeToggle');
        const prefersDarkScheme = window.matchMedia('(prefers-color-scheme: dark)');
```

## Snippet 17
Lines 506-508

```HTML
if (savedTheme) {
          document.body.classList.toggle('dark-theme', savedTheme === 'dark');
          document.documentElement.setAttribute('data-theme', savedTheme);
```

## Snippet 18
Lines 509-514

```HTML
} else {
          // Otherwise use system preference
          document.body.classList.toggle('dark-theme', prefersDarkScheme.matches);
          document.documentElement.setAttribute('data-theme', prefersDarkScheme.matches ? 'dark' : 'light');
        }
```

## Snippet 19
Lines 515-522

```HTML
if (themeToggle) {
          themeToggle.addEventListener('click', () => {
            const isDark = document.body.classList.toggle('dark-theme');
            const theme = isDark ? 'dark' : 'light';
            document.documentElement.setAttribute('data-theme', theme);
            localStorage.setItem('theme', theme);
          });
        }
```

## Snippet 20
Lines 526-533

```HTML
function initializeToastContainer() {
        const container = document.createElement('div');
        container.className = 'toast-container';
        document.body.appendChild(container);
        return container;
      }

      // Show toast notification
```

## Snippet 21
Lines 534-570

```HTML
function showToast(message, type = 'info', duration = 3000) {
        const toastContainer = document.querySelector('.toast-container') || initializeToastContainer();
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;

        // Add appropriate icon based on type
        let icon = '';
        switch(type) {
          case 'success':
            icon = '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41L9 16.17z"/></svg>';
            break;
          case 'error':
            icon = '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"/></svg>';
            break;
          case 'info':
            icon = '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-6h2v6zm0-8h-2V7h2v2z"/></svg>';
            break;
        }

        toast.innerHTML = `
          ${icon}
          <span class="message" role="alert" aria-live="polite">${message}</span>
          <button class="close-button" aria-label="Dismiss notification">
            <svg viewBox="0 0 24 24" fill="currentColor" width="20" height="20">
              <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12 19 6.41z"/>
            </svg>
          </button>
        `;

        // Add close button functionality
        const closeButton = toast.querySelector('.close-button');
        closeButton.addEventListener('click', () => {
          toast.classList.remove('show');
          setTimeout(() => toast.remove(), 300);
        });

        toastContainer.appendChild(toast);
```

## Snippet 22
Lines 571-576

```HTML
// Trigger reflow for animation
        toast.offsetHeight;
        toast.classList.add('show');

        // Auto remove after duration
        setTimeout(() => {
```

## Snippet 23
Lines 577-580

```HTML
if (toast.parentElement) {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300);
          }
```

## Snippet 24
Lines 585-590

```HTML
function autoResizeTextarea(textarea) {
        textarea.style.height = 'auto';
        textarea.style.height = (textarea.scrollHeight) + 'px';
      }

      // Show/hide loading spinner
```

## Snippet 25
Lines 593-596

```HTML
if (spinner) {
          spinner.style.display = 'flex';
        }
        const sendButton = document.getElementById('sendButton');
```

## Snippet 26
Lines 597-600

```HTML
if (sendButton) {
          sendButton.classList.add('loading');
          sendButton.disabled = true;
        }
```

## Snippet 27
Lines 605-608

```HTML
if (spinner) {
          spinner.style.display = 'none';
        }
        const sendButton = document.getElementById('sendButton');
```

## Snippet 28
Lines 609-612

```HTML
if (sendButton) {
          sendButton.classList.remove('loading');
          sendButton.disabled = false;
        }
```

## Snippet 29
Lines 616-622

```HTML
function processMessageContent(content) {
        // Convert markdown to HTML
        const md = window.markdownit({
          html: true,
          breaks: true,
          linkify: true,
          typographer: true,
```

## Snippet 30
Lines 631-638

```HTML
});

        const rawHtml = md.render(content);

        // Sanitize to prevent XSS
        const sanitizedHtml = DOMPurify.sanitize(rawHtml);

        return sanitizedHtml;
```

## Snippet 31
Lines 639-655

```HTML
}

      // Debug DOM elements
      document.addEventListener('DOMContentLoaded', () => {
        console.log('DOM fully loaded');
        console.log('Message container:', document.querySelector('.message-container'));
        console.log('Message input:', document.getElementById('messageInput'));
        console.log('Send button:', document.getElementById('sendButton'));

        // Initialize toast container
        initializeToastContainer();

        // Setup theme toggle
        setupThemeToggle();

        // Setup clear conversation button
        const clearConversationBtn = document.getElementById('clearConversation');
```

## Snippet 32
Lines 656-668

```HTML
if (clearConversationBtn) {
          clearConversationBtn.addEventListener('click', () => {
            console.log('Clearing conversation');
            // Reset conversation history to only include system message
            conversationHistory = [
              {
                role: 'system',
                content: 'You are Claude, a helpful AI assistant created by Anthropic. You provide thoughtful, accurate, and accessible responses.'
              }
            ];

            // Clear message container
            const messageContainer = document.querySelector('.message-container');
```

## Snippet 33
Lines 669-674

```HTML
if (messageContainer) {
              messageContainer.innerHTML = '';
            }

            // Show confirmation toast
            showToast('Conversation cleared', 'success');
```

## Snippet 34
Lines 676-679

```HTML
}

        // Monitor input events
        const messageInput = document.getElementById('messageInput');
```

## Snippet 35
Lines 680-686

```HTML
if (messageInput) {
          messageInput.addEventListener('focus', () => console.log('Input focused'));
          messageInput.addEventListener('input', (e) => {
            console.log('Input changed:', e.target.value);
            autoResizeTextarea(e.target);
          });
```

## Snippet 36
Lines 690-692

```HTML
if (e.key === 'Enter' && !e.shiftKey) {
              e.preventDefault();
              const sendButton = document.getElementById('sendButton');
```

## Snippet 37
Lines 693-695

```HTML
if (sendButton) {
                sendButton.click();
              }
```

## Snippet 38
Lines 698-701

```HTML
}

        // Monitor button clicks
        const sendButton = document.getElementById('sendButton');
```

## Snippet 39
Lines 702-705

```HTML
if (sendButton) {
          sendButton.addEventListener('click', async () => {
            console.log('Send button clicked');
            const message = messageInput.value.trim();
```

## Snippet 40
Lines 706-738

```HTML
if (!message) return;

            // Clear input
            messageInput.value = '';
            autoResizeTextarea(messageInput);

            // Show loading state
            showLoadingSpinner();

            // Add user message to chat and history
            const messageContainer = document.querySelector('.message-container');
            const userMessageWrapper = document.createElement('div');
            userMessageWrapper.className = 'message-wrapper';
            const userMessage = document.createElement('div');
            userMessage.className = 'message user-message';
            userMessage.textContent = message;
            userMessageWrapper.appendChild(userMessage);

            // Add user message action buttons
            const userMessageActions = document.createElement('div');
            userMessageActions.className = 'message-actions';
            userMessageActions.innerHTML = `
              <button class="copy-btn" aria-label="Copy message">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
                  <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
                </svg>
              </button>
            `;
            userMessageWrapper.appendChild(userMessageActions);

            // Add event listener to user message copy button
            const userCopyBtn = userMessageActions.querySelector('.copy-btn');
```

## Snippet 41
Lines 739-743

```HTML
if (userCopyBtn) {
              userCopyBtn.addEventListener('click', async () => {
                try {
                  await navigator.clipboard.writeText(message);
                  showToast('Message copied to clipboard', 'success');
```

## Snippet 42
Lines 744-747

```HTML
} catch (error) {
                  console.error('Failed to copy message:', error);
                  showToast('Failed to copy message', 'error');
                }
```

## Snippet 43
Lines 749-772

```HTML
}

            // Add the user message wrapper to the message container
            messageContainer.appendChild(userMessageWrapper);

            // Add to conversation history
            conversationHistory.push({
              role: 'user',
              content: message
            });

            try {
              console.log('Sending request to API...');
              showToast('Sending message to Claude...', 'info');

              const response = await sendChatMessage(message);
              console.log('Response received, processing stream...');
              showToast('Claude is responding...', 'info');

              // Process streaming response
              const reader = response.body.getReader();
              const decoder = new TextDecoder();
              let fullContent = '';
              let isFirstContent = true;
```

## Snippet 44
Lines 779-789

```HTML
const chunk = decoder.decode(value, { stream: true });
                console.log('Received raw chunk:', chunk.substring(0, 100) + (chunk.length > 100 ? '...' : ''));

                // Add current chunk to buffer and process
                buffer += chunk;

                // Process lines from buffer
                const lines = buffer.split('\n');
                // Keep the last line in buffer as it might be incomplete
                buffer = lines.pop() || '';
```

## Snippet 45
Lines 791-798

```HTML
if (!line.trim() || !line.startsWith('data: ')) continue;

                  try {
                    // Extract the data part
                    const jsonStr = line.slice(6);
                    const data = JSON.parse(jsonStr);
                    console.log('Parsed data:', data);
```

## Snippet 46
Lines 799-801

```HTML
if (data.type === 'content_block_delta' && data.delta && data.delta.text) {
                      fullContent += data.delta.text;
                      updateMessageContent(fullContent);
```

## Snippet 47
Lines 802-805

```HTML
} else if (data.type === 'message_delta' && data.delta && data.delta.content) {
                      // Some APIs send content through message_delta
                      fullContent += data.delta.content;
                      updateMessageContent(fullContent);
```

## Snippet 48
Lines 806-809

```HTML
} else if (data.type === 'delta' && data.content) {
                      // Format used in some versions of the API
                      fullContent += data.content;
                      updateMessageContent(fullContent);
```

## Snippet 49
Lines 810-813

```HTML
} else if (data.content) {
                      // Direct content field
                      fullContent += data.content;
                      updateMessageContent(fullContent);
```

## Snippet 50
Lines 814-818

```HTML
} else if (data.message && data.message.content) {
                      // Alternative format with message object
                      fullContent += data.message.content;
                      updateMessageContent(fullContent);
                    }
```

## Snippet 51
Lines 819-821

```HTML
} catch (error) {
                    console.warn('Error parsing SSE line:', line, error);
                  }
```

## Snippet 52
Lines 826-828

```HTML
if (buffer.trim()) {
                console.log('Processing remaining buffer:', buffer);
                try {
```

## Snippet 53
Lines 831-834

```HTML
if (data.content) {
                      fullContent += data.content;
                      updateMessageContent(fullContent);
                    }
```

## Snippet 54
Lines 836-838

```HTML
} catch (error) {
                  console.warn('Error processing buffer:', error);
                }
```

## Snippet 55
Lines 839-846

```HTML
}

              showToast('Response complete', 'success');

              // Hide loading state
              hideLoadingSpinner();

              // Add assistant's response to history
```

## Snippet 56
Lines 847-853

```HTML
if (fullContent.trim()) {
                conversationHistory.push({
                  role: 'assistant',
                  content: fullContent
                });
              }
```

## Snippet 57
Lines 854-866

```HTML
} catch (error) {
              console.error('Error:', error);
              showToast(`Error: ${error.message}`, 'error');
              const errorMessage = document.createElement('div');
              errorMessage.className = 'message error-message';
              errorMessage.textContent = `Error: ${error.message}`;
              messageContainer.appendChild(errorMessage);

              // Hide loading state
              hideLoadingSpinner();
            }

            messageContainer.scrollTop = messageContainer.scrollHeight;
```

## Snippet 58
Lines 868-871

```HTML
}

        // Monitor message container changes
        const messageContainer = document.querySelector('.message-container');
```

## Snippet 59
Lines 872-875

```HTML
if (messageContainer) {
          const observer = new MutationObserver((mutations) => {
            console.log('Message container updated:', mutations);
          });
```

## Snippet 60
Lines 881-887

```HTML
function updateMessageContent(content) {
        const messageContainer = document.querySelector('.message-container');
        const lastMessage = messageContainer.querySelector('.message-wrapper:last-child .bot-message');

        // Process content with markdown and sanitization
        const processedContent = processMessageContent(content);
```

## Snippet 61
Lines 890-915

```HTML
} else {
          const messageWrapper = document.createElement('div');
          messageWrapper.className = 'message-wrapper';

          // Add message action buttons
          const messageActions = document.createElement('div');
          messageActions.className = 'message-actions';
          messageActions.innerHTML = `
            <button class="copy-btn" aria-label="Copy message">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
                <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
              </svg>
            </button>
          `;

          const message = document.createElement('div');
          message.className = 'message bot-message';
          message.innerHTML = processedContent;

          messageWrapper.appendChild(message);
          messageWrapper.appendChild(messageActions);
          messageContainer.appendChild(messageWrapper);

          // Add event listener to copy button
          const copyBtn = messageActions.querySelector('.copy-btn');
```

## Snippet 62
Lines 916-920

```HTML
if (copyBtn) {
            copyBtn.addEventListener('click', async () => {
              try {
                await navigator.clipboard.writeText(content);
                showToast('Message copied to clipboard', 'success');
```

## Snippet 63
Lines 921-924

```HTML
} catch (error) {
                console.error('Failed to copy message:', error);
                showToast('Failed to copy message', 'error');
              }
```

## Snippet 64
Lines 930-933

```HTML
}

      // Log window errors
      window.onerror = function(message, source, lineno, colno, error) {
```

## Snippet 65
Lines 936-943

```HTML
};

      // Log unhandled promise rejections
      window.addEventListener('unhandledrejection', function(event) {
        console.error('Unhandled promise rejection:', event.reason);
      });

      // Function to send chat message
```

## Snippet 66
Lines 944-968

```HTML
async function sendChatMessage(message) {
        console.log('Sending message to API:', message);

        const requestBody = {
          provider: 'anthropic',
          model: 'claude-3-haiku-20240307',
          prompt: message,
          max_tokens: MAX_TOKENS,
          stream: true
        };

        try {
          console.log('Making request to:', API_ENDPOINT);
          console.log('Request payload:', requestBody);

          const response = await fetch(API_ENDPOINT, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'Accept': 'text/event-stream'
            },
            credentials: 'include',
            body: JSON.stringify(requestBody)
          });
```

## Snippet 67
Lines 973-980

```HTML
if (!response.ok) {
            const errorText = await response.text();
            console.error('API Error:', {
              status: response.status,
              statusText: response.statusText,
              headers: Object.fromEntries([...response.headers]),
              body: errorText
            });
```

## Snippet 68
Lines 982-984

```HTML
}

          return response;
```

## Snippet 69
Lines 985-988

```HTML
} catch (error) {
          console.error('Chat API Error:', error);
          throw error;
        }
```

