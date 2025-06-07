# Code Snippets from toollama/API/api-tools/tools/snippets/core/ui/panel/manager.js

File: `toollama/API/api-tools/tools/snippets/core/ui/panel/manager.js`  
Language: JavaScript  
Extracted: 2025-06-07 05:24:45  

## Snippet 1
Lines 5-8

```JavaScript
export const PanelManager = {
    activePanelId: null,
    isPanelOpen: false,
```

## Snippet 2
Lines 18-32

```JavaScript
closeAllPanels(panels, toggleButtons, panelToggles, sidePanelsContainer, chatContainer, inputContainer) {
        panels.forEach((panel) => panel.classList.remove("active"));
        toggleButtons.forEach((btn) => {
            btn.classList.remove("active");
            btn.setAttribute("aria-pressed", "false");
        });

        panelToggles.classList.add("closed");
        sidePanelsContainer.classList.add("closed");
        chatContainer.classList.add("panel-closed");
        inputContainer.classList.remove("left-panel-open", "right-panel-open");

        this.isPanelOpen = false;
    },
```

## Snippet 3
Lines 43-55

```JavaScript
openPanel(panelId, panels, toggleButtons, panelToggles, sidePanelsContainer, chatContainer, inputContainer) {
        this.closeAllPanels(panels, toggleButtons, panelToggles, sidePanelsContainer, chatContainer, inputContainer);

        const panel = document.getElementById(panelId + "Panel");
        const button = document.querySelector(`[data-panel="${panelId}"]`);

        panel.classList.add("active");
        button.classList.add("active");
        button.setAttribute("aria-pressed", "true");
        panelToggles.classList.remove("closed");
        sidePanelsContainer.classList.remove("closed");
        chatContainer.classList.remove("panel-closed");
```

## Snippet 4
Lines 56-61

```JavaScript
if (["assistants", "help", "settings"].includes(panelId)) {
            inputContainer.classList.add("left-panel-open");
        }

        this.activePanelId = panelId + "Panel";
        this.isPanelOpen = true;
```

## Snippet 5
Lines 74-77

```JavaScript
handleToggleButton(event, panels, toggleButtons, panelToggles, sidePanelsContainer, chatContainer, inputContainer) {
        event.preventDefault();
        const panelId = event.currentTarget.getAttribute("data-panel");
```

