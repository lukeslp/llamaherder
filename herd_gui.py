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
from flask import Flask, request, jsonify, render_template_string, send_file, abort
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

# In-memory undo log and processed files for the session
undo_log = []
undo_lock = Lock()
processed_md_files = []  # List of (md_path, original_name, new_name)
processed_files = {}  # Dictionary to store processed file info for retries

# Check if PIL is available for image processing
try:
    from PIL import Image
    has_pil = True
except ImportError:
    has_pil = False

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
    .bg-surface { background: var(--surface-color); }
    .rounded { border-radius: var(--border-radius); }
    .shadow { box-shadow: var(--shadow); }
    .shadow-md { box-shadow: var(--shadow-md); }
    .p-4 { padding: 2rem; }
    .p-3 { padding: 1rem; }
    .mb-2 { margin-bottom: 0.5rem; }
    .d-flex { display: flex; }
    .align-items-center { align-items: center; }
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
    .file-item .success { color: var(--success-color); }
    .file-item .error { color: var(--error-color); }
    .button-group { display: flex; gap: 0.5rem; margin-top: 0.3rem; }
    .download-container { display: flex; flex-wrap: wrap; gap: 0.5rem; margin-top: 1rem; margin-bottom: 1rem; }
    .processing-count { font-size: 1rem; margin: 0.5rem 0; }
    .form-label { font-weight: bold; margin-bottom: 0.5rem; display: block; }
    .provider-select { width: 100%; max-width: 350px; }
    @media (max-width: 600px) {
      .p-4 { padding: 1rem; }
      .file-item { flex-direction: column; align-items: flex-start; }
      .file-thumb { margin-right: 0; margin-bottom: 0.5rem; }
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
    @media (max-width: 600px) {
      .drop-area { min-width: 0; max-width: 98vw; min-height: 140px; }
      .drop-icon { font-size: 2.2rem; }
      .drop-instructions { font-size: 1.05rem; }
    }
    body.dark-theme .drop-area {
      background: var(--surface-color);
      border-color: var(--primary-color);
    }
    body.dark-theme .drop-area.dragover {
      background: #23272e;
      border-color: var(--btn-bg-hover);
    }
    /* === END BRAND REFERENCE === */
  </style>
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
      <input id="file-input" name="images" type="file" accept="image/*,.heic,.heif,.webp,.gif,.bmp,.tiff,.svg" multiple style="display:none;" aria-label="Select images" />
    </div>
    <button type="button" class="btn btn-secondary" id="dir-btn" style="margin-top: 1rem;">Select Directory</button>
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
      if (e.target !== dirBtn) fileInput.click();
    });
    dropArea.addEventListener('keydown', e => { if (e.key === 'Enter' || e.key === ' ') fileInput.click(); });
    dropArea.addEventListener('dragover', e => { e.preventDefault(); dropArea.classList.add('dragover'); });
    dropArea.addEventListener('dragleave', e => { e.preventDefault(); dropArea.classList.remove('dragover'); });
    dropArea.addEventListener('drop', e => {
      e.preventDefault();
      dropArea.classList.remove('dragover');
      handleFiles(e.dataTransfer.files);
    });
    fileInput.addEventListener('change', e => handleFiles(e.target.files));
    dirBtn.addEventListener('click', e => { dirInput.click(); });
    dirInput.addEventListener('change', e => handleFiles(e.target.files));
    
    // Handle select all checkbox
    selectAllCheckbox.addEventListener('change', () => {
      const checkboxes = document.querySelectorAll('.file-checkbox');
      checkboxes.forEach(checkbox => {
        checkbox.checked = selectAllCheckbox.checked;
        const fileId = checkbox.getAttribute('data-file-id');
        if (selectAllCheckbox.checked) {
          selectedItems.add(fileId);
        } else {
          selectedItems.delete(fileId);
        }
      });
      updateSelectedCount();
      updateBulkButtons();
    });
    
    // Update selected count
    function updateSelectedCount() {
      const count = selectedItems.size;
      selectedCountSpan.textContent = `${count} file${count !== 1 ? 's' : ''} selected`;
      selectedCountSpan.style.display = count > 0 ? 'inline' : 'none';
    }
    
    // Update bulk action buttons
    function updateBulkButtons() {
      const hasSelection = selectedItems.size > 0;
      bulkRetryBtn.disabled = !hasSelection;
      bulkUndoBtn.disabled = !hasSelection;
    }
    
    // Handle selection of individual checkboxes
    function handleFileCheckboxChange(checkbox) {
      const fileId = checkbox.getAttribute('data-file-id');
      if (checkbox.checked) {
        selectedItems.add(fileId);
      } else {
        selectedItems.delete(fileId);
        selectAllCheckbox.checked = false;
      }
      updateSelectedCount();
      updateBulkButtons();
    }
    
    // Bulk retry action
    bulkRetryBtn.addEventListener('click', () => {
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
        for (const result of results) {
          if (result.file_id) {
            updateFileItemAfterBulkAction(result);
          }
        }
        // Reset selection
        selectedItems.clear();
        selectAllCheckbox.checked = false;
        updateSelectedCount();
        updateBulkButtons();
      })
      .catch(err => {
        console.error("Bulk retry failed:", err);
      });
    });
    
    // Bulk undo action
    bulkUndoBtn.addEventListener('click', () => {
      if (selectedItems.size === 0) return;
      
      // Collect undo tokens from the file items
      const undoTokens = [];
      selectedItems.forEach(fileId => {
        const item = document.getElementById(`file-item-${fileId}`);
        if (item) {
          const tokenAttr = item.getAttribute('data-undo-token');
          if (tokenAttr) {
            try {
              const token = JSON.parse(tokenAttr);
              undoTokens.push(token);
            } catch (e) {
              console.error("Invalid undo token:", tokenAttr);
            }
          }
        }
      });
      
      if (undoTokens.length === 0) return;
      
      fetch('/api/bulk_undo', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ undo_tokens: undoTokens })
      })
      .then(r => r.json())
      .then(data => {
        // Add undo success message to each file item
        const results = data.results || [];
        let idx = 0;
        selectedItems.forEach(fileId => {
          const item = document.getElementById(`file-item-${fileId}`);
          if (item && idx < results.length) {
            const result = results[idx++];
            if (result.success) {
              item.innerHTML += `<div class='success'>Undo successful.</div>`;
            } else {
              item.innerHTML += `<div class='error'>Undo failed: ${result.error || "Unknown error"}</div>`;
            }
          }
        });
        
        // Reset selection
        selectedItems.clear();
        selectAllCheckbox.checked = false;
        updateSelectedCount();
        updateBulkButtons();
      })
      .catch(err => {
        console.error("Bulk undo failed:", err);
      });
    });
    
    // Update a file item after bulk action
    function updateFileItemAfterBulkAction(result) {
      const fileItem = document.getElementById(`file-item-${result.file_id}`);
      if (!fileItem) return;
      
      if (result.error) {
        const meta = fileItem.querySelector('.file-meta');
        if (meta) {
          meta.innerHTML = `<strong>${result.original_name}</strong><span class='error'>Error: ${result.error}</span>`;
        }
        return;
      }
      
      // Update the file item with the new data
      const meta = fileItem.querySelector('.file-meta');
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
        retryBtn.setAttribute('aria-label', `Retry processing for ${result.original_name}`);
        retryBtn.onclick = () => retryProcessing(result.file_id, meta);
        buttonGroup.appendChild(retryBtn);
        
        // Add Undo button
        const undoBtn = document.createElement('button');
        undoBtn.className = 'undo-btn btn btn-secondary';
        undoBtn.textContent = 'Undo';
        undoBtn.setAttribute('aria-label', `Undo changes for ${result.original_name}`);
        undoBtn.onclick = () => undoAction(result.undo_token, fileItem);
        buttonGroup.appendChild(undoBtn);
        
        meta.appendChild(buttonGroup);
      }
      
      // Update preview image
      const thumb = fileItem.querySelector('.file-thumb');
      if (thumb) {
        thumb.alt = result.new_name || result.original_name;
        thumb.src = result.preview_url || '';
      }
      
      // Store undo token in the file item
      if (result.undo_token) {
        fileItem.setAttribute('data-undo-token', JSON.stringify(result.undo_token));
      }
    }
    
    // Update handleFiles function to show the bulk actions container
    const originalHandleFiles = handleFiles;
    handleFiles = function(files) {
      // Call the original function
      originalHandleFiles(files);
      
      // Show the bulk actions container if we have files
      const imageFiles = Array.from(files).filter(isImageFile);
      if (imageFiles.length > 0) {
        bulkActionsContainer.style.display = 'block';
      } else {
        bulkActionsContainer.style.display = 'none';
      }
    };
    
    // Modify the file item creation in handleFiles
    function handleFiles(files) {
      const imageFiles = Array.from(files).filter(isImageFile);
      if (!imageFiles.length) return;
      
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
      
      // Create initial placeholders for all files
      for (const file of imageFiles) {
        const item = document.createElement('div');
        item.className = 'file-item bg-surface rounded shadow-md p-3 mb-2';
        item.id = `file-item-${currentImages.length}`;
        
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
      }
      
      // Start processing files one by one
      processNextImage(imageFiles, 0);
    }
    
    function processNextImage(files, index) {
      if (index >= files.length) {
        processingComplete = true;
        processingInfo.style.display = 'none';
        if (hasMd) {
          downloadContainer.style.display = 'flex';
        }
        return;
      }
      
      const formData = new FormData();
      formData.append('images', files[index]);
      formData.append('provider', providerSelect.value);
      
      // Update UI to show currently processing file
      const fileItem = document.getElementById(`file-item-${index}`);
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
        
        // Update display for this specific file
        for (const result of res.results) {
          if (fileItem) {
            const meta = fileItem.querySelector('.file-meta');
            if (result.error) {
              meta.innerHTML = `<strong>${result.original_name}</strong><span class='error'>Error: ${result.error}</span>`;
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
              retryBtn.setAttribute('aria-label', `Retry processing for ${result.original_name}`);
              retryBtn.onclick = () => retryProcessing(result.file_id, meta);
              buttonGroup.appendChild(retryBtn);
              
              // Add Undo button
              const undoBtn = document.createElement('button');
              undoBtn.className = 'undo-btn btn btn-secondary';
              undoBtn.textContent = 'Undo';
              undoBtn.setAttribute('aria-label', `Undo changes for ${result.original_name}`);
              undoBtn.onclick = () => undoAction(result.undo_token, fileItem);
              buttonGroup.appendChild(undoBtn);
              
              meta.appendChild(buttonGroup);
              
              // Update preview image
              const thumb = fileItem.querySelector('.file-thumb');
              thumb.alt = result.new_name || result.original_name;
              thumb.src = result.preview_url || '';
              
              // Store undo token in the file item
              if (result.undo_token) {
                fileItem.setAttribute('data-undo-token', JSON.stringify(result.undo_token));
              }
            }
          }
          
          // If we have at least one MD file, show the download buttons
          if (hasMd && !processingComplete) {
            downloadContainer.style.display = 'flex';
          }
        }
        
        // Process next image
        processNextImage(files, index + 1);
      })
      .catch(err => {
        // Update the processed count even on error
        processedImages++;
        processedCount.textContent = processedImages;
        
        // Update this file's display
        if (fileItem) {
          const meta = fileItem.querySelector('.file-meta');
          meta.innerHTML = `<strong>${files[index].name}</strong><span class='error'>Error: ${err}</span>`;
        }
        
        // Continue with next file
        processNextImage(files, index + 1);
      });
    }
    
    // Update the retryProcessing function for metadata display
    function retryProcessing(fileId, metaElement) {
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
        if (result.error) {
          metaElement.innerHTML = `<strong>${result.original_name}</strong><span class='error'>Error: ${result.error}</span>`;
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
          retryBtn.setAttribute('aria-label', `Retry processing for ${result.original_name}`);
          retryBtn.onclick = () => retryProcessing(result.file_id, metaElement);
          buttonGroup.appendChild(retryBtn);
          
          // Add Undo button
          const undoBtn = document.createElement('button');
          undoBtn.className = 'undo-btn btn btn-secondary';
          undoBtn.textContent = 'Undo';
          undoBtn.setAttribute('aria-label', `Undo changes for ${result.original_name}`);
          undoBtn.onclick = () => undoAction(result.undo_token, metaElement.parentNode.parentNode);
          buttonGroup.appendChild(undoBtn);
          
          meta.appendChild(buttonGroup);
          
          // Update the parent file item data attributes
          const fileItem = metaElement.parentNode.parentNode;
          if (fileItem && result.undo_token) {
            fileItem.setAttribute('data-undo-token', JSON.stringify(result.undo_token));
          }
          
          // Update preview image
          const fileItemContainer = metaElement.parentNode;
          const thumb = fileItemContainer.querySelector('.file-thumb');
          if (thumb) {
            thumb.alt = result.new_name || result.original_name;
            thumb.src = result.preview_url || '';
          }
        }
      })
      .catch(err => {
        metaElement.innerHTML = `<span class='error'>Retry failed: ${err}</span>`;
      });
    }
    
    // Add CSS for file metadata display
    const style = document.createElement('style');
    style.textContent = `
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
    `;
    document.head.appendChild(style);
    
    // Theme toggle logic
    const themeToggleBtn = document.getElementById('theme-toggle-btn');
    const themeToggleLabel = document.getElementById('theme-toggle-label');
    const themeToggleIcon = document.getElementById('theme-toggle-icon');

    function setTheme(dark) {
      if (dark) {
        document.body.classList.add('dark-theme');
        themeToggleBtn.setAttribute('aria-pressed', 'true');
        themeToggleLabel.textContent = 'Dark Mode';
        themeToggleIcon.textContent = '🌙';
      } else {
        document.body.classList.remove('dark-theme');
        themeToggleBtn.setAttribute('aria-pressed', 'false');
        themeToggleLabel.textContent = 'Light Mode';
        themeToggleIcon.textContent = '🌞';
      }
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
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        themeToggleBtn.click();
      }
    });

    // 2. Directory button logic (moved outside drop area)
    // 3. Only allow image files for upload
    function isImageFile(file) {
      return file.type.startsWith('image/') || /\.(heic|heif|webp|gif|bmp|tiff|svg)$/i.test(file.name);
    }

    // Add event listener for the save buttons - add this right before the theme toggle logic
    // Add event listener for Save Alt Text buttons
    document.addEventListener('click', function(e) {
      if (e.target && e.target.classList.contains('save-alt-btn')) {
        const fileId = e.target.getAttribute('data-file-id');
        const textarea = document.getElementById(`alt-text-${fileId}`);
        if (!textarea) return;
        
        const newAlt = textarea.value.trim();
        if (!newAlt) return;
        
        e.target.disabled = true;
        e.target.textContent = 'Saving...';
        
        fetch('/api/update_alt_text', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({ file_id: fileId, alt_text: newAlt })
        })
        .then(r => r.json())
        .then(data => {
          if (data.success) {
            textarea.classList.add('alt-success');
            e.target.textContent = 'Saved!';
            setTimeout(() => {
              textarea.classList.remove('alt-success');
              e.target.textContent = 'Save Alt Text';
              e.target.disabled = false;
            }, 1500);
          } else {
            textarea.classList.add('alt-error');
            e.target.textContent = 'Error!';
            setTimeout(() => {
              textarea.classList.remove('alt-error');
              e.target.textContent = 'Save Alt Text';
              e.target.disabled = false;
            }, 1500);
          }
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
      }
    });

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
  </script>
</body>
</html>
'''

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {
        'jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff', 'webp', 'heic', 'heif', 'svg'
    }

def get_preview_url(path):
    # Serve image preview from upload folder
    return f'/api/preview?path={os.path.basename(path)}'

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
            body { font-family: system-ui, sans-serif; max-width: 900px; margin: 0 auto; padding: 20px; }
            h1 { color: #2d6cdf; }
            .image-container { display: flex; margin-bottom: 30px; border-bottom: 1px solid #eee; padding-bottom: 20px; }
            .image-preview { width: 200px; height: 200px; object-fit: contain; margin-right: 20px; border: 1px solid #ddd; }
            .image-metadata { flex: 1; }
            .metadata-item { margin-bottom: 8px; }
            .label { font-weight: bold; }
        </style>
    </head>
    <body>
        <h1>Herd AI Image Processing Results</h1>
        <p>Generated on {{ date }}</p>
        
        {% for item in results %}
        <div class="image-container">
            <img src="data:image/jpeg;base64,{{ item.image_data }}" class="image-preview" alt="{{ item.alt_text }}">
            <div class="image-metadata">
                <h2>{{ item.new_name }}</h2>
                <div class="metadata-item">
                    <span class="label">Original Filename:</span> {{ item.original_name }}
                </div>
                <div class="metadata-item">
                    <span class="label">Alt Text:</span> {{ item.alt_text }}
                </div>
                <div class="metadata-item">
                    <span class="label">Description:</span> {{ item.description }}
                </div>
                <div class="metadata-item">
                    <span class="label">Provider:</span> {{ item.provider }}
                </div>
                {% if item.dimensions %}
                <div class="metadata-item">
                    <span class="label">Dimensions:</span> {{ item.dimensions }}
                </div>
                {% endif %}
            </div>
        </div>
        {% endfor %}
    </body>
    </html>
    """
    template = env.from_string(html_template)
    
    # Add image data to results
    results_with_images = []
    for result in processed_results:
        # Skip items with errors
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
            
    from datetime import datetime
    return template.render(results=results_with_images, date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

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
    
    if has_bs4:
        # Use BeautifulSoup if available
        soup = BeautifulSoup(html_content, 'html.parser')
        text = soup.get_text(separator='\n')
        
        # Extract images from HTML for display in PDF
        img_tags = soup.find_all('img')
        for img in img_tags:
            if img.get('src') and img['src'].startswith('data:image'):
                # Extract base64 data
                img_data = img['src'].split(',', 1)[1]
                alt_text = img.get('alt', '')
                images.append((img_data, alt_text))
    else:
        # Simple fallback if BeautifulSoup is not available
        text = "Image Processing Results (BeautifulSoup not available for full HTML parsing)"
        # Try to extract images using simple string matching
        import re
        img_matches = re.findall(r'<img[^>]*src="data:image[^"]*base64,([^"]*)"[^>]*alt="([^"]*)"', html_content)
        for img_data, alt_text in img_matches:
            images.append((img_data, alt_text))
    
    # Add a title
    p.setFont("Helvetica-Bold", 18)
    p.drawString(50, height - 40, "Herd AI Image Processing Results")
    p.setFont("Helvetica", 12)
    
    # Process and add each image with its metadata
    y_position = height - 90
    page_num = 1
    
    for i, (img_data, alt_text) in enumerate(images):
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
            if has_pil:
                with Image.open(img_temp) as img:
                    # Scale image to fit on page
                    img_width, img_height = img.size
                    max_width = width - 100
                    max_height = 200
                    scale = min(max_width/img_width, max_height/img_height)
                    new_width = img_width * scale
                    new_height = img_height * scale
                    
                    # Save as JPG for ReportLab compatibility
                    img_temp = io.BytesIO()
                    img.save(img_temp, format='JPEG')
                    img_temp.seek(0)
                    
                    # Draw image
                    p.drawImage(img_temp, 50, y_position - new_height, width=new_width, height=new_height)
                    
                    # Draw metadata
                    y_position -= new_height + 20
            else:
                # Without PIL, we can't scale or display the image properly
                y_position -= 20
        except Exception as e:
            print(f"Error processing image for PDF: {e}")
            y_position -= 20
        
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
        
        if y_position < 100:
            p.showPage()
            page_num += 1
            y_position = height - 60
            p.setFont("Helvetica-Bold", 14)
            p.drawString(50, height - 40, f"Image Results (continued) - Page {page_num}")
            p.setFont("Helvetica", 12)
    
    # Add remaining text
    if text:
        p.setFont("Helvetica", 10)
        lines = text.splitlines()
        for line in lines:
            text_object.textLine(line[:100])  # Truncate very long lines
            if text_object.getY() < 50:
                p.drawText(text_object)
                p.showPage()
                page_num += 1
                text_object = p.beginText(50, height - 60)
                text_object.setFont("Helvetica", 10)
                p.drawString(50, height - 40, f"Additional Information - Page {page_num}")
                
        p.drawText(text_object)
    
    p.save()
    output.seek(0)
    return output

def process_image_for_ollama(image_path):
    """Process an image for Ollama API, following best practices from reference implementation."""
    if not has_pil:
        # Use basic encoding if PIL not available
        try:
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
        except Exception as e:
            print(f"Error encoding image: {e}")
            return None
    
    try:
        # Process with PIL for optimal results
        with Image.open(image_path) as img:
            # Convert to RGB if needed
            if img.mode != 'RGB':
                img = img.convert('RGB')
                
            # Resize if too large
            if img.size[0] > 1024 or img.size[1] > 1024:
                ratio = min(1024/img.size[0], 1024/img.size[1])
                new_size = (int(img.size[0]*ratio), int(img.size[1]*ratio))
                img = img.resize(new_size, Image.LANCZOS if hasattr(Image, 'LANCZOS') else Image.ANTIALIAS)
            
            # Save to bytes
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='JPEG')
            
            # Encode to base64
            return base64.b64encode(img_byte_arr.getvalue()).decode('utf-8')
    
    except Exception as e:
        print(f"Error processing image with PIL: {e}")
        # Fall back to basic encoding
        try:
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
        except Exception as e:
            print(f"Error encoding image: {e}")
            return None

def send_image_to_ollama(image_path, prompt, model="gemma3:4b"):
    """Send image to Ollama API with proper formatting based on Ollama API docs."""
    import requests
    
    # Process image
    image_base64 = process_image_for_ollama(image_path)
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
        
        if response.status_code == 200:
            result = response.json()
            return {
                "text": result.get("message", {}).get("content", ""),
                "model": model,
                "finish_reason": result.get("done", False)
            }
        
        print(f"Chat API failed with status {response.status_code}, trying generate API...")
        
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
                if "error" in error_data:
                    error_msg += f": {error_data['error']}"
            except:
                pass
            return {"text": error_msg, "error": True}
            
    except Exception as e:
        return {"text": f"Error connecting to Ollama API: {str(e)}", "error": True}

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/preview')
def preview():
    path = request.args.get('path')
    if not path:
        abort(404)
    full_path = os.path.join(app.config['UPLOAD_FOLDER'], path)
    if not os.path.exists(full_path):
        abort(404)
    return send_file(full_path)

@app.route('/api/process_images', methods=['POST'])
def process_images():
    files = request.files.getlist('images')
    provider = request.form.get('provider', 'ollama')
    model = request.form.get('model', 'gemma3:4b')  # Get model name if provided
    results = []
    processor = ImageProcessor(provider=provider)
    global processed_md_files
    global processed_files
    
    for file in files:
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
            
            # Get image dimensions if PIL is available
            dimensions = get_image_dimensions(temp_path)
            
            preview_url = get_preview_url(temp_path)
            file_id = f"{os.path.basename(temp_path)}_{hash(temp_path)}"
            
            if provider == 'ollama':
                # Use improved Ollama implementation
                ollama_result = send_image_to_ollama(
                    temp_path,
                    prompt=IMAGE_ALT_TEXT_TEMPLATE,
                    model=model
                )
                
                # Store original path for retry
                processed_files[file_id] = {
                    'path': temp_path,
                    'original_name': file.filename
                }
                
                # Parse result
                data = {}
                if ollama_result.get('text'):
                    try:
                        # First try to find JSON in the response
                        import re
                        json_match = re.search(r'\{.*\}', ollama_result['text'], re.DOTALL)
                        if json_match:
                            json_text = json_match.group(0)
                            data = json.loads(json_text)
                        else:
                            data = json.loads(ollama_result['text'])
                    except Exception as e:
                        print(f"Error parsing JSON: {e}")
                        # Create minimal data with the text
                        data = {
                            "alt_text": "Generated alt text",
                            "description": ollama_result.get('text', ''),
                            "suggested_filename": Path(temp_path).stem
                        }
                
                alt = data.get('alt_text', '')
                desc = data.get('description', '')
                name_raw = data.get('suggested_filename', '')
                new_name = secure_filename(name_raw) + Path(temp_path).suffix if name_raw else filename
                new_path = os.path.join(app.config['UPLOAD_FOLDER'], new_name)
                
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
            else:
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
                if result.get('renamed') and result.get('new_path'):
                    undo_token = {
                        'old_path': temp_path,
                        'new_path': result['new_path']
                    }
                    with undo_lock:
                        undo_log.append(undo_token)
                    
                    # Updated preview URL for renamed file
                    updated_preview_url = get_preview_url(result['new_path'])
                else:
                    updated_preview_url = preview_url
                
                md_id = None
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
        except Exception as e:
            results.append({
                'original_name': file.filename,
                'error': str(e)
            })
    
    return jsonify({'results': results})

@app.route('/api/retry_processing', methods=['POST'])
def retry_processing():
    """Re-process a single image"""
    data = request.get_json()
    file_id = data.get('file_id')
    provider = data.get('provider', 'ollama')
    model = data.get('model', 'gemma3:4b')  # Get model name if provided
    
    if not file_id or file_id not in processed_files:
        return jsonify({'error': 'File not found or invalid file_id'})
    
    file_info = processed_files[file_id]
    temp_path = file_info['path']
    
    if not os.path.exists(temp_path):
        return jsonify({'error': 'Original file no longer exists'})
    
    try:
        # Get file size and type
        file_size = os.path.getsize(temp_path)
        file_size_formatted = format_file_size(file_size)
        file_type = Path(temp_path).suffix.lstrip('.').upper()
        
        # Get image dimensions if PIL is available
        dimensions = get_image_dimensions(temp_path)
        
        preview_url = get_preview_url(temp_path)
        
        if provider == 'ollama':
            # Use improved Ollama implementation
            ollama_result = send_image_to_ollama(
                temp_path,
                prompt=IMAGE_ALT_TEXT_TEMPLATE,
                model=model
            )
            
            # Parse result
            data = {}
            if ollama_result.get('text'):
                try:
                    # First try to find JSON in the response
                    import re
                    json_match = re.search(r'\{.*\}', ollama_result['text'], re.DOTALL)
                    if json_match:
                        json_text = json_match.group(0)
                        data = json.loads(json_text)
                    else:
                        data = json.loads(ollama_result['text'])
                except Exception as e:
                    print(f"Error parsing JSON: {e}")
                    # Create minimal data with the text
                    data = {
                        "alt_text": "Generated alt text",
                        "description": ollama_result.get('text', ''),
                        "suggested_filename": Path(temp_path).stem
                    }
            
            alt = data.get('alt_text', '')
            desc = data.get('description', '')
            name_raw = data.get('suggested_filename', '')
            filename = os.path.basename(temp_path)
            new_name = secure_filename(name_raw) + Path(temp_path).suffix if name_raw else filename
            new_path = os.path.join(app.config['UPLOAD_FOLDER'], new_name)
            
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
        else:
            # Use X.AI
            processor = ImageProcessor(provider=provider)
            result = processor.process_single_image(
                Path(temp_path),
                {'base_dir': app.config['UPLOAD_FOLDER']}
            )
            
            undo_token = None
            if result.get('renamed') and result.get('new_path'):
                undo_token = {
                    'old_path': temp_path,
                    'new_path': result['new_path']
                }
                with undo_lock:
                    undo_log.append(undo_token)
            
            md_id = None
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
    except Exception as e:
        return jsonify({
            'original_name': file_info['original_name'],
            'error': str(e)
        })

@app.route('/api/download_md')
def download_md():
    md_id = request.args.get('md_id')
    if not md_id:
        abort(404)
    for md_path, _, _ in processed_md_files:
        if os.path.basename(md_path) == md_id:
            return send_file(md_path, as_attachment=True)
    abort(404)

@app.route('/api/download_all_md')
def download_all_md():
    # Create a zip of all .md files for the session
    mem_zip = io.BytesIO()
    with zipfile.ZipFile(mem_zip, 'w', zipfile.ZIP_DEFLATED) as zf:
        for md_path, original_name, new_name in processed_md_files:
            arcname = os.path.basename(md_path)
            zf.write(md_path, arcname)
    mem_zip.seek(0)
    return send_file(mem_zip, mimetype='application/zip', as_attachment=True, download_name='herd_markdown_files.zip')

@app.route('/api/download_html')
def download_html():
    """Generate and download HTML file with all processed images and their metadata."""
    # Get all successful results from processed_files
    results = []
    for file_id, file_info in processed_files.items():
        # Skip if there's no original path
        if not file_info.get('path'):
            continue
            
        # Find the corresponding result from processed_md_files
        for md_path, original_name, new_name in processed_md_files:
            if original_name == file_info['original_name']:
                try:
                    # Read description from markdown file
                    md_content = Path(md_path).read_text(encoding='utf-8')
                    lines = md_content.split('\n')
                    alt_text = lines[2][12:] if len(lines) > 2 else ''
                    description = lines[4][16:] if len(lines) > 4 else ''
                    
                    results.append({
                        'original_name': original_name,
                        'new_name': new_name,
                        'alt_text': alt_text,
                        'description': description,
                        'provider': 'Herd AI',
                        'dimensions': ''
                    })
                except Exception as e:
                    print(f"Error reading markdown file {md_path}: {e}")
                break
                
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

@app.route('/api/download_pdf')
def download_pdf():
    """Generate and download PDF file with all processed images and their metadata."""
    # Get all successful results from processed_files
    results = []
    for file_id, file_info in processed_files.items():
        # Skip if there's no original path
        if not file_info.get('path'):
            continue
            
        # Find the corresponding result from processed_md_files
        for md_path, original_name, new_name in processed_md_files:
            if original_name == file_info['original_name']:
                try:
                    # Read description from markdown file
                    md_content = Path(md_path).read_text(encoding='utf-8')
                    lines = md_content.split('\n')
                    alt_text = lines[2][12:] if len(lines) > 2 else ''
                    description = lines[4][16:] if len(lines) > 4 else ''
                    
                    results.append({
                        'original_name': original_name,
                        'new_name': new_name,
                        'alt_text': alt_text,
                        'description': description,
                        'provider': 'Herd AI',
                        'dimensions': ''
                    })
                except Exception as e:
                    print(f"Error reading markdown file {md_path}: {e}")
                break
    
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

@app.route('/api/undo', methods=['POST'])
def undo():
    data = request.get_json()
    token = data.get('undo_token')
    if not token or not isinstance(token, dict):
        return jsonify({'success': False, 'error': 'Invalid undo token.'})
    old_path = token.get('old_path')
    new_path = token.get('new_path')
    if not old_path or not new_path:
        return jsonify({'success': False, 'error': 'Missing file paths.'})
    try:
        if os.path.exists(new_path):
            shutil.move(new_path, old_path)
        with undo_lock:
            undo_log[:] = [t for t in undo_log if t != token]
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/bulk_undo', methods=['POST'])
def bulk_undo():
    """Undo changes for multiple files at once."""
    data = request.get_json()
    tokens = data.get('undo_tokens', [])
    
    if not tokens or not isinstance(tokens, list):
        return jsonify({'success': False, 'error': 'Invalid undo tokens.'})
    
    results = []
    for token in tokens:
        if not isinstance(token, dict):
            results.append({'success': False, 'error': 'Invalid undo token format.'})
            continue
            
        old_path = token.get('old_path')
        new_path = token.get('new_path')
        
        if not old_path or not new_path:
            results.append({'success': False, 'error': 'Missing file paths.'})
            continue
            
        try:
            if os.path.exists(new_path):
                shutil.move(new_path, old_path)
            with undo_lock:
                undo_log[:] = [t for t in undo_log if t != token]
            results.append({'success': True})
        except Exception as e:
            results.append({'success': False, 'error': str(e)})
    
    return jsonify({'results': results})

@app.route('/api/bulk_retry', methods=['POST'])
def bulk_retry():
    """Retry processing for multiple files at once."""
    data = request.get_json()
    file_ids = data.get('file_ids', [])
    provider = data.get('provider', 'ollama')
    model = data.get('model', 'gemma3:4b')
    
    if not file_ids or not isinstance(file_ids, list):
        return jsonify({'success': False, 'error': 'Invalid file IDs.'})
    
    results = []
    for file_id in file_ids:
        if file_id not in processed_files:
            results.append({
                'file_id': file_id,
                'success': False,
                'error': 'File not found or invalid file_id'
            })
            continue
            
        file_info = processed_files[file_id]
        temp_path = file_info['path']
        
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
            
            # Get image dimensions if PIL is available
            dimensions = get_image_dimensions(temp_path)
            
            preview_url = get_preview_url(temp_path)
            
            if provider == 'ollama':
                # Use improved Ollama implementation
                ollama_result = send_image_to_ollama(
                    temp_path,
                    prompt=IMAGE_ALT_TEXT_TEMPLATE,
                    model=model
                )
                
                # Parse result
                result_data = {}
                if ollama_result.get('text'):
                    try:
                        # First try to find JSON in the response
                        import re
                        json_match = re.search(r'\{.*\}', ollama_result['text'], re.DOTALL)
                        if json_match:
                            json_text = json_match.group(0)
                            result_data = json.loads(json_text)
                        else:
                            result_data = json.loads(ollama_result['text'])
                    except Exception as e:
                        print(f"Error parsing JSON: {e}")
                        # Create minimal data with the text
                        result_data = {
                            "alt_text": "Generated alt text",
                            "description": ollama_result.get('text', ''),
                            "suggested_filename": Path(temp_path).stem
                        }
                
                alt = result_data.get('alt_text', '')
                desc = result_data.get('description', '')
                name_raw = result_data.get('suggested_filename', '')
                filename = os.path.basename(temp_path)
                new_name = secure_filename(name_raw) + Path(temp_path).suffix if name_raw else filename
                new_path = os.path.join(app.config['UPLOAD_FOLDER'], new_name)
                
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
            else:
                # Use X.AI
                processor = ImageProcessor(provider=provider)
                proc_result = processor.process_single_image(
                    Path(temp_path),
                    {'base_dir': app.config['UPLOAD_FOLDER']}
                )
                
                undo_token = None
                if proc_result.get('renamed') and proc_result.get('new_path'):
                    undo_token = {
                        'old_path': temp_path,
                        'new_path': proc_result['new_path']
                    }
                    with undo_lock:
                        undo_log.append(undo_token)
                    
                    # Updated preview URL for renamed file
                    updated_preview_url = get_preview_url(proc_result['new_path'])
                else:
                    updated_preview_url = preview_url
                
                md_id = None
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
                
                if proc_result.get('error'):
                    result['success'] = False
            
            results.append(result)
            
        except Exception as e:
            results.append({
                'file_id': file_id,
                'original_name': file_info['original_name'],
                'success': False,
                'error': str(e)
            })
    
    return jsonify({'results': results})

def format_file_size(size_in_bytes):
    """Format file size to human-readable format."""
    if size_in_bytes < 1024:
        return f"{size_in_bytes} B"
    elif size_in_bytes < 1024 * 1024:
        return f"{size_in_bytes / 1024:.1f} KB"
    else:
        return f"{size_in_bytes / (1024 * 1024):.1f} MB"

def get_image_dimensions(image_path):
    """Get image dimensions if PIL is available."""
    if not has_pil:
        return None
    
    try:
        with Image.open(image_path) as img:
            return f"{img.width}x{img.height}"
    except Exception as e:
        print(f"Error getting image dimensions: {e}")
        return None

@app.route('/api/update_alt_text', methods=['POST'])
def update_alt_text():
    data = request.get_json()
    file_id = data.get('file_id')
    new_alt_text = data.get('alt_text', '').strip()
    if not file_id or not new_alt_text:
        return jsonify({'success': False, 'error': 'Missing file_id or alt_text'})
    # Find the markdown file for this file_id
    md_path = None
    for md, orig, new in processed_md_files:
        if file_id in (orig, new, os.path.basename(md)):
            md_path = md
            break
    if not md_path or not os.path.exists(md_path):
        return jsonify({'success': False, 'error': 'Markdown file not found'})
    # Read and update the markdown file
    try:
        lines = Path(md_path).read_text(encoding='utf-8').split('\n')
        # Find the alt text line (assume format: **Alt Text:** ...)
        for i, line in enumerate(lines):
            if line.strip().startswith('**Alt Text:**'):
                lines[i] = f"**Alt Text:** {new_alt_text}"
                break
        Path(md_path).write_text('\n'.join(lines), encoding='utf-8')
        # Optionally, update image metadata here (not implemented for brevity)
        return jsonify({'success': True, 'alt_text': new_alt_text})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    app.run(port=4343, debug=True) 