import { PROMPT_TEMPLATES, DEFAULT_PROMPT, getPrompt } from './prompts.js';
import { patreon as patreonAPI, oauth as patreonOAuth } from 'https://cdn.jsdelivr.net/npm/patreon@0.3.0/+esm';
import { TTSHandler } from './tts.js';
import { ThemeManager } from './theme.js';

console.log('Initializing constants...');

const PATREON = {
    CLIENT_ID: 'mrqWf4Kz2qZ4UkMxUlkT5F8fCq5lJQBIo5UZnrMzrh6v4xan7Ssx1SzE0PVhdD9J',
    CLIENT_SECRET: 'YOUR_CLIENT_SECRET',
    REDIRECT_URI: 'https://api.assisted.space/alt/dev/index.html'
};

// Using a relative URL instead of absolute to handle different environments
const API_BASE_URL = 'https://api.assisted.space/v2';  // This will work with any domain
console.log('Using API base URL:', API_BASE_URL);

const CAMINA_KEY = 'pat_Uk4Z075Oo8RE5Po13rBUoEQNzr3dcKTNmBuf5Qtj1V6QZLiwAeZDaNzfNSLMIca8';
const CAMINA_HOPPER = '7345427862138912773';
const CAMINA_ALT = "7462296933429346310";
const CAMINA_TTS = "7463319430379470854";

// For diagnostic logging
const diagnosticLogs = [];
const originalConsoleLog = console.log;
const originalConsoleError = console.error;

// Override console methods to track diagnostic logs
console.log = function(...args) {
    originalConsoleLog.apply(console, args);
    diagnosticLogs.push({type: 'log', message: args.map(arg => 
        typeof arg === 'object' ? JSON.stringify(arg) : String(arg)
    ).join(' '), timestamp: new Date().toISOString()});
    updateDiagnosticPanel();
};

console.error = function(...args) {
    originalConsoleError.apply(console, args);
    diagnosticLogs.push({type: 'error', message: args.map(arg => 
        typeof arg === 'object' ? JSON.stringify(arg) : String(arg)
    ).join(' '), timestamp: new Date().toISOString()});
    updateDiagnosticPanel();
};

function updateDiagnosticPanel() {
    const panel = document.getElementById('diagnosticOutput');
    if (panel) {
        const logOutput = diagnosticLogs.map(log => 
            `${log.timestamp.split('T')[1].split('.')[0]} [${log.type.toUpperCase()}] ${log.message}`
        ).join('\n');
        panel.textContent = logOutput;
        panel.scrollTop = panel.scrollHeight;
    }
}

console.log('Constants initialized');

export class AltTextGenerator {
    constructor() {
        console.log('Initializing AltTextGenerator...');
        
        // Log the API URL being used for clarity
        console.log(`Using API server: ${API_BASE_URL}`);
        console.log(`API endpoint for images: ${API_BASE_URL}/alt/openai`);
        
        this.uploadArea = document.getElementById('uploadArea');
        this.fileInput = document.getElementById('fileInput');
        this.resultContainer = document.getElementById('resultContainer');
        this.uploadedImage = document.getElementById('uploadedImage');
        this.altTextDisplay = document.getElementById('altTextDisplay');
        this.streamingIndicator = document.querySelector('.streaming-indicator');
        this.progressBar = document.querySelector('.progress-fill');
        this.modelSelector = document.getElementById('modelSelector');
        this.retryButton = document.getElementById('retryButton');
        this.pasteButton = document.getElementById('pasteButton');
        this.pullToRefresh = document.querySelector('.pull-to-refresh');
        this.chatContainer = document.querySelector('.chat-container');
        this.tokenCount = 0;
        this.languageSelector = document.getElementById('languageSelector');
        this.globalRetryButton = document.getElementById('globalRetryButton');
        
        // Diagnostic panel elements
        this.diagnosticPanel = document.getElementById('diagnosticPanel');
        this.diagnosticOutput = document.getElementById('diagnosticOutput');
        this.showDiagnosticButton = document.getElementById('showDiagnosticButton');
        this.toggleDiagnosticButton = document.getElementById('toggleDiagnosticButton');

        // Initialize model selector and current model
        if (this.modelSelector) {
            console.log('Setting up model selector...');
            // Always set to Fast option and disable the selector
            this.modelSelector.value = "gpt-4o-mini-2024-07-18";
            this.modelSelector.disabled = true; // Disable model selection
            this.currentModel = "gpt-4o-mini-2024-07-18";
            // Clear any saved quality setting to ensure it doesn't override
            localStorage.removeItem('quality');
            console.log('Model hard-coded to gpt-4o-mini-2024-07-18');
        } else {
            console.error('Model selector not found in DOM');
        }

        // Load persisted settings
        if (this.promptSelector) {
            const savedOutputType = localStorage.getItem('outputType');
            if (savedOutputType) {
                this.promptSelector.value = savedOutputType;
            }
        }
        // Remove model selection from localStorage handling
        if (this.languageSelector) {
            const savedLanguage = localStorage.getItem('language');
            if (savedLanguage) {
                this.languageSelector.value = savedLanguage;
                this.currentLanguage = savedLanguage;
            }
        }
        
        // Detect browser and device type
        this.isChrome = this.isChromeBrowser();
        this.isMobile = this.isMobileDevice();
        
        // Handle paste button visibility and upload area text
        const desktopText = document.querySelector('.desktop-text');
        if (desktopText) {
            desktopText.textContent = 'Click, drop, or paste an image to generate alt text!';
        }
        
        // Show paste button on all devices
        if (this.pasteButton) {
            this.pasteButton.style.display = 'flex';
        }

        console.log('DOM elements initialized');

        this.LANGUAGE_INSTRUCTIONS = {
            en: "Respond in English",
            es: "Responde en Español",
            fr: "Répondez en Français",
            de: "Antworten Sie auf Deutsch",
            pt: "Responda em Português",
            nl: "Reageer in het Nederlands",
            sv: "Svara på Svenska",
            no: "Svar på Norsk",
            ko: "한국어로 답변해 주세요",
            zh: "请用中文回答",
            ja: "日本語で回答してください"
        };
        this.currentLanguage = 'en';
        this.FALLBACK_LANGUAGE = 'en';
        
        this.messages = [];
        this.md = window.markdownit({
            html: true,
            breaks: true,
            linkify: true,
            typographer: true
        });
        this.isResponding = false;
        this.currentFile = null;
        this.pullStartY = 0;
        this.pullMoveY = 0;
        this.pullRefreshThreshold = 80;
        this.isPulling = false;
        this.isRefreshing = false;
        this.promptSelector = document.getElementById('promptSelector');
        this.currentPrompt = PROMPT_TEMPLATES[DEFAULT_PROMPT];
        this.ttsSelector = document.getElementById('ttsSelector');
        this.ttsBotId = CAMINA_TTS;
        this.audioElement = new Audio();
        this.isProcessingTTS = false;

        console.log('Core properties initialized');

        this.scanContainer = document.getElementById('scanContainer');
        this.scanLine = document.getElementById('scanLine');

        this.patreonOAuthClient = patreonOAuth(PATREON.CLIENT_ID, PATREON.CLIENT_SECRET);
        this.patreonAPIClient = null;

        this.patreonLoginButton = document.getElementById('patreonLoginButton');
        this.retryButton = document.getElementById('retryButton');
        this.pasteButton = document.getElementById('pasteButton');
        this.pullToRefresh = document.querySelector('.pull-to-refresh');
        this.chatContainer = document.querySelector('.chat-container');
        this.languageSelector = document.getElementById('languageSelector');
        
        if (this.patreonLoginButton) {
            console.log('Setting up Patreon login button');
            this.patreonLoginButton.addEventListener('click', () => this.initiatePatreonLogin());
        }

        // Initialize TTS handler only if TTS elements exist
        if (document.getElementById('ttsContainer')) {
            this.ttsHandler = new TTSHandler();
            console.log('TTS handler initialized');
        } else {
            console.log('TTS functionality disabled');
        }

        // Initialize current prompt from prompt selector
        if (this.promptSelector) {
            const selectedPromptType = this.promptSelector.value || DEFAULT_PROMPT;
            const language = this.languageSelector ? this.languageSelector.value : 'en';
            this.currentPrompt = getPrompt(selectedPromptType, language);
            console.log('Initialized prompt:', selectedPromptType, 'in language:', language);
        }

        this.setupEventListeners();
        console.log('Event listeners setup complete');

        console.log('AltTextGenerator initialization complete');

        // Update paste button visibility based on browser
        if (this.pasteButton) {
            if (this.isChrome && !this.isMobile) {
                this.pasteButton.setAttribute('data-chrome-desktop', 'true');
            }
        }

        // Initialize toast container
        this.initializeToastContainer();

        document.addEventListener('DOMContentLoaded', () => {
            window.themeManager = new ThemeManager();
        });

        // Load persisted user settings from localStorage
        if (this.promptSelector) {
            const savedOutputType = localStorage.getItem('outputType');
            if (savedOutputType) {
                this.promptSelector.value = savedOutputType;
            }
        }
        if (this.languageSelector) {
            const savedLanguage = localStorage.getItem('language');
            if (savedLanguage) {
                this.languageSelector.value = savedLanguage;
                this.currentLanguage = savedLanguage;
            }
        }
        if (this.ttsSelector) {
            const savedTTS = localStorage.getItem('tts');
            if (savedTTS) {
                this.ttsSelector.value = savedTTS;
            }
        }
        // Update the current prompt based on loaded settings
        if (this.promptSelector && this.languageSelector) {
            this.currentPrompt = getPrompt(this.promptSelector.value, this.languageSelector.value);
        }
    }

    initializeToastContainer() {
        const container = document.createElement('div');
        container.className = 'toast-container';
        document.body.appendChild(container);
        this.toastContainer = container;
    }

    showToast(message, type = 'info', duration = 3000) {
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        
        // Add appropriate icon based on type
        let icon = '';
        switch(type) {
            case 'success':
                icon = '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41L9 16.17z"/></svg>';
                break;
            case 'error':
                icon = '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"/></svg>';
                break;
            case 'info':
                icon = '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-6h2v6zm0-8h-2V7h2v2z"/></svg>';
                break;
        }
        
        toast.innerHTML = `
            ${icon}
            <span class="message" role="alert" aria-live="polite">${message}</span>
            <button class="close-button" aria-label="Dismiss notification">
                <svg viewBox="0 0 24 24" fill="currentColor" width="20" height="20">
                    <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12 19 6.41z"/>
                </svg>
            </button>
        `;

        // Add close button functionality
        const closeButton = toast.querySelector('.close-button');
        closeButton.addEventListener('click', () => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300);
        });

        this.toastContainer.appendChild(toast);
        // Trigger reflow for animation
        toast.offsetHeight;
        toast.classList.add('show');

        // Auto remove after duration
        setTimeout(() => {
            if (toast.parentElement) {
                toast.classList.remove('show');
                setTimeout(() => toast.remove(), 300);
            }
        }, duration);
    }

    isChromeBrowser() {
        const userAgent = navigator.userAgent.toLowerCase();
        const isChromium = userAgent.includes('chrome') || userAgent.includes('chromium');
        const isSafari = userAgent.includes('safari') && !userAgent.includes('chrome');
        return isChromium && !isSafari;
    }

    isMobileDevice() {
        return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent) 
            || (navigator.maxTouchPoints && navigator.maxTouchPoints > 2);
    }

    async handlePaste(event) {
        console.log('Handling paste event');
        try {
            // Handle clipboard event data first (most reliable)
            if (event?.clipboardData?.items) {
                console.log('Checking clipboard event data');
                const items = event.clipboardData.items;
                for (const item of items) {
                    if (item.type.indexOf('image/') !== -1) {
                        const file = item.getAsFile();
                        if (file) {
                            this.showToast('Image pasted successfully', 'success');
                            await this.handleFile(file);
                            return;
                        }
                    }
                }
            }

            // Try modern Clipboard API as fallback
            if (navigator.clipboard?.read) {
                console.log('Trying Clipboard API');
                try {
                    const clipboardItems = await navigator.clipboard.read();
                    for (const clipboardItem of clipboardItems) {
                        for (const type of clipboardItem.types) {
                            if (type.startsWith('image/')) {
                                const blob = await clipboardItem.getType(type);
                                const file = new File([blob], 'pasted-image.png', { type });
                                await this.handleFile(file);
                                return;
                            }
                        }
                    }
                } catch (clipboardError) {
                    console.log('Clipboard API failed:', clipboardError);
                }
            }

            // If we're on mobile and no image was found, show file picker
            if (this.isMobile) {
                console.log('No image found in clipboard, showing file picker on mobile');
                this.fileInput.click();
            }

            // If no image found
            this.showToast('No image found in clipboard', 'error');
        } catch (error) {
            console.error('Paste error:', error);
            this.showToast('Failed to paste image', 'error');
            if (this.isMobile) {
                this.fileInput.click();
            }
        }
    }

    setupEventListeners() {
        console.log('Setting up event listeners...');
        
        // Diagnostic panel toggle
        if (this.showDiagnosticButton) {
            this.showDiagnosticButton.addEventListener('click', () => {
                if (this.diagnosticPanel) {
                    this.diagnosticPanel.style.display = 'block';
                    updateDiagnosticPanel();
                }
            });
        }
        
        if (this.toggleDiagnosticButton) {
            this.toggleDiagnosticButton.addEventListener('click', () => {
                if (this.diagnosticPanel) {
                    this.diagnosticPanel.style.display = 'none';
                }
            });
        }
        
        // Setup for testing
        document.addEventListener('keydown', (e) => {
            // Ctrl+Alt+D to toggle diagnostic panel
            if (e.ctrlKey && e.altKey && e.key === 'd') {
                if (this.diagnosticPanel) {
                    const currentDisplay = this.diagnosticPanel.style.display;
                    this.diagnosticPanel.style.display = currentDisplay === 'none' ? 'block' : 'none';
                    updateDiagnosticPanel();
                }
            }
        });
        
        if (this.uploadArea && this.fileInput) {
            ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
                this.uploadArea.addEventListener(eventName, (e) => {
                    e.preventDefault();
                    e.stopPropagation();
                });
            });

            this.uploadArea.addEventListener('drop', (e) => {
                console.log('File dropped');
                const files = e.dataTransfer.files;
                if (files.length > 0) {
                    this.handleFile(files[0]);
                }
            });

            this.fileInput.addEventListener('change', (e) => {
                console.log('File selected via input');
                if (e.target.files.length > 0) {
                    this.handleFile(e.target.files[0]);
                }
            });

            this.uploadArea.addEventListener('click', (e) => {
                console.log('Upload area clicked');
                if (!e.target.closest('#pasteButton')) {
                    this.fileInput.click();
                }
            });
        }

        // Add paste event listener to document
        document.addEventListener('paste', (e) => {
            console.log('Paste event detected');
            this.handlePaste(e);
        });
        
        if (this.pasteButton) {
            this.pasteButton.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                if (this.isMobile) {
                    this.handlePaste();
                }
            });
        }

        const copyButton = document.getElementById('copyButton');
        if (copyButton && this.altTextDisplay) {
            copyButton.addEventListener('click', async (e) => {
                e.stopPropagation();
                if (!this.altTextDisplay.textContent) return;

                copyButton.classList.add('loading');
                try {
                    await navigator.clipboard.writeText(this.altTextDisplay.textContent);
                    copyButton.classList.remove('loading');
                    copyButton.classList.add('success');
                    this.showToast('Text copied to clipboard', 'success');
                    setTimeout(() => copyButton.classList.remove('success'), 1500);
                } catch (error) {
                    console.error('Copy failed:', error);
                    copyButton.classList.remove('loading');
                    copyButton.classList.add('error');
                    this.showToast('Failed to copy text', 'error');
                    setTimeout(() => copyButton.classList.remove('error'), 1500);
                }
            });
        }

        if (this.promptSelector) {
            this.promptSelector.addEventListener('change', (e) => {
                localStorage.setItem('outputType', e.target.value);
                console.log('Prompt changed to:', e.target.value);
                const language = this.languageSelector?.value || 'en';
                this.currentPrompt = getPrompt(e.target.value, language);
                console.log('Updated prompt template:', this.currentPrompt);
                // If there's already an image processed, allow regeneration
                if (this.currentFile) {
                    this.retryButton.classList.remove('hidden');
                }
            });
        }

        if (this.languageSelector) {
            this.languageSelector.addEventListener('change', (e) => {
                localStorage.setItem('language', e.target.value);
                console.log('Language changed to:', e.target.value);
                this.currentLanguage = e.target.value;
                this.currentPrompt = getPrompt(this.promptSelector.value, this.currentLanguage);
            });
        }

        if (this.globalRetryButton) {
            this.globalRetryButton.addEventListener('click', () => {
                console.log('Global retry button clicked');
                window.location.reload();
            });
        }

        if (this.retryButton) {
            this.retryButton.addEventListener('click', (e) => {
                console.log('Retry button clicked');
                if (this.currentFile) {
                    this.retryButton.style.display = 'none';
                    this.handleFile(this.currentFile);
                }
                e.stopPropagation();
            });
        }

        if (this.altTextDisplay?.parentElement) {
            this.altTextDisplay.parentElement.addEventListener('click', (e) => {
                if (!e.target.closest('.icon-button') && this.altTextDisplay.textContent) {
                    console.log('Copying alt text to clipboard');
                    navigator.clipboard.writeText(this.altTextDisplay.textContent);
                    this.showCopyConfirmation();
                }
            });
        }

        if (this.ttsSelector) {
            this.ttsSelector.addEventListener('change', (e) => {
                localStorage.setItem('tts', e.target.value);
                console.log('TTS voice changed to:', e.target.value);
                if (e.target.value !== 'none' && this.altTextDisplay.textContent) {
                    this.ttsHandler.handleTTS(this.altTextDisplay.textContent, e.target.value, this.makeApiCall.bind(this), CAMINA_KEY, API_BASE_URL, CAMINA_TTS);
                }
            });
        }

        console.log('Event listeners setup complete');
    }

    updateTokenCount() {
        console.log('Updating token count:', this.tokenCount);
        const tokenCountElement = document.querySelector('.token-count');
        if (tokenCountElement) {
            tokenCountElement.textContent = `${this.tokenCount}`;
        }
    }

    processMessageContent(content) {
        console.log('Processing message content');
        let cleanContent = content
            .replace(/^[\s-]+|[\s-]+$/g, '')
            .replace(/^Alt text:\s*/i, '');
        
        const parsedContent = this.md.render(cleanContent);
        
        const sanitizedContent = DOMPurify.sanitize(parsedContent);
        
        const container = document.createElement("div");
        container.className = "markdown-body message-content";
        container.innerHTML = sanitizedContent;

        container.querySelectorAll("pre code").forEach((block) => {
            hljs.highlightElement(block);
        });

        return container.outerHTML;
    }

    async makeApiCall(content, base64Image, botId = null) {
        console.log('Making API call with:', { 
            hasContent: !!content,
            hasImage: !!base64Image,
            botId
        });

        // Add AbortController for timeout handling
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 30000); // 30 second timeout
        
        try {
            // Handle TTS requests if applicable
            if (botId === this.ttsBotId) {
                const response = await fetch(`${API_BASE_URL}/alt/openai`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Accept': 'text/event-stream'
                    },
                    body: JSON.stringify({
                        bot_id: CAMINA_TTS,
                        message: content,
                        stream: true,
                        user_id: CAMINA_HOPPER
                    }),
                    signal: controller.signal
                });
                clearTimeout(timeoutId);
                return response;
            }

            // Determine the current language (default to English)
            const language = this.languageSelector ? this.languageSelector.value : 'en';
            console.log('Using language:', language);

            // If we have an image, use direct file upload instead of base64
            if (base64Image) {
                console.log('Using file upload method for image (OpenAI)');
                
                // Get the appropriate prompt template based on user selection
                const promptType = this.promptSelector ? this.promptSelector.value : DEFAULT_PROMPT;
                const promptConfig = getPrompt(promptType, language);
                
                // Create FormData for the request
                const formData = new FormData();
                
                // Log file info for debugging
                console.log('File details:', {
                    name: this.currentFile.name,
                    type: this.currentFile.type,
                    size: this.currentFile.size
                });
                
                // Add form data
                formData.append('image', this.currentFile);
                formData.append('model', 'gpt-4o-mini-2024-07-18');
                formData.append('prompt', promptConfig.user);
                formData.append('stream', 'true');
                
                console.log('Sending form data for OpenAI:', {
                    model: 'gpt-4o-mini-2024-07-18',
                    promptLength: promptConfig.user.length,
                    stream: true
                });
                
                // Send the request with FormData instead of JSON
                const url = `${API_BASE_URL}/alt/openai`;
                console.log('Request URL:', url);
                
                const response = await fetch(url, {
                    method: 'POST',
                    body: formData,
                    signal: controller.signal
                });
                clearTimeout(timeoutId);
                return response;
            }

            // For text-only requests (should not happen in this app)
            console.log('Using normal quality path (text only)');
            const promptConfig = getPrompt(this.promptSelector?.value || DEFAULT_PROMPT, language);
            const requestBody = {
                model: "gpt-4o-mini-2024-07-18",
                messages: [
                    { role: "system", content: promptConfig.system },
                    { role: "user", content: promptConfig.user }
                ],
                stream: true
            };

            console.log('Sending API request:', {
                model: "gpt-4o-mini-2024-07-18",
                hasSystemMessage: !!requestBody.messages[0].content,
                hasUserMessage: !!requestBody.messages[1].content
            });

            const response = await fetch(`${API_BASE_URL}/alt/openai`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'text/event-stream'
                },
                body: JSON.stringify(requestBody),
                signal: controller.signal
            });
            clearTimeout(timeoutId);
            return response;
        } catch (error) {
            clearTimeout(timeoutId);
            throw error;
        }
    }
    
    // Helper function to convert File to base64
    fileToBase64(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = () => {
                // Extract base64 data from the result
                // Format is like: "data:image/jpeg;base64,/9j/4AAQSkZJRg..."
                const base64String = reader.result.split(',')[1];
                resolve(base64String);
            };
            reader.onerror = error => reject(error);
            reader.readAsDataURL(file);
        });
    }

    validateLanguageSupport() {
        console.log('Validating language support for:', this.currentLanguage);
        if (!this.LANGUAGE_INSTRUCTIONS[this.currentLanguage]) {
            console.log('Falling back to:', this.FALLBACK_LANGUAGE);
            this.currentLanguage = this.FALLBACK_LANGUAGE;
        }
    }

    async analyzeImage(base64Content, context) {
        console.log('Analyzing image...');
        this.validateLanguageSupport();

        try {
            // We'll keep messages for compatibility but they're not used in the FormData approach
            this.messages = [{
                role: "system",
                content: this.currentPrompt.system
            }, {
                role: "user",
                content: this.currentPrompt.user
            }];

            // Use the non-streaming approach directly rather than trying streaming first
            console.log('Using non-streaming approach for more reliable results');
            
            // Create FormData for the request
            const formData = new FormData();
            formData.append('image', this.currentFile);
            formData.append('model', 'gpt-4o-mini-2024-07-18');
            formData.append('prompt', this.currentPrompt.user);
            formData.append('stream', 'false'); // Explicitly request non-streaming
            
            console.log('File details:', {
                name: this.currentFile.name,
                type: this.currentFile.type,
                size: this.currentFile.size
            });
            
            // Use AbortController for timeout
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 30000); // 30 second timeout
            
            try {
                // Ensure we're using the full absolute URL
                const url = `${API_BASE_URL}/alt/openai`;
                console.log('Request URL:', url);
                
                const response = await fetch(url, {
                    method: 'POST',
                    body: formData,
                    signal: controller.signal
                });
                clearTimeout(timeoutId);
                
                if (!response.ok) {
                    const errorText = await response.text();
                    console.error(`API Error (${response.status}): ${errorText}`);
                    throw new Error(`API Error (${response.status}): ${errorText}`);
                }
                
                // Parse the JSON response
                const result = await response.json();
                console.log('Non-streaming response:', result);
                
                // Update UI immediately
                document.querySelector('.alt-text-container').style.display = 'block';
                this.streamingIndicator.style.display = 'none';
                this.progressBar.style.width = '100%';
                
                // Check for the alt_text field or content in the response
                if (result.alt_text) {
                    this.altTextDisplay.innerHTML = this.processMessageContent(result.alt_text);
                    return result.alt_text;
                } else if (result.content) {
                    this.altTextDisplay.innerHTML = this.processMessageContent(result.content);
                    return result.content;
                } else if (result.message && result.message.content) {
                    this.altTextDisplay.innerHTML = this.processMessageContent(result.message.content);
                    return result.message.content;
                } else {
                    // Create a readable message from any available content
                    let content = JSON.stringify(result);
                    this.altTextDisplay.innerHTML = this.processMessageContent(content);
                    throw new Error('No expected content fields found in response');
                }
                
            } catch (nonStreamingError) {
                clearTimeout(timeoutId);
                console.error('Non-streaming approach failed:', nonStreamingError);
                throw nonStreamingError;
            }
        } catch (error) {
            console.error('Image analysis error:', error);
            this.showToast(`Error: ${error.message || 'Unknown error'}`, 'error');
            return `Error: ${error.message || 'Unknown error'}. Please try again.`;
        }
    }

    async resizeImage(file, maxDimension = 2048) {
        console.log('Resizing image...');
        return new Promise((resolve) => {
            const img = new Image();
            img.onload = () => {
                const canvas = document.createElement('canvas');
                let width = img.width;
                let height = img.height;
                
                if (width > height && width > maxDimension) {
                    height = Math.round((height * maxDimension) / width);
                    width = maxDimension;
                } else if (height > maxDimension) {
                    width = Math.round((width * maxDimension) / height);
                    height = maxDimension;
                }

                canvas.width = width;
                canvas.height = height;
                
                const ctx = canvas.getContext('2d');
                ctx.drawImage(img, 0, 0, width, height);
                
                const base64 = canvas.toDataURL('image/jpeg', 0.9);
                console.log('Image resized successfully');
                resolve(base64.split('base64,')[1]);
            };
            img.src = URL.createObjectURL(file);
        });
    }

    async handleFile(file) {
        console.log('Handling file:', file?.name);
        
        // Reset diagnostics
        diagnosticLogs.length = 0;
        updateDiagnosticPanel();
        
        // Check file size
        const maxSize = 10 * 1024 * 1024; // 10MB
        if (file.size > maxSize) {
            this.showToast('File size exceeds 10MB limit', 'error');
            return;
        }

        // Check file type
        const supportedTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp', 'image/heic', 'image/heif'];
        if (!supportedTypes.includes(file.type)) {
            this.showToast('Unsupported file format. Please upload JPG, PNG, GIF, WEBP, or HEIC', 'error');
            return;
        }

        try {
            this.messages = [];
            this.currentFile = file;
            this.tokenCount = 0;
            this.updateTokenCount();
            
            this.streamingIndicator.style.display = 'flex';
            this.resultContainer.style.display = 'block';
            this.uploadArea.style.display = 'none';
            this.fileInput.style.display = 'none';
            this.retryButton.classList.add('hidden');
            document.getElementById('copyButton').classList.add('hidden');
            document.querySelector('.progress-bar').style.display = 'block';
            this.progressBar.style.width = '0%';
            this.altTextDisplay.textContent = '';
            document.querySelector('.alt-text-container').style.display = 'none';

            const imageUrl = URL.createObjectURL(file) + '#' + new Date().getTime();
            this.uploadedImage.src = imageUrl;
            this.uploadedImage.style.display = 'block';

            this.animateProgress(0, 20, 800);

            this.showToast('Processing image...', 'info');
            
            try {
                // No need for base64 encoding anymore, as we're using direct file upload
                const description = await this.analyzeImage(null, "detailed");
                
                this.animateProgress(90, 100, 400);

                setTimeout(() => {
                    // Show all controls together
                    document.querySelector('.alt-text-container').style.display = 'block';
                    
                    // Reset button states
                    const copyButton = document.getElementById('copyButton');
                    const retryButton = document.getElementById('retryButton');
                    const globalRetryButton = document.getElementById('globalRetryButton');
                    
                    // Ensure all buttons start hidden
                    copyButton.classList.add('hidden');
                    retryButton.classList.add('hidden');
                    globalRetryButton.classList.add('hidden');
                    
                    if (this.altTextDisplay) {
                        this.altTextDisplay.innerHTML = this.processMessageContent(description);
                        
                        // Only show buttons if we have actual content
                        if (this.altTextDisplay.textContent.trim() && 
                            this.altTextDisplay.textContent.trim() !== 'No description available') {
                            // Show copy button first
                            copyButton.classList.remove('hidden');
                            // Show other buttons after a slight delay
                            setTimeout(() => {
                                retryButton.classList.remove('hidden');
                                globalRetryButton.classList.remove('hidden');
                            }, 500);
                        } else {
                            // If no content or error, just show retry buttons
                            globalRetryButton.classList.remove('hidden');
                            this.showToast('Unable to generate alt text. Please try again.', 'error');
                        }
                    }
                    
                    document.querySelector('.progress-bar').style.display = 'none';
                    this.streamingIndicator.style.display = 'none';
                }, 500);
            } catch (error) {
                console.error('Error processing image:', error);
                this.streamingIndicator.style.display = 'none';
                this.progressBar.style.width = '100%';
                document.querySelector('.progress-bar').style.display = 'none';
                
                // Show error message in alt text display
                document.querySelector('.alt-text-container').style.display = 'block';
                this.altTextDisplay.innerHTML = this.processMessageContent('Error processing image. Please try again.');
                
                // Show just the global retry button
                document.getElementById('globalRetryButton').classList.remove('hidden');
                
                this.showToast('Error processing image: ' + (error.message || 'Unknown error'), 'error');
            }
        } catch (error) {
            console.error('File handling error:', error);
            this.showToast('Error processing image: ' + (error.message || 'Unknown error'), 'error');
            
            // Reset UI to allow retry
            document.getElementById('globalRetryButton').classList.remove('hidden');
            this.streamingIndicator.style.display = 'none';
            document.querySelector('.progress-bar').style.display = 'none';
        }
    }

    animateProgress(start, end, duration = 500) {
        console.log('Animating progress:', start, 'to', end);
        const startTime = performance.now();
        const animate = (currentTime) => {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            
            const current = start + (end - start) * this.easeInOutQuart(progress);
            this.progressBar.style.width = `${current}%`;
            
            if (progress < 1) {
                requestAnimationFrame(animate);
            }
        };
        requestAnimationFrame(animate);
    }

    easeInOutQuart(x) {
        return x < 0.5 ? 8 * x * x * x * x : 1 - Math.pow(-2 * x + 2, 4) / 2;
    }

    showCopyConfirmation() {
        console.log('Showing copy confirmation');
        this.showToast('Text copied to clipboard', 'success');
    }

    showRetryButton() {
        console.log('Showing retry button');
        const retryButton = document.getElementById('retryButton');
        if (retryButton) {
            retryButton.classList.remove('hidden');
        }
    }

    setupTTSControls() {
        console.log('Setting up TTS controls');
        const ttsControl = document.getElementById('ttsControl');
        const ttsAudio = document.getElementById('ttsAudio');
        
        const newAudio = ttsAudio.cloneNode();
        ttsAudio.parentNode.replaceChild(newAudio, ttsAudio);
        
        // Add loading state handling
        const updateButtonState = (state) => {
            const buttonText = ttsControl.querySelector('.button-text');
            const loadingSpinner = ttsControl.querySelector('.tts-loading-spinner');
            
            switch(state) {
                case 'loading':
                    loadingSpinner.classList.remove('hidden');
                    buttonText.textContent = 'Generating Audio...';
                    break;
                case 'playing':
                    loadingSpinner.classList.add('hidden');
                    buttonText.textContent = 'Pause Audio';
                    break;
                case 'paused':
                case 'ended':
                    loadingSpinner.classList.add('hidden');
                    buttonText.textContent = 'Play Audio';
                    break;
                case 'error':
                    loadingSpinner.classList.add('hidden');
                    buttonText.textContent = 'Error';
                    break;
            }
        };
        
        ttsControl.addEventListener('click', async () => {
            try {
                if (newAudio.paused) {
                    await newAudio.play();
                    this.showToast('Playing audio description', 'info');
                    // Toggle icons and update text
                    ttsControl.querySelector('.play-icon').classList.remove('active');
                    ttsControl.querySelector('.pause-icon').classList.add('active');
                    ttsControl.querySelector('.error-icon').classList.remove('active');
                    updateButtonState('playing');
                } else {
                    newAudio.pause();
                    this.showToast('Audio paused', 'info');
                    // Toggle icons and update text
                    ttsControl.querySelector('.pause-icon').classList.remove('active');
                    ttsControl.querySelector('.play-icon').classList.add('active');
                    updateButtonState('paused');
                }
            } catch (error) {
                console.error('TTS playback error:', error);
                this.showToast('Failed to play audio', 'error');
                // Update error state
                ttsControl.querySelector('.error-icon').classList.add('active');
                ttsControl.querySelector('.pause-icon').classList.remove('active');
                ttsControl.querySelector('.play-icon').classList.remove('active');
                updateButtonState('error');
            }
        });

        newAudio.addEventListener('play', () => {
            console.log('Audio started playing');
            updateButtonState('playing');
        });
        
        newAudio.addEventListener('pause', () => {
            console.log('Audio paused');
            updateButtonState('paused');
        });
        
        newAudio.addEventListener('ended', () => {
            console.log('Audio playback ended');
            // Reset to play icon and text
            ttsControl.querySelector('.pause-icon').classList.remove('active');
            ttsControl.querySelector('.play-icon').classList.add('active');
            updateButtonState('ended');
        });
        
        newAudio.addEventListener('error', () => {
            console.error('Audio playback error');
            updateButtonState('error');
        });
        
        return newAudio;
    }

    initiatePatreonLogin() {
        console.log('Initiating Patreon login');
        const state = crypto.randomUUID();
        localStorage.setItem('oauth_state', state);
        
        const authUrl = this.patreonOAuthClient.getAuthorizationUrl({
            redirect_uri: PATREON.REDIRECT_URI,
            scope: 'identity identity.memberships',
            state: state
        });
        
        window.location.href = authUrl;
    }

    handlePatreonCallback(code) {
        console.log('Handling Patreon callback');
        try {
            const urlParams = new URLSearchParams(window.location.search);
            const state = urlParams.get('state');
            const storedState = localStorage.getItem('oauth_state');
            
            if (!state || state !== storedState) {
                console.error('Invalid OAuth state');
                throw new Error('Invalid OAuth state');
            }

            window.history.replaceState({}, '', window.location.pathname);
            
            const { store } = this.patreonAPIClient('/current_user?include=memberships');
            const user = store.findAll('user')[0];
            const memberships = store.findAll('member');

            this.displaySubscriptionStatus(user, memberships);
        } catch (error) {
            console.error('Patreon callback error:', error);
            window.location.href = 'https://www.patreon.com/c/lukeslp/membership';
        }
    }

    displaySubscriptionStatus(user, memberships) {
        console.log('Displaying subscription status');
        const hasActivePaidMembership = memberships.some(m => 
            m.patron_status === 'active_patron' &&
            m.pledge && 
            m.pledge.amount_cents > 0 &&
            m.pledge.pledge_status === 'active'
        );

        if (hasActivePaidMembership) {
            console.log('Active paid membership found');
            window.location.href = 'https://actuallyusefulai.com/members/alt/index.html';
        } else {
            console.log('No active paid membership');
            window.location.href = 'https://www.patreon.com/c/lukeslp/membership';
        }
    }

    buildPrompt(command = null) {
        console.log('Building prompt with command:', command);
        const promptType = this.promptSelector?.value || DEFAULT_PROMPT;
        const language = this.languageSelector?.value || 'en';
        const promptConfig = getPrompt(promptType, language);
        return command ? `${promptConfig.system}\n\n${promptConfig.user}\n\n${command}` : `${promptConfig.system}\n\n${promptConfig.user}`;
    }
} 