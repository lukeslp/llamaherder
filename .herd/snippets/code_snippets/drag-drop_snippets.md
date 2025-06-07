# Code Snippets from toollama/API/api-tools/tools/snippets/core/ui/interaction/drag-drop.js

File: `toollama/API/api-tools/tools/snippets/core/ui/interaction/drag-drop.js`  
Language: JavaScript  
Extracted: 2025-06-07 05:23:59  

## Snippet 1
Lines 7-36

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

## Snippet 2
Lines 37-41

```JavaScript
function preventDefaults(e) {
            e.preventDefault();
            e.stopPropagation();
        }
```

## Snippet 3
Lines 42-45

```JavaScript
function highlight(e) {
            uploadArea.classList.add('highlight');
        }
```

## Snippet 4
Lines 46-49

```JavaScript
function unhighlight(e) {
            uploadArea.classList.remove('highlight');
        }
```

## Snippet 5
Lines 51-53

```JavaScript
if (files && files[0]) {
                handleFileSelect(files[0]);
            }
```

