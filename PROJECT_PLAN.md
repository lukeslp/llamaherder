## [Unreleased]

### Git Repository Cleanup

- Resolved issues with git repository management:
  - Fixed issue with large file (Miniconda3 installer) exceeding GitHub's file size limit
  - Added Miniconda installer to .gitignore to prevent future tracking
  - Removed nested git repository in src/bluevibes that was causing push errors
  - Improved repository structure for more reliable deployment

### Environment Variable Loading from .env Files

- Added support for loading environment variables from .env files:
  - Implemented python-dotenv integration in key entry points (herd.py, run_herd.py, herd_tools.py)
  - Added graceful fallback if python-dotenv is not installed, with helpful warning messages
  - Added python-dotenv>=1.0.0 to project_dependencies.txt
  - Environment variables including API keys (XAI_API_KEY, GEMINI_API_KEY, etc.) are now automatically loaded from .env
  - This provides a more secure and convenient way to manage API credentials
  - Users no longer need to set environment variables manually before running the application

### Documentation Updates

 - Added `.github/FUNDING.yml` for project sponsorship links
 - Documented API usage in `snippets/api_interactions.md` and referenced from README

### Enhanced GUI Launch Integration

- Improved GUI launch capabilities with comprehensive integration:
  - Fixed WeasyPrint dependency issues in the GUI module by removing all WeasyPrint dependencies and references
  - Added graceful fallbacks for BeautifulSoup in the PDF generation functionality
  - Added a "Launch GUI" option in the interactive CLI menu for easy access
  - Added 'g' hotkey to directly launch the GUI from anywhere in the CLI
  - Implemented more robust path finding logic to locate herd_gui.py from any working directory
  - Fixed error handling to provide clear feedback if the GUI cannot be launched
  - Ensures the GUI can be launched from both the CLI flag (herd --gui) and the interactive menu
  - Added clear feedback about the GUI web server URL and status
  - Made GUI options consistently available across all entry points to the application

### GUI Launch Integration

- Added direct GUI launch capability from the CLI:
  - Added new `--gui` flag to the CLI command for launching the GUI web application
  - Implemented subprocess-based GUI launcher in `src/herd_ai/herd.py`
  - The command finds the `herd_gui.py` file at the project root and launches it
  - User can now launch the web interface directly with `herd --gui`
  - Displays clear console output with the URL and error handling
  - This resolves the issue of needing to manually locate and run the GUI script

### Comprehensive Process All Feature and Undo Functionality

- Added new "Process All" feature to run all tasks in sequence:
  - Added `--process-all` CLI flag and implemented interactive workflow
  - Users can select which tasks to include via interactive prompts
  - Added a comprehensive workflow that runs dedupe, rename, snippets, citations, idealize, images, and docs in optimal order
  - Each step logs its actions to enable undoing
  - Added rich console formatting for better user experience and accessibility
  - Integrated with the new undo log system

- Added comprehensive undo functionality:
  - Created new `undo_log.py` module to track all operations
  - Added `--undo` CLI flag to revert the last operation
  - Implemented undo handlers for rename, dedupe, and image processing actions
  - Added JSON-based undo log storage in `.herd/undo_log.json`
  - Each operation now logs its parameters and timestamp
  - Provided detailed feedback during undo operations

- Enhanced image processing options:
  - Added interactive prompts for markdown generation, force reprocessing, renaming, and override options
  - Set default values to "yes" for most options to favor thoroughness
  - Added `--generate-md` and `--force` CLI options for non-interactive usage
  - Improved console output formatting for better readability

- Added recursive processing prompts:
  - All operations now prompt for recursive processing by default
  - Set default to "yes" for recursive processing to ensure thorough analysis
  - Added recursive prompt to the "Process All" workflow
  - Preserved the `--recursive` CLI flag for non-interactive mode

### Ollama Renaming Enhancements

- Fixed file renaming with Ollama integration:
  - Updated `src/herd_ai/rename.py` to handle dict responses from `process_with_ai` by extracting the `text` field before parsing suggestions.
  - Modified both `batch_process_files` and `process_rename_file` to use `text_response` for clean filename generation, restoring file renaming functionality.

- Fixed image renaming and metadata embedding for Ollama:
  - Updated `src/herd_ai/image_processor.py` to parse JSON from the `text` field in Ollama's image API responses instead of treating them as plain dicts.
  - Replaced the legacy `as_text` handling logic with robust JSON parsing, ensuring `alt_text`, `description`, `categories`, and `suggested_filename` fields are correctly extracted and applied.

### Ollama Image Processing and CLI Flow Improvements

- Fixed Ollama image processing API request failures:
  - Updated `send_image_prompt_to_ollama` in `src/herd_ai/utils/ollama.py` to use a more compatible payload format for image processing
  - Added fallback mechanism to try both the generate and chat endpoints when processing images with Ollama
  - Improved error handling and reporting for image processing requests
  - Added more robust error detection and reporting in the API response parsing
  - Fixed image encoding to better handle different image formats and sizes
  - This resolves the 400 error responses when trying to process images with Ollama

- Fixed redundant user options in the image processing CLI flow:
  - Removed duplicate prompts for image processing options in `src/herd_ai/cli.py`
  - Centralized user option prompts in the `process_directory` function in `image_processor.py`
  - Added logic to only prompt for options when they haven't been explicitly set
  - Ensured proper integration between the CLI and the image processing module
  - Simplified the image processing action handlers in the CLI to avoid duplicate code
  - This resolves the issue where users were being asked twice for the same options

### Ollama Image Processing Bug Fix

- Fixed critical bug in the Ollama image processing functionality:
  - Modified `send_image_prompt_to_ollama` in `src/herd_ai/utils/ollama.py` to add an `as_text` flag to error responses
  - Updated `image_processor.py` to properly handle dictionary responses with the `as_text` flag
  - Updated `ai_provider.py` to correctly propagate error responses with consistent formatting
  - Fixed error handling in `process_image` and `process_with_ai` functions to prevent "dict has no attribute strip" errors
  - Added comprehensive error handling across the image processing pipeline
  - This resolves the issue where image processing was failing with a 400 error from Ollama

### Image Processing Module Fixes

- Fixed parameter inconsistency in `image_processor.py`:
  - Resolved conflict between the two implementations of `process_directory` function
  - Added missing parameters (`override_md` and `test`) to the wrapper function
  - Updated the function to properly pass all parameters to `process_images_cli`
  - Improved error handling and result reporting
  - Ensured consistent output format that matches the CLI's expectations
  - This fixes the issue where image processing was not working at all from the interactive CLI

### Comprehensive CLI Integration and API Fixes

- Fixed critical issues with multiple modules in the interactive CLI:
  - Added missing `send_image_prompt_to_ollama` function to `src/herd_ai/utils/ollama.py` which was causing image processing to fail
  - Fixed `send_prompt_to_ollama` to accept the `description` parameter for backward compatibility
  - Updated `process_with_ai` and `process_image` functions to correctly call Ollama API with proper parameters
  - Fixed parameter mismatch between the `ai_provider.py` module and the `ollama.py` module
  - Removed Rich Table objects from `idealize_directory` function that were causing CLI display issues
  - Updated `generate_docs` function call to properly include the log_callback

- Standardized Ollama API interface:
  - Fixed parameter inconsistencies across the codebase
  - Ensured all functions have proper error handling and meaningful error messages
  - Added compatibility with the latest Ollama API format for image processing
  - Made parameters consistent across all AI provider interfaces

- Fixed integration issues between components:
  - Resolved parameter naming conflicts between modules
  - Ensured consistent parameter passing throughout the codebase
  - Fixed function signatures to match actual implementations
  - Added proper documentation for all API functions

### CLI Functionality Fixes & Enhancements

- Fixed issues with core modules not working properly when activated through the interactive CLI:
  - Fixed the Citation Extractor (option 3) to properly pass `styles` and `outputs` parameters instead of `formats`
  - Fixed the Idealize Content feature (option 6) to provide proper error handling and feedback
  - Fixed the Generate Docs functionality (option 4) to create necessary directories and provide helpful error messages
  
- Added direct command-line options for all core features outside the interactive menu:
  - Added subcommands for `citations`, `idealize`, and `docs` through the CLI
  - Each subcommand has appropriate options matching their interactive counterparts
  - Command examples:
    - `herd citations --recursive --styles apa mla --outputs md bib`
    - `herd idealize --recursive --exclude .py .js`
    - `herd docs --recursive`
  
- Improved error handling and user feedback:
  - Added detailed success/failure messages for all operations
  - Added progress indicators and file counts
  - Made success/error outputs more visible and consistent
  - Added proper exception handling to prevent silent failures

### Comprehensive CLI Integration Fixes

- Fixed `idealize.py` and `docs.py` modules to properly function from the interactive CLI:
  - Enhanced `idealize_directory()` in `idealize.py` with improved error handling and result reporting
  - Updated `generate_docs()` in `docs.py` to correctly handle log callbacks and return proper result dictionaries
  - Fixed both modules to consistently return success status, error messages, and output paths
  - Ensured both modules create necessary directories and handle file operations safely
  - Both modules now properly handle parameters passed from the CLI including `provider` and `log_callback`
  
- Standardized return values across all modules for consistency:
  - All module functions now return a dictionary with at least `success`, `error`, and output information
  - Error messages are properly formatted and propagated to the user interface
  - Output directories and file paths are consistently returned and displayed
  - All modules provide clear feedback during processing steps

- Enhanced logging and progress reporting:
  - Standardized log callback usage across all modules
  - Removed table display that was causing formatting issues in CLI interface
  - Improved progress indications across both modules
  - Fixed log formatting issues and ensured accessibility of all output text

### Ollama Integration Enhancements

- Added comprehensive Ollama model selection capabilities:
  - Users can now select from all locally installed Ollama models via the Settings menu
  - System resource detection automatically assesses which models are compatible with the user's hardware
  - Models are categorized as "optimal", "compatible", "CPU-only", or "insufficient resources" based on RAM and GPU availability
  - Maintains a history of recently used models for quick switching
  - Displays detailed model information including size, family, and compatibility status
  - Settings persist between sessions

- Added system resource monitoring for Ollama:
  - Detects CPU cores and threads
  - Measures available RAM
  - Identifies GPU type and available VRAM
  - Provides appropriate warnings for models that may run slowly or exceed system capabilities

- Technical improvements:
  - Created new `utils/ollama.py` module with comprehensive Ollama API integration
  - Added configuration persistence for Ollama model selection
  - Updated AI provider integration to use the selected Ollama model
  - Added `psutil` as a dependency for system resource monitoring

### Features
- Refactored `src/herd_ai/citations.py` to allow users to independently select output file format(s) (Markdown, BibTeX, plain text, CSV, etc.) and citation style(s) (APA, MLA, Chicago, IEEE, Vancouver) via CLI or function API.
- Modular extraction for each citation style; easy to add new styles or formats.
- Deduplication of citations by raw string or DOI.
- DOI enrichment via CrossRef is preserved and accessible.
- Outputs a master JSON of all citations in `.herd/citations/citations.json`.
- Generates summary statistics and all requested output formats in `.herd/citations/`.
- CLI entrypoint: `python citations.py /path/to/docs --recursive --styles apa mla --outputs md bib csv`
- All output files are UTF-8 encoded and accessible (screen-reader friendly, semantic markdown, clear CSV headers).
- Comprehensive error handling and logging.
- Extensible and researcher-friendly design.

### API/UX Changes
- Users can now specify `--styles` and `--outputs` independently.
- Output files are named by style (e.g., `CITATIONS.apa.md`, `CITATIONS.mla.bib`).
- CLI help text is clear and comprehensive.

### Accessibility
- All outputs are formatted for accessibility (screen readers, semantic markdown, valid BibTeX, clear CSV headers).
- Errors and progress are surfaced to the user.

### Follow-up Actions
- Update README with new usage examples and accessibility notes.
- Consider adding Vancouver output formatter if needed.

### Bug Fixes
- Corrected the DOI regex pattern in `src/herd_ai/citations.py` to properly escape both single and double quotes inside the character class, resolving the syntax error and ensuring the module can be imported and run from any directory.

### Corrections
- Fixed an unterminated string literal in the DOI regex pattern in `src/herd_ai/citations.py` that caused import errors when running `herd` from a different directory or after pip installation. The regex is now properly escaped and valid Python syntax.
- This restores compatibility for CLI and pip-installed usage across directories.

## Package Improvements

- Fixed import issues that prevented running the package when installed via pip:
  - Removed fallback import patterns that tried local imports without package prefixes.
  - Updated all module imports to use absolute imports (`herd_ai.*`) consistently.
  - Fixed the extract_citations_from_text function to accept an optional styles parameter with a default value of ['apa'].
  
- Improved package structure for modern Python packaging:
  - Added pyproject.toml for modern PEP 517/518 compliant packaging.
  - Added MANIFEST.in to ensure all necessary files are included in the package.
  - Fixed citation regex patterns to avoid syntax errors and escaping issues.
  
- Fixed CLI functionality to work reliably when installed via `pip install -e .`:
  - Updated module imports to prevent "No module named 'rename'" errors.
  - Streamlined imports to improve reliability across different environments.
  - Ensured backward compatibility with existing API calls.

### Technical Details
- Modified DOI regex to use proper string literals and character escaping.
- Fixed reference entries regex patterns to match more reliably.
- Updated all import statements to use absolute package paths.
- Added proper PEP 517 build configuration in pyproject.toml.

## Bug Fixes and Improvements

- Fixed multiple import errors in the CLI module:
  - Added missing `read_project_stats` function to `src/herd_ai/utils/file.py` that analyzes project directories and returns statistics about files, sizes, and extensions
  - Added missing `get_file_count_by_type` function to `src/herd_ai/utils/file.py` that categorizes and counts files by type (document, code, image, etc.)
  - Fixed imports in `src/herd_ai/cli.py` to properly import `scramble_directory` and `generate_sample_files` from `herd_ai.utils.scrambler`
  - These changes ensure the package can be installed and run properly with `pip install -e .` from any directory 

### Robustness and Accessibility Improvements for idealize.py and docs.py

- Refactored `src/herd_ai/idealize.py`:
  - Ensured all CLI and interactive calls pass arguments correctly (`recursive`, `exclude_ext`, `provider`, `log_callback`).
  - Added robust error handling and user feedback throughout the module.
  - Output and backup directories are always created as needed and clearly reported to the user.
  - All outputs are accessible (UTF-8, clear naming, screen-reader friendly).
  - All log and error messages use the provided `log_callback` for consistent, accessible feedback.
  - The function now always returns a result dictionary with `success`, `files_processed`, `files_idealized`, `output_dir`, `backup_dir`, and `error` as appropriate.
  - Fixed any Rich formatting issues in log messages.

- Refactored `src/herd_ai/docs.py`:
  - Added support for a `log_callback` parameter for all feedback and progress reporting.
  - Ensured output directory for README is created as needed and clearly reported.
  - Added robust error handling for all file and directory operations.
  - All outputs are accessible (UTF-8, clear naming, screen-reader friendly).
  - All log and error messages use the provided `log_callback` for consistent, accessible feedback.
  - The function now always returns a result dictionary with `success`, `files_processed`, `readme_path`, and `error` as appropriate.
  - Fixed any Rich formatting issues in log messages.

- Updated CLI integration:
  - Both modules now provide clear, accessible feedback and error messages in both direct CLI and interactive workflows.
  - All outputs and errors are reported in a user-friendly, accessible manner.

- Accessibility and Documentation:
  - All outputs are formatted for accessibility (screen readers, semantic markdown, clear file naming).
  - Improved documentation and changelog to reflect these changes.

### Fixed Interactive CLI Menu for All Modules

- Fixed issues with modules exiting back to menu instantly from the interactive CLI:
  - Fixed `image_processor.py` integration:
    - Properly implemented `process_directory` to return a result dictionary with comprehensive details
    - Added robust error handling and feedback 
    - Added clear success/error status for accessibility
    - Ensured all paths and directories are created correctly
  - Fixed `snippets.py` integration: 
    - Updated `process_directory` to properly handle log_callback
    - Added comprehensive result dictionary with success status
    - Improved error handling and user feedback
  - Updated CLI to properly import and call these functions with all required parameters
  - Ensured all options are properly passed to these functions when called from the interactive menu
  - All modules now correctly capture and display results to the user

Now all features are accessible through both direct CLI commands and the interactive menu interface.

## [Bug Fix] Settings Menu Activation in CLI (Date: YYYY-MM-DD)

### Implementation Details
- Fixed a bug in `src/herd_ai/cli.py` where pressing 's' for "Settings" in the interactive menu (arrow-key navigation mode) did not open the settings menu and instead reloaded the main menu.
- Added logic to the arrow-key navigation input handler to call `handle_settings_menu()` when 's' is pressed, matching the behavior of the fallback (Prompt-based) path.
- After returning from the settings menu, the main menu is re-rendered, and the user can continue interacting as expected.

### Functionality Changes
- The settings menu is now accessible via the 's' key in both navigation modes (arrow-key and prompt-based), improving accessibility and user experience.
- No existing functionality or navigation patterns were broken.

### Accessibility Considerations
- Ensured that the settings menu is accessible via keyboard navigation.
- Provided clear feedback when entering and exiting the settings menu.

### Follow-up Actions
- Consider refactoring input handling logic to further unify special key handling across navigation modes for maintainability.

## [Bug Fix] Ollama Model Selection Settings Menu (Date: YYYY-MM-DD)

### Implementation Details
- Fixed a NameError in the settings menu (option 3) of the interactive CLI where selecting an Ollama model failed due to OLLAMA_TEXT_MODEL not being defined.
- Imported `OLLAMA_TEXT_MODEL` from `herd_ai.config` at the top of `src/herd_ai/cli.py` to ensure a valid default model is always available.
- This resolves the error and allows users to select and switch Ollama models from the settings menu without interruption.

### Functionality Changes
- The settings menu now correctly displays and uses the default Ollama model name when no custom model is set.
- No other functionality or navigation patterns were affected.

### Accessibility Considerations
- Ensured that the model selection menu always presents a valid, descriptive default model name for clarity and usability.

### Follow-up Actions
- Consider making the default model configurable via `config.json` or environment variable for greater flexibility.

## [Bug Fix] Ollama Multimodal Image Processing (Date: YYYY-MM-DD)

### Implementation Details
- Fixed a critical bug in `send_image_prompt_to_ollama` in `src/herd_ai/utils/ollama.py` where the image processing was failing due to incorrect API payload formatting.
- Updated the implementation to follow Ollama's official API documentation for multimodal inputs:
  - Now tries the chat API first using the proper `{"role": "user", "content": prompt, "images": [base64_image]}` format
  - Falls back to the generate API if needed, using the correct `"prompt": prompt, "images": [base64_image]` format
  - Removed the incorrect `[image]` placeholder which was causing the "invalid image index" errors
- The fix resolves both the "invalid image index: 1" and "invalid image index: 0" errors previously encountered
- Also fixes the file renaming functionality that was broken as a consequence of the failing image processing

### Functionality Changes
- Ollama image processing now works correctly for all images, matching the behavior of X.AI and other providers
- The implementation now prioritizes the chat API (as recommended by Ollama docs) and falls back to the generate API if needed
- Improved error handling and logging for better diagnosis of future issues
- File renaming based on AI-detected content now works properly with Ollama

### Accessibility Considerations
- The restored functionality ensures users can get descriptive file names and alt text for images regardless of which AI provider they use
- Consistency across providers (Ollama, X.AI, Gemini) improves the overall user experience and accessibility
- The fix ensures that people using the local Ollama option can access the same quality of image description and processing as those using cloud providers

### Technical Notes
- The bug was caused by an incorrect understanding of the Ollama multimodal API format
- The fix is based on the official Ollama API documentation and best practices
- No other functionality should be affected by this change

### Ollama Renaming Enhancements

- Fixed file renaming with Ollama integration:
  - Updated `src/herd_ai/rename.py` to handle dict responses from `process_with_ai` by extracting the `text` field before parsing suggestions.
  - Modified both `batch_process_files` and `process_rename_file` to use `text_response` for clean filename generation, restoring file renaming functionality.

- Fixed image renaming and metadata embedding for Ollama:
  - Updated `src/herd_ai/image_processor.py` to parse JSON from the `text` field in Ollama's image API responses instead of treating them as plain dicts.
  - Replaced the legacy `as_text` handling logic with robust JSON parsing, ensuring `alt_text`, `description`, `categories`, and `suggested_filename` fields are correctly extracted and applied.

## [Unreleased] - herd_gui.py Web App: Enhanced Metadata and Bulk Operations

##### Added
- **Enhanced Metadata Display:**
  - Added display of both the provider and specific model used for processing
  - Added image dimensions (width x height) display
  - Added file size (KB/MB) display
  - Added file type/extension display
  - Added original filename alongside the renamed file

- **Bulk Operations via Checkbox Selection:**
  - Added checkbox selection for multiple/all processed images
  - Added bulk undo functionality to revert changes for selected images
  - Added bulk retry functionality to reprocess selected images

- **API Enhancements:**
  - Added `/api/bulk_undo` endpoint for reverting multiple images at once
  - Added `/api/bulk_retry` endpoint for reprocessing multiple images at once
  - Enhanced metadata in API responses to include dimensions, file size, file type, etc.

- **Preview Image Improvements:**
  - Fixed issue where preview images would break after processing
  - Ensured preview URLs are updated to point to the renamed files
  - Maintained image previews across undo/retry operations

##### Fixed
- Removed WeasyPrint dependency, which was causing startup errors on macOS
- Improved PDF generation using only ReportLab, with better image and metadata handling
- Enhanced error handling and response formatting for all API endpoints

##### Impact
- Significantly improved metadata display gives users more information about their processed images
- Bulk actions via checkbox selection enhance workflow efficiency for batch operations
- Fixed preview images improve the user experience by showing consistent thumbnails
- Improved PDF reports with actual embedded images and proper metadata

## [Unreleased] - herd_gui.py Web App: Full Brand Restyle & Theme Toggle Fix

##### Added
- Replaced all hardcoded colors in the UI with CSS variables from the unified brand style guide.
- Overhauled the <style> block in HTML_TEMPLATE to use only variables and new class conventions (e.g., .btn, .btn-primary, .form-input, .bg-surface, .rounded, .shadow, etc.).
- Updated all static HTML elements to use the new classes and variables for backgrounds, borders, and text.
- Updated all JavaScript DOM manipulations to ensure dynamically created elements (file-item, buttons, etc.) use the correct classes and inherit CSS variables.
- Ensured all interactive elements have visible focus states and ARIA labels in both light and dark mode.
- Theme toggle now works globally and instantly, switching all UI elements between light and dark themes using only CSS variables.
- Maintained and improved accessibility: all controls remain keyboard and screen-reader accessible, and focus states are visible in both themes.
- Responsive design patterns and semantic structure preserved.

##### Impact
- The UI is now visually consistent, modern, and fully aligned with the brand style guide.
- Theme toggle is robust and works for all elements, including dynamic content.
- Accessibility is improved: all focus states, ARIA labels, and keyboard navigation are preserved and enhanced.
- User experience is more polished, with clear, consistent styling and better support for both light and dark environments.

## [Unreleased] - herd_gui.py Web App: PDF/HTML Export and Real-time Processing

##### Added
- Added PDF export functionality for generating professional reports with all processed images and their metadata
- Added HTML export capability for web-friendly documentation of processed images and metadata
- Implemented real-time image processing that shows results as each image is processed instead of waiting for all to complete
- Added download buttons for PDF and HTML exports alongside the existing Markdown download option
- Added processing counter that shows progress (X/Y images processed) during batch operations

##### Technical Implementation
- Used WeasyPrint for high-quality PDF generation from HTML content
- Implemented Jinja2 templates for consistent HTML report formatting
- Added real-time processing using sequential API calls with progress tracking
- Embedded image data directly in the HTML/PDF exports for completely self-contained documentation
- Processing counter updates in real-time as each image completes

##### Accessibility Improvements
- All generated PDFs maintain accessible structure with proper headings, alt text, and content organization
- HTML exports use semantic markup and maintain proper heading hierarchy
- Processing status is conveyed clearly with both visual indicators and screen-reader accessible text
- Download buttons for different formats have clear, descriptive labels
- Real-time processing provides immediate feedback rather than forcing users to wait for batch completion

##### User Experience Enhancements
- Users can now see results immediately as each image is processed
- Multiple export formats (Markdown, HTML, PDF) provide flexibility for different documentation needs
- Self-contained PDF and HTML reports include embedded images for easy sharing and archiving
- Download options are clearly presented in the UI with descriptive labels
- Processing counter provides clear indication of progress during batch operations

## [Unreleased] - herd_gui.py Web App: Previews, Metadata, and Markdown Download

##### Added
- Image preview thumbnails are now shown for each uploaded/processed image.
- Both concise alt text and long-form description are generated and displayed for each image.
- Metadata is displayed for each image, including whether alt/description was embedded, provider used, and image dimensions.
- Each image has a download button for its generated Markdown (.md) file.
- Added a "Download All Markdown" button to download all .md files as a zip for the current run.

##### Changed
- Improved frontend accessibility: all new controls are keyboard and screen-reader accessible, with clear ARIA labels and semantic HTML.
- Backend now tracks and serves .md files for individual and bulk download.
- Restyled the drop zone to be visually prominent and central:
  - Increased size, bold 3px dashed border, and larger min/max width for prominence.
  - Added a large folder icon and clear, accessible instructions.
  - Strong focus and dragover states for keyboard and mouse users.
  - Ensured the drop zone is always centered in the main container and stands out in both light and dark themes.
  - Improved ARIA labeling and keyboard accessibility.

##### Impact
- Users can visually confirm uploads, review all generated accessibility metadata, and easily download documentation for individual images or in bulk.
- The web app is more robust, accessible, and user-friendly for both individual and batch workflows.

##### Accessibility Considerations
- All new features are accessible by keyboard and screen reader.
- Thumbnails have alt text, and all controls are labeled.
- Download and undo actions are accessible and clearly indicated.

## [Unreleased] - herd_gui.py Web App: Editable Alt Text

##### Added
- **Editable Alt Text:**
  - Added textarea field for each processed image to edit and customize the alt text
  - Added "Save Alt Text" button to save changes
  - Visual feedback when saving (success/error indicators)
  - Changes are saved to the Markdown file automatically

- **Accessibility:**
  - Properly labeled alt text fields with clear focus states
  - Keyboard accessible save buttons
  - Clear success/error feedback for screen readers
  - Easy copying and pasting of alt text

##### Fixed
- Completely removed WeasyPrint dependency that was causing startup errors on macOS
- Ensured alt text is editable even after retrying or bulk processing

##### Impact
- Users can now correct, improve, or customize AI-generated alt text
- The editing capability ensures alt text meets exact content needs
- Improves accessibility workflow by allowing refinement of auto-generated text
- Seamless integration with existing Markdown and file processing systems

## [YYYY-MM-DD] Cohere Provider Integration

### Implementation Details
- Added Cohere as a supported AI provider in both CLI and GUI.
- Updated `herd_ai/config.py` to include `cohere` in `AI_PROVIDERS`, set `DEFAULT_COHERE_MODEL`, and store the API key.
- Implemented `process_with_cohere` in `herd_ai/utils/ai_provider.py` to handle Cohere's unique API and message format.
- Updated provider selection logic in CLI and GUI to allow choosing Cohere.
- Added Cohere to the provider dropdown in the GUI with the label 'Cohere (command-a-03-2025, API)'.
- All CLI and GUI flows (file renaming, image processing, etc.) now support Cohere as a provider.

### Usage Example
- CLI: Use `--provider cohere` to select Cohere for any operation.
- GUI: Select 'Cohere' from the provider dropdown before processing files or images.
- Example Python usage:
  ```python
  from herd_ai.utils.ai_provider import process_with_ai
  result = process_with_ai(
      prompt="Summarize this text: ...",
      provider="cohere",
      model="command-a-03-2025",
      messages=[{"role": "user", "content": "Summarize this text: ..."}]
  )
  print(result["text"])
  ```

### API Key Handling
- The Cohere API key is stored in `herd_ai/config.py` for development. For production, use environment variables or a secure config.

### Accessibility Considerations
- All CLI and GUI feedback for Cohere is consistent with other providers.
- Errors and results are surfaced clearly to the user.

### Follow-up Actions
- Consider supporting Cohere's tool use and structured outputs in future updates.
- Add advanced options for Cohere (e.g., streaming, response format) if needed.

### CLI Module Interface Fixes 

- Fixed all CLI module interfaces to work properly:
  - Fixed the Analysis Report module to correctly process document analysis and show results
  - Fixed the Citations module to handle citation styles and output formats properly
  - Fixed the Idealize Content module to use the idealize_directory wrapper function
  - Fixed the Scramble Files and Sample Files modules to use direct function calls
  - Added proper result handling and user feedback for all modules
  - Ensured all modules properly wait for user input before returning to the menu
  - Fixed issue where some modules would immediately return to the CLI

### OpenAI Provider Integration

- Added comprehensive OpenAI integration:
  - Implemented OpenAI as a full-featured AI provider in `src/herd_ai/utils/ai_provider.py`
  - Added support for both text and image processing with OpenAI models
  - Added OpenAI model listing capability to fetch available models
  - Implemented proper API key handling from config and environment variables
  - Added robust error handling for OpenAI API requests
  - Added base64 image encoding for vision model compatibility
  - Added OpenAI to the list of supported providers in config.py
  - Updated dependencies to include OpenAI>=1.0.0 package

### CLI Navigation Improvements

- Enhanced command-line interface with improved navigation:
  - Added ability to change target directory during a session using the 'd' key from main menu
  - Improved Ctrl-C handling to go back one menu level instead of exiting immediately
  - Added menu level tracking to provide context-aware navigation
  - Return to main menu when pressing Ctrl-C in submenus (like settings or actions)
  - Exit only when pressing Ctrl-C from the main menu
  - Updated help text to indicate directory change option
  - These changes make the CLI more intuitive, user-friendly, and prevent accidental exits

### API Key Configuration Fix

- Fixed critical bug in settings menu API key configuration:
  - Added support for setting API keys for all providers including Cohere and Gemini
  - Implemented comprehensive error handling to prevent crashes when configuring API keys
  - Added support for environment variable fallbacks when config saving fails
  - Fixed UX issues with provider-specific API key configuration
  - Protected against API key setting crashes with try/except blocks
  - This resolves issues where setting API keys for certain providers would crash the application

## Recent Implementations

### Added Cohere Provider Module
- Created a dedicated `src/herd_ai/utils/cohere.py` module that implements all Cohere API functionality
- Features include:
  - Text prompt processing with Cohere models
  - Chat message handling with proper formatting
  - Model listing functionality
  - Comprehensive error handling

### AI Provider System Updates
- Refactored `ai_provider.py` to use the dedicated Cohere module
- Removed embedded Cohere implementation from `ai_provider.py`
- Updated model selection logic in `config.py` to better support Cohere models
- Ensured consistent model naming across all providers

### Configuration and Runtime Improvements
- Fixed inconsistent model variable names in `get_model_for_file` function
- Added better fallback mechanisms for code file handling
- Improved error handling in `run_herd.py`
- Added diagnostic suggestions when imports fail
- Added pydantic version checking to prevent dependency conflicts

### CLI Improvements
- Added comprehensive help screen accessible via '?' key
- Fixed Group import issue in CLI display components