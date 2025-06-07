# Code Snippets from toollama/API/static/styles.css

File: `toollama/API/static/styles.css`  
Language: CSS  
Extracted: 2025-06-07 05:16:35  

## Snippet 1
Lines 1-17

```CSS
/* Variables */
:root {
    --primary-color: #6366f1;
    --primary-hover: #4f46e5;
    --secondary-color: #f0f4f8;
    --text-color: #333;
    --light-text: #6b7280;
    --border-color: #e2e8f0;
    --error-color: #ef4444;
    --success-color: #22c55e;
    --dark-bg: #111827;
    --container-width: 1200px;
    --border-radius: 8px;
    --shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    --transition: all 0.3s ease;
}
```

## Snippet 2
Lines 18-43

```CSS
/* Reset & Base Styles */
* {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
}

body {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
    line-height: 1.6;
    color: var(--text-color);
    background-color: #f9fafb;
    min-height: 100vh;
}

a {
    color: var(--primary-color);
    text-decoration: none;
}

img {
    max-width: 100%;
    height: auto;
    display: block;
}
```

## Snippet 3
Lines 44-76

```CSS
/* Layout */
.container {
    max-width: var(--container-width);
    margin: 0 auto;
    padding: 2rem 1rem;
}

header {
    text-align: center;
    margin-bottom: 2rem;
}

header h1 {
    font-size: 2.5rem;
    margin-bottom: 0.5rem;
    background: linear-gradient(135deg, var(--primary-color), #8b5cf6);
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
}

header p {
    color: var(--light-text);
    font-size: 1.1rem;
}

main {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 2rem;
    margin-bottom: 2rem;
}
```

## Snippet 4
Lines 77-82

```CSS
@media (max-width: 768px) {
    main {
        grid-template-columns: 1fr;
    }
}
```

## Snippet 5
Lines 83-176

```CSS
/* Form Styles */
.input-section {
    background-color: white;
    border-radius: var(--border-radius);
    padding: 1.5rem;
    box-shadow: var(--shadow);
}

.form-group {
    margin-bottom: 1.5rem;
}

label {
    display: block;
    margin-bottom: 0.5rem;
    font-weight: 500;
    color: var(--text-color);
}

select, textarea {
    width: 100%;
    padding: 0.75rem;
    border: 1px solid var(--border-color);
    border-radius: var(--border-radius);
    font-size: 1rem;
    transition: var(--transition);
}

select:focus, textarea:focus {
    outline: none;
    border-color: var(--primary-color);
    box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.2);
}

textarea {
    resize: vertical;
    min-height: 100px;
}

.prompt-controls {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: 0.5rem;
}

#prompt-counter {
    color: var(--light-text);
    font-size: 0.875rem;
}

.text-button {
    background: none;
    border: none;
    color: var(--primary-color);
    cursor: pointer;
    font-size: 0.875rem;
    transition: var(--transition);
}

.text-button:hover {
    color: var(--primary-hover);
    text-decoration: underline;
}

.form-actions {
    display: flex;
    justify-content: flex-end;
}

.primary-button {
    background-color: var(--primary-color);
    color: white;
    border: none;
    border-radius: var(--border-radius);
    padding: 0.75rem 1.5rem;
    font-size: 1rem;
    font-weight: 500;
    cursor: pointer;
    transition: var(--transition);
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.primary-button:hover {
    background-color: var(--primary-hover);
    transform: translateY(-1px);
}

.primary-button:active {
    transform: translateY(0);
}
```

## Snippet 6
Lines 177-235

```CSS
/* Result Section */
.result-section {
    background-color: white;
    border-radius: var(--border-radius);
    padding: 1.5rem;
    box-shadow: var(--shadow);
}

.result-section h2 {
    margin-bottom: 1rem;
    text-align: center;
}

.image-container {
    position: relative;
    min-height: 300px;
    border: 2px dashed var(--border-color);
    border-radius: var(--border-radius);
    margin-bottom: 1rem;
    display: flex;
    justify-content: center;
    align-items: center;
    overflow: hidden;
}

.placeholder {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    color: var(--light-text);
    padding: 2rem;
    text-align: center;
}

.placeholder i {
    font-size: 3rem;
    margin-bottom: 1rem;
    opacity: 0.5;
}

#result-container {
    width: 100%;
    height: 100%;
    display: flex;
    justify-content: center;
    align-items: center;
}

#result-image {
    max-height: 500px;
    object-fit: contain;
    border-radius: var(--border-radius);
}

.hidden {
    display: none !important;
}
```

## Snippet 7
Lines 236-260

```CSS
/* Loading Indicator */
#loading-indicator {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: rgba(255, 255, 255, 0.8);
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    z-index: 10;
}

.spinner {
    width: 50px;
    height: 50px;
    border: 5px solid var(--secondary-color);
    border-top-color: var(--primary-color);
    border-radius: 50%;
    animation: spin 1s linear infinite;
    margin-bottom: 1rem;
}
```

## Snippet 8
Lines 261-266

```CSS
@keyframes spin {
    to {
        transform: rotate(360deg);
    }
}
```

## Snippet 9
Lines 267-294

```CSS
/* Error Display */
.error-display {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: rgba(254, 226, 226, 0.9);
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    z-index: 10;
    padding: 1rem;
    text-align: center;
}

.error-display i {
    font-size: 2.5rem;
    color: var(--error-color);
    margin-bottom: 1rem;
}

#error-message {
    color: var(--error-color);
    font-weight: 500;
}
```

## Snippet 10
Lines 295-330

```CSS
/* Result Controls */
.result-controls {
    display: flex;
    justify-content: center;
    gap: 1rem;
    margin-top: 1rem;
}

.action-button {
    background-color: white;
    color: var(--text-color);
    border: 1px solid var(--border-color);
    border-radius: var(--border-radius);
    padding: 0.5rem 1rem;
    font-size: 0.875rem;
    cursor: pointer;
    transition: var(--transition);
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.action-button:hover {
    background-color: var(--secondary-color);
    border-color: var(--light-text);
}

#download-btn {
    color: var(--primary-color);
    border-color: var(--primary-color);
}

#download-btn:hover {
    background-color: rgba(99, 102, 241, 0.1);
}
```

## Snippet 11
Lines 331-335

```CSS
/* Provider-specific options */
.provider-options {
    display: none;
}
```

## Snippet 12
Lines 336-356

```CSS
/* Footer */
footer {
    text-align: center;
    color: var(--light-text);
    font-size: 0.875rem;
    margin-top: 2rem;
    padding-top: 1rem;
    border-top: 1px solid var(--border-color);
}

footer p {
    margin-bottom: 0.5rem;
}

footer code {
    background-color: var(--secondary-color);
    padding: 0.2rem 0.4rem;
    border-radius: 4px;
    font-size: 0.8rem;
}
```

## Snippet 13
Lines 357-374

```CSS
/* Form Controls */
input[type="number"],
input[type="range"] {
    width: 100%;
    padding: 0.75rem;
    border: 1px solid var(--border-color);
    border-radius: var(--border-radius);
    font-size: 1rem;
    transition: var(--transition);
}

input[type="number"]:focus,
input[type="range"]:focus {
    outline: none;
    border-color: var(--primary-color);
    box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.2);
}
```

## Snippet 14
Lines 375-403

```CSS
/* Range slider styling */
input[type="range"] {
    -webkit-appearance: none;
    height: 8px;
    background: var(--border-color);
    border-radius: 4px;
    padding: 0;
}

input[type="range"]::-webkit-slider-thumb {
    -webkit-appearance: none;
    width: 20px;
    height: 20px;
    border-radius: 50%;
    background: var(--primary-color);
    cursor: pointer;
    border: none;
    margin-top: -6px;
}

input[type="range"]::-moz-range-thumb {
    width: 20px;
    height: 20px;
    border-radius: 50%;
    background: var(--primary-color);
    cursor: pointer;
    border: none;
}
```

## Snippet 15
Lines 404-413

```CSS
/* Temperature display */
#temperature-value {
    display: inline-block;
    min-width: 3em;
    text-align: right;
    color: var(--light-text);
    font-size: 0.875rem;
    margin-left: 0.5rem;
}
```

## Snippet 16
Lines 414-424

```CSS
/* Number input */
input[type="number"] {
    -moz-appearance: textfield;
}

input[type="number"]::-webkit-outer-spin-button,
input[type="number"]::-webkit-inner-spin-button {
    -webkit-appearance: none;
    margin: 0;
}
```

## Snippet 17
Lines 425-429

```CSS
/* Form group spacing */
.form-group + .form-group {
    margin-top: 1.5rem;
}
```

## Snippet 18
Lines 430-437

```CSS
/* Provider options spacing */
.provider-options {
    background-color: var(--secondary-color);
    padding: 1rem;
    border-radius: var(--border-radius);
    margin-bottom: 1rem;
}
```

## Snippet 19
Lines 438-450

```CSS
/* Option groups */
.option-group {
    border-bottom: 1px solid var(--border-color);
    padding-bottom: 1rem;
    margin-bottom: 1rem;
}

.option-group:last-child {
    border-bottom: none;
    padding-bottom: 0;
    margin-bottom: 0;
}
```

## Snippet 20
Lines 451-456

```CSS
/* Help text */
.help-text {
    font-size: 0.875rem;
    color: var(--light-text);
    margin-top: 0.25rem;
}
```

