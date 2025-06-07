/**
 * Assisted.Space API Tester
 * JavaScript for handling user interactions and API calls
 */

// Constants
const API_BASE_URL = '/api.assisted.space/v2';
const API_KEY = 'test_api_key'; // Hard-coded API key for testing
const DEFAULT_PROVIDER = 'anthropic';

// DOM Elements
// Tabs
const tabButtons = document.querySelectorAll('.tab-button');
const tabPanes = document.querySelectorAll('.tab-pane');

// Chat Elements
const chatInput = document.getElementById('chat-input');
const sendChatButton = document.getElementById('send-chat');
const conversationArea = document.getElementById('conversation-area');
const chatModel = document.getElementById('chat-model');
const maxTokens = document.getElementById('max-tokens');
const systemPrompt = document.getElementById('system-prompt');
const clearConversationButton = document.getElementById('clear-conversation');

// Alt Text Elements
const altModel = document.getElementById('alt-model');
const altPrompt = document.getElementById('alt-prompt');
const imagePreview = document.getElementById('image-preview');
const previewImage = document.getElementById('preview-image');
const imageUpload = document.getElementById('image-upload');
const uploadButton = document.getElementById('upload-button');
const generateAltTextButton = document.getElementById('generate-alt-text');
const altTextOutput = document.getElementById('alt-text-output');
const copyAltTextButton = document.getElementById('copy-alt-text');

// Tools Elements
const toolModel = document.getElementById('tool-model');
const toolPrompt = document.getElementById('tool-prompt');
const toolDefinitions = document.getElementById('tool-definitions');
const callToolButton = document.getElementById('call-tool');
const toolOutput = document.getElementById('tool-output');

// Loading Overlay
const loadingOverlay = document.getElementById('loading-overlay');

// Global Variables
let selectedFile = null;
let conversationId = 'test-' + Date.now();

// Event Listeners
document.addEventListener('DOMContentLoaded', () => {
    // Tab Navigation
    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            // Remove active class from all buttons and panes
            tabButtons.forEach(btn => btn.classList.remove('active'));
            tabPanes.forEach(pane => pane.classList.remove('active'));
            
            // Add active class to clicked button and corresponding pane
            button.classList.add('active');
            const tabId = button.getAttribute('data-tab');
            document.getElementById(tabId).classList.add('active');
        });
    });
    
    // Chat Functionality
    chatInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendChatMessage();
        }
    });
    
    sendChatButton.addEventListener('click', sendChatMessage);
    clearConversationButton.addEventListener('click', clearConversation);
    
    // Alt Text Functionality
    imagePreview.addEventListener('click', () => imageUpload.click());
    uploadButton.addEventListener('click', () => imageUpload.click());
    
    imageUpload.addEventListener('change', handleImageUpload);
    generateAltTextButton.addEventListener('click', generateAltText);
    copyAltTextButton.addEventListener('click', copyAltTextToClipboard);
    
    // Tools Functionality
    callToolButton.addEventListener('click', callTool);
});

// Tab Functions
function showTab(tabId) {
    tabButtons.forEach(btn => {
        if (btn.getAttribute('data-tab') === tabId) {
            btn.classList.add('active');
        } else {
            btn.classList.remove('active');
        }
    });
    
    tabPanes.forEach(pane => {
        if (pane.id === tabId) {
            pane.classList.add('active');
        } else {
            pane.classList.remove('active');
        }
    });
}

// Chat Functions
async function sendChatMessage() {
    const message = chatInput.value.trim();
    if (message === '') return;
    
    // Add user message to conversation
    addMessageToConversation('user', message);
    chatInput.value = '';
    
    // Show loading
    showLoading();
    
    try {
        const response = await fetch(`${API_BASE_URL}/chat/stream`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-API-Key': API_KEY
            },
            body: JSON.stringify({
                provider: DEFAULT_PROVIDER,
                model: chatModel.value,
                prompt: message,
                max_tokens: parseInt(maxTokens.value),
                system_prompt: systemPrompt.value,
                conversation_id: conversationId,
                stream: true
            })
        });
        
        if (!response.ok) {
            throw new Error(`API request failed with status ${response.status}`);
        }
        
        // Create a new assistant message container
        const assistantMessageElem = document.createElement('div');
        assistantMessageElem.className = 'message assistant';
        
        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';
        
        const paragraph = document.createElement('p');
        messageContent.appendChild(paragraph);
        assistantMessageElem.appendChild(messageContent);
        conversationArea.appendChild(assistantMessageElem);
        
        // Scroll to bottom
        conversationArea.scrollTop = conversationArea.scrollHeight;
        
        // Read streaming response
        const reader = response.body.getReader();
        let assistantResponse = '';
        
        while (true) {
            const { done, value } = await reader.read();
            if (done) break;
            
            // Convert bytes to text
            const text = new TextDecoder().decode(value);
            const lines = text.split('\n').filter(line => line.trim());
            
            for (const line of lines) {
                try {
                    const data = JSON.parse(line);
                    
                    if (data.error) {
                        throw new Error(data.error);
                    }
                    
                    if (data.type === 'delta' && data.content) {
                        assistantResponse += data.content;
                        paragraph.textContent = assistantResponse;
                        // Scroll to bottom as content is added
                        conversationArea.scrollTop = conversationArea.scrollHeight;
                    } else if (typeof data === 'string') {
                        assistantResponse += data;
                        paragraph.textContent = assistantResponse;
                        conversationArea.scrollTop = conversationArea.scrollHeight;
                    }
                } catch (e) {
                    console.error('Error parsing streaming response:', e);
                }
            }
        }
    } catch (error) {
        console.error('Error sending chat message:', error);
        addMessageToConversation('system', `Error: ${error.message}`);
    } finally {
        hideLoading();
    }
}

function addMessageToConversation(role, content) {
    const messageElem = document.createElement('div');
    messageElem.className = `message ${role}`;
    
    const messageContent = document.createElement('div');
    messageContent.className = 'message-content';
    
    const paragraph = document.createElement('p');
    paragraph.textContent = content;
    messageContent.appendChild(paragraph);
    
    messageElem.appendChild(messageContent);
    conversationArea.appendChild(messageElem);
    
    // Scroll to bottom
    conversationArea.scrollTop = conversationArea.scrollHeight;
}

async function clearConversation() {
    try {
        // Call API to clear conversation
        const response = await fetch(`${API_BASE_URL}/chat/clear`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-API-Key': API_KEY
            },
            body: JSON.stringify({
                provider: DEFAULT_PROVIDER
            })
        });
        
        if (!response.ok) {
            throw new Error(`API request failed with status ${response.status}`);
        }
        
        // Clear conversation UI
        conversationArea.innerHTML = '';
        addMessageToConversation('system', 'Conversation cleared.');
        
        // Generate new conversation ID
        conversationId = 'test-' + Date.now();
    } catch (error) {
        console.error('Error clearing conversation:', error);
        addMessageToConversation('system', `Error: ${error.message}`);
    }
}

// Alt Text Functions
function handleImageUpload(event) {
    const file = event.target.files[0];
    if (!file) return;
    
    // Display preview
    const reader = new FileReader();
    reader.onload = function(e) {
        previewImage.src = e.target.result;
        previewImage.style.display = 'block';
        document.querySelector('.upload-placeholder').style.display = 'none';
    };
    reader.readAsDataURL(file);
    
    selectedFile = file;
    generateAltTextButton.disabled = false;
}

async function generateAltText() {
    if (!selectedFile) {
        altTextOutput.textContent = 'Please select an image first.';
        return;
    }
    
    // Show loading
    showLoading();
    
    try {
        const formData = new FormData();
        formData.append('image', selectedFile);
        formData.append('provider', DEFAULT_PROVIDER);
        formData.append('model', altModel.value);
        formData.append('prompt', altPrompt.value);
        formData.append('stream', 'false');
        
        const response = await fetch(`${API_BASE_URL}/alt/generate`, {
            method: 'POST',
            headers: {
                'X-API-Key': API_KEY
            },
            body: formData
        });
        
        if (!response.ok) {
            throw new Error(`API request failed with status ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.error) {
            throw new Error(data.error);
        }
        
        altTextOutput.textContent = data.alt_text;
        copyAltTextButton.disabled = false;
    } catch (error) {
        console.error('Error generating alt text:', error);
        altTextOutput.textContent = `Error: ${error.message}`;
    } finally {
        hideLoading();
    }
}

function copyAltTextToClipboard() {
    const text = altTextOutput.textContent;
    navigator.clipboard.writeText(text).then(
        () => {
            // Success feedback
            const originalText = copyAltTextButton.innerHTML;
            copyAltTextButton.innerHTML = '<i class="fas fa-check"></i> Copied!';
            setTimeout(() => {
                copyAltTextButton.innerHTML = originalText;
            }, 2000);
        },
        () => {
            alert('Failed to copy text to clipboard');
        }
    );
}

// Tools Functions
async function callTool() {
    const prompt = toolPrompt.value.trim();
    if (prompt === '') {
        toolOutput.textContent = 'Please enter a prompt.';
        return;
    }
    
    let tools;
    try {
        tools = JSON.parse(toolDefinitions.value);
    } catch (error) {
        toolOutput.textContent = `Error parsing tool definitions: ${error.message}`;
        return;
    }
    
    // Show loading
    showLoading();
    
    try {
        const response = await fetch(`${API_BASE_URL}/tools/call`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-API-Key': API_KEY
            },
            body: JSON.stringify({
                provider: DEFAULT_PROVIDER,
                model: toolModel.value,
                prompt: prompt,
                tools: tools
            })
        });
        
        if (!response.ok) {
            throw new Error(`API request failed with status ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.error) {
            throw new Error(data.error);
        }
        
        // Format the output
        let formattedOutput = `Model: ${data.model}\n\n`;
        formattedOutput += `Content:\n${data.content}\n\n`;
        
        if (data.tool_calls && data.tool_calls.length > 0) {
            formattedOutput += 'Tool Calls:\n';
            data.tool_calls.forEach((call, index) => {
                formattedOutput += `\nTool Call #${index + 1}:\n`;
                formattedOutput += `Name: ${call.name}\n`;
                formattedOutput += `Input: ${JSON.stringify(call.input, null, 2)}\n`;
            });
        }
        
        toolOutput.textContent = formattedOutput;
    } catch (error) {
        console.error('Error calling tool:', error);
        toolOutput.textContent = `Error: ${error.message}`;
    } finally {
        hideLoading();
    }
}

// Utility Functions
function showLoading() {
    loadingOverlay.classList.remove('hidden');
}

function hideLoading() {
    loadingOverlay.classList.add('hidden');
} 