# Code Snippets from toollama/API/api-tools/tools/snippets/processed/file_handling.js

File: `toollama/API/api-tools/tools/snippets/processed/file_handling.js`  
Language: JavaScript  
Extracted: 2025-06-07 05:21:25  

## Snippet 1
Lines 6-33

```JavaScript
// Supported File Types
export const FileTypes = {
    supportedTypes: [
        // Image Formats
        'image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp',
        'image/heic', 'image/heif', 'image/avif', 'image/tiff', 'image/bmp',
        'image/x-icon', 'image/vnd.microsoft.icon', 'image/svg+xml',
        'image/vnd.adobe.photoshop', 'image/x-adobe-dng', 'image/x-canon-cr2',
        'image/x-nikon-nef', 'image/x-sony-arw', 'image/x-fuji-raf',
        'image/x-olympus-orf', 'image/x-panasonic-rw2', 'image/x-rgb',
        'image/x-portable-pixmap', 'image/x-portable-graymap',
        'image/x-portable-bitmap',
        // Video Formats
        'video/mp4', 'video/quicktime', 'video/webm', 'video/x-msvideo',
        'video/x-flv', 'video/x-ms-wmv', 'video/x-matroska', 'video/3gpp',
        'video/x-m4v', 'video/x-ms-asf', 'video/x-mpegURL', 'video/x-ms-vob',
        'video/x-ms-tmp', 'video/x-mpeg', 'video/mp2t',
        // Generic
        'application/octet-stream'
    ],

    isSupported(fileType) {
        return this.supportedTypes.includes(fileType) ||
               fileType.startsWith('image/') ||
               fileType.startsWith('video/');
    },

    validateFile(file) {
```

## Snippet 2
Lines 34-36

```JavaScript
if (!file || (!file.type.startsWith('image/') && !file.type.startsWith('video/'))) {
            throw new Error('Unsupported file type');
        }
```

## Snippet 3
Lines 37-39

```JavaScript
if (file.size > 20 * 1024 * 1024) {
            throw new Error('File size exceeds limit');
        }
```

## Snippet 4
Lines 40-43

```JavaScript
if (!this.isSupported(file.type)) {
            throw new Error('Sorry, that file type confuses me.');
        }
        return true;
```

## Snippet 5
Lines 45-49

```JavaScript
};

// File Processing
export const FileProcessor = {
    async handleFileSelect(file) {
```

## Snippet 6
Lines 50-53

```JavaScript
if (!FileTypes.isSupported(file.type)) {
            throw new Error('Unsupported file type');
        }
        return await this.processFile(file);
```

## Snippet 7
Lines 54-68

```JavaScript
},

    async processFile(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = (e) => resolve(e.target.result);
            reader.onerror = (e) => reject(e);
            reader.readAsDataURL(file);
        });
    },

    createFileEmbed(file, fileUrl) {
        const container = document.createElement('div');
        container.className = 'file-embed';
```

## Snippet 8
Lines 69-73

```JavaScript
if (file.type.startsWith('image/')) {
            const img = document.createElement('img');
            img.src = fileUrl;
            img.alt = file.name;
            container.appendChild(img);
```

## Snippet 9
Lines 74-81

```JavaScript
} else if (file.type.startsWith('video/')) {
            const video = document.createElement('video');
            video.src = fileUrl;
            video.controls = true;
            container.appendChild(video);
        }

        return container;
```

## Snippet 10
Lines 85-90

```JavaScript
if (file.type === "text/html") {
            const url = URL.createObjectURL(file);
            window.open(url, "_blank");
            return true;
        }
        return false;
```

## Snippet 11
Lines 92-99

```JavaScript
};

// Clipboard Handler
export const ClipboardHandler = {
    async copyToClipboard(text) {
        try {
            await navigator.clipboard.writeText(text);
            return true;
```

## Snippet 12
Lines 100-103

```JavaScript
} catch (err) {
            console.error("Copy failed:", err);
            throw new Error("Copy failed, try again");
        }
```

## Snippet 13
Lines 104-111

```JavaScript
},

    setupClipboardHandling(pasteButton, processImageCallback) {
        // Universal paste handler
        document.addEventListener('paste', async (e) => {
            e.preventDefault();

            const clipboardData = e.clipboardData || window.clipboardData;
```

## Snippet 14
Lines 112-118

```JavaScript
if (!clipboardData) {
                console.log('No clipboard data available');
                return;
            }

            // Handle pasted files
            const clipboardFiles = clipboardData.files;
```

## Snippet 15
Lines 121-125

```JavaScript
if (FileTypes.isSupported(file.type)) {
                        console.log('File found in clipboard:', file.type);
                        await processImageCallback(file);
                        return;
                    }
```

## Snippet 16
Lines 127-130

```JavaScript
}

            // Handle clipboard items
            const items = clipboardData.items;
```

## Snippet 17
Lines 135-138

```JavaScript
if (file && FileTypes.isSupported(file.type)) {
                            await processImageCallback(file);
                            return;
                        }
```

## Snippet 18
Lines 154-157

```JavaScript
},

    async handleAndroidPaste(processImageCallback) {
        try {
```

## Snippet 19
Lines 162-164

```JavaScript
if (type.startsWith('image/') || type.startsWith('video/')) {
                            const blob = await item.getType(type);
                            const fileExtension = type.split('/')[1];
```

## Snippet 20
Lines 165-167

```JavaScript
const file = new File([blob], `pasted-file.${fileExtension}`, { type });
                            await processImageCallback(file);
                            return;
```

## Snippet 21
Lines 175-178

```JavaScript
} catch (e) {
            console.error('Error reading clipboard:', e);
            alert('Failed to read clipboard. Please ensure the app has clipboard permissions.');
        }
```

## Snippet 22
Lines 179-188

```JavaScript
},

    async handleDefaultPaste() {
        const tempTextArea = document.createElement('textarea');
        tempTextArea.style.cssText = 'opacity:0;position:absolute;left:-9999px;';
        document.body.appendChild(tempTextArea);
        tempTextArea.focus();

        try {
            await document.execCommand('paste');
```

