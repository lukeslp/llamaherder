# Code Snippets from toollama/API/api-tools/tools/snippets/processed/accessibility_utils.js

File: `toollama/API/api-tools/tools/snippets/processed/accessibility_utils.js`  
Language: JavaScript  
Extracted: 2025-06-07 05:20:56  

## Snippet 1
Lines 6-20

```JavaScript
export const AccessibilityUtils = {
    // Display Mode Management
    initializeDisplayMode() {
        const savedMode = localStorage.getItem("displayMode") || "light-mode";
        document.body.classList.remove("light-mode", "dark-mode");
        document.body.classList.add(savedMode);
    },

    toggleDayNightMode() {
        const currentMode = localStorage.getItem("displayMode") || "light-mode";
        const newMode = currentMode === "dark-mode" ? "light-mode" : "dark-mode";
        document.body.classList.remove("light-mode", "dark-mode");
        document.body.classList.add(newMode);
        localStorage.setItem("displayMode", newMode);
```

## Snippet 2
Lines 23-28

```JavaScript
if (loadingGif) {
            loadingGif.src = loadingGif.src.replace(
                `triangle_construct_${currentMode.split('-')[0]}.gif`,
                `triangle_construct_${newMode.split('-')[0]}.gif`
            );
        }
```

## Snippet 3
Lines 37-60

```JavaScript
],

    currentFontIndex: 0,

    toggleFont() {
        const root = document.documentElement;
        this.currentFontIndex = (this.currentFontIndex + 1) % this.availableFonts.length;
        const newFont = this.availableFonts[this.currentFontIndex];

        // Remove all font classes
        this.availableFonts.forEach((font) => {
            root.classList.remove(font.class);
        });

        // Add new font class
        root.classList.add(newFont.class);
        root.style.setProperty("--font-primary", `'${newFont.name}', sans-serif`);
        localStorage.setItem("preferredFont", newFont.name);

        return newFont.name;
    },

    initializeFontPreferences() {
        const savedFont = localStorage.getItem("preferredFont");
```

## Snippet 4
Lines 63-66

```JavaScript
if (fontIndex !== -1) {
                this.currentFontIndex = fontIndex - 1; // Subtract 1 because toggleFont will add 1
                this.toggleFont();
            }
```

## Snippet 5
Lines 68-72

```JavaScript
},

    // Font Size Management
    initializeFontScale() {
        const savedScale = localStorage.getItem("fontScale");
```

## Snippet 6
Lines 73-76

```JavaScript
if (savedScale) {
            document.documentElement.style.setProperty("--font-scale", savedScale);
            this.updateFontSizeDisplay(savedScale);
        }
```

## Snippet 7
Lines 77-85

```JavaScript
},

    changeFontSize(action) {
        const root = document.documentElement;
        const currentScale = parseFloat(
            getComputedStyle(root).getPropertyValue("--font-scale")
        );

        let newScale;
```

## Snippet 8
Lines 88-91

```JavaScript
} else if (action === "decrease") {
            newScale = Math.max(currentScale - 0.1, 0.8);
        }
```

## Snippet 9
Lines 92-96

```JavaScript
if (newScale) {
            root.style.setProperty("--font-scale", newScale);
            localStorage.setItem("fontScale", newScale.toString());
            this.updateFontSizeDisplay(newScale);
        }
```

## Snippet 10
Lines 97-108

```JavaScript
},

    resetFontSize() {
        const defaultScale = 1.0;
        const root = document.documentElement;
        root.style.setProperty("--font-scale", `${defaultScale}`);
        localStorage.setItem("fontScale", `${defaultScale}`);
        this.updateFontSizeDisplay(defaultScale);
    },

    updateFontSizeDisplay(scale) {
        const fontSizeDisplay = document.getElementById("currentFontSize");
```

## Snippet 11
Lines 109-111

```JavaScript
if (fontSizeDisplay) {
            fontSizeDisplay.textContent = `${Math.round(scale * 100)}%`;
        }
```

## Snippet 12
Lines 112-156

```JavaScript
},

    // Text-to-Speech
    initializeTextToSpeech() {
        const synth = window.speechSynthesis;

        return {
            speak: (text, priority = "polite") => {
                const utterance = new SpeechSynthesisUtterance(text);
                utterance.rate = parseFloat(localStorage.getItem("speechRate")) || 1;
                utterance.pitch = parseFloat(localStorage.getItem("speechPitch")) || 1;
                synth.speak(utterance);
            },

            adjustSpeechRate: (direction) => {
                const currentRate = parseFloat(localStorage.getItem("speechRate")) || 1;
                const newRate = direction === "increase"
                    ? Math.min(currentRate + 0.1, 2)
                    : Math.max(currentRate - 0.1, 0.5);
                localStorage.setItem("speechRate", newRate.toString());
                return newRate;
            }
        };
    },

    // Switch Control
    initializeSwitchControl() {
        let currentFocusIndex = 0;
        const focusableElements = 'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])';
        let scanning = false;
        let scanInterval;

        return {
            moveToNextElement: () => {
                const elements = Array.from(document.querySelectorAll(focusableElements));
                currentFocusIndex = (currentFocusIndex + 1) % elements.length;
                elements[currentFocusIndex].focus();
            },

            selectCurrentElement: () => {
                document.activeElement.click();
            },

            toggleScanning: () => {
                scanning = !scanning;
```

## Snippet 13
Lines 157-162

```JavaScript
if (scanning) {
                    scanInterval = setInterval(() => {
                        const elements = Array.from(document.querySelectorAll(focusableElements));
                        currentFocusIndex = (currentFocusIndex + 1) % elements.length;
                        elements[currentFocusIndex].focus();
                    }, 2000);
```

## Snippet 14
Lines 163-166

```JavaScript
} else {
                    clearInterval(scanInterval);
                }
                return scanning;
```

## Snippet 15
Lines 169-177

```JavaScript
},

    // Eye Gaze Support
    initializeEyeGaze(dwellTime = 1000) {
        let dwellTimer;
        let lastElement;

        return {
            handleGaze: (element) => {
```

## Snippet 16
Lines 178-181

```JavaScript
if (element !== lastElement) {
                    clearTimeout(dwellTimer);
                    lastElement = element;
```

## Snippet 17
Lines 182-188

```JavaScript
if (element.matches('button, [role="button"]')) {
                        dwellTimer = setTimeout(() => {
                            element.click();
                            element.classList.add("dwell-activated");
                            setTimeout(() => element.classList.remove("dwell-activated"), 200);
                        }, dwellTime);
                    }
```

## Snippet 18
Lines 192-197

```JavaScript
},

    // ARIA and Keyboard Support
    setupAccessibilityFeatures() {
        // Set up ARIA landmarks
        document.querySelectorAll('[role="region"]').forEach(region => {
```

## Snippet 19
Lines 198-200

```JavaScript
if (!region.hasAttribute('aria-label')) {
                region.setAttribute('aria-label', region.id || 'Content region');
            }
```

## Snippet 20
Lines 205-207

```JavaScript
if (!element.hasAttribute('tabindex')) {
                element.setAttribute('tabindex', '0');
            }
```

## Snippet 21
Lines 210-217

```JavaScript
// Add screen reader announcements for dynamic content
        const announcer = document.createElement('div');
        announcer.setAttribute('aria-live', 'polite');
        announcer.setAttribute('aria-atomic', 'true');
        announcer.className = 'sr-only';
        document.body.appendChild(announcer);

        return announcer;
```

