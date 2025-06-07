# Code Snippets from toollama/API/api-tools/tools/snippets/core/media/tts.js

File: `toollama/API/api-tools/tools/snippets/core/media/tts.js`  
Language: JavaScript  
Extracted: 2025-06-07 05:23:27  

## Snippet 1
Lines 5-21

```JavaScript
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

## Snippet 2
Lines 22-27

```JavaScript
if (!response.ok) {
                throw new Error('TTS generation failed');
            }

            const audioUrl = await this.processStreamResponse(response);
            return this.createAudioElement(audioUrl);
```

## Snippet 3
Lines 28-31

```JavaScript
} catch (error) {
            console.error('TTS generation error:', error);
            throw error;
        }
```

## Snippet 4
Lines 32-37

```JavaScript
},

    async processStreamResponse(response) {
        const reader = response.body.getReader();
        let content = '';
```

## Snippet 5
Lines 40-44

```JavaScript
if (done) break;

            const chunk = new TextDecoder().decode(value);
            const lines = chunk.split('\n');
```

## Snippet 6
Lines 48-50

```JavaScript
if (data.type === 'delta') {
                        content += data.content;
                    }
```

## Snippet 7
Lines 53-55

```JavaScript
}

        const urlMatch = content.match(/\((https?:\/\/[^\s]+)\)/);
```

## Snippet 8
Lines 56-60

```JavaScript
if (!urlMatch) {
            throw new Error('No audio URL found in response');
        }

        return urlMatch[1];
```

## Snippet 9
Lines 61-84

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

