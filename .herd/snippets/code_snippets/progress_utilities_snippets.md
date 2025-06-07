# Code Snippets from toollama/API/api-tools/tools/snippets/processed/progress_utilities.js

File: `toollama/API/api-tools/tools/snippets/processed/progress_utilities.js`  
Language: JavaScript  
Extracted: 2025-06-07 05:21:34  

## Snippet 1
Lines 6-14

```JavaScript
// Progress Bar Management
export const ProgressManager = {
    progressInterval: null,

    startProgress(progressBar, maxProgress = 90, increment = 1, interval = 300) {
        let progress = 0;
        progressBar.style.width = "0%";

        this.progressInterval = setInterval(() => {
```

## Snippet 2
Lines 15-18

```JavaScript
if (progress < maxProgress) {
                progress += increment;
                progressBar.style.width = `${progress}%`;
            }
```

## Snippet 3
Lines 23-26

```JavaScript
if (this.progressInterval) {
            clearInterval(this.progressInterval);
            this.progressInterval = null;
        }
```

## Snippet 4
Lines 27-29

```JavaScript
if (progressBar) {
            progressBar.style.width = "0%";
        }
```

## Snippet 5
Lines 33-35

```JavaScript
if (progressBar) {
            progressBar.style.width = `${progress}%`;
        }
```

## Snippet 6
Lines 36-41

```JavaScript
},

    async simulateStreamProgress(progressBar, startProgress = 40, maxProgress = 95, increment = 0.8, interval = 300) {
        let currentProgress = startProgress;
        return new Promise((resolve) => {
            const streamInterval = setInterval(() => {
```

## Snippet 7
Lines 42-44

```JavaScript
if (currentProgress < maxProgress) {
                    currentProgress += increment;
                    this.setProgress(progressBar, currentProgress);
```

## Snippet 8
Lines 52-56

```JavaScript
};

// Loading State Management
export const LoadingState = {
    setLoadingState(button, isLoading, loadingText = 'Processing...') {
```

## Snippet 9
Lines 57-60

```JavaScript
if (isLoading) {
            button.classList.add("loading");
            button.innerHTML = `<i class="fas fa-spinner fa-spin"></i> ${loadingText}`;
            button.disabled = true;
```

## Snippet 10
Lines 65-72

```JavaScript
},

    async withLoadingState(button, operation, loadingText = 'Processing...') {
        const originalButtonText = button.innerHTML;
        this.setLoadingState(button, true, loadingText);

        try {
            await operation();
```

