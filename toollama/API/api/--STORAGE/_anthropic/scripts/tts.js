export class TTSHandler {
    constructor() {
        console.log('Initializing TTSHandler');
        this.ttsControl = document.getElementById('ttsControl');
        this.ttsAudio = document.getElementById('ttsAudio');
        
        if (!this.ttsControl || !this.ttsAudio) {
            console.log('TTS elements not found, TTS functionality disabled');
            this.isProcessingTTS = false;
            return;
        }
        
        this.audioElement = this.setupTTSControls();
        this.isProcessingTTS = false;
    }

    setupTTSControls() {
        console.log('Setting up TTS controls');
        
        if (!this.ttsControl || !this.ttsAudio) {
            return null;
        }
        
        const newAudio = this.ttsAudio.cloneNode(true);
        this.ttsAudio.parentNode.replaceChild(newAudio, this.ttsAudio);
        
        this.ttsControl.addEventListener('click', async () => {
            try {
                if (newAudio.paused) {
                    console.log('Attempting to play audio');
                    await newAudio.play();
                } else {
                    newAudio.pause();
                }
            } catch (error) {
                console.error('Error playing audio:', error);
                this.updateTTSState('error');
            }
        });

        newAudio.addEventListener('play', () => {
            console.log('Audio started playing');
            this.updateTTSState('playing');
        });
        newAudio.addEventListener('pause', () => {
            console.log('Audio paused');
            this.updateTTSState('ready');
        });
        newAudio.addEventListener('ended', () => {
            console.log('Audio playback ended');
            this.updateTTSState('ready');
        });
        newAudio.addEventListener('error', () => {
            console.error('Audio error occurred');
            this.updateTTSState('error');
        });
        
        return newAudio;
    }

    updateTTSState(state, message = '') {
        console.log('Updating TTS state to:', state, message);
        const control = document.getElementById('ttsControl');
        const container = document.getElementById('ttsContainer');
        
        if (!control || !container) return;
        
        // Remove all state classes
        control.classList.remove('loading', 'playing', 'error', 'ready');
        
        // Update button state
        control.classList.add(state);
        control.setAttribute('aria-busy', state === 'loading');
        
        // Update icons
        const playIcon = control.querySelector('.play-icon');
        const pauseIcon = control.querySelector('.pause-icon');
        const errorIcon = control.querySelector('.error-icon');
        const spinner = control.querySelector('.tts-loading-spinner');
        
        if (playIcon) playIcon.classList.toggle('active', state === 'ready');
        if (pauseIcon) pauseIcon.classList.toggle('active', state === 'playing');
        if (errorIcon) errorIcon.classList.toggle('active', state === 'error');
        if (spinner) spinner.classList.toggle('hidden', state !== 'loading');
        
        // Update ARIA labels
        const labels = {
            loading: 'Generating audio description',
            ready: 'Play audio description',
            playing: 'Pause audio description',
            error: 'Audio generation failed'
        };
        control.setAttribute('aria-label', labels[state]);
        
        // Show error message if provided
        if (message && state === 'error') {
            this.showToast(message, 'error');
        }
    }

    async handleTTS(text, voice, apiCallFunction, apiKey, apiBaseUrl, ttsBotId) {
        if (!this.ttsControl || !this.ttsAudio || !this.audioElement) {
            console.log('TTS functionality is disabled');
            return;
        }
        
        console.log('Handling TTS request:', { voice, ttsBotId });
        const ttsContainer = document.getElementById('ttsContainer');
        const ttsControl = document.getElementById('ttsControl');
        const ttsAudio = document.getElementById('ttsAudio');
        
        if (!ttsContainer || !ttsControl || !ttsAudio) {
            console.error('Required TTS elements not found');
            return;
        }

        this.updateTTSState('loading');
        ttsContainer.classList.remove('hidden');

        try {
            const audioUrl = await this.generateTTS(text, voice, apiCallFunction, apiKey, apiBaseUrl, ttsBotId);
            console.log('Generated audio URL:', audioUrl);
            
            ttsAudio.innerHTML = '';
            const source = document.createElement('source');
            source.src = audioUrl;
            source.type = this.getAudioMimeType(audioUrl);
            ttsAudio.appendChild(source);
            
            await new Promise((resolve, reject) => {
                ttsAudio.onloadedmetadata = resolve;
                ttsAudio.onerror = () => reject(new Error('Failed to load audio'));
                ttsAudio.load();
            });
            
            this.updateTTSState('ready');
            
            // Set up audio event listeners
            ttsAudio.onplay = () => this.updateTTSState('playing');
            ttsAudio.onpause = () => this.updateTTSState('ready');
            ttsAudio.onended = () => this.updateTTSState('ready');
            ttsAudio.onerror = () => this.updateTTSState('error', 'Audio playback failed');
            
        } catch (error) {
            console.error('TTS generation failed:', error);
            this.updateTTSState('error', 'Failed to generate audio description');
        }
    }

    async generateTTS(text, voice, apiCallFunction, apiKey, apiBaseUrl, ttsBotId) {
        console.log('Generating TTS with params:', { text, voice, ttsBotId });
        const payloadText = `Generate text to speech in ${voice} voice: ${text}`;
        
        try {
            const response = await apiCallFunction(payloadText, null, ttsBotId);
            const responseText = await response.text();
            const lines = responseText.split('\n');
            let audioUrl = '';
            
            console.log('Processing TTS response');
            for (const line of lines) {
                if (line.startsWith('data: ')) {
                    try {
                        const data = JSON.parse(line.slice(6));
                        if (data.type === 'delta' && data.content) {
                            audioUrl += data.content;
                        }
                    } catch (e) {
                        console.warn('Error parsing response line:', e);
                    }
                }
            }
            
            if (!audioUrl) {
                console.error('No audio URL found in response');
                throw new Error("No audio URL constructed from response");
            }
            
            const cleanUrl = audioUrl.replace(/["\\s]+$/, '');
            console.log('Successfully generated audio URL');
            return cleanUrl;
        } catch (error) {
            console.error('Error generating TTS:', error);
            throw error;
        }
    }

    showTTSError(message) {
        console.error('Showing TTS error:', message);
        const status = document.querySelector('.tts-status');
        if (status) {
            status.innerHTML = `<div class="tts-error">${message}</div>`;
        } else {
            console.warn('TTS status element not found');
        }
    }

    getAudioMimeType(url) {
        const extension = url.split('.').pop().split(/[#?]/)[0].toLowerCase();
        console.log('Determining MIME type for extension:', extension);
        switch(extension) {
            case 'mp3': return 'audio/mpeg';
            case 'wav': return 'audio/wav';
            case 'ogg': return 'audio/ogg';
            default: return 'audio/mpeg';
        }
    }
}