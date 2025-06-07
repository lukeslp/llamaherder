# Code Snippets from toollama/API/api-tools/tools/snippets/processed/media_utils.js

File: `toollama/API/api-tools/tools/snippets/processed/media_utils.js`  
Language: JavaScript  
Extracted: 2025-06-07 05:21:35  

## Snippet 1
Lines 6-34

```JavaScript
// Media Type Support
export const MediaTypes = {
    // Supported media formats
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
Lines 35-37

```JavaScript
if (!file) {
            throw new Error('No file provided');
        }
```

## Snippet 3
Lines 38-40

```JavaScript
if (!file.type.startsWith('image/') && !file.type.startsWith('video/')) {
            throw new Error('Unsupported file type');
        }
```

## Snippet 4
Lines 41-43

```JavaScript
if (file.size > 20 * 1024 * 1024) {
            throw new Error('File size exceeds 20MB limit');
        }
```

## Snippet 5
Lines 44-47

```JavaScript
if (!this.isSupported(file.type)) {
            throw new Error('File format not supported');
        }
        return true;
```

## Snippet 6
Lines 49-52

```JavaScript
};

// Alt Text Generation
export const AltTextGenerator = {
```

## Snippet 7
Lines 55-59

```JavaScript
base: "Generate concise, descriptive alt text for this image that captures its essential details and context.",
        shorter: "Generate brief alt text under 300 characters, focusing on critical details only.",
        longer: "Generate detailed alt text (800+ characters) with comprehensive visual description.",
        enhance: "Use additional context and research to generate detailed alt text, including artist/source attribution.",
        retry: "Generate alternative alt text with a different perspective or focus."
```

## Snippet 8
Lines 60-65

```JavaScript
},

    // Build prompt based on command
    buildPrompt(command = "") {
        let prompt = this.promptTemplates.base;
```

## Snippet 9
Lines 66-70

```JavaScript
if (command && this.promptTemplates[command]) {
            prompt = this.promptTemplates[command];
        }

        return prompt;
```

## Snippet 10
Lines 73-92

```JavaScript
// Process media file for alt text generation
    async processMedia(file, options = {}) {
        try {
            MediaTypes.validateFile(file);

            // Convert file to base64 or appropriate format
            const fileData = await this.prepareFileData(file);

            // Generate alt text based on options
            const altText = await this.generateAltText(fileData, options);

            return {
                success: true,
                altText,
                file: {
                    name: file.name,
                    type: file.type,
                    size: file.size
                }
            };
```

## Snippet 11
Lines 93-101

```JavaScript
} catch (error) {
            console.error('Media processing error:', error);
            return {
                success: false,
                error: error.message,
                file: file ? {
                    name: file.name,
                    type: file.type,
                    size: file.size
```

## Snippet 12
Lines 107-130

```JavaScript
// Prepare file data for processing
    async prepareFileData(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = (e) => resolve(e.target.result);
            reader.onerror = (e) => reject(new Error('File reading failed'));
            reader.readAsDataURL(file);
        });
    },

    // Generate alt text using API
    async generateAltText(fileData, options = {}) {
        const response = await fetch(`${options.apiUrl || '/api/alt-text'}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                image: fileData,
                command: options.command || 'base',
                prompt: this.buildPrompt(options.command)
            })
        });
```

## Snippet 13
Lines 131-135

```JavaScript
if (!response.ok) {
            throw new Error('Alt text generation failed');
        }

        return await response.json();
```

## Snippet 14
Lines 137-156

```JavaScript
};

// Text-to-Speech Processing
export const TTSProcessor = {
    async generateTTS(text, options = {}) {
        try {
            const response = await fetch(`${options.apiUrl || '/api/tts'}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'text/event-stream'
                },
                body: JSON.stringify({
                    text,
                    voice: options.voice || 'default',
                    speed: options.speed || 1.0,
                    pitch: options.pitch || 1.0
                })
            });
```

## Snippet 15
Lines 157-162

```JavaScript
if (!response.ok) {
                throw new Error('TTS generation failed');
            }

            const audioUrl = await this.processStreamResponse(response);
            return this.createAudioElement(audioUrl);
```

## Snippet 16
Lines 163-166

```JavaScript
} catch (error) {
            console.error('TTS generation error:', error);
            throw error;
        }
```

## Snippet 17
Lines 167-172

```JavaScript
},

    async processStreamResponse(response) {
        const reader = response.body.getReader();
        let content = '';
```

## Snippet 18
Lines 175-179

```JavaScript
if (done) break;

            const chunk = new TextDecoder().decode(value);
            const lines = chunk.split('\n');
```

## Snippet 19
Lines 183-185

```JavaScript
if (data.type === 'delta') {
                        content += data.content;
                    }
```

## Snippet 20
Lines 188-190

```JavaScript
}

        const urlMatch = content.match(/\((https?:\/\/[^\s]+)\)/);
```

## Snippet 21
Lines 191-195

```JavaScript
if (!urlMatch) {
            throw new Error('No audio URL found in response');
        }

        return urlMatch[1];
```

## Snippet 22
Lines 196-219

```JavaScript
},

    createAudioElement(audioUrl) {
        const container = document.createElement('div');
        container.className = 'audio-container';
        container.setAttribute('role', 'region');
        container.setAttribute('aria-label', 'Audio Player');

        const audio = document.createElement('audio');
        audio.controls = true;
        audio.src = audioUrl;
        audio.setAttribute('aria-label', 'Text-to-Speech Audio');
        container.appendChild(audio);

        const downloadLink = document.createElement('a');
        downloadLink.href = audioUrl;
        downloadLink.download = 'tts_output.mp3';
        downloadLink.textContent = 'Download Audio';
        downloadLink.className = 'download-link';
        downloadLink.setAttribute('aria-label', 'Download audio file');
        container.appendChild(downloadLink);

        return container;
    }
```

