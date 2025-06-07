# Code Snippets from toollama/API/api-tools/tools/snippets/core/ui/interaction/stream.js

File: `toollama/API/api-tools/tools/snippets/core/ui/interaction/stream.js`  
Language: JavaScript  
Extracted: 2025-06-07 05:24:32  

## Snippet 1
Lines 5-11

```JavaScript
export const StreamManager = {
    setupStream(config) {
        const {
            onDelta = () => {},
            onComplete = () => {},
            onError = console.error,
            decoder = new TextDecoder()
```

## Snippet 2
Lines 12-16

```JavaScript
} = config;

        return {
            async processStream(reader) {
                try {
```

## Snippet 3
Lines 25-27

```JavaScript
if (line.startsWith('data:')) {
                                try {
                                    const data = JSON.parse(line.slice(5));
```

## Snippet 4
Lines 30-32

```JavaScript
} else if (data.type === 'complete') {
                                        onComplete(data);
                                    }
```

## Snippet 5
Lines 33-35

```JavaScript
} catch (error) {
                                    onError('Error parsing stream:', error);
                                }
```

## Snippet 6
Lines 39-41

```JavaScript
} catch (error) {
                    onError('Stream processing error:', error);
                }
```

