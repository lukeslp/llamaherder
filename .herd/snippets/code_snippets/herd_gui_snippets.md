# Code Snippets from templates/herd_gui.html

File: `templates/herd_gui.html`  
Language: HTML  
Extracted: 2025-06-07 05:08:09  

## Snippet 1
Lines 1-6

```HTML
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Herd AI Image Processor</title>
```

## Snippet 2
Lines 8-27

```HTML
</head>
<body>
  <button id="theme-toggle-btn" class="btn btn-secondary" aria-pressed="false" aria-label="Toggle dark mode" style="position: absolute; top: 1rem; right: 1rem; z-index: 2000;">
    <span id="theme-toggle-icon" aria-hidden="true">🌞</span> <span id="theme-toggle-label">Light Mode</span>
  </button>
  <main class="bg-surface rounded shadow p-4" style="max-width: 900px; margin: 2rem auto;">
    <h1 class="text-primary">Herd AI Image Processor</h1>
    <form id="upload-form" enctype="multipart/form-data" tabindex="0" aria-label="Image upload form" autocomplete="off">
      <label for="provider-select" class="form-label">Model/Provider:</label>
      <select id="provider-select" class="form-input provider-select" aria-label="Select model/provider">
        <option value="ollama" selected>Ollama (mistral-small3.1:latest, default)</option>
        <option value="xai">X.AI</option>
        <option value="cohere">Cohere (command-a-03-2025, API)</option>
      </select>
    </form>
    <div class="drop-area bg-surface rounded shadow-md p-4 mb-2" id="drop-area" tabindex="0" aria-label="Drop images here or click to select">
      <span class="drop-icon" aria-hidden="true">📂</span>
      <div class="drop-instructions">Drag and drop images here</div>
      <div class="drop-hint">or <label for="file-input" style="color: var(--primary-color); cursor: pointer; text-decoration: underline;">click to select</label></div>
      <small>Supports multiple files and folders.</small>
```

## Snippet 3
Lines 31-50

```HTML
<input id="dir-input" name="dir-images" type="file" accept="image/*,.heic,.heif,.webp,.gif,.bmp,.tiff,.svg" multiple webkitdirectory directory style="display:none;" aria-label="Select directory of images" />
    <button type="submit" style="display:none;">Upload</button>
    <div id="processing-info" class="processing-count" style="display:none;">
      Processing: <span id="processed-count">0</span>/<span id="total-count">0</span> images
    </div>
    <div class="download-container" id="download-container" style="display:none;">
      <button type="button" class="btn btn-primary" id="download-all-btn">Download All Markdown</button>
      <button type="button" class="btn btn-primary" id="download-html-btn">Download HTML Report</button>
      <button type="button" class="btn btn-primary" id="download-pdf-btn">Download PDF Report</button>
    </div>
    <div class="bulk-actions" id="bulk-actions" style="display:none; margin: 1rem 0;">
      <div class="select-all-container" style="margin-bottom: 0.5rem;">
        <input type="checkbox" id="select-all" aria-label="Select all files" style="margin-right: 0.5rem;">
        <label for="select-all">Select All</label>
      </div>
      <button type="button" class="btn btn-secondary" id="bulk-retry-btn" disabled>Retry Selected</button>
      <button type="button" class="btn btn-secondary" id="bulk-undo-btn" disabled>Undo Selected</button>
      <span id="selected-count" style="margin-left: 1rem; display: none;">0 files selected</span>
    </div>
    <div class="file-list" id="file-list" aria-live="polite"></div>
```

