# Code Snippets from toollama/API/api-tools/tools/snippets/core/progress/bar.js

File: `toollama/API/api-tools/tools/snippets/core/progress/bar.js`  
Language: JavaScript  
Extracted: 2025-06-07 05:22:01  

## Snippet 1
Lines 18-22

```JavaScript
startProgress(progressBar, maxProgress = 90, increment = 1, interval = 300) {
        let progress = 0;
        progressBar.style.width = "0%";

        this.progressInterval = setInterval(() => {
```

## Snippet 2
Lines 23-26

```JavaScript
if (progress < maxProgress) {
                progress += increment;
                progressBar.style.width = `${progress}%`;
            }
```

## Snippet 3
Lines 35-38

```JavaScript
if (this.progressInterval) {
            clearInterval(this.progressInterval);
            this.progressInterval = null;
        }
```

## Snippet 4
Lines 39-41

```JavaScript
if (progressBar) {
            progressBar.style.width = "0%";
        }
```

## Snippet 5
Lines 50-52

```JavaScript
if (progressBar) {
            progressBar.style.width = `${progress}%`;
        }
```

## Snippet 6
Lines 64-67

```JavaScript
async simulateStreamProgress(progressBar, startProgress = 40, maxProgress = 95, increment = 0.8, interval = 300) {
        let currentProgress = startProgress;
        return new Promise((resolve) => {
            const streamInterval = setInterval(() => {
```

## Snippet 7
Lines 68-70

```JavaScript
if (currentProgress < maxProgress) {
                    currentProgress += increment;
                    this.setProgress(progressBar, currentProgress);
```

