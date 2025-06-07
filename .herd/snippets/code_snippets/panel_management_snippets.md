# Code Snippets from toollama/API/api-tools/tools/snippets/processed/panel_management.js

File: `toollama/API/api-tools/tools/snippets/processed/panel_management.js`  
Language: JavaScript  
Extracted: 2025-06-07 05:21:30  

## Snippet 1
Lines 6-38

```JavaScript
// Panel State Management
export const PanelManager = {
    activePanelId: null,
    isPanelOpen: false,

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

## Snippet 2
Lines 39-44

```JavaScript
if (["assistants", "help", "settings"].includes(panelId)) {
            inputContainer.classList.add("left-panel-open");
        }

        this.activePanelId = panelId + "Panel";
        this.isPanelOpen = true;
```

## Snippet 3
Lines 45-50

```JavaScript
},

    handleToggleButton(event, panels, toggleButtons, panelToggles, sidePanelsContainer, chatContainer, inputContainer) {
        event.preventDefault();
        const panelId = event.currentTarget.getAttribute("data-panel");
```

## Snippet 4
Lines 57-62

```JavaScript
};

// Panel Logo Management
export const PanelLogoManager = {
    addPanelLogo(logoUrl = "https://i.imgur.com/aSNdzIx.gif") {
        const sidePanel = document.querySelector(".right-panel-container");
```

## Snippet 5
Lines 63-68

```JavaScript
if (!sidePanel) {
            console.error("Side panel container not found.");
            return;
        }

        let logo = document.querySelector(".side-panel-logo");
```

## Snippet 6
Lines 69-102

```JavaScript
if (!logo) {
            logo = document.createElement("img");
            logo.src = logoUrl;
            logo.className = "side-panel-logo";
            logo.alt = "Panel Logo";
            logo.style.cssText = `
                position: absolute;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                width: 120px;
                height: 120px;
                opacity: 0.5;
                z-index: 1;
            `;
            sidePanel.appendChild(logo);
        }

        // Show logo when panel is empty
        const observer = new MutationObserver(() => {
            const panelContent = sidePanel.querySelector(".panel-content");
            const isEmpty = !panelContent || !panelContent.children.length;
            logo.style.display = isEmpty ? "block" : "none";
        });

        observer.observe(sidePanel, {
            childList: true,
            subtree: true,
        });

        // Initial state
        const panelContent = sidePanel.querySelector(".panel-content");
        const isEmpty = !panelContent || !panelContent.children.length;
        logo.style.display = isEmpty ? "block" : "none";
```

## Snippet 7
Lines 104-110

```JavaScript
};

// Panel Mutation Observer
export const PanelObserver = {
    setupMutationObservers(leftPanelContainer, updateCallback) {
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
```

## Snippet 8
Lines 111-113

```JavaScript
if (mutation.attributeName === "class") {
                    requestAnimationFrame(updateCallback);
                }
```

## Snippet 9
Lines 115-121

```JavaScript
});

        observer.observe(leftPanelContainer, {
            attributes: true,
        });

        return observer;
```

