# Code Snippets from toollama/API/api-tools/tools/snippets/core/templates/components.js

File: `toollama/API/api-tools/tools/snippets/core/templates/components.js`  
Language: JavaScript  
Extracted: 2025-06-07 05:22:30  

## Snippet 1
Lines 10-26

```JavaScript
uploadArea: () => `
        <div id="uploadArea"
             class="upload-area"
             aria-labelledby="upload-heading"
             role="button"
             tabindex="0"
             aria-pressed="false">
            <i class="fas fa-cloud-upload-alt upload-icon" aria-hidden="true"></i>
            <h2 id="upload-heading" class="upload-text">
                Drop, paste, or click to upload!
            </h2>
            <div class="upload-subtext">
                JPG, JPEG, PNG, GIF, WEBP, and more. Try any format, it might work!<br /><br />
                Max size: 20MB
            </div>
            <input type="file"
                   id="fileInput"
```

## Snippet 2
Lines 36-67

```JavaScript
resultContainer: () => `
        <div id="resultContainer"
             class="result-container"
             role="region"
             aria-live="polite"
             aria-atomic="true">
            <div id="streamingIndicator"
                 class="streaming-indicator"
                 role="status"
                 aria-live="assertive">
                <img id="uploadedImage"
                     class="uploaded-image"
                     src=""
                     alt="Processing..." />
                <div class="progress-bar"
                     role="progressbar"
                     aria-valuemin="0"
                     aria-valuemax="100">
                    <div class="progress-fill"></div>
                </div>
            </div>
            <div id="altTextDisplay"
                 class="alt-text-display"
                 role="textbox"
                 aria-readonly="true"></div>
            <button id="copyButton"
                    class="copy-button"
                    aria-label="Copy Alt Text to Clipboard">
                <i class="fas fa-copy" aria-hidden="true"></i> Copy to Clipboard
            </button>
        </div>`,
```

## Snippet 3
Lines 72-91

```JavaScript
controlButtons: () => `
        <button id="settingsButton"
                class="settings-button"
                aria-haspopup="true"
                aria-controls="settings-tray"
                aria-label="Open Settings">
            <i class="fas fa-question" aria-hidden="true"></i>
        </button>
        <button id="pasteButton"
                class="paste-button"
                aria-label="Paste Image">
            <i class="fas fa-paste"></i> Paste Image
        </button>
        <button id="restartButton"
                class="restart-button"
                aria-label="Start Over"
                onclick="window.location.reload()">
            <i class="fas fa-redo"></i> Start Over
        </button>`,
```

## Snippet 4
Lines 98-111

```JavaScript
supportButtons: (donateUrl = "https://coolhand.gumroad.com/l/donate?layout=profile", patreonUrl = "https://assisted.space/join") => `
        <div class="support-buttons">
            <a href="${donateUrl}"
               target="_blank"
               class="support-button">
                <i class="fas fa-heart"></i> Tip
            </a>
            <a href="${patreonUrl}"
               target="_blank"
               class="support-button">
                <i class="fas fa-star"></i> Patreon
            </a>
        </div>`,
```

## Snippet 5
Lines 117-126

```JavaScript
settingsTray: (content) => `
        <div id="settings-tray"
             class="tray"
             aria-labelledby="about-heading"
             role="dialog">
            <div class="tray-content">
                <h3 id="about-heading">What is this?</h3>
                ${content}
            </div>
        </div>`
```

