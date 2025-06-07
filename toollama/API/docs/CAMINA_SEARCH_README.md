# Camina Search: Web Search & Summary Expert

This repository provides tools for using the `coolhand/camina-search:23b` model with the Assisted.Space API, enabling powerful web search and content summarization capabilities.

## Features

- **Advanced Web Search**: Perform searches using Google, Bing, or Baidu engines
- **Content Extraction**: Read and process content from URLs
- **Intelligent Summarization**: Identify key points and critical data from multiple sources
- **Source Credibility Assessment**: Evaluate the reliability of information sources
- **Structured Responses**: Present information in a clear, organized format with citations
- **Tool Calling Support**: Use the API's tool calling capabilities to interact with search engines and web content

## Prerequisites

- Python 3.7+ with `requests` and `asyncio` libraries
- The `infinite_search.py` tool (located in the expected path: `./api-tools/tools/tools/tools2/infinite_search.py`)
- Internet connection to access the Assisted.Space API

## Installation

1. Clone this repository or download the `camina_search_runner.py` script
2. Ensure you have the required Python libraries installed:

```bash
pip install requests
```

## Usage

Run the interactive script:

```bash
python camina_search_runner.py
```

The script will:
1. Check if the API is accessible
2. Start an interactive session where you can ask questions

### Interactive Commands

- Type your questions or search queries normally
- Type `exit` or `quit` to end the session
- Type `save` to save the conversation history to a JSON file
- Type `clear` to start a new conversation

### Example Queries

- "What are the latest developments in quantum computing?"
- "Find information about climate change impacts in coastal cities"
- "Search for recent studies on intermittent fasting benefits"
- "What are the current trends in renewable energy adoption?"

## How It Works

The `camina_search_runner.py` script:

1. **Defines Tools**: Sets up the web search and URL reading tools in the format expected by the API
2. **Handles User Input**: Processes user queries and sends them to the model
3. **Processes Tool Calls**: When the model requests information, executes the appropriate tools
4. **Returns Results**: Sends tool results back to the model for analysis and summarization
5. **Presents Responses**: Displays the model's final response with proper formatting

## Technical Details

### API Integration

The script connects to the Assisted.Space API at `https://api.assisted.space/v2` and uses the following endpoints:
- `/chat/ollama` - For chat interactions with the model
- `/models/ollama` - To check available models

### Tool Implementation

The script implements four main tools:

1. **google_search**: Performs a search using Google
2. **bing_search**: Performs a search using Bing
3. **baidu_search**: Performs a search using Baidu
4. **read_url**: Extracts and reads content from a specified URL

These tools are defined in the API's tool calling format and are made available to the model during chat sessions.

### Conversation Management

The script maintains a conversation history and supports:
- Saving conversations to JSON files
- Clearing the conversation to start fresh
- Tracking tool usage and results

## Limitations

- The script requires internet access to connect to the API
- Search results depend on the quality of the search engines and content extraction
- Processing time may vary based on the complexity of the query and number of tool calls

## Acknowledgments

- Based on the `coolhand/camina-search:23b` model
- Uses the `infinite_search.py` tool for web search capabilities 