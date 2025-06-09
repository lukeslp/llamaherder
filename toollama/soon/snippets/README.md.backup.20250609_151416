# UI and Utility Components

A collection of reusable JavaScript modules for building accessible chat and UI interfaces.

## Core UI Components

### `chat-ui.js`
Chat interface components and message handling:
- `MessageManager`: Create and manage chat messages with ARIA support
- `InputManager`: Handle input events and container geometry
- `MobileHandler`: Mobile-specific UI adaptations
- `ChatDisplayManager`: Update chat display and show notifications

### `panel_management.js`
Panel and sidebar management:
- `PanelManager`: Handle panel state and transitions
- `PanelLogoManager`: Manage panel logos and empty states
- `PanelObserver`: Watch for panel state changes

### `accessibility_utils.js`
Comprehensive accessibility features:
- Display Mode Management:
  - Light/dark mode toggle with GIF adaptation
  - Persistent preferences
- Font Management:
  - Multiple font families (Open Sans, Inclusive Sans, Arial, System UI)
  - Font size scaling (0.8x to 2.0x)
  - Persistent preferences
- Text-to-Speech:
  - Speech synthesis with rate control
  - Adjustable pitch and speed
  - Priority announcements
- Switch Control:
  - Keyboard navigation enhancement
  - Auto-scanning mode
  - Focus management
- Eye Gaze Support:
  - Dwell clicking
  - Visual feedback
  - Configurable timing
- ARIA and Keyboard Support:
  - Automatic ARIA landmarks
  - Focus management
  - Screen reader announcements
  - Keyboard navigation

### `html_templates.js`
Reusable HTML components with accessibility support:
- `Templates`: Collection of accessible HTML templates
  - Upload area with drag-and-drop
  - Result containers with ARIA live regions
  - Control buttons with proper ARIA attributes
  - Support buttons and settings tray
- `TemplateUtils`: Template manipulation utilities
  - Element creation from templates
  - Container injection
  - Append operations

### `markdown_utils.js`
Markdown processing and academic writing support:
- `MarkdownProcessor`: Advanced markdown configuration
  - Syntax highlighting with language detection
  - Math expressions (inline and block) with KaTeX
  - Tables with multiline and rowspan support
  - Footnotes and definition lists
  - Screen reader optimized math rendering
  - ARIA-enhanced document structure
- Academic Features:
  - Citation Styles:
    - APA, MLA, Chicago, IEEE, Harvard formats
    - In-text citations and references
    - Automatic bibliography generation
  - Document Structure:
    - Abstract, keywords, acknowledgments sections
    - Figure and table numbering
    - Equation numbering and cross-referencing
  - Bibliography Management:
    - Reference tracking and counting
    - Sorted bibliography generation
    - Citation ID generation
- `LinkEmbedder`: Smart link handling
  - YouTube video embedding with accessibility
  - PDF preview and validation
  - DOI and PubMed citations with metadata
  - Async content loading with fallbacks

### `media_utils.js`
Media processing and accessibility features:
- `MediaTypes`: Comprehensive media format support
  - Extensive image format support (JPEG, PNG, WEBP, RAW, etc.)
  - Video format support (MP4, WebM, MOV, etc.)
  - File validation and size limits
  - MIME type checking
- `AltTextGenerator`: Alt text generation utilities
  - Multiple alt text styles (concise, detailed, enhanced)
  - Customizable prompt templates
  - File processing and validation
  - Error handling and reporting
- `TTSProcessor`: Text-to-speech functionality
  - Streaming audio generation
  - Accessible audio player
  - Download capabilities
  - Voice and speed customization

### `prompt_utils.js`
Prompt templates and management:
- `AltTextPrompts`: Alt text generation templates
  - Base prompt for standard descriptions
  - Specialized interpretation prompts
  - Modification commands
- `AcademicPrompts`: Academic writing templates
  - Citation analysis prompts
  - Literature review prompts
  - Research writing prompts
- `PromptManager`: Prompt manipulation utilities
  - Prompt combination
  - Constraint addition
  - Example integration
  - Format specification
- `FormatTemplates`: Response format templates
  - JSON formats
  - Markdown structures
  - Text templates

## Utilities

### `api_utilities.js`
API configuration and messaging:
- `API_CONFIG`: Dynamic base URL configuration
- `MessageRotator`: Rotating message system with fade effects
- `ImageCounter`: Image processing counter with live updates

### `file_handling.js`
File and clipboard operations:
- `FileTypes`: Extensive file type validation (images, videos, documents)
- `FileProcessor`: File processing with preview generation
- `ClipboardHandler`: Cross-platform clipboard operations with fallbacks

### `progress_utilities.js`
Progress and loading state management:
- `ProgressManager`: Customizable progress bar animations
- `LoadingState`: Loading state management with spinners
- `simulateStreamProgress`: Smooth progress simulation for streams

### `error_handling.js`
Error handling and retry logic:
- `ErrorHandler`: Timeout and retry with exponential backoff
- `withErrorHandling`: Error boundary wrapper
- Cleanup and recovery mechanisms

### `conversation_utils.js`
Conversation management and analysis:
- `ConversationExporter`: Export conversations to HTML
  - Styled message formatting
  - Timestamp and metadata inclusion
  - Downloadable HTML files
- `ConversationSummarizer`: AI-powered conversation analysis
  - Main points extraction
  - Action items identification
  - Reference tracking
  - Code snippet analysis
  - Question tracking
- `SummaryUIManager`: Summary display management
  - Loading state handling
  - Panel content updates
  - Syntax highlighting
  - Template-based rendering

## State Management

### `session_management.js`
Session and history management:
- `SessionManager`: Session persistence with TTL
- `ChatHistoryManager`: Chat history with local storage
- `FileManager`: File operations and external link handling
- `StateManager`: Application state initialization

### `bot_management.js`
Bot and assistant management:
- `BotManager`: Bot UI with categories and states
- `AssistantManager`: Assistant interface with avatars
- Premium/Professional state handling

## Usage

Import the modules you need:

```javascript
import { MessageManager, InputManager } from './chat-ui.js';
import { PanelManager } from './panel_management.js';
import { AccessibilityUtils } from './accessibility_utils.js';
```

Initialize accessibility features:

```javascript
// Initialize core accessibility features
const accessibility = AccessibilityUtils;
accessibility.initializeDisplayMode();
accessibility.initializeFontPreferences();

// Set up text-to-speech
const tts = accessibility.initializeTextToSpeech();
tts.speak("Welcome to the application");

// Initialize switch control
const switchControl = accessibility.initializeSwitchControl();
switchControl.toggleScanning(); // Start auto-scanning

// Set up eye gaze
const eyeGaze = accessibility.initializeEyeGaze(1000); // 1 second dwell time
document.addEventListener('mousemove', (e) => {
    eyeGaze.handleGaze(e.target);
});
```

Initialize UI components:

```javascript
// Set up chat components
const messagesList = document.getElementById('messages');
const messageInput = document.getElementById('messageInput');
const sendButton = document.getElementById('sendButton');

InputManager.setupEventListeners(messageInput, sendButton, () => {
    // Handle message sending
});

// Set up panels with accessibility
PanelManager.openPanel('chat', panels, toggleButtons, panelToggles);
```

Handle files and clipboard:

```javascript
import { FileProcessor, ClipboardHandler } from './file_handling.js';

// Set up file handling
const fileProcessor = FileProcessor;
fileProcessor.handleFileSelect(file).then(result => {
    const embed = fileProcessor.createFileEmbed(file, result);
    container.appendChild(embed);
});

// Set up clipboard
ClipboardHandler.setupClipboardHandling(pasteButton, async (file) => {
    await fileProcessor.handleFileSelect(file);
});
```

## Contributing

When adding new functionality:
1. Place it in the appropriate module based on responsibility
2. Follow the existing patterns for error handling and accessibility
3. Document any new exports or configuration options
4. Ensure backward compatibility
5. Include ARIA attributes and keyboard support
6. Test with screen readers and keyboard navigation 

### `interaction_utils.js`
User interaction management:
- `UIStateManager`: UI state handling
  - State initialization
  - Processing state toggling
  - UI reset functionality
- `DragDropHandler`: Drag and drop operations
  - File drop zone setup
  - Highlight and feedback
  - File handling
- `ButtonManager`: Button event management
  - Button setup and configuration
  - Loading state handling
  - Event binding
- `TrayManager`: Settings tray control
  - Tray toggle functionality
  - Click outside handling
  - Keyboard accessibility
- `ScrollManager`: Scroll behavior
  - Auto-scroll functionality
  - Smooth scrolling
  - Scroll position tracking
- `ToastManager`: Notification system
  - Configurable duration
  - Show/hide methods
  - Automatic cleanup
- `InputManager`: Input field handling
  - Submit button integration
  - Enter key support
  - Validation
  - Clear/focus methods
- `StreamManager`: Stream processing
  - Delta updates
  - Completion handling
  - Error management
  - Decoder configuration 