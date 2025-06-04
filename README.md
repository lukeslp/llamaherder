# Herd AI

![PyPI Version](https://img.shields.io/pypi/v/herd-ai)
![License](https://img.shields.io/github/license/lukesteuber/herd)

A comprehensive document and code management toolkit powered by AI. Herd AI leverages Large Language Models for intelligent file organization, content extraction, and document analysis.

## Features

- **Smart File Renaming**: Automatically generate meaningful filenames based on content
- **Code Snippet Extraction**: Extract and organize important code segments
- **Citation Management**: Extract and format citations from research documents
- **Document Idealization**: Create canonical, cleaned versions of text content
- **Image Processing**: Generate alt text and description for image files
- **Documentation Generation**: Create comprehensive documentation for code repositories
- **Deduplication**: Find and manage duplicate files efficiently
- **Interactive CLI**: User-friendly interface with intuitive navigation and directory switching

## Installation

Install from PyPI:

```bash
pip install herd-ai
```

## Quick Start

```python
# Process files in a directory (CLI)
herd --dir ~/Documents/project --rename --recursive

# Extract code snippets 
herd --dir ~/code/project --snippets

# Generate documentation
herd --dir ~/code/project --docs

# Process images
herd --dir ~/images --images

# Launch interactive CLI
herd

# Use in your Python code
from pathlib import Path
from herd_ai.rename import process_renames
from herd_ai.snippets import process_snippets

# Smart file renaming
process_renames(Path("~/Documents/project"), recursive=True, provider="ollama")

# Extract code snippets
process_snippets(Path("~/code/project"), recursive=True, provider="ollama")
```

## AI Provider Support

Herd AI supports multiple AI providers:

- **Ollama** (default): Uses local models like Llama, Gemma, Mistral
- **X.AI**: Uses X.AI/Grok models for advanced processing
- **Google Gemini**: Uses Google's Gemini API for text and image processing
- **OpenAI**: Uses OpenAI's API for text and image processing
- **Cohere**: Uses Cohere's API for text processing

Select your provider with the `--provider` flag:

```bash
herd --dir ~/Documents --rename --provider openai
```

Or in code:

```python
process_renames(Path("~/Documents"), provider="openai")
```

## Interactive CLI

Herd features an intuitive interactive CLI with the following keyboard shortcuts:

- **Numeric keys (1-9)**: Select menu options
- **s**: Access settings menu (change provider, set API keys)
- **d**: Change target directory without restarting
- **q**: Quit the current menu or application
- **Ctrl+C**: Go back one menu level (or exit if at main menu)

Launch the interactive CLI:

```bash
herd
```

## Documentation

For full documentation, visit [the Herd AI documentation](https://github.com/lukesteuber/herd/docs).

## Development

See [DEVELOPMENT.md](DEVELOPMENT.md) for information on contributing to Herd AI.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
