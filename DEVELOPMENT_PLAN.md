# Herd AI Development Guide

This document explains the package structure and development workflow for Herd AI (formerly LlamaCleaner).

## Package Structure

Herd AI uses a modern `src`-based layout following best practices for Python packaging:

```
herd-ai/
├── LICENSE
├── README.md                 # User documentation
├── DEVELOPMENT.md            # Developer documentation (this file)
├── PROJECT_PLAN.md           # Detailed project history and roadmap
├── setup.py                  # Traditional setup script
├── pyproject.toml            # Modern build configuration (PEP 517/518)
├── MANIFEST.in               # Package data specifications
├── herd.py                   # Entry point script
├── run_herd.py               # Convenience runner script
└── src/                      # Source directory
    └── herd_ai/              # Main package
        ├── __init__.py       # Package initialization
        ├── __main__.py       # Module entry point
        ├── cli.py            # Command line interface
        ├── rename.py         # File renaming functionality
        ├── snippets.py       # Code snippet extraction
        ├── citations.py      # Citation extraction and management
        ├── docs.py           # Documentation generation
        ├── idealize.py       # Content idealization
        ├── image_processor.py # Image processing and alt text
        # ... other modules
        └── utils/            # Utility functions
            ├── __init__.py
            ├── ollama.py     # Ollama API integration
            ├── xai.py        # X.AI API integration
            ├── gemini.py     # Google Gemini API integration
            ├── ai_provider.py # AI provider abstraction
            ├── file.py       # File handling utilities
            # ... other utility modules
```

## Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/lukesteuber/herd.git
   cd herd
   ```

2. Create a development environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install in development mode:
   ```bash
   pip install -e .
   ```

## Key Components

- **src/herd_ai**: The main package containing all functionality
- **src/herd_ai/cli.py**: The command-line interface
- **src/herd_ai/utils/**: Utility functions used across the package
- **src/herd_ai/config.py**: Configuration for AI providers, paths, and settings

## AI Provider Support

Herd AI supports multiple AI providers that can be used interchangeably:

1. **Ollama** (default): Local models via Ollama API
   - Configure with environment variables: `OLLAMA_API_URL`, `OLLAMA_TEXT_MODEL`, `OLLAMA_IMAGE_MODEL`
   - Default models: `gemma3:4b` (text), `gemma3:4b` (images)

2. **X.AI**: X.AI/Grok models via API
   - Configure with environment variables: `XAI_API_URL`, `XAI_API_KEY`, `XAI_TEXT_MODEL`, `XAI_IMAGE_MODEL`
   - Default models: `grok-3-beta` (text), `grok-2-vision-latest` (images)
   
3. **Google Gemini**: Google's Gemini API
   - Configure with environment variables: `GEMINI_API_URL`, `GEMINI_API_KEY`, `GEMINI_TEXT_MODEL`, `GEMINI_IMAGE_MODEL`
   - Default models: `gemini-2.5-flash-preview-04-17` (text and images)

4. **OpenAI**: OpenAI models via their API
   - Configure with environment variable: `OPENAI_API_KEY`
   - Default model: `gpt-4o` (text and images)
   
5. **Cohere**: Cohere models via their API
   - Configure with environment variable: `COHERE_API_KEY`
   - Default model: `command-a-03-2025`

When developing new features, always support all providers through the provider parameter:

```python
def my_function(file_path, provider=None):
    # Get provider from config if not explicitly provided
    if provider is None:
        provider = get_provider_from_config()
    
    # Always pass provider to AI functions
    result = process_with_ai(file_path, prompt, provider=provider)
```

## CLI Best Practices

When enhancing the CLI in `src/herd_ai/cli.py`:

1. **Handle KeyboardInterrupt (Ctrl-C) gracefully**:
   - Return to the main menu when in submenus instead of exiting
   - Only exit the application when at main menu level
   - Never let exceptions crash the application

2. **Support directory switching**:
   - Directory change should be possible without restarting
   - Update all path references after changing directory

3. **Protect API key configuration**:
   - Use try/except blocks to prevent crashes
   - Support environment variables for all API keys
   - Fall back to environment when config saving fails
   - Provide clear error messages to users

## Making Changes

1. Make changes to the code in the `src/herd_ai` directory
2. Run the command-line tool directly with:
   ```bash
   python -m herd_ai --help
   ```
   or
   ```bash
   python herd.py --help
   ```

3. Test changes locally with:
   ```bash
   python run_herd.py --help
   ```

## Testing

1. Test each AI provider functionality:
   ```bash
   # Test with Ollama (default)
   python run_herd.py --dir test_files --rename
   
   # Test with X.AI 
   python run_herd.py --dir test_files --rename --provider xai --api-key YOUR_KEY
   
   # Test with Gemini
   python run_herd.py --dir test_files --rename --provider gemini --api-key YOUR_KEY
   
   # Test with OpenAI
   python run_herd.py --dir test_files --rename --provider openai --api-key YOUR_KEY
   
   # Test with Cohere
   python run_herd.py --dir test_files --rename --provider cohere --api-key YOUR_KEY
   ```

2. Verify all main modules work with the provider:
   - rename.py
   - snippets.py
   - citations.py
   - docs.py
   - idealize.py
   - image_processor.py

3. Check the interactive CLI functions correctly:
   - Test navigation with Ctrl-C
   - Test directory switching
   - Test API key configuration
   - Test all menu options

## Packaging

### Building the Package

```bash
# Install build tools if you don't have them
pip install build twine

# Build the package
python -m build
```

This will create distribution files in the `dist/` directory.

### Testing the Package Locally

```bash
pip install dist/herd_ai-0.2.0-py3-none-any.whl
herd --help
```

### Publishing to PyPI

1. Create a PyPI account if you don't have one
2. Configure your PyPI credentials in `~/.pypirc` or with environment variables

3. Upload to PyPI Test first:
   ```bash
   python -m twine upload --repository-url https://test.pypi.org/legacy/ dist/*
   ```

4. After testing, upload to the main PyPI:
   ```bash
   python -m twine upload dist/*
   ```

## Transition Notes

Herd AI was previously known as LlamaCleaner. The transition involved:

1. Renaming the package from `llamacleaner` to `herd-ai`
2. Changing the CLI command from `llamacleaner` to `herd`
3. Reorganizing the code to use a src-based layout
4. Updating all import statements

Both commands (`herd` and `llamacleaner`) are maintained for backward compatibility. 