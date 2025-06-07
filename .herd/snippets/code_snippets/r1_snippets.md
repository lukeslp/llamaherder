# Code Snippets from toollama/storage/r1.html

File: `toollama/storage/r1.html`  
Language: HTML  
Extracted: 2025-06-07 05:11:14  

## Snippet 1
Lines 1-8

```HTML
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>r1 • accessible, ethical ai</title>

    <!-- External Dependencies -->
```

## Snippet 2
Lines 9-39

```HTML
<script src="https://cdn.jsdelivr.net/npm/markdown-it@13.0.1/dist/markdown-it.min.js"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.7.0/styles/github.min.css">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.7.0/highlight.min.js"></script>

    <style>
        :root {
            --primary-bg: #ffffff;
            --secondary-bg: #f8f9fa;
            --primary-text: #000000;
            --secondary-text: #4a4a4a;
            --accent-color: #0066cc;
            --border-color: #e0e0e0;
            --success-color: #28a745;
            --error-color: #dc3545;
            --thought-bg: #e0f7fa;
            --thought-border: #b2ebf2;
        }

        body {
            margin: 0;
            padding: 0;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: var(--primary-bg);
            color: var(--primary-text);
            line-height: 1.6;
        }

        .app-container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 1rem;
```

## Snippet 3
Lines 40-43

```HTML
height: calc(100vh - 60px); /* Adjust for title height */
            display: flex;
            flex-direction: column;
            position: relative;
```

## Snippet 4
Lines 44-49

```HTML
}

        .chat-container {
            flex-grow: 1;
            border: 1px solid var(--border-color);
            border-radius: 8px;
```

## Snippet 5
Lines 51-53

```HTML
overflow-y: auto; /* Enable vertical scrolling */
            background: var(--secondary-bg);
            padding: 1rem;
```

## Snippet 6
Lines 56-178

```HTML
}

        .message-container {
            margin-bottom: 1rem;
        }

        .message {
            padding: 1rem;
            border-radius: 8px;
            max-width: 80%;
            list-style: none;
        }

        .user-message {
            background: var(--accent-color);
            color: white;
            margin-left: auto;
        }

        .bot-message {
            background: white;
            border: 1px solid var(--border-color);
        }

        .input-container {
            display: flex;
            flex-direction: column;
            gap: 1rem;
            padding: 1rem;
            background: var(--primary-bg);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            position: fixed;
            bottom: 1rem;
            left: 50%;
            transform: translateX(-50%);
            width: calc(100% - 2rem);
            max-width: 1168px;
            box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.05);
        }

        .input-controls {
            display: flex;
            gap: 1rem;
            width: 100%;
        }

        #messageInput {
            flex-grow: 1;
            padding: 0.75rem;
            border: 1px solid var(--border-color);
            border-radius: 4px;
            font-size: 1rem;
            min-height: 2.5rem;
            max-height: 150px;
            resize: vertical;
            font-family: inherit;
            line-height: 1.5;
        }

        button {
            padding: 0.75rem 1.5rem;
            background: var(--accent-color);
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 1rem;
            transition: opacity 0.2s;
        }

        button:hover {
            opacity: 0.9;
        }

        button:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }

        .file-input-container {
            position: relative;
        }

        #fileInput {
            display: none;
        }

        .file-label {
            padding: 0.75rem 1.5rem;
            background: var(--secondary-bg);
            border: 1px solid var(--border-color);
            border-radius: 4px;
            cursor: pointer;
            display: inline-block;
        }

        #fileName {
            margin-left: 0.5rem;
            color: var(--secondary-text);
            font-size: 0.9rem;
        }

        .loading {
            opacity: 0.7;
            pointer-events: none;
        }

        #toast {
            position: fixed;
            top: 1rem;
            right: 1rem;
            padding: 1rem;
            background: var(--error-color);
            color: white;
            border-radius: 4px;
            display: none;
        }

        #toast.show {
            display: block;
        }
```

## Snippet 7
Lines 179-184

```HTML
/* Markdown Styling */
        .markdown-body {
            font-size: 1rem;
            line-height: 1.6;
        }
```

## Snippet 8
Lines 185-206

```HTML
/* Code block styling */
        .markdown-body pre {
            background: #000000;
            padding: 1rem;
            border-radius: 8px;
            overflow-x: auto;
            margin: 1rem 0;
            max-width: 100%;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        }

        .markdown-body pre code {
            color: #d4d4d4;
            font-family: 'Menlo', 'Monaco', 'Courier New', monospace;
            font-size: 0.9rem;
            line-height: 1.5;
            background: transparent;
            padding: 0;
            white-space: pre-wrap;
            word-break: break-word;
        }
```

## Snippet 9
Lines 207-216

```HTML
/* Inline code styling */
        .markdown-body code:not(pre code) {
            background: #f0f0f0;
            color: #e01e5a;
            padding: 0.2rem 0.4rem;
            border-radius: 4px;
            font-family: 'Menlo', 'Monaco', 'Courier New', monospace;
            font-size: 0.9em;
        }
```

## Snippet 10
Lines 217-222

```HTML
/* Message content container */
        .message-content {
            max-width: 100%;
            overflow-x: hidden;
        }
```

## Snippet 11
Lines 223-248

```HTML
/* Bot message specific styling */
        .bot-message .markdown-body {
            padding: 0.5rem;
            overflow-x: auto;
        }

        .page-title {
            text-align: center;
            padding: 1rem;
            margin: 0;
            font-size: 1.5rem;
            color: var(--accent-color);
            border-bottom: 1px solid var(--border-color);
            background: var(--primary-bg);
        }

        .thought-bubble {
            background: var(--thought-bg);
            border: 1px solid var(--thought-border);
            border-radius: 20px;
            padding: 10px 20px;
            margin-bottom: 1rem;
            position: relative;
            font-style: italic;
            color: var(--secondary-text);
            max-width: 60%;
```

## Snippet 12
Lines 249-251

```HTML
margin-left: 30px; /* Space for bubbles */
            margin-right: auto;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
```

## Snippet 13
Lines 254-263

```HTML
/* Remove the old triangle and add thought bubbles */
        .thought-bubble::before,
        .thought-bubble::after {
            content: '';
            position: absolute;
            background: var(--thought-bg);
            border: 1px solid var(--thought-border);
            border-radius: 50%;
        }
```

## Snippet 14
Lines 264-271

```HTML
/* Larger bubble */
        .thought-bubble::before {
            width: 20px;
            height: 20px;
            left: -25px;
            top: 15px;
        }
```

## Snippet 15
Lines 272-299

```HTML
/* Smaller bubble */
        .thought-bubble::after {
            width: 10px;
            height: 10px;
            left: -35px;
            top: 20px;
        }

        .message-separator {
            width: 100%;
            height: 1px;
            background-color: var(--border-color);
            margin: 20px 0;
            position: relative;
        }

        .message-separator::after {
            content: 'Message';
            position: absolute;
            top: -10px;
            left: 50%;
            transform: translateX(-50%);
            background: var(--primary-bg);
            padding: 0 10px;
            color: var(--secondary-text);
            font-size: 0.9rem;
        }
```

## Snippet 16
Lines 300-332

```HTML
/* Preview area */
        .preview-container {
            display: none;
            padding: 0.75rem;
            background: #f0f0f0;
            border-radius: 4px;
            margin-bottom: 0.5rem;
            font-family: 'Menlo', 'Monaco', 'Courier New', monospace;
            font-size: 0.9rem;
            max-height: 200px;
            overflow-y: auto;
        }

        .preview-container.active {
            display: block;
        }

        .toggle-preview-button {
            background: var(--accent-color);
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 0.9rem;
            padding: 0.5rem 1rem;
            margin-bottom: 0.5rem;
            transition: opacity 0.2s;
        }

        .toggle-preview-button:hover {
            opacity: 0.9;
        }
```

## Snippet 17
Lines 334-336

```HTML
@media screen and (max-width: 768px) {
            .app-container {
                padding: 0.5rem;
```

## Snippet 18
Lines 338-358

```HTML
}

            .chat-container {
                margin-bottom: 60px;
                padding: 0.5rem;
                max-height: calc(100vh - 120px);
            }

            .input-container {
                padding: 0.5rem;
                width: calc(100% - 1rem);
                max-width: 100%;
                bottom: 0;
            }

            .input-controls {
                gap: 0.5rem;
            }

            #messageInput {
                padding: 0.5rem;
```

## Snippet 19
Lines 360-389

```HTML
}

            button {
                padding: 0.5rem 1rem;
            }

            .message {
                max-width: 90%;
                padding: 0.75rem;
            }

            .thought-bubble {
                max-width: 80%;
                margin-left: 20px;
                padding: 8px 16px;
            }

            .page-title {
                padding: 0.75rem;
                font-size: 1.25rem;
            }

            .preview-container {
                max-height: 150px;
                padding: 0.5rem;
            }

            .file-label {
                padding: 0.5rem 1rem;
            }
```

## Snippet 20
Lines 392-415

```HTML
@media screen and (max-width: 480px) {
            .app-container {
                padding: 0.25rem;
            }

            .chat-container {
                padding: 0.25rem;
            }

            .message {
                max-width: 95%;
                padding: 0.5rem;
            }

            .markdown-body pre {
                padding: 0.5rem;
                margin: 0.5rem 0;
            }

            .thought-bubble {
                max-width: 85%;
                margin-left: 15px;
            }
        }
```

## Snippet 21
Lines 417-443

```HTML
</head>
<body>
    <h1 class="page-title"><a href="https://ollama.com/library/deepseek-r1">DeepSeek R1</a></h1>
    <div class="app-container">
        <div class="chat-container">
            <ul id="messages" style="list-style: none; padding: 0; margin: 0;"></ul>
        </div>

        <div class="input-container">
            <button class="toggle-preview-button" id="togglePreviewButton">Show Preview</button>
            <div class="preview-container" id="previewContainer"></div>
            <div class="input-controls">
                <div class="file-input-container">
                    <label for="fileInput" class="file-label">📎</label>
                    <input type="file" id="fileInput">
                    <span id="fileName"></span>
                </div>
                <textarea id="messageInput" placeholder="Type your message..." rows="1"></textarea>
                <button id="sendButton">Send</button>
            </div>
        </div>
    </div>

    <div id="toast"></div>

    <script>
        // Load model configuration
```

## Snippet 22
Lines 444-451

```HTML
async function loadModelConfig() {
            try {
                const response = await fetch('models.json');
                const config = await response.json();
                state.currentModel = config.defaultModel;

                // Find the current model configuration
                const currentModelConfig = config.availableModels.find(model => model.name === state.currentModel);
```

## Snippet 23
Lines 452-454

```HTML
if (currentModelConfig) {
                    updateAttachmentUI(currentModelConfig.attach);
                }
```

## Snippet 24
Lines 455-458

```HTML
} catch (error) {
                console.error('Error loading model config:', error);
                showToast('Error loading model configuration');
            }
```

## Snippet 25
Lines 459-477

```HTML
}

        // Initialize on page load
        document.addEventListener('DOMContentLoaded', async () => {
            // Initialize markdown-it
            state.md = window.markdownit();

            // Load configuration and set up streaming
            await loadModelConfig();
            setStreaming(true, true);

            // Send introduction message after a short delay to ensure everything is initialized
            setTimeout(() => {
                const messageInput = document.getElementById("messageInput");
                messageInput.value = "Introduce yourself and explain who created you, any other relevant information, and your abilities and functions, with examples; then write a short story about an alien named Alf in the magical land of Bluesky.";
                sendMessage();
            }, 100);
        });
```

## Snippet 26
Lines 481-491

```HTML
if (thoughtMatch) {
                const thoughtContent = thoughtMatch[1].trim();
                const mainContent = content.replace(/<think>.*?<\/think>/s, '').trim();

                const thoughtHtml = `<div class="thought-bubble">${thoughtContent}</div>`;
                const mainHtml = state.md.render(mainContent);

                return thoughtHtml + mainHtml;
            }

            return state.md.render(content);
```

