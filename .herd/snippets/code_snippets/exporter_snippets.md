# Code Snippets from toollama/API/api-tools/tools/snippets/core/conversation/exporter.js

File: `toollama/API/api-tools/tools/snippets/core/conversation/exporter.js`  
Language: JavaScript  
Extracted: 2025-06-07 05:21:57  

## Snippet 1
Lines 11-16

```JavaScript
downloadConversation(messages, botName = "Assistant") {
        console.log("[Export] Starting conversation export...");
        const now = new Date();
        const dateTime = now.toLocaleString();

        const htmlContent = `
```

## Snippet 2
Lines 17-52

```JavaScript
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

## Snippet 3
Lines 53-64

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

## Snippet 4
Lines 68-75

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

