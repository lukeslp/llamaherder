# Code Snippets from toollama/API/api-tools/tools/snippets/core/ui/interaction/input.js

File: `toollama/API/api-tools/tools/snippets/core/ui/interaction/input.js`  
Language: JavaScript  
Extracted: 2025-06-07 05:24:27  

## Snippet 1
Lines 5-13

```JavaScript
export const InputManager = {
    setupInput(config) {
        const {
            input,
            submitButton,
            onSubmit,
            onKeyPress = true,
            clearOnSubmit = true,
            validation = (value) => value.trim() !== ''
```

## Snippet 2
Lines 16-19

```JavaScript
if (!input || !submitButton || !onSubmit) return;

        const handleSubmit = () => {
            const value = input.value;
```

## Snippet 3
Lines 20-22

```JavaScript
if (!validation(value)) return;

            onSubmit(value);
```

## Snippet 4
Lines 23-25

```JavaScript
if (clearOnSubmit) {
                input.value = '';
            }
```

## Snippet 5
Lines 32-35

```JavaScript
if (event.key === 'Enter' && !event.shiftKey) {
                    event.preventDefault();
                    handleSubmit();
                }
```

## Snippet 6
Lines 37-39

```JavaScript
}

        return {
```

