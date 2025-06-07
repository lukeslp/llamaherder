# Code Snippets from toollama/API/api-tools/tools/snippets/processed/more_snippets.js

File: `toollama/API/api-tools/tools/snippets/processed/more_snippets.js`  
Language: JavaScript  
Extracted: 2025-06-07 05:21:44  

## Snippet 1
Lines 1-13

```JavaScript
// Device detection
export const isMobile = () => /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
export const isAndroid = () => /Android/i.test(navigator.userAgent);

// Image processing
export const resizeImage = async (file, maxDimension = 2048) => {
    return new Promise((resolve) => {
        const img = new Image();
        img.onload = () => {
            const canvas = document.createElement('canvas');
            let width = img.width;
            let height = img.height;
```

## Snippet 2
Lines 14-16

```JavaScript
if (width > height && width > maxDimension) {
                height = Math.round((height * maxDimension) / width);
                width = maxDimension;
```

## Snippet 3
Lines 17-29

```JavaScript
} else if (height > maxDimension) {
                width = Math.round((width * maxDimension) / height);
                height = maxDimension;
            }

            canvas.width = width;
            canvas.height = height;

            const ctx = canvas.getContext('2d');
            ctx.drawImage(img, 0, 0, width, height);

            const base64 = canvas.toDataURL('image/jpeg', 0.9);
            resolve(base64.split('base64,')[1]);
```

## Snippet 4
Lines 36-41

```JavaScript
export const ALT_TEXT_SYSTEM_PROMPT = `You're an Alt Text Specialist, dedicated to creating precise and accessible alt text for digital images, especially memes. Your primary goal is to ensure visually impaired individuals can engage with imagery by providing concise, accurate, and ethically-minded descriptions.

Create Alt Text
- **Depict essential visuals and visible text accurately.**
- **Avoid adding social-emotional context or narrative interpretations unless specifically requested.**
- **Refrain from speculating on artists' intentions.**
```

## Snippet 5
Lines 43-49

```JavaScript
- **Maintain clarity and consistency for all descriptions, including direct image links.**
- **Character limit:** All descriptions must be under 1000 characters.`;

// Content processing
export const cleanupContent = (content) => {
    return content
        .replace(/^[\s-]+|[\s-]+$/g, '') // Remove leading/trailing spaces and dashes
```

## Snippet 6
Lines 51-86

```JavaScript
};

// URL utilities
export const createCacheBustedUrl = (file) => {
    return URL.createObjectURL(file) + '#' + new Date().getTime();
};

export const revokeCacheBustedUrl = (url) => {
    URL.revokeObjectURL(url.split('#')[0]);
};

// Pull to refresh constants
export const PULL_REFRESH_THRESHOLD = 80;

// Animation utilities
export const createStreamingCharSpan = (char) => {
    const span = document.createElement('span');
    span.textContent = char;
    span.className = 'streaming-char';
    return span;
};

// Default model
export const DEFAULT_MODEL = "coolhand/impossible_alt:13b";

// API endpoint
export const API_BASE_URL = "https://7584e4c6571c.ngrok.app/api";

// API interactions
export const makeApiCall = async (messages, base64Image, model, apiBaseUrl) => {
    const requestBody = {
        model,
        messages,
        stream: true
    };
```

## Snippet 7
Lines 87-106

```JavaScript
if (base64Image) {
        requestBody.messages[requestBody.messages.length - 1].images = [base64Image];
    }

    console.log("API Request details:", {
        url: `${apiBaseUrl}/chat`,
        body: {
            ...requestBody,
            messages: requestBody.messages,
            images: requestBody.images ? ['[Image Data]'] : undefined
        }
    });

    return fetch(`${apiBaseUrl}/chat`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(requestBody)
    });
```

## Snippet 8
Lines 107-112

```JavaScript
};

export const processStreamedResponse = async (response, {
    onContent = () => {},
    onDone = () => {},
    onError = () => {}
```

## Snippet 9
Lines 113-119

```JavaScript
} = {}) => {
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let fullContent = "";
    let totalTokens = 0;

    try {
```

## Snippet 10
Lines 128-132

```JavaScript
if (line.trim() === '') continue;

                try {
                    const data = JSON.parse(line);
```

## Snippet 11
Lines 133-137

```JavaScript
if (data.message?.content) {
                        fullContent += data.message.content;
                        onContent(data.message.content);
                    }
```

## Snippet 12
Lines 138-148

```JavaScript
if (data.done) {
                        totalTokens = data.prompt_eval_count + data.eval_count;
                        onDone({
                            fullContent,
                            totalTokens,
                            messages: [{
                                role: "assistant",
                                content: fullContent
                            }]
                        });
                    }
```

## Snippet 13
Lines 149-152

```JavaScript
} catch (error) {
                    console.warn("Error parsing line:", line, error);
                    continue;
                }
```

## Snippet 14
Lines 155-159

```JavaScript
} catch (error) {
        onError(error);
        throw error;
    }
```

## Snippet 15
Lines 161-167

```JavaScript
};

// Clipboard utilities
export const copyToClipboard = async (text) => {
    try {
        await navigator.clipboard.writeText(text);
        return true;
```

## Snippet 16
Lines 168-171

```JavaScript
} catch (error) {
        console.error('Failed to copy text:', error);
        return false;
    }
```

## Snippet 17
Lines 172-181

```JavaScript
};

// Image analysis
export const analyzeImage = async (base64Content, model, apiBaseUrl) => {
    try {
        const messages = [{
            role: "system",
            content: ALT_TEXT_SYSTEM_PROMPT
        }, {
            role: "user",
```

## Snippet 18
Lines 184-187

```JavaScript
}];

        const response = await makeApiCall(messages, base64Content, model, apiBaseUrl);
```

## Snippet 19
Lines 188-193

```JavaScript
if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`API Error (${response.status}): ${errorText}`);
        }

        return response;
```

## Snippet 20
Lines 194-197

```JavaScript
} catch (error) {
        console.error('Error analyzing image:', error);
        throw error;
    }
```

## Snippet 21
Lines 198-206

```JavaScript
};

// Patreon Integration
export const PATREON_CONFIG = {
    CLIENT_ID: 'mrqWf4Kz2qZ4UkMxUlkT5F8fCq5lJQBIo5UZnrMzrh6v4xan7Ssx1SzE0PVhdD9J',
    REDIRECT_URI: 'https://actuallyusefulai.com/alt/dev/index.html',
    API_BASE: 'https://actuallyusefulai.com/api/v1/prod/auth'
};
```

## Snippet 22
Lines 207-209

```JavaScript
export class PatreonIntegration {
    constructor(loginButtonId = 'donorLogin') {
        this.donorButton = document.getElementById(loginButtonId);
```

## Snippet 23
Lines 210-215

```JavaScript
if (!this.donorButton) {
            console.warn(`Button with id '${loginButtonId}' not found`);
            return;
        }
        this.setupInitialButton();
        this.setupAuth();
```

## Snippet 24
Lines 216-218

```JavaScript
}

    setupInitialButton() {
```

## Snippet 25
Lines 219-221

```JavaScript
if (localStorage.getItem('patreonToken')) {
            this.donorButton.textContent = 'Logout';
            this.donorButton.onclick = () => this.handleLogout();
```

## Snippet 26
Lines 226-233

```JavaScript
}

    setupAuth() {
        const urlParams = new URLSearchParams(window.location.search);
        const code = urlParams.get('code');
        const state = urlParams.get('state');
        const storedState = localStorage.getItem('oauth_state');
```

## Snippet 27
Lines 237-242

```JavaScript
} else {
                console.error('State mismatch - possible CSRF attempt');
                this.donorButton.textContent = 'Login Failed - Try Again';
            }
            localStorage.removeItem('oauth_state');
            window.history.replaceState({}, document.title, window.location.pathname);
```

## Snippet 28
Lines 245-247

```JavaScript
if (localStorage.getItem('patreonToken')) {
            this.validateToken();
        }
```

## Snippet 29
Lines 248-263

```JavaScript
}

    async initiateOAuth() {
        try {
            const state = crypto.randomUUID ? crypto.randomUUID() : Math.random().toString(36).substring(2);
            localStorage.setItem('oauth_state', state);

            const params = new URLSearchParams({
                response_type: 'code',
                client_id: PATREON_CONFIG.CLIENT_ID,
                redirect_uri: PATREON_CONFIG.REDIRECT_URI,
                scope: 'identity identity.memberships campaigns campaigns.members',
                state: state
            });

            window.location.href = `https://www.patreon.com/oauth2/authorize?${params.toString()}`;
```

## Snippet 30
Lines 264-267

```JavaScript
} catch (error) {
            console.error('Error initiating OAuth:', error);
            this.donorButton.textContent = 'Login Failed - Try Again';
        }
```

## Snippet 31
Lines 268-283

```JavaScript
}

    async handleOAuthCallback(code) {
        try {
            const response = await fetch(`${PATREON_CONFIG.API_BASE}/patreon/token`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    code,
                    grant_type: 'authorization_code',
                    redirect_uri: PATREON_CONFIG.REDIRECT_URI
                })
            });
```

## Snippet 32
Lines 284-290

```JavaScript
if (!response.ok) {
                const errorData = await response.json();
                console.error('Token exchange failed:', errorData);
                throw new Error('Failed to get access token');
            }

            const data = await response.json();
```

## Snippet 33
Lines 291-297

```JavaScript
if (!data.success || !data.access_token) {
                throw new Error('Invalid token response');
            }

            localStorage.setItem('patreonToken', data.access_token);
            this.donorButton.textContent = 'Logout';
            this.donorButton.onclick = () => this.handleLogout();
```

## Snippet 34
Lines 298-302

```JavaScript
} catch (error) {
            console.error('Error during authentication:', error);
            this.donorButton.textContent = 'Login Failed - Try Again';
            this.donorButton.onclick = () => this.initiateOAuth();
        }
```

## Snippet 35
Lines 303-306

```JavaScript
}

    async validateToken() {
        const token = localStorage.getItem('patreonToken');
```

## Snippet 36
Lines 307-314

```JavaScript
if (!token) return;

        try {
            const response = await fetch(`${PATREON_CONFIG.API_BASE}/validate`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
```

## Snippet 37
Lines 318-322

```JavaScript
if (!response.ok) {
                throw new Error('Token validation failed');
            }

            const data = await response.json();
```

## Snippet 38
Lines 323-326

```JavaScript
if (!data.valid) {
                this.handleLogout();
            }
            return data.user;
```

## Snippet 39
Lines 327-331

```JavaScript
} catch (error) {
            console.error('Error validating token:', error);
            this.handleLogout();
            return null;
        }
```

## Snippet 40
Lines 332-346

```JavaScript
}

    handleLogout() {
        localStorage.removeItem('patreonToken');
        localStorage.removeItem('oauth_state');
        this.donorButton.textContent = 'Donor Login';
        this.donorButton.onclick = () => this.initiateOAuth();
    }

    static isLoggedIn() {
        return !!localStorage.getItem('patreonToken');
    }

    static async getCurrentUser() {
        const token = localStorage.getItem('patreonToken');
```

## Snippet 41
Lines 347-354

```JavaScript
if (!token) return null;

        try {
            const response = await fetch(`${PATREON_CONFIG.API_BASE}/validate`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
```

## Snippet 42
Lines 358-361

```JavaScript
if (!response.ok) return null;

            const data = await response.json();
            return data.valid ? data.user : null;
```

## Snippet 43
Lines 362-365

```JavaScript
} catch (error) {
            console.error('Error getting current user:', error);
            return null;
        }
```

## Snippet 44
Lines 366-370

```JavaScript
}

    static getToken() {
        return localStorage.getItem('patreonToken');
    }
```

## Snippet 45
Lines 374-378

```JavaScript
/*
// Initialize Patreon integration
const patreon = new PatreonIntegration('donorLogin');

// Check login status
```

## Snippet 46
Lines 379-381

```JavaScript
if (PatreonIntegration.isLoggedIn()) {
    // Get current user
    const user = await PatreonIntegration.getCurrentUser();
```

## Snippet 47
Lines 382-384

```JavaScript
if (user) {
        console.log('Logged in as:', user.full_name);
    }
```

## Snippet 48
Lines 385-388

```JavaScript
}

// Make authenticated API calls
const token = PatreonIntegration.getToken();
```

## Snippet 49
Lines 389-395

```JavaScript
if (token) {
    const response = await fetch('your-api-endpoint', {
        headers: {
            'Authorization': `Bearer ${token}`
        }
    });
}
```

