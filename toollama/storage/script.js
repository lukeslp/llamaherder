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
function initializeTheme() {
  const themeToggle = document.getElementById('themeToggle');
  if (!themeToggle) {
    console.warn('Theme toggle element not found');
    return;
  }
  themeToggle.checked = state.theme === 'dark';
  document.body.setAttribute('data-theme', state.theme);
}

function toggleTheme() {
  state.theme = state.theme === 'light' ? 'dark' : 'light';
  localStorage.setItem('theme', state.theme);
  document.body.setAttribute('data-theme', state.theme);
}

// Settings panel
function initializeSettings() {
  const settingsButton = document.getElementById('settingsButton');
  const settingsPanel = document.getElementById('settingsPanel');
  const closeSettings = document.querySelector('.close-settings');
  const themeToggle = document.getElementById('themeToggle');

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
    if (!settingsPanel.contains(e.target) && !settingsButton.contains(e.target)) {
      settingsPanel.classList.remove('active');
    }
  });
}

// File handling functions
function handleFileSelect(event) {
  const file = event.target.files[0];
  if (file) {
    state.currentFile = file;
    document.getElementById('fileName').textContent = file.name;
    console.log("File selected:", file.name);
  }
}

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

function setLoading(isLoading) {
  const sendButton = document.getElementById('sendButton');
  const container = document.querySelector('.chat-container');
  
  if (isLoading) {
    sendButton.classList.add('loading');
    sendButton.disabled = true;
    container.classList.add('loading');
  } else {
    sendButton.classList.remove('loading');
    sendButton.disabled = false;
    container.classList.remove('loading');
  }
}

function setStreaming(isStreaming, isModelLoading = false) {
  const container = document.querySelector('.chat-container');
  
  if (isStreaming) {
    container.classList.add('streaming');
    if (isModelLoading) {
      container.classList.add('model-loading');
    } else {
      container.classList.remove('model-loading');
    }
  } else {
    container.classList.remove('streaming', 'model-loading');
  }
}

function processMessageContent(content, type) {
  // Configure markdown-it with code highlighting
  if (!state.md.configured) {
    state.md.set({
      html: false, // Disable HTML rendering
      breaks: true,
      linkify: true,
      highlight: function (str, lang) {
        if (lang && hljs.getLanguage(lang)) {
          try {
            return hljs.highlight(str, { language: lang }).value;
          } catch (__) {}
        }
        return ''; // use external default escaping
      }
    });
    state.md.configured = true;
  }

  // Only process "think" tags for bot messages
  if (type === "bot-message") {
    // Check if we're in a thinking block
    if (content.includes('<think>') && !content.includes('</think>')) {
      // We're in an incomplete thinking block
      const thoughts = content.replace('<think>', '')
        .split('\n')
        .filter(thought => thought.trim())
        .map(thought => `<div class="thought-bubble">${state.md.render(thought.trim())}</div>`)
        .join('');
      
      return thoughts;
    }
    
    // Check if we're completing a thinking block
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
  }
  
  // Regular content (no think tags or user messages)
  return `<div class="message-content">${state.md.render(content)}</div>`;
}

function createMessageItem(content, type) {
  console.log("Creating message item:", {content, type});
  const messagesList = document.getElementById("messages");
  
  const container = document.createElement("div");
  container.className = `message-container ${type}-container`;
  
  const messageEl = document.createElement("li");
  messageEl.className = `message ${type} markdown-body`;
  messageEl.innerHTML = processMessageContent(content, type);
  
  // Highlight any code blocks
  messageEl.querySelectorAll('pre code').forEach((block) => {
    hljs.highlightElement(block);
  });

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
    
    return { messageEl, tokenCountEl, container };
  } else {
    container.appendChild(messageEl);
    messagesList.appendChild(container);
    return { messageEl };
  }
}

function autoScroll() {
  const chatBox = document.querySelector(".chat-container");
  chatBox.scrollTop = chatBox.scrollHeight;
}

async function sendMessage() {
  const messageInput = document.getElementById("messageInput");
  const content = messageInput.value.trim();
  const hasFile = state.currentFile !== null;
  
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

    // Add file if present
    if (hasFile) {
      const base64Content = await readFileAsBase64(state.currentFile);
      
      // For models that support images (like llava)
      if (state.currentModel.includes('llava')) {
        requestBody.images = [base64Content];
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
    
    const { messageEl: botMessageEl, tokenCountEl, container: botContainer } = 
      createMessageItem("", "bot-message");
    let fullContent = "";
    let totalTokens = 0;

    while (true) {
      const { value, done } = await reader.read();
      if (done) {
        // Only hide streaming indicator when we're done reading the stream
        setStreaming(false);
        break;
      }

      const chunk = decoder.decode(value, { stream: true });
      const lines = chunk.split('\n');
      
      for (const line of lines) {
        if (line.trim() === '') continue;
        
        try {
          const data = JSON.parse(line);
          
          if (data.message?.content) {
            fullContent += data.message.content;
            botMessageEl.innerHTML = processMessageContent(fullContent, "bot-message");
            autoScroll();
          }
          
          if (data.done) {
            totalTokens = data.prompt_eval_count + data.eval_count;
            tokenCountEl.textContent = `Tokens: ${totalTokens}`;
            state.messages.push({
              role: "assistant",
              content: fullContent
            });
          }
        } catch (error) {
          console.warn("Error parsing line:", line, error);
          continue;
        }
      }
    }
  } catch (error) {
    console.error("Error:", error);
    showToast(`Error: ${error.message}`);
    setStreaming(false); // Hide streaming indicator on error
  } finally {
    setLoading(false);
    state.isResponding = false;
  }
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
    
    // Check if content looks like code (has multiple lines or special characters)
    const content = input.value;
    const looksLikeCode = content.includes('\n') || 
                         content.includes('{') || 
                         content.includes('}') ||
                         content.includes(';') ||
                         /^(const|let|var|function|import|export|class)\s/.test(content);
    
    if (looksLikeCode && content.trim()) {
        previewContainer.textContent = content;
        toggleButton.style.display = "block"; // Show button if there's content
    } else {
        previewContainer.textContent = '';
        toggleButton.style.display = "none"; // Hide button if no content
        previewContainer.classList.remove('active');
        toggleButton.textContent = "Show Preview";
    }
});

document
  .getElementById("messageInput")
  .addEventListener("keydown", function(event) {
    if (event.key === "Enter" && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
    }
  });
console.log("Added keydown handler to message input");

document
  .getElementById("fileInput")
  .addEventListener("change", handleFileSelect);
console.log("Added file input handler");

function showToast(message, duration = 3000) {
  console.log("Showing toast:", message);
  const toast = document.getElementById('toast');
  toast.textContent = message;
  toast.classList.add('show');
  
  setTimeout(() => {
    toast.classList.remove('show');
  }, duration);
}

async function sendIntroductionPrompt() {
  const messageInput = document.getElementById("messageInput");
  const selectedModel = document.getElementById("modelSelect").value;
  
  if (selectedModel.startsWith('drummer-')) {
    messageInput.value = "List your capabilities and available tools.";
  } else {
    messageInput.value = "Introduce yourself and your capabilities.";
  }
  
  try {
    await sendMessage();
  } finally {
    // Hide model loading indicator after introduction is complete
    setStreaming(false, true);
  }
}

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
  
  if (state.isResponding) {
    createSystemMessage("Waiting for current response to complete before switching models...");
    
    const checkInterval = setInterval(() => {
      if (!state.isResponding) {
        clearInterval(checkInterval);
        completeModelSwitch();
      }
    }, 100);
  } else {
    completeModelSwitch();
  }

  async function completeModelSwitch() {
    state.currentModel = selectedModel;
    createSystemMessage(`Switching from ${previousModel} to ${selectedModel}...`);
    setStreaming(true, true); // Show model loading indicator
    try {
      await sendIntroductionPrompt();
    } catch (error) {
      console.error('Error during model switch:', error);
      showToast('Error switching models. Please try again.');
      setStreaming(false, true); // Hide model loading indicator on error
    }
  }
});

async function loadModelConfig() {
  try {
    const response = await fetch('models.json');
    const config = await response.json();
    state.currentModel = config.defaultModel;

    // Find the current model configuration
    const currentModelConfig = config.availableModels.find(model => model.name === state.currentModel);
    if (currentModelConfig) {
      updateAttachmentUI(currentModelConfig.attach);
    }
  } catch (error) {
    console.error('Error loading model config:', error);
    showToast('Error loading model configuration');
  }
}

function updateAttachmentUI(attachOption) {
  const fileInputContainer = document.querySelector('.file-input-container');
  const fileInput = document.getElementById('fileInput');
  const fileLabel = document.querySelector('.file-label');

  switch (attachOption) {
    case 'files':
      fileInput.setAttribute('accept', '*/*');
      fileInputContainer.style.display = 'block';
      fileLabel.textContent = '📎 Attach File';
      break;
    case 'images':
      fileInput.setAttribute('accept', 'image/*');
      fileInputContainer.style.display = 'block';
      fileLabel.textContent = '📎 Attach Image';
      break;
    case 'all':
      fileInput.removeAttribute('accept');
      fileInputContainer.style.display = 'block';
      fileLabel.textContent = '📎 Attach File/Image';
      break;
    case 'none':
    default:
      fileInputContainer.style.display = 'none';
      break;
  }
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
// window.addEventListener("load", async () => { ... }); 