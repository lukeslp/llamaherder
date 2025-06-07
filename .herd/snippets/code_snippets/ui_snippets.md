# Code Snippets from toollama/API/api-tools/tools/snippets/core/conversation/ui.js

File: `toollama/API/api-tools/tools/snippets/core/conversation/ui.js`  
Language: JavaScript  
Extracted: 2025-06-07 05:21:55  

## Snippet 1
Lines 9-11

```JavaScript
showLoadingState() {
        console.log("[Summary] Showing loading state");
        const sidePanel = document.querySelector(".side-panel-container");
```

## Snippet 2
Lines 12-17

```JavaScript
if (!sidePanel) return;

        sidePanel.classList.add("open");
        document.querySelector(".page-content")?.classList.add("panel-open");

        let logo = sidePanel.querySelector(".side-panel-logo");
```

## Snippet 3
Lines 18-27

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

## Snippet 4
Lines 28-30

```JavaScript
if (summaryContainer) {
            summaryContainer.innerHTML = '';
        }
```

## Snippet 5
Lines 38-40

```JavaScript
if (logo) {
            logo.style.display = 'none';
        }
```

## Snippet 6
Lines 49-54

```JavaScript
if (!sidePanel) return;

        sidePanel.classList.add("open");
        document.querySelector(".page-content")?.classList.add("panel-open");

        Object.entries(analysisData).forEach(([containerId, data]) => {
```

## Snippet 7
Lines 55-58

```JavaScript
if (!Array.isArray(data) || data.length === 0) return;

            const panelContainer = sidePanel.querySelector(`#panel-${containerId}`);
            const containerContent = panelContainer?.querySelector(".container-content");
```

## Snippet 8
Lines 59-61

```JavaScript
if (!containerContent) return;

            containerContent.innerHTML = this.generateContentHtml(containerId, data);
```

## Snippet 9
Lines 65-69

```JavaScript
if (window.hljs) {
            document.querySelectorAll('pre code').forEach((block) => {
                window.hljs.highlightBlock(block);
            });
        }
```

## Snippet 10
Lines 78-100

```JavaScript
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

## Snippet 11
Lines 101-103

```JavaScript
<h4>${item.language} Code Snippet</h4>
                    <pre><code class="language-${item.language.toLowerCase()}">${item.snippet}</code></pre>
                    ${item.description ? `<p>${item.description}</p>` : ""}
```

## Snippet 12
Lines 106-117

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

## Snippet 13
Lines 118-120

```JavaScript
};

        return data.map(item => templates[type](item)).join("");
```

