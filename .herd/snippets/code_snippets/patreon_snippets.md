# Code Snippets from toollama/API/api-tools/tools/snippets/core/auth/patreon.js

File: `toollama/API/api-tools/tools/snippets/core/auth/patreon.js`  
Language: JavaScript  
Extracted: 2025-06-07 05:22:38  

## Snippet 1
Lines 8-13

```JavaScript
export const PATREON_CONFIG = {
    CLIENT_ID: 'mrqWf4Kz2qZ4UkMxUlkT5F8fCq5lJQBIo5UZnrMzrh6v4xan7Ssx1SzE0PVhdD9J',
    REDIRECT_URI: 'https://actuallyusefulai.com/alt/dev/index.html',
    API_BASE: 'https://actuallyusefulai.com/api/v1/prod/auth'
};
```

## Snippet 2
Lines 24-29

```JavaScript
if (!this.donorButton) {
            console.warn(`Button with id '${loginButtonId}' not found`);
            return;
        }
        this.setupInitialButton();
        this.setupAuth();
```

## Snippet 3
Lines 36-38

```JavaScript
if (localStorage.getItem('patreonToken')) {
            this.donorButton.textContent = 'Logout';
            this.donorButton.onclick = () => this.handleLogout();
```

## Snippet 4
Lines 48-53

```JavaScript
setupAuth() {
        const urlParams = new URLSearchParams(window.location.search);
        const code = urlParams.get('code');
        const state = urlParams.get('state');
        const storedState = localStorage.getItem('oauth_state');
```

## Snippet 5
Lines 57-62

```JavaScript
} else {
                console.error('State mismatch - possible CSRF attempt');
                this.donorButton.textContent = 'Login Failed - Try Again';
            }
            localStorage.removeItem('oauth_state');
            window.history.replaceState({}, document.title, window.location.pathname);
```

## Snippet 6
Lines 65-67

```JavaScript
if (localStorage.getItem('patreonToken')) {
            this.validateToken();
        }
```

## Snippet 7
Lines 73-86

```JavaScript
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

## Snippet 8
Lines 87-90

```JavaScript
} catch (error) {
            console.error('Error initiating OAuth:', error);
            this.donorButton.textContent = 'Login Failed - Try Again';
        }
```

## Snippet 9
Lines 97-110

```JavaScript
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

## Snippet 10
Lines 111-117

```JavaScript
if (!response.ok) {
                const errorData = await response.json();
                console.error('Token exchange failed:', errorData);
                throw new Error('Failed to get access token');
            }

            const data = await response.json();
```

## Snippet 11
Lines 118-124

```JavaScript
if (!data.success || !data.access_token) {
                throw new Error('Invalid token response');
            }

            localStorage.setItem('patreonToken', data.access_token);
            this.donorButton.textContent = 'Logout';
            this.donorButton.onclick = () => this.handleLogout();
```

## Snippet 12
Lines 125-129

```JavaScript
} catch (error) {
            console.error('Error during authentication:', error);
            this.donorButton.textContent = 'Login Failed - Try Again';
            this.donorButton.onclick = () => this.initiateOAuth();
        }
```

## Snippet 13
Lines 138-145

```JavaScript
if (!token) return;

        try {
            const response = await fetch(`${PATREON_CONFIG.API_BASE}/validate`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
```

## Snippet 14
Lines 149-153

```JavaScript
if (!response.ok) {
                throw new Error('Token validation failed');
            }

            const data = await response.json();
```

## Snippet 15
Lines 154-157

```JavaScript
if (!data.valid) {
                this.handleLogout();
            }
            return data.user;
```

## Snippet 16
Lines 158-162

```JavaScript
} catch (error) {
            console.error('Error validating token:', error);
            this.handleLogout();
            return null;
        }
```

## Snippet 17
Lines 168-174

```JavaScript
handleLogout() {
        localStorage.removeItem('patreonToken');
        localStorage.removeItem('oauth_state');
        this.donorButton.textContent = 'Donor Login';
        this.donorButton.onclick = () => this.initiateOAuth();
    }
```

## Snippet 18
Lines 179-182

```JavaScript
static isLoggedIn() {
        return !!localStorage.getItem('patreonToken');
    }
```

## Snippet 19
Lines 189-196

```JavaScript
if (!token) return null;

        try {
            const response = await fetch(`${PATREON_CONFIG.API_BASE}/validate`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
```

## Snippet 20
Lines 200-203

```JavaScript
if (!response.ok) return null;

            const data = await response.json();
            return data.valid ? data.user : null;
```

## Snippet 21
Lines 204-207

```JavaScript
} catch (error) {
            console.error('Error getting current user:', error);
            return null;
        }
```

## Snippet 22
Lines 214-216

```JavaScript
static getToken() {
        return localStorage.getItem('patreonToken');
    }
```

