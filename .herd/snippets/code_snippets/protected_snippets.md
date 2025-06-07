# Code Snippets from toollama/API/api-tools/tools/snippets/core/auth/protected.js

File: `toollama/API/api-tools/tools/snippets/core/auth/protected.js`  
Language: JavaScript  
Extracted: 2025-06-07 05:22:36  

## Snippet 1
Lines 5-11

```JavaScript
export const ProtectedContentAuth = {
    // Configuration
    config: {
        apiBaseUrl: 'https://actuallyusefulai.com/api/v1/prod/auth',
        redirectUri: 'https://actuallyusefulai.com/auth/index.html'
    },
```

## Snippet 2
Lines 19-26

```JavaScript
if (!accessToken) {
            console.warn('No access token found, redirecting to login...');
            window.location.href = this.config.redirectUri;
            return;
        }

        try {
            const userResponse = await fetch(`${this.config.apiBaseUrl}/patreon/user`, {
```

## Snippet 3
Lines 33-35

```JavaScript
if (!userData?.membership_details?.length || userData.membership_details[0].pledge_amount < 1) {
                console.warn('User does not meet pledge requirements, redirecting...');
                window.location.href = 'https://actuallyusefulai.com/auth';
```

## Snippet 4
Lines 39-42

```JavaScript
} catch (error) {
            console.error('Error verifying user:', error);
            window.location.href = 'https://actuallyusefulai.com/auth';
        }
```

## Snippet 5
Lines 48-50

```JavaScript
setupProtectedContent() {
        window.addEventListener('DOMContentLoaded', () => this.checkPatreonAccess());
    }
```

