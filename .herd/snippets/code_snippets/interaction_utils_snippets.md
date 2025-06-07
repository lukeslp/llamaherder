# Code Snippets from toollama/API/api-tools/tools/snippets/processed/interaction_utils.js

File: `toollama/API/api-tools/tools/snippets/processed/interaction_utils.js`  
Language: JavaScript  
Extracted: 2025-06-07 05:21:39  

## Snippet 1
Lines 6-21

```JavaScript
// UI State Management
export const UIStateManager = {
    // Initialize UI state
    initializeState() {
        return {
            isProcessing: false,
            isUploading: false,
            isPanelOpened: false,
            currentFileId: null,
            pendingFiles: [],
            debounceTimeout: null
        };
    },

    // Toggle processing state
    toggleProcessingState(pasteButton, restartButton, isProcessing) {
```

## Snippet 2
Lines 22-24

```JavaScript
if (isProcessing) {
            pasteButton.classList.add('hidden');
            restartButton.classList.remove('hidden');
```

## Snippet 3
Lines 34-36

```JavaScript
if (elements.resultContainer) {
            elements.resultContainer.style.display = "none";
        }
```

## Snippet 4
Lines 37-39

```JavaScript
if (elements.uploadArea) {
            elements.uploadArea.style.display = "flex";
        }
```

## Snippet 5
Lines 40-44

```JavaScript
if (elements.copyButton) {
            elements.copyButton.style.display = "none";
        }

        // Reset progress
```

## Snippet 6
Lines 45-49

```JavaScript
if (elements.progressBar) {
            elements.progressBar.style.width = "0%";
        }

        // Reset messages
```

## Snippet 7
Lines 50-59

```JavaScript
if (elements.altTextDisplay) {
            elements.altTextDisplay.textContent = "";
        }

        // Reset buttons
        this.toggleProcessingState(
            elements.pasteButton,
            elements.restartButton,
            false
        );
```

## Snippet 8
Lines 61-65

```JavaScript
};

// Drag and Drop Handler
export const DragDropHandler = {
    setupDragDrop(uploadArea, fileInput, handleFileSelect) {
```

## Snippet 9
Lines 66-95

```JavaScript
if (!uploadArea || !fileInput) return;

        // Prevent default drag behaviors
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            uploadArea.addEventListener(eventName, preventDefaults, false);
            document.body.addEventListener(eventName, preventDefaults, false);
        });

        // Highlight drop zone when item is dragged over it
        ['dragenter', 'dragover'].forEach(eventName => {
            uploadArea.addEventListener(eventName, highlight, false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            uploadArea.addEventListener(eventName, unhighlight, false);
        });

        // Handle dropped files
        uploadArea.addEventListener('drop', event => {
            const dt = event.dataTransfer;
            const files = dt.files;

            handleFiles(files);
        }, false);

        // Handle clicked files
        fileInput.addEventListener('change', event => {
            handleFiles(event.target.files);
        }, false);
```

## Snippet 10
Lines 96-100

```JavaScript
function preventDefaults(e) {
            e.preventDefault();
            e.stopPropagation();
        }
```

## Snippet 11
Lines 101-104

```JavaScript
function highlight(e) {
            uploadArea.classList.add('highlight');
        }
```

## Snippet 12
Lines 105-108

```JavaScript
function unhighlight(e) {
            uploadArea.classList.remove('highlight');
        }
```

## Snippet 13
Lines 110-112

```JavaScript
if (files && files[0]) {
                handleFileSelect(files[0]);
            }
```

## Snippet 14
Lines 115-126

```JavaScript
};

// Button Manager
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

## Snippet 15
Lines 130-134

```JavaScript
if (pasteButton && handlers.paste) {
            pasteButton.addEventListener('click', handlers.paste);
        }

        // Restart button
```

## Snippet 16
Lines 135-139

```JavaScript
if (restartButton && handlers.restart) {
            restartButton.addEventListener('click', handlers.restart);
        }

        // Copy button
```

## Snippet 17
Lines 140-144

```JavaScript
if (copyButton && handlers.copy) {
            copyButton.addEventListener('click', handlers.copy);
        }

        // Settings button
```

## Snippet 18
Lines 145-149

```JavaScript
if (settingsButton && handlers.settings) {
            settingsButton.addEventListener('click', handlers.settings);
        }

        // TTS button
```

## Snippet 19
Lines 150-152

```JavaScript
if (ttsButton && handlers.tts) {
            ttsButton.addEventListener('click', handlers.tts);
        }
```

## Snippet 20
Lines 156-159

```JavaScript
if (isLoading) {
            button.classList.add('loading');
            button.innerHTML = `<i class="fas fa-spinner fa-spin"></i> ${loadingText}`;
            button.disabled = true;
```

## Snippet 21
Lines 160-164

```JavaScript
} else {
            button.classList.remove('loading');
            button.innerHTML = originalHtml;
            button.disabled = false;
        }
```

## Snippet 22
Lines 166-170

```JavaScript
};

// Tray Manager
export const TrayManager = {
    setupTray(tray, settingsButton) {
```

## Snippet 23
Lines 171-189

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

## Snippet 24
Lines 190-192

```JavaScript
if (isOpen && !tray.contains(e.target) && e.target !== settingsButton) {
                toggleTray();
            }
```

## Snippet 25
Lines 197-199

```JavaScript
if (isOpen && e.key === 'Escape') {
                toggleTray();
            }
```

## Snippet 26
Lines 200-204

```JavaScript
});

        return {
            toggle: toggleTray,
            close: () => {
```

## Snippet 27
Lines 212-216

```JavaScript
};

// Scroll Manager
export const ScrollManager = {
    setupScrollHandlers(container) {
```

## Snippet 28
Lines 217-233

```JavaScript
if (!container) return;

        // Auto-scroll on content change
        const autoScroll = () => {
            container.scrollTop = container.scrollHeight;
        };

        // Smooth scroll to bottom
        const smoothScrollToBottom = () => {
            container.scrollTo({
                top: container.scrollHeight,
                behavior: 'smooth'
            });
        };

        // Handle scroll events
        container.addEventListener('scroll', () => {
```

## Snippet 29
Lines 234-236

```JavaScript
if (container.scrollTop + container.clientHeight >= container.scrollHeight - 10) {
                // User has scrolled to bottom
                container.dataset.autoScroll = 'true';
```

## Snippet 30
Lines 241-247

```JavaScript
});

        return {
            autoScroll,
            smoothScrollToBottom,
            isAtBottom: () => container.dataset.autoScroll === 'true'
        };
```

## Snippet 31
Lines 249-254

```JavaScript
};

// Toast Notification Manager
export const ToastManager = {
    setupToast(containerId = 'toast', defaultDuration = 3000) {
        const toastElement = document.getElementById(containerId);
```

## Snippet 32
Lines 255-269

```JavaScript
if (!toastElement) return null;

        return {
            show: (message, duration = defaultDuration) => {
                toastElement.textContent = message;
                toastElement.classList.add('show');

                setTimeout(() => {
                    toastElement.classList.remove('show');
                }, duration);
            },
            hide: () => {
                toastElement.classList.remove('show');
            }
        };
```

## Snippet 33
Lines 271-282

```JavaScript
};

// Input Manager
export const InputManager = {
    setupInput(config) {
        const {
            input,
            submitButton,
            onSubmit,
            onKeyPress = true,
            clearOnSubmit = true,
            validation = (value) => value.trim() !== ''
```

## Snippet 34
Lines 285-288

```JavaScript
if (!input || !submitButton || !onSubmit) return;

        const handleSubmit = () => {
            const value = input.value;
```

## Snippet 35
Lines 289-291

```JavaScript
if (!validation(value)) return;

            onSubmit(value);
```

## Snippet 36
Lines 292-294

```JavaScript
if (clearOnSubmit) {
                input.value = '';
            }
```

## Snippet 37
Lines 301-304

```JavaScript
if (event.key === 'Enter' && !event.shiftKey) {
                    event.preventDefault();
                    handleSubmit();
                }
```

## Snippet 38
Lines 306-308

```JavaScript
}

        return {
```

## Snippet 39
Lines 315-324

```JavaScript
};

// Stream Content Manager
export const StreamManager = {
    setupStream(config) {
        const {
            onDelta = () => {},
            onComplete = () => {},
            onError = console.error,
            decoder = new TextDecoder()
```

## Snippet 40
Lines 325-329

```JavaScript
} = config;

        return {
            async processStream(reader) {
                try {
```

## Snippet 41
Lines 338-340

```JavaScript
if (line.startsWith('data:')) {
                                try {
                                    const data = JSON.parse(line.slice(5));
```

## Snippet 42
Lines 343-345

```JavaScript
} else if (data.type === 'complete') {
                                        onComplete(data);
                                    }
```

## Snippet 43
Lines 346-348

```JavaScript
} catch (error) {
                                    onError('Error parsing stream:', error);
                                }
```

## Snippet 44
Lines 352-354

```JavaScript
} catch (error) {
                    onError('Stream processing error:', error);
                }
```

