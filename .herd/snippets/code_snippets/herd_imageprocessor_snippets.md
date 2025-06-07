# Code Snippets from storage/gui/herd_imageprocessor.py

File: `storage/gui/herd_imageprocessor.py`  
Language: Python  
Extracted: 2025-06-07 05:08:22  

## Snippet 1
Lines 1-30

```Python
"""
Herd AI Image Processor GUI
Note: WeasyPrint has been completely removed due to dependency issues on macOS.
PDF generation now uses ReportLab exclusively.
"""
import os
import tempfile
import shutil
import json
import base64
import io
from pathlib import Path
from flask import Flask, request, jsonify, render_template, render_template_string, send_file, abort
from werkzeug.utils import secure_filename
from threading import Lock
from src.herd_ai.image_processor import ImageProcessor
from src.herd_ai.utils.xai import IMAGE_ALT_TEXT_TEMPLATE
import zipfile
import markdown
import jinja2
import uuid
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch

# Flask app setup
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = tempfile.mkdtemp(prefix="herd_gui_uploads_")
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max upload
```

## Snippet 2
Lines 37-43

```Python
# Check if PIL is available for image processing
try:
    from PIL import Image
    has_pil = True
except ImportError:
    has_pil = False
```

## Snippet 3
Lines 44-59

```Python
# Check if BeautifulSoup is available for HTML parsing
try:
    from bs4 import BeautifulSoup
    has_bs4 = True
except ImportError:
    has_bs4 = False

# HTML template (modern, accessible, fully brand-styled)
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Herd AI Image Processor</title>
  <style>
```

## Snippet 4
Lines 60-94

```Python
/* === BEGIN BRAND REFERENCE - UNIFIED STYLE GUIDE === */
    :root {
      --background-color: #f5f7fa;
      --surface-color: #fff;
      --primary-color: #2d6cdf;
      --secondary-color: #eaf1fb;
      --accent-color: #1b1b1b;
      --success-color: #2ecc40;
      --error-color: #ff4136;
      --border-radius: 8px;
      --font-size: 1.1rem;
      --shadow: 0 2px 8px rgba(44, 62, 80, 0.08);
      --shadow-md: 0 4px 16px rgba(44, 62, 80, 0.12);
      --input-bg: #fff;
      --input-border: #cfd8dc;
      --input-focus: #2d6cdf;
      --btn-bg: #2d6cdf;
      --btn-bg-hover: #174a8c;
      --btn-text: #fff;
      --btn-secondary-bg: #eaf1fb;
      --btn-secondary-text: #2d6cdf;
      --btn-secondary-border: #2d6cdf;
      --card-bg: #fff;
      --card-border: #e0e0e0;
      --card-shadow: 0 2px 8px rgba(44, 62, 80, 0.08);
      --focus-outline: 2px solid #2d6cdf;
    }
    body {
      font-family: system-ui, sans-serif;
      background: var(--background-color);
      color: var(--accent-color);
      margin: 0;
      padding: 0;
      min-height: 100vh;
    }
```

## Snippet 5
Lines 104-115

```Python
.text-primary { color: var(--primary-color); }
    .btn {
      display: inline-block;
      font-size: 1rem;
      font-weight: 500;
      border-radius: var(--border-radius);
      padding: 0.4rem 1.2rem;
      border: none;
      cursor: pointer;
      transition: background 0.2s, color 0.2s, border 0.2s;
      outline: none;
    }
```

## Snippet 6
Lines 116-175

```Python
.btn:focus { outline: var(--focus-outline); }
    .btn-primary {
      background: var(--btn-bg);
      color: var(--btn-text);
    }
    .btn-primary:hover, .btn-primary:focus {
      background: var(--btn-bg-hover);
    }
    .btn-secondary {
      background: var(--btn-secondary-bg);
      color: var(--btn-secondary-text);
      border: 1px solid var(--btn-secondary-border);
    }
    .btn-secondary:hover, .btn-secondary:focus {
      background: var(--btn-bg);
      color: var(--btn-text);
    }
    .form-input {
      width: 100%;
      padding: 0.5rem 1rem;
      border-radius: var(--border-radius);
      border: 1px solid var(--input-border);
      background: var(--input-bg);
      color: var(--accent-color);
      font-size: 1rem;
      margin-bottom: 1rem;
      transition: border 0.2s;
    }
    .form-input:focus {
      border-color: var(--input-focus);
      outline: var(--focus-outline);
    }
    .file-item {
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      border-radius: var(--border-radius);
      box-shadow: var(--card-shadow);
      margin-bottom: 0.5rem;
      padding: 1rem;
      display: flex;
      flex-direction: row;
      gap: 1rem;
      font-size: var(--font-size);
      align-items: center;
    }
    .file-thumb {
      width: 80px;
      height: 80px;
      object-fit: cover;
      border-radius: var(--border-radius);
      border: 1px solid var(--input-border);
      background: var(--input-bg);
      margin-right: 1rem;
    }
    .file-meta {
      flex: 1;
      display: flex;
      flex-direction: column;
      gap: 0.2rem;
    }
```

## Snippet 7
Lines 187-250

```Python
}
    body.dark-theme {
      --background-color: #181c20;
      --surface-color: #23272e;
      --primary-color: #7ab7ff;
      --secondary-color: #23272e;
      --accent-color: #f5f7fa;
      --input-bg: #23272e;
      --input-border: #3a3f4b;
      --btn-bg: #174a8c;
      --btn-bg-hover: #2d6cdf;
      --btn-text: #fff;
      --btn-secondary-bg: #23272e;
      --btn-secondary-text: #7ab7ff;
      --btn-secondary-border: #7ab7ff;
      --card-bg: #23272e;
      --card-border: #3a3f4b;
      --focus-outline: 2px solid #7ab7ff;
    }
    .drop-area {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      border: 3px dashed var(--primary-color);
      border-radius: var(--border-radius);
      background: var(--surface-color);
      min-height: 220px;
      min-width: 320px;
      width: 100%;
      max-width: 540px;
      margin: 2.5rem auto 2rem auto;
      text-align: center;
      transition: background 0.2s, border-color 0.2s, box-shadow 0.2s;
      box-shadow: 0 4px 24px rgba(44, 62, 80, 0.10);
      outline: none;
      position: relative;
    }
    .drop-area:focus {
      border-color: var(--btn-bg-hover);
      box-shadow: 0 0 0 4px rgba(45, 108, 223, 0.15);
    }
    .drop-area.dragover {
      background: var(--secondary-color);
      border-color: var(--btn-bg-hover);
      box-shadow: 0 0 0 6px rgba(45, 108, 223, 0.18);
    }
    .drop-icon {
      font-size: 3.5rem;
      color: var(--primary-color);
      margin-bottom: 0.5rem;
      display: block;
    }
    .drop-instructions {
      font-size: 1.25rem;
      font-weight: 600;
      color: var(--accent-color);
      margin-bottom: 0.25rem;
    }
    .drop-hint {
      font-size: 1rem;
      color: #6c7a89;
      margin-bottom: 0.5rem;
    }
```

## Snippet 8
Lines 255-263

```Python
}
    body.dark-theme .drop-area {
      background: var(--surface-color);
      border-color: var(--primary-color);
    }
    body.dark-theme .drop-area.dragover {
      background: #23272e;
      border-color: var(--btn-bg-hover);
    }
```

## Snippet 9
Lines 266-284

```Python
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
      </select>
    </form>
    <div class="drop-area bg-surface rounded shadow-md p-4 mb-2" id="drop-area" tabindex="0" aria-label="Drop images here or click to select">
      <span class="drop-icon" aria-hidden="true">📂</span>
      <div class="drop-instructions">Drag and drop images here</div>
      <div class="drop-hint">or <label for="file-input" style="color: var(--primary-color); cursor: pointer; text-decoration: underline;">click to select</label></div>
      <small>Supports multiple files and folders.</small>
```

## Snippet 10
Lines 288-310

```Python
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

    <!-- Add bulk actions container -->
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

## Snippet 11
Lines 311-345

```Python
</main>
  <script>
    const dropArea = document.getElementById('drop-area');
    const fileInput = document.getElementById('file-input');
    const dirInput = document.getElementById('dir-input');
    const dirBtn = document.getElementById('dir-btn');
    const fileList = document.getElementById('file-list');
    const providerSelect = document.getElementById('provider-select');
    const downloadAllBtn = document.getElementById('download-all-btn');
    const downloadHtmlBtn = document.getElementById('download-html-btn');
    const downloadPdfBtn = document.getElementById('download-pdf-btn');
    const downloadContainer = document.getElementById('download-container');
    const processingInfo = document.getElementById('processing-info');
    const processedCount = document.getElementById('processed-count');
    const totalCount = document.getElementById('total-count');

    // Track processing status
    let processedImages = 0;
    let totalImages = 0;
    let processingComplete = false;
    let hasMd = false;
    let currentImages = [];

    // Add new JavaScript to handle bulk actions
    const bulkActionsContainer = document.getElementById('bulk-actions');
    const selectAllCheckbox = document.getElementById('select-all');
    const bulkRetryBtn = document.getElementById('bulk-retry-btn');
    const bulkUndoBtn = document.getElementById('bulk-undo-btn');
    const selectedCountSpan = document.getElementById('selected-count');

    // Track selected items
    let selectedItems = new Set();

    document.getElementById('upload-form').addEventListener('submit', e => e.preventDefault());
    dropArea.addEventListener('click', e => {
```

## Snippet 12
Lines 350-356

```Python
dropArea.addEventListener('dragleave', e => { e.preventDefault(); dropArea.classList.remove('dragover'); });
    dropArea.addEventListener('drop', e => {
      e.preventDefault();
      dropArea.classList.remove('dragover');
      handleFiles(e.dataTransfer.files);
    });
    fileInput.addEventListener('change', e => handleFiles(e.target.files));
```

## Snippet 13
Lines 357-365

```Python
dirBtn.addEventListener('click', e => { dirInput.click(); });
    dirInput.addEventListener('change', e => handleFiles(e.target.files));

    // Handle select all checkbox
    selectAllCheckbox.addEventListener('change', () => {
      const checkboxes = document.querySelectorAll('.file-checkbox');
      checkboxes.forEach(checkbox => {
        checkbox.checked = selectAllCheckbox.checked;
        const fileId = checkbox.getAttribute('data-file-id');
```

## Snippet 14
Lines 384-390

```Python
function updateBulkButtons() {
      const hasSelection = selectedItems.size > 0;
      bulkRetryBtn.disabled = !hasSelection;
      bulkUndoBtn.disabled = !hasSelection;
    }

    // Handle selection of individual checkboxes
```

## Snippet 15
Lines 395-400

```Python
} else {
        selectedItems.delete(fileId);
        selectAllCheckbox.checked = false;
      }
      updateSelectedCount();
      updateBulkButtons();
```

## Snippet 16
Lines 405-419

```Python
if (selectedItems.size === 0) return;

      const fileIds = Array.from(selectedItems);
      fetch('/api/bulk_retry', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
          file_ids: fileIds,
          provider: providerSelect.value
        })
      })
      .then(r => r.json())
      .then(data => {
        // Handle response and update UI
        const results = data.results || [];
```

## Snippet 17
Lines 421-423

```Python
if (result.file_id) {
            updateFileItemAfterBulkAction(result);
          }
```

## Snippet 18
Lines 424-429

```Python
}
        // Reset selection
        selectedItems.clear();
        selectAllCheckbox.checked = false;
        updateSelectedCount();
        updateBulkButtons();
```

## Snippet 19
Lines 430-433

```Python
})
      .catch(err => {
        console.error("Bulk retry failed:", err);
      });
```

## Snippet 20
Lines 438-443

```Python
if (selectedItems.size === 0) return;

      // Collect undo tokens from the file items
      const undoTokens = [];
      selectedItems.forEach(fileId => {
        const item = document.getElementById(`file-item-${fileId}`);
```

## Snippet 21
Lines 446-449

```Python
if (tokenAttr) {
            try {
              const token = JSON.parse(tokenAttr);
              undoTokens.push(token);
```

## Snippet 22
Lines 450-452

```Python
} catch (e) {
              console.error("Invalid undo token:", tokenAttr);
            }
```

## Snippet 23
Lines 457-461

```Python
if (undoTokens.length === 0) return;

      fetch('/api/bulk_undo', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
```

## Snippet 24
Lines 463-470

```Python
})
      .then(r => r.json())
      .then(data => {
        // Add undo success message to each file item
        const results = data.results || [];
        let idx = 0;
        selectedItems.forEach(fileId => {
          const item = document.getElementById(`file-item-${fileId}`);
```

## Snippet 25
Lines 475-477

```Python
} else {
              item.innerHTML += `<div class='error'>Undo failed: ${result.error || "Unknown error"}</div>`;
            }
```

## Snippet 26
Lines 479-485

```Python
});

        // Reset selection
        selectedItems.clear();
        selectAllCheckbox.checked = false;
        updateSelectedCount();
        updateBulkButtons();
```

## Snippet 27
Lines 486-489

```Python
})
      .catch(err => {
        console.error("Bulk undo failed:", err);
      });
```

## Snippet 28
Lines 499-502

```Python
if (meta) {
          meta.innerHTML = `<strong>${result.original_name}</strong><span class='error'>Error: ${result.error}</span>`;
        }
        return;
```

## Snippet 29
Lines 503-506

```Python
}

      // Update the file item with the new data
      const meta = fileItem.querySelector('.file-meta');
```

## Snippet 30
Lines 507-531

```Python
if (meta) {
        meta.innerHTML = `
          <div class="file-names">
            <strong>New Name: ${result.new_name}</strong>
            <div><small>Original: ${result.original_name}</small></div>
          </div>
          <div class="alt-text-container">
            <label for="alt-text-${result.file_id}" class="form-label">Alt Text:</label>
            <textarea id="alt-text-${result.file_id}" class="alt-textarea" rows="2">${result.alt_text}</textarea>
            <button class="btn btn-secondary save-alt-btn" data-file-id="${result.file_id}">Save Alt Text</button>
          </div>
          <span><b>Description:</b> ${result.description}</span>
          <div class="file-metadata">
            <span><b>Provider/Model:</b> ${result.provider}/${result.model}</span>
            <span><b>Dimensions:</b> ${result.dimensions || 'Unknown'}</span>
            <span><b>Size:</b> ${result.file_size}</span>
            <span><b>Type:</b> ${result.file_type}</span>
            <span><b>Metadata embedded:</b> ${result.metadata_embedded ? 'Yes' : 'No'}</span>
          </div>
        `;

        // Add button group
        const buttonGroup = document.createElement('div');
        buttonGroup.className = 'button-group';
```

## Snippet 31
Lines 532-547

```Python
if (result.md_id) {
          hasMd = true;
          const mdBtn = document.createElement('button');
          mdBtn.className = 'md-btn btn btn-primary';
          mdBtn.textContent = 'Download Markdown';
          mdBtn.onclick = () => window.open(`/api/download_md?md_id=${encodeURIComponent(result.md_id)}`);
          buttonGroup.appendChild(mdBtn);

          // Make sure download buttons are visible
          downloadContainer.style.display = 'flex';
        }

        // Add Retry button again
        const retryBtn = document.createElement('button');
        retryBtn.className = 'retry-btn btn btn-secondary';
        retryBtn.textContent = 'Retry';
```

## Snippet 32
Lines 548-555

```Python
retryBtn.setAttribute('aria-label', `Retry processing for ${result.original_name}`);
        retryBtn.onclick = () => retryProcessing(result.file_id, meta);
        buttonGroup.appendChild(retryBtn);

        // Add Undo button
        const undoBtn = document.createElement('button');
        undoBtn.className = 'undo-btn btn btn-secondary';
        undoBtn.textContent = 'Undo';
```

## Snippet 33
Lines 561-564

```Python
}

      // Update preview image
      const thumb = fileItem.querySelector('.file-thumb');
```

## Snippet 34
Lines 565-570

```Python
if (thumb) {
        thumb.alt = result.new_name || result.original_name;
        thumb.src = result.preview_url || '';
      }

      // Store undo token in the file item
```

## Snippet 35
Lines 571-573

```Python
if (result.undo_token) {
        fileItem.setAttribute('data-undo-token', JSON.stringify(result.undo_token));
      }
```

## Snippet 36
Lines 576-581

```Python
// Update handleFiles function to show the bulk actions container
    const originalHandleFiles = handleFiles;
    handleFiles = function(files) {
      // Call the original function
      originalHandleFiles(files);
```

## Snippet 37
Lines 596-614

```Python
// Reset state for new batch
      fileList.innerHTML = '';
      downloadContainer.style.display = 'none';
      bulkActionsContainer.style.display = 'block';
      hasMd = false;
      processedImages = 0;
      totalImages = imageFiles.length;
      processingComplete = false;
      currentImages = [];
      selectedItems.clear();
      selectAllCheckbox.checked = false;
      updateSelectedCount();
      updateBulkButtons();

      // Display processing counter
      processedCount.textContent = '0';
      totalCount.textContent = imageFiles.length;
      processingInfo.style.display = 'block';
```

## Snippet 38
Lines 616-620

```Python
for (const file of imageFiles) {
        const item = document.createElement('div');
        item.className = 'file-item bg-surface rounded shadow-md p-3 mb-2';
        item.id = `file-item-${currentImages.length}`;
```

## Snippet 39
Lines 621-658

```Python
// Add checkbox for selection
        const checkboxContainer = document.createElement('div');
        checkboxContainer.className = 'checkbox-container';
        checkboxContainer.style.marginRight = '10px';

        const checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.className = 'file-checkbox';
        checkbox.setAttribute('data-file-id', currentImages.length);
        checkbox.setAttribute('aria-label', `Select ${file.name}`);
        checkbox.addEventListener('change', () => handleFileCheckboxChange(checkbox));

        checkboxContainer.appendChild(checkbox);

        const contentContainer = document.createElement('div');
        contentContainer.className = 'd-flex align-items-center';
        contentContainer.style.flex = '1';

        const thumb = document.createElement('img');
        thumb.className = 'file-thumb';
        thumb.alt = file.name;
        thumb.src = URL.createObjectURL(file);

        const meta = document.createElement('div');
        meta.className = 'file-meta';
        meta.innerHTML = `<strong>${file.name}</strong><span>Waiting to process...</span>`;

        contentContainer.appendChild(thumb);
        contentContainer.appendChild(meta);

        item.appendChild(checkboxContainer);
        item.appendChild(contentContainer);
        fileList.appendChild(item);

        currentImages.push({
          file: file,
          index: currentImages.length
        });
```

## Snippet 40
Lines 666-668

```Python
if (index >= files.length) {
        processingComplete = true;
        processingInfo.style.display = 'none';
```

## Snippet 41
Lines 669-672

```Python
if (hasMd) {
          downloadContainer.style.display = 'flex';
        }
        return;
```

## Snippet 42
Lines 673-680

```Python
}

      const formData = new FormData();
      formData.append('images', files[index]);
      formData.append('provider', providerSelect.value);

      // Update UI to show currently processing file
      const fileItem = document.getElementById(`file-item-${index}`);
```

## Snippet 43
Lines 681-695

```Python
if (fileItem) {
        const meta = fileItem.querySelector('.file-meta');
        meta.innerHTML = `<strong>${files[index].name}</strong><span>Processing...</span>`;
      }

      fetch('/api/process_images', {
        method: 'POST',
        body: formData
      })
      .then(r => r.json())
      .then(res => {
        // Update the processed count
        processedImages++;
        processedCount.textContent = processedImages;
```

## Snippet 44
Lines 702-727

```Python
} else {
              // Updated metadata display with new fields
              meta.innerHTML = `
                <div class="file-names">
                  <strong>New Name: ${result.new_name}</strong>
                  <div><small>Original: ${result.original_name}</small></div>
                </div>
                <div class="alt-text-container">
                  <label for="alt-text-${result.file_id}" class="form-label">Alt Text:</label>
                  <textarea id="alt-text-${result.file_id}" class="alt-textarea" rows="2">${result.alt_text}</textarea>
                  <button class="btn btn-secondary save-alt-btn" data-file-id="${result.file_id}">Save Alt Text</button>
                </div>
                <span><b>Description:</b> ${result.description}</span>
                <div class="file-metadata">
                  <span><b>Provider/Model:</b> ${result.provider}/${result.model}</span>
                  <span><b>Dimensions:</b> ${result.dimensions || 'Unknown'}</span>
                  <span><b>Size:</b> ${result.file_size}</span>
                  <span><b>Type:</b> ${result.file_type}</span>
                  <span><b>Metadata embedded:</b> ${result.metadata_embedded ? 'Yes' : 'No'}</span>
                </div>
              `;

              // Add button group
              const buttonGroup = document.createElement('div');
              buttonGroup.className = 'button-group';
```

## Snippet 45
Lines 728-740

```Python
if (result.md_id) {
                hasMd = true;
                const mdBtn = document.createElement('button');
                mdBtn.className = 'md-btn btn btn-primary';
                mdBtn.textContent = 'Download Markdown';
                mdBtn.onclick = () => window.open(`/api/download_md?md_id=${encodeURIComponent(result.md_id)}`);
                buttonGroup.appendChild(mdBtn);
              }

              // Add Retry button
              const retryBtn = document.createElement('button');
              retryBtn.className = 'retry-btn btn btn-secondary';
              retryBtn.textContent = 'Retry';
```

## Snippet 46
Lines 741-748

```Python
retryBtn.setAttribute('aria-label', `Retry processing for ${result.original_name}`);
              retryBtn.onclick = () => retryProcessing(result.file_id, meta);
              buttonGroup.appendChild(retryBtn);

              // Add Undo button
              const undoBtn = document.createElement('button');
              undoBtn.className = 'undo-btn btn btn-secondary';
              undoBtn.textContent = 'Undo';
```

## Snippet 47
Lines 749-760

```Python
undoBtn.setAttribute('aria-label', `Undo changes for ${result.original_name}`);
              undoBtn.onclick = () => undoAction(result.undo_token, fileItem);
              buttonGroup.appendChild(undoBtn);

              meta.appendChild(buttonGroup);

              // Update preview image
              const thumb = fileItem.querySelector('.file-thumb');
              thumb.alt = result.new_name || result.original_name;
              thumb.src = result.preview_url || '';

              // Store undo token in the file item
```

## Snippet 48
Lines 761-763

```Python
if (result.undo_token) {
                fileItem.setAttribute('data-undo-token', JSON.stringify(result.undo_token));
              }
```

## Snippet 49
Lines 768-770

```Python
if (hasMd && !processingComplete) {
            downloadContainer.style.display = 'flex';
          }
```

## Snippet 50
Lines 775-781

```Python
})
      .catch(err => {
        // Update the processed count even on error
        processedImages++;
        processedCount.textContent = processedImages;

        // Update this file's display
```

## Snippet 51
Lines 782-788

```Python
if (fileItem) {
          const meta = fileItem.querySelector('.file-meta');
          meta.innerHTML = `<strong>${files[index].name}</strong><span class='error'>Error: ${err}</span>`;
        }

        // Continue with next file
        processNextImage(files, index + 1);
```

## Snippet 52
Lines 794-807

```Python
if (!fileId) return;

      metaElement.innerHTML = '<span>Processing again...</span>';

      fetch('/api/retry_processing', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
          file_id: fileId,
          provider: providerSelect.value
        })
      })
      .then(r => r.json())
      .then(result => {
```

## Snippet 53
Lines 810-835

```Python
} else {
          // Updated metadata display with new fields
          metaElement.innerHTML = `
            <div class="file-names">
              <strong>New Name: ${result.new_name}</strong>
              <div><small>Original: ${result.original_name}</small></div>
            </div>
            <div class="alt-text-container">
              <label for="alt-text-${result.file_id}" class="form-label">Alt Text:</label>
              <textarea id="alt-text-${result.file_id}" class="alt-textarea" rows="2">${result.alt_text}</textarea>
              <button class="btn btn-secondary save-alt-btn" data-file-id="${result.file_id}">Save Alt Text</button>
            </div>
            <span><b>Description:</b> ${result.description}</span>
            <div class="file-metadata">
              <span><b>Provider/Model:</b> ${result.provider}/${result.model}</span>
              <span><b>Dimensions:</b> ${result.dimensions || 'Unknown'}</span>
              <span><b>Size:</b> ${result.file_size}</span>
              <span><b>Type:</b> ${result.file_type}</span>
              <span><b>Metadata embedded:</b> ${result.metadata_embedded ? 'Yes' : 'No'}</span>
            </div>
          `;

          // Add button group
          const buttonGroup = document.createElement('div');
          buttonGroup.className = 'button-group';
```

## Snippet 54
Lines 836-851

```Python
if (result.md_id) {
            hasMd = true;
            const mdBtn = document.createElement('button');
            mdBtn.className = 'md-btn btn btn-primary';
            mdBtn.textContent = 'Download Markdown';
            mdBtn.onclick = () => window.open(`/api/download_md?md_id=${encodeURIComponent(result.md_id)}`);
            buttonGroup.appendChild(mdBtn);

            // Make sure download buttons are visible
            downloadContainer.style.display = 'flex';
          }

          // Add Retry button again
          const retryBtn = document.createElement('button');
          retryBtn.className = 'retry-btn btn btn-secondary';
          retryBtn.textContent = 'Retry';
```

## Snippet 55
Lines 852-859

```Python
retryBtn.setAttribute('aria-label', `Retry processing for ${result.original_name}`);
          retryBtn.onclick = () => retryProcessing(result.file_id, metaElement);
          buttonGroup.appendChild(retryBtn);

          // Add Undo button
          const undoBtn = document.createElement('button');
          undoBtn.className = 'undo-btn btn btn-secondary';
          undoBtn.textContent = 'Undo';
```

## Snippet 56
Lines 860-867

```Python
undoBtn.setAttribute('aria-label', `Undo changes for ${result.original_name}`);
          undoBtn.onclick = () => undoAction(result.undo_token, metaElement.parentNode.parentNode);
          buttonGroup.appendChild(undoBtn);

          meta.appendChild(buttonGroup);

          // Update the parent file item data attributes
          const fileItem = metaElement.parentNode.parentNode;
```

## Snippet 57
Lines 868-874

```Python
if (fileItem && result.undo_token) {
            fileItem.setAttribute('data-undo-token', JSON.stringify(result.undo_token));
          }

          // Update preview image
          const fileItemContainer = metaElement.parentNode;
          const thumb = fileItemContainer.querySelector('.file-thumb');
```

## Snippet 58
Lines 875-878

```Python
if (thumb) {
            thumb.alt = result.new_name || result.original_name;
            thumb.src = result.preview_url || '';
          }
```

## Snippet 59
Lines 880-883

```Python
})
      .catch(err => {
        metaElement.innerHTML = `<span class='error'>Retry failed: ${err}</span>`;
      });
```

## Snippet 60
Lines 886-888

```Python
// Add CSS for file metadata display
    const style = document.createElement('style');
    style.textContent = `
```

## Snippet 61
Lines 889-927

```Python
.file-names { margin-bottom: 8px; }
      .file-metadata {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin-top: 8px;
        margin-bottom: 8px;
      }
      .file-metadata span {
        background-color: var(--secondary-color);
        padding: 3px 8px;
        border-radius: 4px;
        font-size: 0.9rem;
      }
      .checkbox-container {
        display: flex;
        align-items: center;
        padding: 0 10px;
      }
      .file-checkbox {
        width: 18px;
        height: 18px;
        cursor: pointer;
      }
      #select-all {
        width: 18px;
        height: 18px;
        cursor: pointer;
      }
      .bulk-actions {
        background-color: var(--surface-color);
        border-radius: var(--border-radius);
        padding: 10px 15px;
        box-shadow: var(--shadow);
        margin-bottom: 15px;
      }
      body.dark-theme .file-metadata span {
        background-color: var(--surface-color);
      }
```

## Snippet 62
Lines 928-935

```Python
`;
    document.head.appendChild(style);

    // Theme toggle logic
    const themeToggleBtn = document.getElementById('theme-toggle-btn');
    const themeToggleLabel = document.getElementById('theme-toggle-label');
    const themeToggleIcon = document.getElementById('theme-toggle-icon');
```

## Snippet 63
Lines 937-941

```Python
if (dark) {
        document.body.classList.add('dark-theme');
        themeToggleBtn.setAttribute('aria-pressed', 'true');
        themeToggleLabel.textContent = 'Dark Mode';
        themeToggleIcon.textContent = '🌙';
```

## Snippet 64
Lines 942-947

```Python
} else {
        document.body.classList.remove('dark-theme');
        themeToggleBtn.setAttribute('aria-pressed', 'false');
        themeToggleLabel.textContent = 'Light Mode';
        themeToggleIcon.textContent = '🌞';
      }
```

## Snippet 65
Lines 948-961

```Python
}

    // Detect system preference on load
    let prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    setTheme(prefersDark);

    // Toggle theme on button click
    themeToggleBtn.addEventListener('click', () => {
      const isDark = document.body.classList.contains('dark-theme');
      setTheme(!isDark);
    });

    // Keyboard accessibility: toggle on Enter/Space
    themeToggleBtn.addEventListener('keydown', (e) => {
```

## Snippet 66
Lines 962-965

```Python
if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        themeToggleBtn.click();
      }
```

## Snippet 67
Lines 970-973

```Python
function isImageFile(file) {
      return file.type.startsWith('image/') || /\.(heic|heif|webp|gif|bmp|tiff|svg)$/i.test(file.name);
    }
```

## Snippet 68
Lines 977-979

```Python
if (e.target && e.target.classList.contains('save-alt-btn')) {
        const fileId = e.target.getAttribute('data-file-id');
        const textarea = document.getElementById(`alt-text-${fileId}`);
```

## Snippet 69
Lines 980-982

```Python
if (!textarea) return;

        const newAlt = textarea.value.trim();
```

## Snippet 70
Lines 983-990

```Python
if (!newAlt) return;

        e.target.disabled = true;
        e.target.textContent = 'Saving...';

        fetch('/api/update_alt_text', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
```

## Snippet 71
Lines 995-1002

```Python
if (data.success) {
            textarea.classList.add('alt-success');
            e.target.textContent = 'Saved!';
            setTimeout(() => {
              textarea.classList.remove('alt-success');
              e.target.textContent = 'Save Alt Text';
              e.target.disabled = false;
            }, 1500);
```

## Snippet 72
Lines 1003-1011

```Python
} else {
            textarea.classList.add('alt-error');
            e.target.textContent = 'Error!';
            setTimeout(() => {
              textarea.classList.remove('alt-error');
              e.target.textContent = 'Save Alt Text';
              e.target.disabled = false;
            }, 1500);
          }
```

## Snippet 73
Lines 1012-1021

```Python
})
        .catch(() => {
          textarea.classList.add('alt-error');
          e.target.textContent = 'Error!';
          setTimeout(() => {
            textarea.classList.remove('alt-error');
            e.target.textContent = 'Save Alt Text';
            e.target.disabled = false;
          }, 1500);
        });
```

## Snippet 74
Lines 1025-1068

```Python
// Add CSS for the textarea and feedback states - add this right after the existing style element
    const additionalStyle = document.createElement('style');
    additionalStyle.textContent = `
      .alt-text-container {
        margin: 10px 0;
      }
      .alt-textarea {
        width: 100%;
        min-height: 60px;
        font-size: 1rem;
        border-radius: var(--border-radius);
        border: 1px solid var(--input-border);
        background: var(--input-bg);
        color: var(--accent-color);
        padding: 8px 12px;
        margin-bottom: 8px;
        resize: vertical;
        transition: border-color 0.2s;
      }
      .alt-textarea:focus {
        border-color: var(--input-focus);
        outline: var(--focus-outline);
      }
      .save-alt-btn {
        font-size: 0.9rem;
        padding: 4px 12px;
        margin-bottom: 8px;
      }
      .alt-success {
        border-color: var(--success-color) !important;
        background-color: rgba(46, 204, 64, 0.1);
      }
      .alt-error {
        border-color: var(--error-color) !important;
        background-color: rgba(255, 65, 54, 0.1);
      }
      body.dark-theme .alt-success {
        background-color: rgba(46, 204, 64, 0.2);
      }
      body.dark-theme .alt-error {
        background-color: rgba(255, 65, 54, 0.2);
      }
    `;
    document.head.appendChild(additionalStyle);
```

## Snippet 75
Lines 1074-1078

```Python
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {
        'jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff', 'webp', 'heic', 'heif', 'svg'
    }
```

## Snippet 76
Lines 1079-1082

```Python
def get_preview_url(path):
    # Serve image preview from upload folder
    return f'/api/preview?path={os.path.basename(path)}'
```

## Snippet 77
Lines 1083-1093

```Python
def generate_html_content(processed_results):
    """Generate HTML content from processed image results."""
    env = jinja2.Environment(autoescape=True)
    html_template = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Herd AI Image Processing Results</title>
        <style>
```

## Snippet 78
Lines 1102-1104

```Python
</head>
    <body>
        <h1>Herd AI Image Processing Results</h1>
```

## Snippet 79
Lines 1132-1138

```Python
</body>
    </html>
    """
    template = env.from_string(html_template)

    # Add image data to results
    results_with_images = []
```

## Snippet 80
Lines 1141-1153

```Python
if result.get('error'):
            continue

        result_copy = dict(result)
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], result['new_name'])

        try:
            with open(image_path, "rb") as img_file:
                result_copy['image_data'] = base64.b64encode(img_file.read()).decode('utf-8')
                results_with_images.append(result_copy)
        except Exception as e:
            print(f"Error encoding image {image_path}: {e}")
```

## Snippet 81
Lines 1157-1168

```Python
def generate_pdf_from_html(html_content):
    """Generate a PDF from HTML content using ReportLab."""
    output = io.BytesIO()
    p = canvas.Canvas(output, pagesize=letter)
    width, height = letter
    text_object = p.beginText(50, height - 50)
    text_object.setFont("Helvetica", 12)

    # Extract text and images from HTML
    text = ""
    images = []
```

## Snippet 82
Lines 1177-1181

```Python
if img.get('src') and img['src'].startswith('data:image'):
                # Extract base64 data
                img_data = img['src'].split(',', 1)[1]
                alt_text = img.get('alt', '')
                images.append((img_data, alt_text))
```

## Snippet 83
Lines 1184-1187

```Python
text = "Image Processing Results (BeautifulSoup not available for full HTML parsing)"
        # Try to extract images using simple string matching
        import re
        img_matches = re.findall(r'<img[^>]*src="data:image[^"]*base64,([^"]*)"[^>]*alt="([^"]*)"', html_content)
```

## Snippet 84
Lines 1191-1199

```Python
# Add a title
    p.setFont("Helvetica-Bold", 18)
    p.drawString(50, height - 40, "Herd AI Image Processing Results")
    p.setFont("Helvetica", 12)

    # Process and add each image with its metadata
    y_position = height - 90
    page_num = 1
```

## Snippet 85
Lines 1201-1212

```Python
if y_position < 100:  # If we're near the bottom of the page
            p.showPage()
            page_num += 1
            y_position = height - 60
            p.setFont("Helvetica-Bold", 14)
            p.drawString(50, height - 40, f"Image Results (continued) - Page {page_num}")
            p.setFont("Helvetica", 12)

        try:
            # Create a temporary image file from base64 data
            img_bytes = base64.b64decode(img_data)
            img_temp = io.BytesIO(img_bytes)
```

## Snippet 86
Lines 1213-1222

```Python
if has_pil:
                with Image.open(img_temp) as img:
                    # Scale image to fit on page
                    img_width, img_height = img.size
                    max_width = width - 100
                    max_height = 200
                    scale = min(max_width/img_width, max_height/img_height)
                    new_width = img_width * scale
                    new_height = img_height * scale
```

## Snippet 87
Lines 1223-1232

```Python
# Save as JPG for ReportLab compatibility
                    img_temp = io.BytesIO()
                    img.save(img_temp, format='JPEG')
                    img_temp.seek(0)

                    # Draw image
                    p.drawImage(img_temp, 50, y_position - new_height, width=new_width, height=new_height)

                    # Draw metadata
                    y_position -= new_height + 20
```

## Snippet 88
Lines 1240-1251

```Python
# Add image metadata as text
        p.setFont("Helvetica-Bold", 12)
        p.drawString(50, y_position, f"Image #{i+1}")
        p.setFont("Helvetica", 10)
        y_position -= 15
        p.drawString(50, y_position, f"Alt Text: {alt_text[:100]}")
        y_position -= 15

        # Add separator line
        p.line(50, y_position - 10, width - 50, y_position - 10)
        y_position -= 30
```

## Snippet 89
Lines 1252-1259

```Python
if y_position < 100:
            p.showPage()
            page_num += 1
            y_position = height - 60
            p.setFont("Helvetica-Bold", 14)
            p.drawString(50, height - 40, f"Image Results (continued) - Page {page_num}")
            p.setFont("Helvetica", 12)
```

## Snippet 90
Lines 1261-1263

```Python
if text:
        p.setFont("Helvetica", 10)
        lines = text.splitlines()
```

## Snippet 91
Lines 1266-1273

```Python
if text_object.getY() < 50:
                p.drawText(text_object)
                p.showPage()
                page_num += 1
                text_object = p.beginText(50, height - 60)
                text_object.setFont("Helvetica", 10)
                p.drawString(50, height - 40, f"Additional Information - Page {page_num}")
```

## Snippet 92
Lines 1276-1279

```Python
p.save()
    output.seek(0)
    return output
```

## Snippet 93
Lines 1283-1290

```Python
# Use basic encoding if PIL not available
        try:
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
        except Exception as e:
            print(f"Error encoding image: {e}")
            return None
```

## Snippet 94
Lines 1299-1301

```Python
if img.size[0] > 1024 or img.size[1] > 1024:
                ratio = min(1024/img.size[0], 1024/img.size[1])
                new_size = (int(img.size[0]*ratio), int(img.size[1]*ratio))
```

## Snippet 95
Lines 1304-1310

```Python
# Save to bytes
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='JPEG')

            # Encode to base64
            return base64.b64encode(img_byte_arr.getvalue()).decode('utf-8')
```

## Snippet 96
Lines 1311-1320

```Python
except Exception as e:
        print(f"Error processing image with PIL: {e}")
        # Fall back to basic encoding
        try:
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
        except Exception as e:
            print(f"Error encoding image: {e}")
            return None
```

## Snippet 97
Lines 1321-1326

```Python
def send_image_to_ollama(image_path, prompt, model="gemma3:4b"):
    """Send image to Ollama API with proper formatting based on Ollama API docs."""
    import requests

    # Process image
    image_base64 = process_image_for_ollama(image_path)
```

## Snippet 98
Lines 1327-1356

```Python
if not image_base64:
        return {"text": "Error processing image", "error": True}

    # First try chat API endpoint with proper multimodal format
    try:
        host = "http://localhost:11434"

        # Chat API format
        chat_payload = {
            "model": model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt,
                    "images": [image_base64]
                }
            ],
            "stream": False,
            "options": {
                "temperature": 0.7
            }
        }

        print(f"Sending image to Ollama via chat API")
        response = requests.post(
            f"{host}/api/chat",
            json=chat_payload,
            timeout=90
        )
```

## Snippet 99
Lines 1357-1366

```Python
if response.status_code == 200:
            result = response.json()
            return {
                "text": result.get("message", {}).get("content", ""),
                "model": model,
                "finish_reason": result.get("done", False)
            }

        print(f"Chat API failed with status {response.status_code}, trying generate API...")
```

## Snippet 100
Lines 1367-1388

```Python
except Exception as e:
        print(f"Error with chat API: {e}")

    # Fall back to generate API
    try:
        generate_payload = {
            "model": model,
            "prompt": prompt,
            "images": [image_base64],
            "stream": False,
            "options": {
                "temperature": 0.7
            }
        }

        print(f"Sending image to Ollama via generate API")
        response = requests.post(
            f"{host}/api/generate",
            json=generate_payload,
            timeout=90
        )
```

## Snippet 101
Lines 1389-1399

```Python
if response.status_code == 200:
            result = response.json()
            return {
                "text": result.get("response", ""),
                "model": model,
                "finish_reason": result.get("done", False)
            }
        else:
            error_msg = f"Ollama API request failed: {response.status_code}"
            try:
                error_data = response.json()
```

## Snippet 102
Lines 1402-1405

```Python
except:
                pass
            return {"text": error_msg, "error": True}
```

## Snippet 103
Lines 1410-1413

```Python
def index():
    # Render the modularized template
    return render_template('herd_gui.html')
```

## Snippet 104
Lines 1417-1419

```Python
if not path:
        abort(404)
    full_path = os.path.join(app.config['UPLOAD_FOLDER'], path)
```

## Snippet 105
Lines 1420-1423

```Python
if not os.path.exists(full_path):
        abort(404)
    return send_file(full_path)
```

## Snippet 106
Lines 1425-1427

```Python
def process_images():
    files = request.files.getlist('images')
    provider = request.form.get('provider', 'ollama')
```

## Snippet 107
Lines 1428-1433

```Python
model = request.form.get('model', 'gemma3:4b')  # Get model name if provided
    results = []
    processor = ImageProcessor(provider=provider)
    global processed_md_files
    global processed_files
```

## Snippet 108
Lines 1435-1451

```Python
if not allowed_file(file.filename):
            results.append({
                'original_name': file.filename,
                'error': 'Unsupported file type.'
            })
            continue

        filename = secure_filename(file.filename)
        temp_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(temp_path)

        try:
            # Get file size and type
            file_size = os.path.getsize(temp_path)
            file_size_formatted = format_file_size(file_size)
            file_type = Path(temp_path).suffix.lstrip('.').upper()
```

## Snippet 109
Lines 1458-1465

```Python
if provider == 'ollama':
                # Use improved Ollama implementation
                ollama_result = send_image_to_ollama(
                    temp_path,
                    prompt=IMAGE_ALT_TEXT_TEMPLATE,
                    model=model
                )
```

## Snippet 110
Lines 1466-1473

```Python
# Store original path for retry
                processed_files[file_id] = {
                    'path': temp_path,
                    'original_name': file.filename
                }

                # Parse result
                data = {}
```

## Snippet 111
Lines 1474-1478

```Python
if ollama_result.get('text'):
                    try:
                        # First try to find JSON in the response
                        import re
                        json_match = re.search(r'\{.*\}', ollama_result['text'], re.DOTALL)
```

## Snippet 112
Lines 1479-1483

```Python
if json_match:
                            json_text = json_match.group(0)
                            data = json.loads(json_text)
                        else:
                            data = json.loads(ollama_result['text'])
```

## Snippet 113
Lines 1484-1492

```Python
except Exception as e:
                        print(f"Error parsing JSON: {e}")
                        # Create minimal data with the text
                        data = {
                            "alt_text": "Generated alt text",
                            "description": ollama_result.get('text', ''),
                            "suggested_filename": Path(temp_path).stem
                        }
```

## Snippet 114
Lines 1499-1516

```Python
if new_name != filename and not os.path.exists(new_path):
                    shutil.move(temp_path, new_path)
                else:
                    new_path = temp_path

                # Generate markdown file
                md_content = f"# {Path(new_name).stem}\n\n**Alt Text:** {alt}\n\n**Description:** {desc}\n"
                md_path = os.path.splitext(new_path)[0] + '.md'
                with open(md_path, 'w', encoding='utf-8') as f:
                    f.write(md_content)

                md_id = os.path.basename(md_path)
                processed_md_files.append((md_path, file.filename, new_name))

                undo_token = {'old_path': temp_path, 'new_path': new_path}
                with undo_lock:
                    undo_log.append(undo_token)
```

## Snippet 115
Lines 1517-1536

```Python
# Generate a new preview URL for the renamed file
                updated_preview_url = get_preview_url(new_path)

                results.append({
                    'file_id': file_id,
                    'original_name': file.filename,
                    'new_name': os.path.basename(new_path),
                    'alt_text': alt or 'Not generated',
                    'description': desc,
                    'metadata_embedded': bool(alt and desc),
                    'provider': 'Ollama',
                    'model': ollama_result.get('model', model),
                    'dimensions': dimensions,
                    'file_size': file_size_formatted,
                    'file_type': file_type,
                    'md_id': md_id,
                    'preview_url': updated_preview_url,
                    'undo_token': undo_token,
                    'error': None
                })
```

## Snippet 116
Lines 1538-1550

```Python
# Store original path for retry
                processed_files[file_id] = {
                    'path': temp_path,
                    'original_name': file.filename
                }

                # Use X.AI
                result = processor.process_single_image(
                    Path(temp_path),
                    {'base_dir': app.config['UPLOAD_FOLDER']}
                )

                undo_token = None
```

## Snippet 117
Lines 1551-1558

```Python
if result.get('renamed') and result.get('new_path'):
                    undo_token = {
                        'old_path': temp_path,
                        'new_path': result['new_path']
                    }
                    with undo_lock:
                        undo_log.append(undo_token)
```

## Snippet 118
Lines 1561-1564

```Python
else:
                    updated_preview_url = preview_url

                md_id = None
```

## Snippet 119
Lines 1565-1585

```Python
if result.get('markdown_path'):
                    md_id = os.path.basename(result['markdown_path'])
                    processed_md_files.append((result['markdown_path'], file.filename, os.path.basename(result.get('new_path', temp_path))))

                results.append({
                    'file_id': file_id,
                    'original_name': file.filename,
                    'new_name': os.path.basename(result.get('new_path', temp_path)),
                    'alt_text': result.get('alt_text_generated') and 'Generated' or 'Not generated',
                    'description': result.get('markdown_path') and Path(result['markdown_path']).read_text(encoding='utf-8').split('\n')[2][12:] or '',
                    'metadata_embedded': result.get('alt_text_generated', False),
                    'provider': 'X.AI',
                    'model': result.get('model', 'Default X.AI Model'),
                    'dimensions': dimensions or result.get('dimensions', ''),
                    'file_size': file_size_formatted,
                    'file_type': file_type,
                    'md_id': md_id,
                    'preview_url': updated_preview_url,
                    'undo_token': undo_token,
                    'error': result.get('error')
                })
```

## Snippet 120
Lines 1586-1591

```Python
except Exception as e:
            results.append({
                'original_name': file.filename,
                'error': str(e)
            })
```

## Snippet 121
Lines 1595-1599

```Python
def retry_processing():
    """Re-process a single image"""
    data = request.get_json()
    file_id = data.get('file_id')
    provider = data.get('provider', 'ollama')
```

## Snippet 122
Lines 1602-1607

```Python
if not file_id or file_id not in processed_files:
        return jsonify({'error': 'File not found or invalid file_id'})

    file_info = processed_files[file_id]
    temp_path = file_info['path']
```

## Snippet 123
Lines 1608-1616

```Python
if not os.path.exists(temp_path):
        return jsonify({'error': 'Original file no longer exists'})

    try:
        # Get file size and type
        file_size = os.path.getsize(temp_path)
        file_size_formatted = format_file_size(file_size)
        file_type = Path(temp_path).suffix.lstrip('.').upper()
```

## Snippet 124
Lines 1622-1631

```Python
if provider == 'ollama':
            # Use improved Ollama implementation
            ollama_result = send_image_to_ollama(
                temp_path,
                prompt=IMAGE_ALT_TEXT_TEMPLATE,
                model=model
            )

            # Parse result
            data = {}
```

## Snippet 125
Lines 1632-1636

```Python
if ollama_result.get('text'):
                try:
                    # First try to find JSON in the response
                    import re
                    json_match = re.search(r'\{.*\}', ollama_result['text'], re.DOTALL)
```

## Snippet 126
Lines 1637-1641

```Python
if json_match:
                        json_text = json_match.group(0)
                        data = json.loads(json_text)
                    else:
                        data = json.loads(ollama_result['text'])
```

## Snippet 127
Lines 1642-1650

```Python
except Exception as e:
                    print(f"Error parsing JSON: {e}")
                    # Create minimal data with the text
                    data = {
                        "alt_text": "Generated alt text",
                        "description": ollama_result.get('text', ''),
                        "suggested_filename": Path(temp_path).stem
                    }
```

## Snippet 128
Lines 1658-1675

```Python
if new_name != filename and not os.path.exists(new_path):
                shutil.move(temp_path, new_path)
            else:
                new_path = temp_path

            # Generate markdown file
            md_content = f"# {Path(new_name).stem}\n\n**Alt Text:** {alt}\n\n**Description:** {desc}\n"
            md_path = os.path.splitext(new_path)[0] + '.md'
            with open(md_path, 'w', encoding='utf-8') as f:
                f.write(md_content)

            md_id = os.path.basename(md_path)
            processed_md_files.append((md_path, file_info['original_name'], new_name))

            undo_token = {'old_path': temp_path, 'new_path': new_path}
            with undo_lock:
                undo_log.append(undo_token)
```

## Snippet 129
Lines 1676-1695

```Python
# Generate a new preview URL for the renamed file
            updated_preview_url = get_preview_url(new_path)

            return jsonify({
                'file_id': file_id,
                'original_name': file_info['original_name'],
                'new_name': os.path.basename(new_path),
                'alt_text': alt or 'Not generated',
                'description': desc,
                'metadata_embedded': bool(alt and desc),
                'provider': 'Ollama',
                'model': ollama_result.get('model', model),
                'dimensions': dimensions,
                'file_size': file_size_formatted,
                'file_type': file_type,
                'md_id': md_id,
                'preview_url': updated_preview_url,
                'undo_token': undo_token,
                'error': None
            })
```

## Snippet 130
Lines 1696-1704

```Python
else:
            # Use X.AI
            processor = ImageProcessor(provider=provider)
            result = processor.process_single_image(
                Path(temp_path),
                {'base_dir': app.config['UPLOAD_FOLDER']}
            )

            undo_token = None
```

## Snippet 131
Lines 1705-1713

```Python
if result.get('renamed') and result.get('new_path'):
                undo_token = {
                    'old_path': temp_path,
                    'new_path': result['new_path']
                }
                with undo_lock:
                    undo_log.append(undo_token)

            md_id = None
```

## Snippet 132
Lines 1714-1734

```Python
if result.get('markdown_path'):
                md_id = os.path.basename(result['markdown_path'])
                processed_md_files.append((result['markdown_path'], file_info['original_name'], os.path.basename(result.get('new_path', temp_path))))

            return jsonify({
                'file_id': file_id,
                'original_name': file_info['original_name'],
                'new_name': os.path.basename(result.get('new_path', temp_path)),
                'alt_text': result.get('alt_text_generated') and 'Generated' or 'Not generated',
                'description': result.get('markdown_path') and Path(result['markdown_path']).read_text(encoding='utf-8').split('\n')[2][12:] or '',
                'metadata_embedded': result.get('alt_text_generated', False),
                'provider': 'X.AI',
                'model': result.get('model', 'Default X.AI Model'),
                'dimensions': dimensions or result.get('dimensions', ''),
                'file_size': file_size_formatted,
                'file_type': file_type,
                'md_id': md_id,
                'preview_url': updated_preview_url,
                'undo_token': undo_token,
                'error': result.get('error')
            })
```

## Snippet 133
Lines 1735-1740

```Python
except Exception as e:
        return jsonify({
            'original_name': file_info['original_name'],
            'error': str(e)
        })
```

## Snippet 134
Lines 1756-1758

```Python
for md_path, original_name, new_name in processed_md_files:
            arcname = os.path.basename(md_path)
            zf.write(md_path, arcname)
```

## Snippet 135
Lines 1763-1766

```Python
def download_html():
    """Generate and download HTML file with all processed images and their metadata."""
    # Get all successful results from processed_files
    results = []
```

## Snippet 136
Lines 1769-1772

```Python
if not file_info.get('path'):
            continue

        # Find the corresponding result from processed_md_files
```

## Snippet 137
Lines 1774-1778

```Python
if original_name == file_info['original_name']:
                try:
                    # Read description from markdown file
                    md_content = Path(md_path).read_text(encoding='utf-8')
                    lines = md_content.split('\n')
```

## Snippet 138
Lines 1780-1789

```Python
description = lines[4][16:] if len(lines) > 4 else ''

                    results.append({
                        'original_name': original_name,
                        'new_name': new_name,
                        'alt_text': alt_text,
                        'description': description,
                        'provider': 'Herd AI',
                        'dimensions': ''
                    })
```

## Snippet 139
Lines 1790-1793

```Python
except Exception as e:
                    print(f"Error reading markdown file {md_path}: {e}")
                break
```

## Snippet 140
Lines 1794-1807

```Python
# Generate HTML content
    html_content = generate_html_content(results)

    # Return HTML file
    html_io = io.BytesIO(html_content.encode('utf-8'))
    html_io.seek(0)

    return send_file(
        html_io,
        mimetype='text/html',
        as_attachment=True,
        download_name='herd_image_results.html'
    )
```

## Snippet 141
Lines 1809-1812

```Python
def download_pdf():
    """Generate and download PDF file with all processed images and their metadata."""
    # Get all successful results from processed_files
    results = []
```

## Snippet 142
Lines 1815-1818

```Python
if not file_info.get('path'):
            continue

        # Find the corresponding result from processed_md_files
```

## Snippet 143
Lines 1820-1824

```Python
if original_name == file_info['original_name']:
                try:
                    # Read description from markdown file
                    md_content = Path(md_path).read_text(encoding='utf-8')
                    lines = md_content.split('\n')
```

## Snippet 144
Lines 1826-1835

```Python
description = lines[4][16:] if len(lines) > 4 else ''

                    results.append({
                        'original_name': original_name,
                        'new_name': new_name,
                        'alt_text': alt_text,
                        'description': description,
                        'provider': 'Herd AI',
                        'dimensions': ''
                    })
```

## Snippet 145
Lines 1836-1839

```Python
except Exception as e:
                    print(f"Error reading markdown file {md_path}: {e}")
                break
```

## Snippet 146
Lines 1840-1856

```Python
# Generate HTML content first
    html_content = generate_html_content(results)

    # Convert to PDF
    pdf_data = generate_pdf_from_html(html_content)

    # Return PDF file
    pdf_io = io.BytesIO(pdf_data)
    pdf_io.seek(0)

    return send_file(
        pdf_io,
        mimetype='application/pdf',
        as_attachment=True,
        download_name='herd_image_results.pdf'
    )
```

## Snippet 147
Lines 1858-1860

```Python
def undo():
    data = request.get_json()
    token = data.get('undo_token')
```

## Snippet 148
Lines 1861-1864

```Python
if not token or not isinstance(token, dict):
        return jsonify({'success': False, 'error': 'Invalid undo token.'})
    old_path = token.get('old_path')
    new_path = token.get('new_path')
```

## Snippet 149
Lines 1865-1867

```Python
if not old_path or not new_path:
        return jsonify({'success': False, 'error': 'Missing file paths.'})
    try:
```

## Snippet 150
Lines 1882-1885

```Python
if not tokens or not isinstance(tokens, list):
        return jsonify({'success': False, 'error': 'Invalid undo tokens.'})

    results = []
```

## Snippet 151
Lines 1887-1893

```Python
if not isinstance(token, dict):
            results.append({'success': False, 'error': 'Invalid undo token format.'})
            continue

        old_path = token.get('old_path')
        new_path = token.get('new_path')
```

## Snippet 152
Lines 1894-1898

```Python
if not old_path or not new_path:
            results.append({'success': False, 'error': 'Missing file paths.'})
            continue

        try:
```

## Snippet 153
Lines 1911-1916

```Python
"""Retry processing for multiple files at once."""
    data = request.get_json()
    file_ids = data.get('file_ids', [])
    provider = data.get('provider', 'ollama')
    model = data.get('model', 'gemma3:4b')
```

## Snippet 154
Lines 1917-1920

```Python
if not file_ids or not isinstance(file_ids, list):
        return jsonify({'success': False, 'error': 'Invalid file IDs.'})

    results = []
```

## Snippet 155
Lines 1922-1932

```Python
if file_id not in processed_files:
            results.append({
                'file_id': file_id,
                'success': False,
                'error': 'File not found or invalid file_id'
            })
            continue

        file_info = processed_files[file_id]
        temp_path = file_info['path']
```

## Snippet 156
Lines 1933-1947

```Python
if not os.path.exists(temp_path):
            results.append({
                'file_id': file_id,
                'success': False,
                'error': 'Original file no longer exists'
            })
            continue

        try:
            # Process this file directly since we can't mock the request context
            # Get file size and type
            file_size = os.path.getsize(temp_path)
            file_size_formatted = format_file_size(file_size)
            file_type = Path(temp_path).suffix.lstrip('.').upper()
```

## Snippet 157
Lines 1953-1962

```Python
if provider == 'ollama':
                # Use improved Ollama implementation
                ollama_result = send_image_to_ollama(
                    temp_path,
                    prompt=IMAGE_ALT_TEXT_TEMPLATE,
                    model=model
                )

                # Parse result
                result_data = {}
```

## Snippet 158
Lines 1963-1967

```Python
if ollama_result.get('text'):
                    try:
                        # First try to find JSON in the response
                        import re
                        json_match = re.search(r'\{.*\}', ollama_result['text'], re.DOTALL)
```

## Snippet 159
Lines 1968-1972

```Python
if json_match:
                            json_text = json_match.group(0)
                            result_data = json.loads(json_text)
                        else:
                            result_data = json.loads(ollama_result['text'])
```

## Snippet 160
Lines 1973-1981

```Python
except Exception as e:
                        print(f"Error parsing JSON: {e}")
                        # Create minimal data with the text
                        result_data = {
                            "alt_text": "Generated alt text",
                            "description": ollama_result.get('text', ''),
                            "suggested_filename": Path(temp_path).stem
                        }
```

## Snippet 161
Lines 1989-2006

```Python
if new_name != filename and not os.path.exists(new_path):
                    shutil.move(temp_path, new_path)
                else:
                    new_path = temp_path

                # Generate markdown file
                md_content = f"# {Path(new_name).stem}\n\n**Alt Text:** {alt}\n\n**Description:** {desc}\n"
                md_path = os.path.splitext(new_path)[0] + '.md'
                with open(md_path, 'w', encoding='utf-8') as f:
                    f.write(md_content)

                md_id = os.path.basename(md_path)
                processed_md_files.append((md_path, file_info['original_name'], new_name))

                undo_token = {'old_path': temp_path, 'new_path': new_path}
                with undo_lock:
                    undo_log.append(undo_token)
```

## Snippet 162
Lines 2007-2027

```Python
# Generate a new preview URL for the renamed file
                updated_preview_url = get_preview_url(new_path)

                result = {
                    'file_id': file_id,
                    'original_name': file_info['original_name'],
                    'new_name': os.path.basename(new_path),
                    'alt_text': alt or 'Not generated',
                    'description': desc,
                    'metadata_embedded': bool(alt and desc),
                    'provider': 'Ollama',
                    'model': ollama_result.get('model', model),
                    'dimensions': dimensions,
                    'file_size': file_size_formatted,
                    'file_type': file_type,
                    'md_id': md_id,
                    'preview_url': updated_preview_url,
                    'undo_token': undo_token,
                    'success': True,
                    'error': None
                }
```

## Snippet 163
Lines 2028-2036

```Python
else:
                # Use X.AI
                processor = ImageProcessor(provider=provider)
                proc_result = processor.process_single_image(
                    Path(temp_path),
                    {'base_dir': app.config['UPLOAD_FOLDER']}
                )

                undo_token = None
```

## Snippet 164
Lines 2037-2044

```Python
if proc_result.get('renamed') and proc_result.get('new_path'):
                    undo_token = {
                        'old_path': temp_path,
                        'new_path': proc_result['new_path']
                    }
                    with undo_lock:
                        undo_log.append(undo_token)
```

## Snippet 165
Lines 2047-2050

```Python
else:
                    updated_preview_url = preview_url

                md_id = None
```

## Snippet 166
Lines 2051-2073

```Python
if proc_result.get('markdown_path'):
                    md_id = os.path.basename(proc_result['markdown_path'])
                    processed_md_files.append((proc_result['markdown_path'], file_info['original_name'], os.path.basename(proc_result.get('new_path', temp_path))))

                result = {
                    'file_id': file_id,
                    'original_name': file_info['original_name'],
                    'new_name': os.path.basename(proc_result.get('new_path', temp_path)),
                    'alt_text': proc_result.get('alt_text_generated') and 'Generated' or 'Not generated',
                    'description': proc_result.get('markdown_path') and Path(proc_result['markdown_path']).read_text(encoding='utf-8').split('\n')[2][12:] or '',
                    'metadata_embedded': proc_result.get('alt_text_generated', False),
                    'provider': 'X.AI',
                    'model': proc_result.get('model', 'Default X.AI Model'),
                    'dimensions': dimensions or proc_result.get('dimensions', ''),
                    'file_size': file_size_formatted,
                    'file_type': file_type,
                    'md_id': md_id,
                    'preview_url': updated_preview_url,
                    'undo_token': undo_token,
                    'success': True,
                    'error': proc_result.get('error')
                }
```

## Snippet 167
Lines 2079-2086

```Python
except Exception as e:
            results.append({
                'file_id': file_id,
                'original_name': file_info['original_name'],
                'success': False,
                'error': str(e)
            })
```

## Snippet 168
Lines 2100-2109

```Python
if not has_pil:
        return None

    try:
        with Image.open(image_path) as img:
            return f"{img.width}x{img.height}"
    except Exception as e:
        print(f"Error getting image dimensions: {e}")
        return None
```

## Snippet 169
Lines 2111-2114

```Python
def update_alt_text():
    data = request.get_json()
    file_id = data.get('file_id')
    new_alt_text = data.get('alt_text', '').strip()
```

## Snippet 170
Lines 2123-2128

```Python
if not md_path or not os.path.exists(md_path):
        return jsonify({'success': False, 'error': 'Markdown file not found'})
    # Read and update the markdown file
    try:
        lines = Path(md_path).read_text(encoding='utf-8').split('\n')
        # Find the alt text line (assume format: **Alt Text:** ...)
```

