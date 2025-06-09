# Drummer Search Runner

A robust web search and summary tool powered by the Drummer Search model series using Ollama.

## Overview

Drummer Search Runner is a powerful command-line tool that provides web search capabilities combined with comprehensive, well-cited summaries. It uses the Drummer Search models (available in 3b, 7b, and 24b sizes) to:

1. Generate multiple search queries based on your original question
2. Execute web searches across different search engines
3. Extract and organize relevant information
4. Create detailed, well-structured summaries with proper citations

The tool provides real-time progress updates throughout the search and summarization process, letting you know exactly what's happening at each step.

## Features

- **Multiple Model Sizes**: Choose between small (3b), medium (7b), and large (24b) models based on your needs and available resources
- **Intelligent Model Selection**: Automatically selects the most appropriate model size for each task based on query complexity
- **Progress Tracking**: Visual progress bar with detailed step descriptions
- **Comprehensive Summaries**: Produces detailed, well-structured summaries (1000-1500+ words)
- **Proper Citations**: All information includes source attribution and a comprehensive references section
- **Conversation History**: Maintain and save conversation history for future reference
- **Command-line Interface**: Easy-to-use CLI with interactive mode or single-query options

## Requirements

- Python 3.7+
- `requests` library
- Ollama installed and running with the Drummer Search models available
- The infinite_search.py tool (included in the api-tools directory)

## Installation

1. Ensure Ollama is installed and running
2. Make sure the Drummer Search models are available in Ollama:
   ```bash
   ollama pull coolhand/drummer-search:3b
   ollama pull coolhand/drummer-search:7b
   ollama pull coolhand/drummer-search:24b
   ```
3. Clone this repository
4. Install the required Python packages:
   ```bash
   pip install requests
   ```

## Usage

### Interactive Mode

Run the script without arguments to use interactive mode:

```bash
python drummer_search_runner.py
```

In interactive mode, you can:
- Type your question to get a comprehensive search and summary
- Use `model small|medium|large` to change the model size
- Type `save` to save the conversation history
- Type `clear` to start a new conversation
- Type `exit` or `quit` to end the session

### Single Query Mode

Run the script with a query to get a single response:

```bash
python drummer_search_runner.py --query "What are the latest developments in quantum computing?"
```

### Model Selection

Choose a specific model size with the `--model` argument:

```bash
python drummer_search_runner.py --model small
```

Options:
- `small` (3b): Fastest, but least capable
- `medium` (7b): Good balance of speed and quality
- `large` (24b): Most capable, but slowest

## How It Works

1. **Query Expansion**: The tool analyzes your question and generates multiple related search queries to explore different aspects of the topic.

2. **Parallel Searches**: It executes searches across different search engines to gather comprehensive information.

3. **Smart Model Selection**: The tool intelligently selects the appropriate model size for each task:
   - Small model (3b) for query generation when complexity is low
   - Medium model (7b) for search tasks
   - Large model (24b) for complex summarization

4. **URL Extraction & Organization**: The tool extracts and organizes URLs from search results, grouping them by domain.

5. **Comprehensive Summary Generation**: Using the gathered information, it creates a detailed summary with proper citations that covers all aspects of the topic.

6. **Citation Processing**: The summary includes citations for all information and ends with a comprehensive references section.

## Progress Tracking

The tool provides detailed progress updates throughout the process:

1. Starting search process (0%)
2. Generating search queries (5%)
3. Search queries generated (15%)
4. Executing searches (15-40%)
5. Processing search results (45%)
6. Generating comprehensive summary (50-90%)
7. Finalizing summary and formatting references (90%)
8. Search and summary complete (100%)

## Customization

You can customize the tool by modifying the following variables in the script:

- `API_BASE_URL`: The base URL for the API
- `DRUMMER_MODELS`: The available model variants and their names

## Troubleshooting

If you encounter issues:

1. Ensure Ollama is running and accessible
2. Verify the Drummer Search models are installed in Ollama
3. Check your internet connection
4. For API errors, check if the API endpoint is accessible

## Credits

- Based on the Camina Search implementation
- Uses the infinite_search.py tool for web searches
- Powered by Ollama and the Drummer Search models

## License

This project is licensed under the MIT License. 