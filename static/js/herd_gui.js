// Herd GUI JavaScript
// All logic from the HTML_TEMPLATE in herd_gui.py

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

// Bulk actions
const bulkActionsContainer = document.getElementById('bulk-actions');
const selectAllCheckbox = document.getElementById('select-all');
const bulkRetryBtn = document.getElementById('bulk-retry-btn');
const bulkUndoBtn = document.getElementById('bulk-undo-btn');
const selectedCountSpan = document.getElementById('selected-count');
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

// Select all checkbox
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

function updateSelectedCount() {
  const count = selectedItems.size;
  selectedCountSpan.textContent = `${count} file${count !== 1 ? 's' : ''} selected`;
  selectedCountSpan.style.display = count > 0 ? 'inline' : 'none';
}
function updateBulkButtons() {
  const hasSelection = selectedItems.size > 0;
  bulkRetryBtn.disabled = !hasSelection;
  bulkUndoBtn.disabled = !hasSelection;
}
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
    const results = data.results || [];
    for (const result of results) {
      if (result.file_id) {
        updateFileItemAfterBulkAction(result);
      }
    }
    selectedItems.clear();
    selectAllCheckbox.checked = false;
    updateSelectedCount();
    updateBulkButtons();
  })
  .catch(err => {
    console.error("Bulk retry failed:", err);
  });
});

bulkUndoBtn.addEventListener('click', () => {
  if (selectedItems.size === 0) return;
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
    selectedItems.clear();
    selectAllCheckbox.checked = false;
    updateSelectedCount();
    updateBulkButtons();
  })
  .catch(err => {
    console.error("Bulk undo failed:", err);
  });
});

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
    const buttonGroup = document.createElement('div');
    buttonGroup.className = 'button-group';
    if (result.md_id) {
      hasMd = true;
      const mdBtn = document.createElement('button');
      mdBtn.className = 'md-btn btn btn-primary';
      mdBtn.textContent = 'Download Markdown';
      mdBtn.onclick = () => window.open(`/api/download_md?md_id=${encodeURIComponent(result.md_id)}`);
      buttonGroup.appendChild(mdBtn);
      downloadContainer.style.display = 'flex';
    }
    const retryBtn = document.createElement('button');
    retryBtn.className = 'retry-btn btn btn-secondary';
    retryBtn.textContent = 'Retry';
    retryBtn.setAttribute('aria-label', `Retry processing for ${result.original_name}`);
    retryBtn.onclick = () => retryProcessing(result.file_id, meta);
    buttonGroup.appendChild(retryBtn);
    const undoBtn = document.createElement('button');
    undoBtn.className = 'undo-btn btn btn-secondary';
    undoBtn.textContent = 'Undo';
    undoBtn.setAttribute('aria-label', `Undo changes for ${result.original_name}`);
    undoBtn.onclick = () => undoAction(result.undo_token, fileItem);
    buttonGroup.appendChild(undoBtn);
    meta.appendChild(buttonGroup);
  }
  const thumb = fileItem.querySelector('.file-thumb');
  if (thumb) {
    thumb.alt = result.new_name || result.original_name;
    thumb.src = result.preview_url || '';
  }
  if (result.undo_token) {
    fileItem.setAttribute('data-undo-token', JSON.stringify(result.undo_token));
  }
}

const originalHandleFiles = handleFiles;
handleFiles = function(files) {
  originalHandleFiles(files);
  const imageFiles = Array.from(files).filter(isImageFile);
  if (imageFiles.length > 0) {
    bulkActionsContainer.style.display = 'block';
  } else {
    bulkActionsContainer.style.display = 'none';
  }
};

function handleFiles(files) {
  const imageFiles = Array.from(files).filter(isImageFile);
  if (!imageFiles.length) return;
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
  processedCount.textContent = '0';
  totalCount.textContent = imageFiles.length;
  processingInfo.style.display = 'block';
  for (const file of imageFiles) {
    const item = document.createElement('div');
    item.className = 'file-item bg-surface rounded shadow-md p-3 mb-2';
    item.id = `file-item-${currentImages.length}`;
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
    processedImages++;
    processedCount.textContent = processedImages;
    for (const result of res.results) {
      if (fileItem) {
        const meta = fileItem.querySelector('.file-meta');
        if (result.error) {
          meta.innerHTML = `<strong>${result.original_name}</strong><span class='error'>Error: ${result.error}</span>`;
        } else {
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
          const retryBtn = document.createElement('button');
          retryBtn.className = 'retry-btn btn btn-secondary';
          retryBtn.textContent = 'Retry';
          retryBtn.setAttribute('aria-label', `Retry processing for ${result.original_name}`);
          retryBtn.onclick = () => retryProcessing(result.file_id, meta);
          buttonGroup.appendChild(retryBtn);
          const undoBtn = document.createElement('button');
          undoBtn.className = 'undo-btn btn btn-secondary';
          undoBtn.textContent = 'Undo';
          undoBtn.setAttribute('aria-label', `Undo changes for ${result.original_name}`);
          undoBtn.onclick = () => undoAction(result.undo_token, fileItem);
          buttonGroup.appendChild(undoBtn);
          meta.appendChild(buttonGroup);
          const thumb = fileItem.querySelector('.file-thumb');
          thumb.alt = result.new_name || result.original_name;
          thumb.src = result.preview_url || '';
          if (result.undo_token) {
            fileItem.setAttribute('data-undo-token', JSON.stringify(result.undo_token));
          }
        }
      }
      if (hasMd && !processingComplete) {
        downloadContainer.style.display = 'flex';
      }
    }
    processNextImage(files, index + 1);
  })
  .catch(err => {
    processedImages++;
    processedCount.textContent = processedImages;
    if (fileItem) {
      const meta = fileItem.querySelector('.file-meta');
      meta.innerHTML = `<strong>${files[index].name}</strong><span class='error'>Error: ${err}</span>`;
    }
    processNextImage(files, index + 1);
  });
}

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
      const buttonGroup = document.createElement('div');
      buttonGroup.className = 'button-group';
      if (result.md_id) {
        hasMd = true;
        const mdBtn = document.createElement('button');
        mdBtn.className = 'md-btn btn btn-primary';
        mdBtn.textContent = 'Download Markdown';
        mdBtn.onclick = () => window.open(`/api/download_md?md_id=${encodeURIComponent(result.md_id)}`);
        buttonGroup.appendChild(mdBtn);
        downloadContainer.style.display = 'flex';
      }
      const retryBtn = document.createElement('button');
      retryBtn.className = 'retry-btn btn btn-secondary';
      retryBtn.textContent = 'Retry';
      retryBtn.setAttribute('aria-label', `Retry processing for ${result.original_name}`);
      retryBtn.onclick = () => retryProcessing(result.file_id, metaElement);
      buttonGroup.appendChild(retryBtn);
      const undoBtn = document.createElement('button');
      undoBtn.className = 'undo-btn btn btn-secondary';
      undoBtn.textContent = 'Undo';
      undoBtn.setAttribute('aria-label', `Undo changes for ${result.original_name}`);
      undoBtn.onclick = () => undoAction(result.undo_token, metaElement.parentNode.parentNode);
      buttonGroup.appendChild(undoBtn);
      metaElement.appendChild(buttonGroup);
      const fileItem = metaElement.parentNode.parentNode;
      if (fileItem && result.undo_token) {
        fileItem.setAttribute('data-undo-token', JSON.stringify(result.undo_token));
      }
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

function isImageFile(file) {
  return file.type.startsWith('image/') || /\.(heic|heif|webp|gif|bmp|tiff|svg)$/i.test(file.name);
}

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
let prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
setTheme(prefersDark);
themeToggleBtn.addEventListener('click', () => {
  const isDark = document.body.classList.contains('dark-theme');
  setTheme(!isDark);
});
themeToggleBtn.addEventListener('keydown', (e) => {
  if (e.key === 'Enter' || e.key === ' ') {
    e.preventDefault();
    themeToggleBtn.click();
  }
}); 