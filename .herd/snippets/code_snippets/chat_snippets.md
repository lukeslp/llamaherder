# Code Snippets from toollama/API/api-tools/tools/snippets/core/streaming/chat.js

File: `toollama/API/api-tools/tools/snippets/core/streaming/chat.js`  
Language: JavaScript  
Extracted: 2025-06-07 05:23:43  

## Snippet 1
Lines 17-24

```JavaScript
constructor(config = {}) {
        this.apiBaseUrl = config.apiBaseUrl || process.env.API_BASE_URL;
        this.apiKey = config.apiKey || process.env.API_KEY;
        this.model = config.model || process.env.DEFAULT_MODEL;
        this.md = window.markdownit();
        this.messages = [];
    }
```

## Snippet 2
Lines 30-43

```JavaScript
processMessageContent(content) {
        const parsedContent = this.md.render(content);
        const container = document.createElement("div");
        container.className = "markdown-body message-content";
        container.innerHTML = parsedContent;

        // Apply syntax highlighting
        container.querySelectorAll("pre code").forEach((block) => {
            hljs.highlightElement(block);
        });

        return container.outerHTML;
    }
```

## Snippet 3
Lines 51-72

```JavaScript
if (!content?.trim()) return;

        this.messages.push({
            role: "user",
            content: content
        });

        try {
            const response = await fetch(`${this.apiBaseUrl}/api/chat/completions`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.apiKey}`
                },
                body: JSON.stringify({
                    messages: this.messages,
                    model: this.model,
                    stream: true,
                    ...options
                })
            });
```

## Snippet 4
Lines 73-81

```JavaScript
if (!response.ok) {
                const errorData = await response.json().catch(() => null);
                throw new Error(`HTTP error! status: ${response.status}${errorData ? ' - ' + JSON.stringify(errorData) : ''}`);
            }

            let fullContent = "";
            const reader = response.body.getReader();
            const decoder = new TextDecoder();
```

## Snippet 5
Lines 84-88

```JavaScript
if (done) break;

                const chunk = decoder.decode(value);
                const lines = chunk.split('\n');
```

## Snippet 6
Lines 91-94

```JavaScript
if (line.startsWith('data: ')) {
                        try {
                            const parsed = JSON.parse(line.slice(6));
                            const content = parsed.choices?.[0]?.delta?.content;
```

## Snippet 7
Lines 97-99

```JavaScript
if (options.onChunk) {
                                    options.onChunk(content, fullContent);
                                }
```

## Snippet 8
Lines 101-103

```JavaScript
} catch (e) {
                            console.warn('Error parsing chunk:', e);
                        }
```

## Snippet 9
Lines 106-112

```JavaScript
}

            this.messages.push({
                role: "assistant",
                content: fullContent
            });
```

## Snippet 10
Lines 113-116

```JavaScript
if (options.onComplete) {
                options.onComplete(fullContent);
            }
```

## Snippet 11
Lines 119-122

```JavaScript
if (options.onError) {
                options.onError(error);
            }
            throw error;
```

