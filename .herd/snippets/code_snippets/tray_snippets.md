# Code Snippets from toollama/API/api-tools/tools/snippets/core/ui/interaction/tray.js

File: `toollama/API/api-tools/tools/snippets/core/ui/interaction/tray.js`  
Language: JavaScript  
Extracted: 2025-06-07 05:24:02  

## Snippet 1
Lines 7-25

```JavaScript
if (!tray || !settingsButton) return;

        let isOpen = false;

        const toggleTray = () => {
            isOpen = !isOpen;
            tray.classList.toggle('open', isOpen);
            settingsButton.setAttribute('aria-expanded', isOpen.toString());
            settingsButton.classList.toggle('active', isOpen);
        };

        // Toggle on button click
        settingsButton.addEventListener('click', (e) => {
            e.preventDefault();
            toggleTray();
        });

        // Close on outside click
        document.addEventListener('click', (e) => {
```

## Snippet 2
Lines 26-28

```JavaScript
if (isOpen && !tray.contains(e.target) && e.target !== settingsButton) {
                toggleTray();
            }
```

## Snippet 3
Lines 33-35

```JavaScript
if (isOpen && e.key === 'Escape') {
                toggleTray();
            }
```

## Snippet 4
Lines 36-40

```JavaScript
});

        return {
            toggle: toggleTray,
            close: () => {
```

