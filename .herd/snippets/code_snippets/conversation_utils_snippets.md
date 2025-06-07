# Code Snippets from toollama/API/api-tools/tools/snippets/processed/conversation_utils.js

File: `toollama/API/api-tools/tools/snippets/processed/conversation_utils.js`  
Language: JavaScript  
Extracted: 2025-06-07 05:20:53  

## Snippet 1
Lines 6-49

```JavaScript
// Conversation Export
export const ConversationExporter = {
    downloadConversation(messages, botName = "Assistant") {
        console.log("[Export] Starting conversation export...");
        const now = new Date();
        const dateTime = now.toLocaleString();

        const htmlContent = `
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Conversation Download - ${dateTime}</title>
    <style>
        body {
            font-family: 'Open Sans', Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #ffffff;
            color: #2c3e50;
            line-height: 1.6;
        }
        .message {
            padding: 15px;
            margin: 10px 0;
            border-radius: 8px;
        }
        .user-message {
            background-color: #f5f5f5;
            margin-left: 20%;
        }
        .bot-message {
            background-color: #e8f4f8;
            margin-right: 20%;
        }
        .system-message {
            background-color: #fff3e0;
            text-align: center;
            font-style: italic;
        }
    </style>
</head>
<body>
```

## Snippet 2
Lines 50-61

```JavaScript
<h1>Conversation with ${botName} - ${dateTime}</h1>
    <div class="conversation">
        ${Array.from(messages)
            .map((msg) => {
                const className = msg.className.split(" ")[1];
                const content = msg.querySelector(".message-content")
                    ? msg.querySelector(".message-content").innerHTML
                    : msg.innerHTML;
                return `<div class="message ${className}">${content}</div>`;
            })
            .join("\n")}
    </div>
```

## Snippet 3
Lines 65-72

```JavaScript
const blob = new Blob([htmlContent], { type: "text/html" });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `conversation-${now.toISOString().split("T")[0]}.html`;
        a.click();
        window.URL.revokeObjectURL(url);
        console.log("[Export] Export complete");
```

## Snippet 4
Lines 74-82

```JavaScript
};

// Conversation Summary
export const ConversationSummarizer = {
    systemPrompt: `You are a conversation analysis assistant. Analyze the following exchange and respond ONLY with a JSON object in this exact format, ensuring to include relevant items in each array (do not return empty arrays unless there is truly nothing to report):

{
  "summary": [{"point": "Main points from the conversation", "context": "Additional context or details"}],
  "todos": [{"task": "Any action items or tasks mentioned", "priority": "high|medium|low", "context": "Task details"}],
```

## Snippet 5
Lines 87-112

```JavaScript
}

Important: Analyze the conversation thoroughly and include all relevant information. Do not return empty arrays unless that category truly has no relevant content.`,

    async summarizeConversation(userMessage, assistantResponse, apiUrl) {
        console.log("[Summary] Analyzing conversation");
        const conversationText = `User: ${userMessage}\nAssistant: ${assistantResponse}`;

        const summaryPayload = {
            message: conversationText,
            system_prompt: this.systemPrompt,
            bot_id: "7432075476698546182",
            user_id: `summary_${Date.now()}`,
            conversation_id: `summary_${Date.now()}`
        };

        try {
            const response = await fetch(`${apiUrl}/chat`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "Accept": "text/event-stream"
                },
                body: JSON.stringify(summaryPayload)
            });
```

## Snippet 6
Lines 113-117

```JavaScript
if (!response.ok) {
                throw new Error(`Summary request failed: ${response.status}`);
            }

            return await this.processStreamResponse(response);
```

## Snippet 7
Lines 118-121

```JavaScript
} catch (error) {
            console.error("[Summary] Error:", error);
            throw error;
        }
```

## Snippet 8
Lines 122-128

```JavaScript
},

    async processStreamResponse(response) {
        const reader = response.body.getReader();
        const decoder = new TextDecoder("utf-8");
        let accumulatedData = "";
```

## Snippet 9
Lines 139-142

```JavaScript
if (!eventData) continue;

                    try {
                        const data = JSON.parse(eventData);
```

## Snippet 10
Lines 147-150

```JavaScript
if (jsonMatch) {
                                return JSON.parse(jsonMatch[0]);
                            }
                            throw new Error("No valid JSON found in response");
```

## Snippet 11
Lines 152-154

```JavaScript
} catch (e) {
                        console.error("[Summary] Stream processing error:", e);
                    }
```

## Snippet 12
Lines 160-166

```JavaScript
};

// Summary UI Manager
export const SummaryUIManager = {
    showLoadingState() {
        console.log("[Summary] Showing loading state");
        const sidePanel = document.querySelector(".side-panel-container");
```

## Snippet 13
Lines 167-172

```JavaScript
if (!sidePanel) return;

        sidePanel.classList.add("open");
        document.querySelector(".page-content")?.classList.add("panel-open");

        let logo = sidePanel.querySelector(".side-panel-logo");
```

## Snippet 14
Lines 173-182

```JavaScript
if (!logo) {
            logo = document.createElement("img");
            logo.src = "https://i.imgur.com/aSNdzIx.gif";
            logo.className = "side-panel-logo";
            logo.alt = "Loading...";
            sidePanel.appendChild(logo);
        }
        logo.style.display = 'block';

        const summaryContainer = document.querySelector("#panel-summary .container-content");
```

## Snippet 15
Lines 183-185

```JavaScript
if (summaryContainer) {
            summaryContainer.innerHTML = '';
        }
```

## Snippet 16
Lines 186-189

```JavaScript
},

    hideLoadingState() {
        const logo = document.querySelector(".side-panel-logo");
```

## Snippet 17
Lines 190-192

```JavaScript
if (logo) {
            logo.style.display = 'none';
        }
```

## Snippet 18
Lines 193-196

```JavaScript
},

    updatePanelContent(analysisData) {
        const sidePanel = document.querySelector(".side-panel-container");
```

## Snippet 19
Lines 197-202

```JavaScript
if (!sidePanel) return;

        sidePanel.classList.add("open");
        document.querySelector(".page-content")?.classList.add("panel-open");

        Object.entries(analysisData).forEach(([containerId, data]) => {
```

## Snippet 20
Lines 203-206

```JavaScript
if (!Array.isArray(data) || data.length === 0) return;

            const panelContainer = sidePanel.querySelector(`#panel-${containerId}`);
            const containerContent = panelContainer?.querySelector(".container-content");
```

## Snippet 21
Lines 207-209

```JavaScript
if (!containerContent) return;

            containerContent.innerHTML = this.generateContentHtml(containerId, data);
```

## Snippet 22
Lines 213-217

```JavaScript
if (window.hljs) {
            document.querySelectorAll('pre code').forEach((block) => {
                window.hljs.highlightBlock(block);
            });
        }
```

## Snippet 23
Lines 218-242

```JavaScript
},

    generateContentHtml(type, data) {
        const templates = {
            summary: (item) => `
                <div class="panel-item">
                    <h4>${item.point}</h4>
                    ${item.context ? `<p>${item.context}</p>` : ""}
                </div>`,

            todos: (item) => `
                <div class="panel-item">
                    <h4>${item.task}</h4>
                    <p>Priority: ${item.priority}</p>
                    ${item.context ? `<p>${item.context}</p>` : ""}
                </div>`,

            references: (item) => `
                <div class="panel-item">
                    <h4><a href="${item.url}" target="_blank" rel="noopener noreferrer">${item.title}</a></h4>
                    ${item.context ? `<p>${item.context}</p>` : ""}
                </div>`,

            code: (item) => `
                <div class="panel-item">
```

## Snippet 24
Lines 243-245

```JavaScript
<h4>${item.language} Code Snippet</h4>
                    <pre><code class="language-${item.language.toLowerCase()}">${item.snippet}</code></pre>
                    ${item.description ? `<p>${item.description}</p>` : ""}
```

## Snippet 25
Lines 248-259

```JavaScript
embedded: (item) => `
                <div class="panel-item">
                    <h4>${item.type}</h4>
                    <p>${item.content}</p>
                    ${item.description ? `<p>${item.description}</p>` : ""}
                </div>`,

            questions: (item) => `
                <div class="panel-item">
                    <h4>${item.question}</h4>
                    ${item.context ? `<p>${item.context}</p>` : ""}
                </div>`
```

## Snippet 26
Lines 260-262

```JavaScript
};

        return data.map(item => templates[type](item)).join("");
```

