# Code Snippets from toollama/storage/script.js

File: `toollama/storage/script.js`  
Language: JavaScript  
Extracted: 2025-06-07 05:11:11  

## Snippet 1
Lines 1-14

```JavaScript
const API_BASE_URL = "https://ai.assisted.space/api";
console.log("API_BASE_URL:", API_BASE_URL);

const state = {
  currentModel: "camina:latest",
  md: window.markdownit(),
  messages: [],
  currentFile: null,
  isResponding: false,
  theme: localStorage.getItem('theme') || 'light'
};
console.log("Initial state:", state);

// Theme handling
```

## Snippet 2
Lines 17-22

```JavaScript
if (!themeToggle) {
    console.warn('Theme toggle element not found');
    return;
  }
  themeToggle.checked = state.theme === 'dark';
  document.body.setAttribute('data-theme', state.theme);
```

## Snippet 3
Lines 25-31

```JavaScript
function toggleTheme() {
  state.theme = state.theme === 'light' ? 'dark' : 'light';
  localStorage.setItem('theme', state.theme);
  document.body.setAttribute('data-theme', state.theme);
}

// Settings panel
```

## Snippet 4
Lines 32-37

```JavaScript
function initializeSettings() {
  const settingsButton = document.getElementById('settingsButton');
  const settingsPanel = document.getElementById('settingsPanel');
  const closeSettings = document.querySelector('.close-settings');
  const themeToggle = document.getElementById('themeToggle');
```

## Snippet 5
Lines 38-54

```JavaScript
if (!settingsButton || !settingsPanel || !closeSettings || !themeToggle) {
    console.warn('One or more settings elements not found');
    return;
  }

  settingsButton.addEventListener('click', () => {
    settingsPanel.classList.toggle('active');
  });

  closeSettings.addEventListener('click', () => {
    settingsPanel.classList.remove('active');
  });

  themeToggle.addEventListener('change', toggleTheme);

  // Close settings panel when clicking outside
  document.addEventListener('click', (e) => {
```

## Snippet 6
Lines 55-57

```JavaScript
if (!settingsPanel.contains(e.target) && !settingsButton.contains(e.target)) {
      settingsPanel.classList.remove('active');
    }
```

## Snippet 7
Lines 64-68

```JavaScript
if (file) {
    state.currentFile = file;
    document.getElementById('fileName').textContent = file.name;
    console.log("File selected:", file.name);
  }
```

## Snippet 8
Lines 71-82

```JavaScript
async function readFileAsBase64(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => {
      const base64String = reader.result.split(',')[1];
      resolve(base64String);
    };
    reader.onerror = reject;
    reader.readAsDataURL(file);
  });
}
```

## Snippet 9
Lines 83-86

```JavaScript
function setLoading(isLoading) {
  const sendButton = document.getElementById('sendButton');
  const container = document.querySelector('.chat-container');
```

## Snippet 10
Lines 87-90

```JavaScript
if (isLoading) {
    sendButton.classList.add('loading');
    sendButton.disabled = true;
    container.classList.add('loading');
```

## Snippet 11
Lines 91-95

```JavaScript
} else {
    sendButton.classList.remove('loading');
    sendButton.disabled = false;
    container.classList.remove('loading');
  }
```

## Snippet 12
Lines 115-119

```JavaScript
if (!state.md.configured) {
    state.md.set({
      html: false, // Disable HTML rendering
      breaks: true,
      linkify: true,
```

## Snippet 13
Lines 135-145

```JavaScript
if (content.includes('<think>') && !content.includes('</think>')) {
      // We're in an incomplete thinking block
      const thoughts = content.replace('<think>', '')
        .split('\n')
        .filter(thought => thought.trim())
        .map(thought => `<div class="thought-bubble">${state.md.render(thought.trim())}</div>`)
        .join('');

      return thoughts;
    }
```

## Snippet 14
Lines 147-161

```JavaScript
if (content.includes('</think>')) {
      const [thoughtContent, mainContent] = content.split('</think>');

      const thoughts = thoughtContent.replace('<think>', '')
        .split('\n')
        .filter(thought => thought.trim())
        .map(thought => `<div class="thought-bubble">${state.md.render(thought.trim())}</div>`)
        .join('');

      const separator = '<div class="message-separator"></div>';
      const mainHtml = mainContent ?
        `<div class="message-content">${state.md.render(mainContent.trim())}</div>` : '';

      return thoughts + separator + mainHtml;
    }
```

## Snippet 15
Lines 162-165

```JavaScript
}

  // Regular content (no think tags or user messages)
  return `<div class="message-content">${state.md.render(content)}</div>`;
```

## Snippet 16
Lines 168-175

```JavaScript
function createMessageItem(content, type) {
  console.log("Creating message item:", {content, type});
  const messagesList = document.getElementById("messages");

  const container = document.createElement("div");
  container.className = `message-container ${type}-container`;

  const messageEl = document.createElement("li");
```

## Snippet 17
Lines 176-183

```JavaScript
messageEl.className = `message ${type} markdown-body`;
  messageEl.innerHTML = processMessageContent(content, type);

  // Highlight any code blocks
  messageEl.querySelectorAll('pre code').forEach((block) => {
    hljs.highlightElement(block);
  });
```

## Snippet 18
Lines 184-197

```JavaScript
if (type === "bot-message") {
    const metadataEl = document.createElement("div");
    metadataEl.className = "message-metadata";

    const tokenCountEl = document.createElement("span");
    tokenCountEl.className = "token-count";
    tokenCountEl.textContent = "Calculating tokens...";

    metadataEl.appendChild(tokenCountEl);

    container.appendChild(messageEl);
    container.appendChild(metadataEl);
    messagesList.appendChild(container);
```

## Snippet 19
Lines 206-210

```JavaScript
function autoScroll() {
  const chatBox = document.querySelector(".chat-container");
  chatBox.scrollTop = chatBox.scrollHeight;
}
```

## Snippet 20
Lines 211-215

```JavaScript
async function sendMessage() {
  const messageInput = document.getElementById("messageInput");
  const content = messageInput.value.trim();
  const hasFile = state.currentFile !== null;
```

## Snippet 21
Lines 216-230

```JavaScript
if (!content && !hasFile) return;

  setLoading(true);
  state.isResponding = true;

  // Prepare the user message
  let userMessage = {
    role: "user",
    content: content || "What do you see in this image?"
  };

  // Add to messages array
  state.messages.push(userMessage);

  // Show in UI
```

## Snippet 22
Lines 231-242

```JavaScript
const { messageEl } = createMessageItem(content || "📎 Attached file", "user-message");
  messageInput.value = "";
  messageInput.style.height = 'auto'; // Reset height after sending
  autoScroll(); // Auto-scroll after user message

  try {
    const requestBody = {
      model: state.currentModel,
      messages: state.messages,
      stream: true
    };
```

## Snippet 23
Lines 244-247

```JavaScript
if (hasFile) {
      const base64Content = await readFileAsBase64(state.currentFile);

      // For models that support images (like llava)
```

## Snippet 24
Lines 250-261

```JavaScript
} else {
        // For other models, embed image in the message
        userMessage.content = content ?
          `${content}\n[Attached Image: ${state.currentFile.name}]` :
          "What do you see in this image?";
        userMessage.images = [base64Content];
      }

      // Clear file after preparing request
      state.currentFile = null;
      document.getElementById('fileName').textContent = '';
      document.getElementById('fileInput').value = '';
```

## Snippet 25
Lines 262-283

```JavaScript
}

    console.log("API Request details:", {
      url: `${API_BASE_URL}/api/chat`,
      body: {
        ...requestBody,
        messages: requestBody.messages,
        images: requestBody.images ? ['[Image Data]'] : undefined
      }
    });

    const response = await fetch(`${API_BASE_URL}/chat`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(requestBody),
    });

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
```

## Snippet 26
Lines 284-288

```JavaScript
const { messageEl: botMessageEl, tokenCountEl, container: botContainer } =
      createMessageItem("", "bot-message");
    let fullContent = "";
    let totalTokens = 0;
```

## Snippet 27
Lines 291-296

```JavaScript
if (done) {
        // Only hide streaming indicator when we're done reading the stream
        setStreaming(false);
        break;
      }
```

## Snippet 28
Lines 301-305

```JavaScript
if (line.trim() === '') continue;

        try {
          const data = JSON.parse(line);
```

## Snippet 29
Lines 306-311

```JavaScript
if (data.message?.content) {
            fullContent += data.message.content;
            botMessageEl.innerHTML = processMessageContent(fullContent, "bot-message");
            autoScroll();
          }
```

## Snippet 30
Lines 312-319

```JavaScript
if (data.done) {
            totalTokens = data.prompt_eval_count + data.eval_count;
            tokenCountEl.textContent = `Tokens: ${totalTokens}`;
            state.messages.push({
              role: "assistant",
              content: fullContent
            });
          }
```

## Snippet 31
Lines 320-323

```JavaScript
} catch (error) {
          console.warn("Error parsing line:", line, error);
          continue;
        }
```

## Snippet 32
Lines 326-329

```JavaScript
} catch (error) {
    console.error("Error:", error);
    showToast(`Error: ${error.message}`);
    setStreaming(false); // Hide streaming indicator on error
```

## Snippet 33
Lines 334-352

```JavaScript
}

// Event Listeners
document
  .getElementById("sendButton")
  .addEventListener("click", sendMessage);
console.log("Added click handler to send button");

document.getElementById("togglePreviewButton").style.display = "none"; // Hide button initially

document.getElementById("messageInput").addEventListener("input", function(e) {
    const input = e.target;
    const previewContainer = document.getElementById("previewContainer");
    const toggleButton = document.getElementById("togglePreviewButton");

    // Auto-expand textarea
    input.style.height = 'auto';
    input.style.height = (input.scrollHeight) + 'px';
```

## Snippet 34
Lines 353-360

```JavaScript
// Check if content looks like code (has multiple lines or special characters)
    const content = input.value;
    const looksLikeCode = content.includes('\n') ||
                         content.includes('{') ||
                         content.includes('}') ||
                         content.includes(';') ||
                         /^(const|let|var|function|import|export|class)\s/.test(content);
```

## Snippet 35
Lines 375-378

```JavaScript
if (event.key === "Enter" && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
    }
```

## Snippet 36
Lines 380-386

```JavaScript
console.log("Added keydown handler to message input");

document
  .getElementById("fileInput")
  .addEventListener("change", handleFileSelect);
console.log("Added file input handler");
```

## Snippet 37
Lines 387-397

```JavaScript
function showToast(message, duration = 3000) {
  console.log("Showing toast:", message);
  const toast = document.getElementById('toast');
  toast.textContent = message;
  toast.classList.add('show');

  setTimeout(() => {
    toast.classList.remove('show');
  }, duration);
}
```

## Snippet 38
Lines 398-401

```JavaScript
async function sendIntroductionPrompt() {
  const messageInput = document.getElementById("messageInput");
  const selectedModel = document.getElementById("modelSelect").value;
```

## Snippet 39
Lines 404-409

```JavaScript
} else {
    messageInput.value = "Introduce yourself and your capabilities.";
  }

  try {
    await sendMessage();
```

## Snippet 40
Lines 416-433

```JavaScript
function createSystemMessage(content) {
  const messagesList = document.getElementById("messages");
  const container = document.createElement("div");
  container.className = "message-container system-container";

  const messageEl = document.createElement("li");
  messageEl.className = "message system-message";
  messageEl.textContent = content;

  container.appendChild(messageEl);
  messagesList.appendChild(container);
  autoScroll();
}

document.getElementById("modelSelect").addEventListener("change", async (event) => {
  const selectedModel = event.target.value;
  const previousModel = state.currentModel;
```

## Snippet 41
Lines 435-437

```JavaScript
createSystemMessage("Waiting for current response to complete before switching models...");

    const checkInterval = setInterval(() => {
```

## Snippet 42
Lines 438-441

```JavaScript
if (!state.isResponding) {
        clearInterval(checkInterval);
        completeModelSwitch();
      }
```

## Snippet 43
Lines 449-452

```JavaScript
createSystemMessage(`Switching from ${previousModel} to ${selectedModel}...`);
    setStreaming(true, true); // Show model loading indicator
    try {
      await sendIntroductionPrompt();
```

## Snippet 44
Lines 453-457

```JavaScript
} catch (error) {
      console.error('Error during model switch:', error);
      showToast('Error switching models. Please try again.');
      setStreaming(false, true); // Hide model loading indicator on error
    }
```

## Snippet 45
Lines 461-468

```JavaScript
async function loadModelConfig() {
  try {
    const response = await fetch('models.json');
    const config = await response.json();
    state.currentModel = config.defaultModel;

    // Find the current model configuration
    const currentModelConfig = config.availableModels.find(model => model.name === state.currentModel);
```

## Snippet 46
Lines 469-471

```JavaScript
if (currentModelConfig) {
      updateAttachmentUI(currentModelConfig.attach);
    }
```

## Snippet 47
Lines 472-475

```JavaScript
} catch (error) {
    console.error('Error loading model config:', error);
    showToast('Error loading model configuration');
  }
```

## Snippet 48
Lines 478-484

```JavaScript
function updateAttachmentUI(attachOption) {
  const fileInputContainer = document.querySelector('.file-input-container');
  const fileInput = document.getElementById('fileInput');
  const fileLabel = document.querySelector('.file-label');

  switch (attachOption) {
    case 'files':
```

## Snippet 49
Lines 494-502

```JavaScript
case 'all':
      fileInput.removeAttribute('accept');
      fileInputContainer.style.display = 'block';
      fileLabel.textContent = '📎 Attach File/Image';
      break;
    case 'none':
    default:
      fileInputContainer.style.display = 'none';
      break;
```

## Snippet 50
Lines 504-517

```JavaScript
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', async () => {
  await loadModelConfig();
  setStreaming(true, true);

  // Set and send the introduction message
  const messageInput = document.getElementById("messageInput");
  messageInput.value = "Introduce yourself and explain who created you, any other relevant information, and your abilities and functions, with examples";
  await sendMessage();
});

// Remove or comment out the window.load event listener since we're handling initialization in DOMContentLoaded
```

