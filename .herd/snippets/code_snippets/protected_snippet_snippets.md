# Code Snippets from toollama/API/api-tools/tools/snippets/processed/protected_snippet.js

File: `toollama/API/api-tools/tools/snippets/processed/protected_snippet.js`  
Language: JavaScript  
Extracted: 2025-06-07 05:21:40  

## Snippet 1
Lines 1-5

```JavaScript
<script>
    const clientId = 'mrqWf4Kz2qZ4UkMxUlkT5F8fCq5lJQBIo5UZnrMzrh6v4xan7Ssx1SzE0PVhdD9J';
    const redirectUri = 'https://actuallyusefulai.com/auth/index.html';
    const apiBaseUrl = 'https://actuallyusefulai.com/api/v1/prod/auth';
```

## Snippet 2
Lines 9-16

```JavaScript
if (!accessToken) {
            console.warn('No access token found, redirecting to login...');
            window.location.href = redirectUri;
            return;
        }

        try {
            const userResponse = await fetch(`${apiBaseUrl}/patreon/user`, {
```

## Snippet 3
Lines 23-25

```JavaScript
if (!userData?.membership_details?.length || userData.membership_details[0].pledge_amount < 1) {
                console.warn('User does not meet pledge requirements, redirecting...');
                window.location.href = 'https://actuallyusefulai.com/auth';
```

## Snippet 4
Lines 29-32

```JavaScript
} catch (error) {
            console.error('Error verifying user:', error);
            window.location.href = 'https://actuallyusefulai.com/auth';
        }
```

