# Code Snippets from toollama/API/static/app.js

File: `toollama/API/static/app.js`  
Language: JavaScript  
Extracted: 2025-06-07 05:16:37  

## Snippet 1
Lines 1-4

```JavaScript
// Constants
const API_BASE_URL = window.location.hostname === 'localhost' ? 'http://localhost:8000/v2' : 'https://ai.assisted.space/v2';
const MAX_PROMPT_LENGTH = 1000;
```

## Snippet 2
Lines 5-10

```JavaScript
// API endpoint for image generation
const GENERATE_URL = `${API_BASE_URL}/generate`;

// Provider-specific models
const PROVIDER_MODELS = {
    openai: [
```

## Snippet 3
Lines 21-71

```JavaScript
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
```

## Snippet 4
Lines 72-89

```JavaScript
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
```

## Snippet 5
Lines 90-120

```JavaScript
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
```

## Snippet 6
Lines 121-125

```JavaScript
if (temperatureSlider && temperatureValue) {
        temperatureSlider.addEventListener('input', (e) => {
            temperatureValue.textContent = e.target.value;
        });
    }
```

## Snippet 7
Lines 129-142

```JavaScript
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
```

## Snippet 8
Lines 146-161

```JavaScript
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
```

## Snippet 9
Lines 166-169

```JavaScript
function populateModels(provider) {
    // Clear existing options
    elements.modelSelect.innerHTML = '';
```

## Snippet 10
Lines 170-181

```JavaScript
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
```

## Snippet 11
Lines 182-185

```JavaScript
if (models.length > 0) {
        elements.modelSelect.value = models[0].id;
        state.currentModel = models[0].id;
    }
```

## Snippet 12
Lines 189-193

```JavaScript
function updatePromptCounter() {
    const length = elements.prompt.value.length;
    elements.promptCounter.textContent = `${length}/${MAX_PROMPT_LENGTH}`;

    // Update visual feedback based on length
```

## Snippet 13
Lines 202-211

```JavaScript
async function handleFormSubmit(e) {
    e.preventDefault();

    // Get form data
    const formData = new FormData(elements.form);
    const prompt = formData.get('prompt');
    const provider = formData.get('provider');
    let model = formData.get('model');

    // Validate prompt length
```

## Snippet 14
Lines 212-216

```JavaScript
if (prompt.length === 0) {
        showError('Please enter a prompt');
        return;
    }
```

## Snippet 15
Lines 225-240

```JavaScript
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
```

## Snippet 16
Lines 241-246

```JavaScript
// Add model parameter for all providers
    requestData.model = model;

    // Add provider-specific parameters
    switch (provider) {
        case 'openai':
```

## Snippet 17
Lines 248-253

```JavaScript
if (model === 'dall-e-3') {
                requestData.quality = formData.get('quality');
                requestData.style = formData.get('style');
            }

            // Add size based on model
```

## Snippet 18
Lines 268-270

```JavaScript
case 'xai':
            // X.AI doesn't support style or hdr parameters
            const seed = formData.get('seed');
```

## Snippet 19
Lines 279-284

```JavaScript
// Save request for retries
    state.lastRequest = requestData;

    // Generate image
    try {
        await generateImage(requestData);
```

## Snippet 20
Lines 285-287

```JavaScript
} catch (error) {
        showError(error.message || 'Failed to generate image');
    }
```

## Snippet 21
Lines 292-295

```JavaScript
// Check if we're running from a file:// URL
    const isLocalFile = window.location.protocol === 'file:';

    // If running from file://, show local dev instructions
```

## Snippet 22
Lines 296-312

```JavaScript
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
```

## Snippet 23
Lines 313-330

```JavaScript
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
```

## Snippet 24
Lines 331-351

```JavaScript
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
```

## Snippet 25
Lines 352-362

```JavaScript
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
```

## Snippet 26
Lines 363-366

```JavaScript
} catch (error) {
        console.error('API connectivity check failed:', error);
        updateServerStatus('offline', 'API connection failed');
    }
```

## Snippet 27
Lines 370-373

```JavaScript
function updateServerStatus(status, message) {
    // Remove all status classes first
    elements.statusIndicator.classList.remove('status-online', 'status-offline', 'status-unknown');
```

## Snippet 28
Lines 374-380

```JavaScript
// Add appropriate class based on status
    elements.statusIndicator.classList.add(`status-${status}`);

    // Update status text
    elements.statusText.textContent = message;

    // If offline, disable the form
```

## Snippet 29
Lines 381-384

```JavaScript
if (status === 'offline') {
        elements.form.classList.add('disabled');
        elements.generateBtn.disabled = true;
        showError('API server is not available. Please host the page on a web server and ensure the API is accessible.');
```

## Snippet 30
Lines 385-389

```JavaScript
} else {
        elements.form.classList.remove('disabled');
        elements.generateBtn.disabled = false;
        elements.errorDisplay.classList.add('hidden');
    }
```

## Snippet 31
Lines 393-397

```JavaScript
async function generateImage(requestData) {
    showLoading(true);
    state.isGenerating = true;

    try {
```

## Snippet 32
Lines 398-414

```JavaScript
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
```

## Snippet 33
Lines 415-424

```JavaScript
if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            console.error('API Error Response:', errorData);
            throw new Error(errorData.error || `Server responded with status: ${response.status}`);
        }

        const data = await response.json();
        console.log('API Response:', data);

        // Handle successful response
```

## Snippet 34
Lines 425-429

```JavaScript
if (data.data && data.data.length > 0) {
            const imageData = data.data[0];
            // Handle both URL and base64 responses
            const imageUrl = imageData.url || (imageData.b64_json ? `data:image/png;base64,${imageData.b64_json}` : null);
```

## Snippet 35
Lines 430-436

```JavaScript
if (imageUrl) {
                displayImage(imageUrl);
                state.imageUrl = imageUrl;

                // Set download filename based on prompt
                const truncatedPrompt = state.currentPrompt.substring(0, 20).replace(/[^a-z0-9]/gi, '-').toLowerCase();
                state.downloadFilename = `${truncatedPrompt}-${Date.now()}.png`;
```

## Snippet 36
Lines 437-439

```JavaScript
} else {
                throw new Error('No valid image data returned from API');
            }
```

## Snippet 37
Lines 440-442

```JavaScript
} else {
            throw new Error('No image data returned from API');
        }
```

## Snippet 38
Lines 443-445

```JavaScript
} catch (error) {
        console.error('Error generating image:', error);
        showError(error.message || 'Failed to generate image');
```

## Snippet 39
Lines 453-463

```JavaScript
function displayImage(imageUrl) {
    // Hide placeholder and error
    elements.placeholder.classList.add('hidden');
    elements.errorDisplay.classList.add('hidden');

    // Show result container and controls
    elements.resultContainer.classList.remove('hidden');
    elements.resultControls.classList.remove('hidden');

    // Set image source
    elements.resultImage.src = imageUrl;
```

## Snippet 40
Lines 472-478

```JavaScript
if (!state.imageUrl) {
        showError('No image available to download');
        return;
    }

    try {
        let blob;
```

## Snippet 41
Lines 479-484

```JavaScript
if (state.imageUrl.startsWith('data:')) {
            // Handle base64 data URLs (Gemini case)
            const base64Data = state.imageUrl.split(',')[1];
            const byteCharacters = atob(base64Data);
            const byteArrays = [];
```

## Snippet 42
Lines 485-487

```JavaScript
for (let offset = 0; offset < byteCharacters.length; offset += 1024) {
                const slice = byteCharacters.slice(offset, offset + 1024);
                const byteNumbers = new Array(slice.length);
```

## Snippet 43
Lines 488-492

```JavaScript
for (let i = 0; i < slice.length; i++) {
                    byteNumbers[i] = slice.charCodeAt(i);
                }
                const byteArray = new Uint8Array(byteNumbers);
                byteArrays.push(byteArray);
```

## Snippet 44
Lines 496-502

```JavaScript
} else {
            // For non-data URLs, use our proxy endpoint
            const apiUrl = window.API_BASE_URL || API_BASE_URL;
            const proxyUrl = `${apiUrl}/proxy-image?url=${encodeURIComponent(state.imageUrl)}`;

            // Add provider-specific headers
            const headers = {
```

## Snippet 45
Lines 507-515

```JavaScript
if (state.currentProvider === 'xai') {
                headers['X-API-Key'] = 'xai-IxAzklP9jWAhmKaE3pz9PBfcTAowVgNAd9fx1iWwYHNL7kowydC3MAmrMweXROg1q19dq5lye3NG6nmK';
            }

            const response = await fetch(proxyUrl, {
                credentials: 'include',
                headers: headers
            });
```

## Snippet 46
Lines 516-523

```JavaScript
if (!response.ok) {
                console.error('Download failed:', response.status, response.statusText);
                throw new Error('Failed to download image');
            }

            blob = await response.blob();

            // Verify we got an image
```

## Snippet 47
Lines 524-527

```JavaScript
if (!blob.type.startsWith('image/')) {
                console.error('Invalid content type:', blob.type);
                throw new Error('Invalid image data received');
            }
```

## Snippet 48
Lines 528-543

```JavaScript
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
```

## Snippet 49
Lines 544-547

```JavaScript
} catch (error) {
        console.error('Error downloading image:', error);
        showError('Failed to download image');
    }
```

## Snippet 50
Lines 560-579

```JavaScript
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
```

## Snippet 51
Lines 581-586

```JavaScript
if (isLoading) {
        elements.generateBtn.disabled = true;
        elements.loadingIndicator.classList.remove('hidden');
        elements.placeholder.classList.add('hidden');
        elements.resultContainer.classList.add('hidden');
        elements.errorDisplay.classList.add('hidden');
```

## Snippet 52
Lines 594-609

```JavaScript
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
```

