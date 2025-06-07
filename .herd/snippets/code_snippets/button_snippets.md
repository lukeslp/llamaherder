# Code Snippets from toollama/API/api-tools/tools/snippets/core/ui/interaction/button.js

File: `toollama/API/api-tools/tools/snippets/core/ui/interaction/button.js`  
Language: JavaScript  
Extracted: 2025-06-07 05:24:26  

## Snippet 1
Lines 5-13

```JavaScript
export const ButtonManager = {
    setupButtons(config) {
        const {
            pasteButton,
            restartButton,
            copyButton,
            settingsButton,
            ttsButton,
            handlers
```

## Snippet 2
Lines 17-21

```JavaScript
if (pasteButton && handlers.paste) {
            pasteButton.addEventListener('click', handlers.paste);
        }

        // Restart button
```

## Snippet 3
Lines 22-26

```JavaScript
if (restartButton && handlers.restart) {
            restartButton.addEventListener('click', handlers.restart);
        }

        // Copy button
```

## Snippet 4
Lines 27-31

```JavaScript
if (copyButton && handlers.copy) {
            copyButton.addEventListener('click', handlers.copy);
        }

        // Settings button
```

## Snippet 5
Lines 32-36

```JavaScript
if (settingsButton && handlers.settings) {
            settingsButton.addEventListener('click', handlers.settings);
        }

        // TTS button
```

## Snippet 6
Lines 37-39

```JavaScript
if (ttsButton && handlers.tts) {
            ttsButton.addEventListener('click', handlers.tts);
        }
```

## Snippet 7
Lines 43-46

```JavaScript
if (isLoading) {
            button.classList.add('loading');
            button.innerHTML = `<i class="fas fa-spinner fa-spin"></i> ${loadingText}`;
            button.disabled = true;
```

## Snippet 8
Lines 47-51

```JavaScript
} else {
            button.classList.remove('loading');
            button.innerHTML = originalHtml;
            button.disabled = false;
        }
```

