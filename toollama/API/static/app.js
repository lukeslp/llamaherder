// Constants
const API_BASE_URL = window.location.hostname === 'localhost' ? 'http://localhost:8000/v2' : 'https://ai.assisted.space/v2';
const MAX_PROMPT_LENGTH = 1000;

// API endpoint for image generation
const GENERATE_URL = `${API_BASE_URL}/generate`;

// Provider-specific models
const PROVIDER_MODELS = {
    openai: [
        { id: 'dall-e-3', name: 'DALL-E 3' },
        { id: 'dall-e-2', name: 'DALL-E 2' }
    ],
    xai: [
        { id: 'grok-2-image', name: 'Grok-2-Image' }
    ],
    gemini: [
        { id: 'gemini-2.0-flash-exp-image-generation', name: 'Gemini 2.0 Flash' },
        { id: 'gemini-1.5-flash-image-generation', name: 'Gemini 1.5 Flash' }
    ]
};

// DOM Elements
const elements = {
    form: document.getElementById('image-form'),
    provider: document.getElementById('provider'),
    modelSelect: document.getElementById('model-select'),
    prompt: document.getElementById('prompt'),
    promptCounter: document.getElementById('prompt-counter'),
    clearPrompt: document.getElementById('clear-prompt'),
    generateBtn: document.getElementById('generate-btn'),
    loadingIndicator: document.getElementById('loading-indicator'),
    resultContainer: document.getElementById('result-container'),
    resultImage: document.getElementById('result-image'),
    placeholder: document.getElementById('placeholder'),
    errorDisplay: document.getElementById('error-display'),
    errorMessage: document.getElementById('error-message'),
    resultControls: document.getElementById('result-controls'),
    downloadBtn: document.getElementById('download-btn'),
    retryBtn: document.getElementById('retry-btn'),
    newPromptBtn: document.getElementById('new-prompt-btn'),
    
    // Server status elements
    statusIndicator: document.getElementById('status-indicator'),
    statusText: document.getElementById('status-text'),
    localDevInstructions: document.getElementById('local-dev-instructions'),
    
    // Provider-specific option containers
    providerOptions: document.querySelectorAll('.provider-options'),
    openaiOptions: document.querySelectorAll('.openai-options'),
    xaiOptions: document.querySelectorAll('.xai-options'),
    geminiOptions: document.querySelectorAll('.gemini-options'),
    
    // Additional form fields
    quality: document.getElementById('quality'),
    style: document.getElementById('style'),
    size: document.getElementById('size')
};

// State management
let state = {
    currentProvider: 'openai',
    currentModel: '',
    currentPrompt: '',
    imageUrl: null,
    isGenerating: false,
    lastRequest: null,
    downloadFilename: 'generated-image.png',
};

// Initialize the application
async function init() {
    // Check API connectivity first
    await checkApiConnectivity();
    
    // Set initial provider and populate models
    updateProviderOptions(elements.provider.value);
    populateModels(elements.provider.value);
    
    // Set up event listeners
    setupEventListeners();
    
    // Initialize prompt counter
    updatePromptCounter();
    
    console.log('Image Generator initialized');
}

// Setup event listeners
function setupEventListeners() {
    // Form submission
    elements.form.addEventListener('submit', handleFormSubmit);
    
    // Provider change
    elements.provider.addEventListener('change', (e) => {
        updateProviderOptions(e.target.value);
        populateModels(e.target.value);
    });
    
    // Prompt input
    elements.prompt.addEventListener('input', updatePromptCounter);
    
    // Clear prompt button
    elements.clearPrompt.addEventListener('click', () => {
        elements.prompt.value = '';
        updatePromptCounter();
    });
    
    // Download button
    elements.downloadBtn.addEventListener('click', downloadImage);
    
    // Retry button
    elements.retryBtn.addEventListener('click', regenerateImage);
    
    // New prompt button
    elements.newPromptBtn.addEventListener('click', resetForm);
    
    // Temperature slider
    const temperatureSlider = document.getElementById('temperature');
    const temperatureValue = document.getElementById('temperature-value');
    if (temperatureSlider && temperatureValue) {
        temperatureSlider.addEventListener('input', (e) => {
            temperatureValue.textContent = e.target.value;
        });
    }
}

// Update provider-specific options
function updateProviderOptions(provider) {
    state.currentProvider = provider;
    
    // Hide all provider-specific options first
    elements.providerOptions.forEach(el => {
        el.style.display = 'none';
    });
    
    // Show provider-specific options based on selected provider
    switch (provider) {
        case 'openai':
            elements.openaiOptions.forEach(el => {
                el.style.display = 'block';
            });
            // Set default model for OpenAI
            populateModels('openai');
            break;
        case 'xai':
            elements.xaiOptions.forEach(el => {
                el.style.display = 'block';
            });
            // For X.AI, set the model directly since there's only one option
            state.currentModel = 'grok-2-image';
            elements.modelSelect.value = 'grok-2-image';
            break;
        case 'gemini':
            elements.geminiOptions.forEach(el => {
                el.style.display = 'block';
            });
            // For Gemini, always use 2.0 Flash model
            state.currentModel = 'gemini-2.0-flash-exp-image-generation';
            elements.modelSelect.value = 'gemini-2.0-flash-exp-image-generation';
            break;
    }
}

// Populate model dropdown based on provider
function populateModels(provider) {
    // Clear existing options
    elements.modelSelect.innerHTML = '';
    
    // Get models for the selected provider
    const models = PROVIDER_MODELS[provider] || [];
    
    // Add options to select
    models.forEach(model => {
        const option = document.createElement('option');
        option.value = model.id;
        option.textContent = model.name;
        elements.modelSelect.appendChild(option);
    });
    
    // Set default selection
    if (models.length > 0) {
        elements.modelSelect.value = models[0].id;
        state.currentModel = models[0].id;
    }
}

// Update the prompt character counter
function updatePromptCounter() {
    const length = elements.prompt.value.length;
    elements.promptCounter.textContent = `${length}/${MAX_PROMPT_LENGTH}`;
    
    // Update visual feedback based on length
    if (length > MAX_PROMPT_LENGTH) {
        elements.promptCounter.style.color = 'var(--error-color)';
    } else {
        elements.promptCounter.style.color = 'var(--light-text)';
    }
}

// Handle form submission
async function handleFormSubmit(e) {
    e.preventDefault();
    
    // Get form data
    const formData = new FormData(elements.form);
    const prompt = formData.get('prompt');
    const provider = formData.get('provider');
    let model = formData.get('model');
    
    // Validate prompt length
    if (prompt.length === 0) {
        showError('Please enter a prompt');
        return;
    }
    
    if (prompt.length > MAX_PROMPT_LENGTH) {
        showError(`Prompt is too long (max ${MAX_PROMPT_LENGTH} characters)`);
        return;
    }
    
    // Force specific models for providers with fixed options
    if (provider === 'xai') {
        model = 'grok-2-image';
    } else if (provider === 'gemini') {
        model = 'gemini-2.0-flash-exp-image-generation';
    }
    
    // Save current state
    state.currentPrompt = prompt;
    state.currentProvider = provider;
    state.currentModel = model;
    
    // Create request object with common parameters
    const requestData = {
        provider: provider,
        prompt: prompt,
        response_format: formData.get('response_format') || 'url'
    };
    
    // Add model parameter for all providers
    requestData.model = model;
    
    // Add provider-specific parameters
    switch (provider) {
        case 'openai':
            // Only add quality and style for DALL-E 3
            if (model === 'dall-e-3') {
                requestData.quality = formData.get('quality');
                requestData.style = formData.get('style');
            }
            
            // Add size based on model
            if (model === 'dall-e-2') {
                requestData.size = '1024x1024'; // DALL-E 2 only supports square
            } else {
                requestData.size = formData.get('size');
            }
            
            // Handle number of images based on model
            if (model === 'dall-e-3') {
                requestData.n = 1; // DALL-E 3 only supports single image
            } else {
                requestData.n = parseInt(formData.get('n') || '1', 10);
            }
            break;
            
        case 'xai':
            // X.AI doesn't support style or hdr parameters
            const seed = formData.get('seed');
            if (seed) requestData.seed = parseInt(seed, 10);
            break;
            
        case 'gemini':
            requestData.temperature = parseFloat(formData.get('temperature') || '0.7');
            break;
    }
    
    // Save request for retries
    state.lastRequest = requestData;
    
    // Generate image
    try {
        await generateImage(requestData);
    } catch (error) {
        showError(error.message || 'Failed to generate image');
    }
}

// Check connectivity to API server
async function checkApiConnectivity() {
    // Check if we're running from a file:// URL
    const isLocalFile = window.location.protocol === 'file:';
    
    // If running from file://, show local dev instructions
    if (isLocalFile) {
        elements.localDevInstructions.classList.remove('hidden');
    }
    
    try {
        // First try the API endpoint as configured
        let response = await fetch(`${API_BASE_URL}`, {
            method: 'GET',
            headers: {
                'Accept': 'application/json',
            },
            mode: 'cors',
            credentials: 'include',
            // Set a timeout to avoid long waits
            signal: AbortSignal.timeout(5000)
        });
        
        if (response.ok) {
            // API is online
            updateServerStatus('online', 'API server connected');
            return;
        }
        
        // If that fails, try local development server
        const localApiUrl = 'http://localhost:8000/v2';
        response = await fetch(localApiUrl, {
            method: 'GET',
            headers: {
                'Accept': 'application/json',
            },
            mode: 'cors',
            // Set a timeout to avoid long waits
            signal: AbortSignal.timeout(3000)
        });
        
        if (response.ok) {
            // Local API is online, update the base URL
            updateServerStatus('online', 'Connected to local server');
            // Update to use local server
            window.API_BASE_URL = localApiUrl;
            window.GENERATE_URL = `${localApiUrl}/generate`;
            return;
        }
        
        // If both fail, try one more fallback
        const altApiUrl = 'http://localhost:8000/v2';
        response = await fetch(altApiUrl, {
            method: 'GET',
            headers: {
                'Accept': 'application/json',
            },
            mode: 'cors',
            // Set a timeout to avoid long waits
            signal: AbortSignal.timeout(3000)
        });
        
        if (response.ok) {
            // Alt API is online, update the base URL
            updateServerStatus('online', 'Connected to alternate server');
            // Update to use alternate server
            window.API_BASE_URL = altApiUrl;
            window.GENERATE_URL = `${altApiUrl}/generate`;
            return;
        }
        
        // If all servers fail
        updateServerStatus('offline', 'API server unavailable');
    } catch (error) {
        console.error('API connectivity check failed:', error);
        updateServerStatus('offline', 'API connection failed');
    }
}

// Update server status indicator
function updateServerStatus(status, message) {
    // Remove all status classes first
    elements.statusIndicator.classList.remove('status-online', 'status-offline', 'status-unknown');
    
    // Add appropriate class based on status
    elements.statusIndicator.classList.add(`status-${status}`);
    
    // Update status text
    elements.statusText.textContent = message;
    
    // If offline, disable the form
    if (status === 'offline') {
        elements.form.classList.add('disabled');
        elements.generateBtn.disabled = true;
        showError('API server is not available. Please host the page on a web server and ensure the API is accessible.');
    } else {
        elements.form.classList.remove('disabled');
        elements.generateBtn.disabled = false;
        elements.errorDisplay.classList.add('hidden');
    }
}

// Generate image using API
async function generateImage(requestData) {
    showLoading(true);
    state.isGenerating = true;
    
    try {
        // Use window.GENERATE_URL if it exists (from the connectivity check)
        const apiUrl = window.GENERATE_URL || GENERATE_URL;
        
        console.log('Sending request to:', apiUrl);
        console.log('Request data:', requestData);
        
        const response = await fetch(apiUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'Origin': window.location.origin
            },
            credentials: 'include',
            body: JSON.stringify(requestData)
        });
        
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            console.error('API Error Response:', errorData);
            throw new Error(errorData.error || `Server responded with status: ${response.status}`);
        }
        
        const data = await response.json();
        console.log('API Response:', data);
        
        // Handle successful response
        if (data.data && data.data.length > 0) {
            const imageData = data.data[0];
            // Handle both URL and base64 responses
            const imageUrl = imageData.url || (imageData.b64_json ? `data:image/png;base64,${imageData.b64_json}` : null);
            
            if (imageUrl) {
                displayImage(imageUrl);
                state.imageUrl = imageUrl;
                
                // Set download filename based on prompt
                const truncatedPrompt = state.currentPrompt.substring(0, 20).replace(/[^a-z0-9]/gi, '-').toLowerCase();
                state.downloadFilename = `${truncatedPrompt}-${Date.now()}.png`;
            } else {
                throw new Error('No valid image data returned from API');
            }
        } else {
            throw new Error('No image data returned from API');
        }
    } catch (error) {
        console.error('Error generating image:', error);
        showError(error.message || 'Failed to generate image');
    } finally {
        showLoading(false);
        state.isGenerating = false;
    }
}

// Display the generated image
function displayImage(imageUrl) {
    // Hide placeholder and error
    elements.placeholder.classList.add('hidden');
    elements.errorDisplay.classList.add('hidden');
    
    // Show result container and controls
    elements.resultContainer.classList.remove('hidden');
    elements.resultControls.classList.remove('hidden');
    
    // Set image source
    elements.resultImage.src = imageUrl;
    elements.resultImage.alt = `AI generated image for prompt: ${state.currentPrompt.substring(0, 50)}...`;
    
    // Scroll to image if needed
    elements.resultImage.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

// Download the generated image
async function downloadImage() {
    if (!state.imageUrl) {
        showError('No image available to download');
        return;
    }
    
    try {
        let blob;
        if (state.imageUrl.startsWith('data:')) {
            // Handle base64 data URLs (Gemini case)
            const base64Data = state.imageUrl.split(',')[1];
            const byteCharacters = atob(base64Data);
            const byteArrays = [];
            
            for (let offset = 0; offset < byteCharacters.length; offset += 1024) {
                const slice = byteCharacters.slice(offset, offset + 1024);
                const byteNumbers = new Array(slice.length);
                for (let i = 0; i < slice.length; i++) {
                    byteNumbers[i] = slice.charCodeAt(i);
                }
                const byteArray = new Uint8Array(byteNumbers);
                byteArrays.push(byteArray);
            }
            
            blob = new Blob(byteArrays, {type: 'image/png'});
        } else {
            // For non-data URLs, use our proxy endpoint
            const apiUrl = window.API_BASE_URL || API_BASE_URL;
            const proxyUrl = `${apiUrl}/proxy-image?url=${encodeURIComponent(state.imageUrl)}`;
            
            // Add provider-specific headers
            const headers = {
                'Accept': 'image/*'
            };
            
            // Add authorization headers for X.AI if needed
            if (state.currentProvider === 'xai') {
                headers['X-API-Key'] = 'xai-IxAzklP9jWAhmKaE3pz9PBfcTAowVgNAd9fx1iWwYHNL7kowydC3MAmrMweXROg1q19dq5lye3NG6nmK';
            }
            
            const response = await fetch(proxyUrl, {
                credentials: 'include',
                headers: headers
            });
            
            if (!response.ok) {
                console.error('Download failed:', response.status, response.statusText);
                throw new Error('Failed to download image');
            }
            
            blob = await response.blob();
            
            // Verify we got an image
            if (!blob.type.startsWith('image/')) {
                console.error('Invalid content type:', blob.type);
                throw new Error('Invalid image data received');
            }
        }
        
        // Create download link
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.style.display = 'none';
        a.href = url;
        a.download = state.downloadFilename;
        
        // Trigger download
        document.body.appendChild(a);
        a.click();
        
        // Cleanup
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
    } catch (error) {
        console.error('Error downloading image:', error);
        showError('Failed to download image');
    }
}

// Regenerate image with the same parameters
function regenerateImage() {
    if (state.lastRequest) {
        generateImage(state.lastRequest);
    } else {
        showError('No previous request found');
    }
}

// Reset the form for a new prompt
function resetForm() {
    // Don't change provider or model selections
    elements.prompt.value = '';
    updatePromptCounter();
    
    // Hide results and show placeholder
    elements.resultContainer.classList.add('hidden');
    elements.resultControls.classList.add('hidden');
    elements.errorDisplay.classList.add('hidden');
    elements.placeholder.classList.remove('hidden');
    
    // Reset state
    state.currentPrompt = '';
    state.imageUrl = null;
    
    // Focus on prompt textarea
    elements.prompt.focus();
}

// Show loading indicator
function showLoading(isLoading) {
    if (isLoading) {
        elements.generateBtn.disabled = true;
        elements.loadingIndicator.classList.remove('hidden');
        elements.placeholder.classList.add('hidden');
        elements.resultContainer.classList.add('hidden');
        elements.errorDisplay.classList.add('hidden');
    } else {
        elements.generateBtn.disabled = false;
        elements.loadingIndicator.classList.add('hidden');
    }
}

// Show error message
function showError(message) {
    // Hide other elements
    elements.loadingIndicator.classList.add('hidden');
    elements.resultContainer.classList.add('hidden');
    elements.placeholder.classList.add('hidden');
    
    // Show error message
    elements.errorDisplay.classList.remove('hidden');
    elements.errorMessage.textContent = message;
    
    // Unfocus from the submit button so the button can be clicked again
    elements.generateBtn.blur();
}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', init); 