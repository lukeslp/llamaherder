# ToolLama MoE (Mixture of Experts)

A sophisticated AI orchestration system that coordinates multiple specialized models and tools to handle tasks ranging from simple queries to complex multi-step operations. Features real-time monitoring and strategic optimization through a DeepSeek-powered observer.

## Features

- **Natural Language Task Processing**: Understands and decomposes complex requests
- **Dynamic Tool Selection**: Automatically chooses the best tools for each task
- **Real-time Monitoring**: Continuous performance analysis and optimization
- **Extensive API Integration**: Connected with 40+ specialized services
- **Accessibility Focus**: Built-in accessibility features and auditing
- **Comprehensive Documentation**: Auto-generated guides and examples
- **Alt Text Generation**: Multiple Flask implementations for generating accessible image descriptions

## Quick Start

### Prerequisites

```bash
# 1. Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# 2. Install Required Models
ollama pull mistral:22b   # Primary Agent
ollama pull mistral:7b    # Domain Specialists
ollama pull llama:3.2-3b  # Task Executors
ollama pull deepseek-r1:14b # System Observer

# 3. Install Python Dependencies
pip install -r requirements.txt

# 4. Configure Environment
cp .env.example .env
# Edit .env with your API keys
```

### Basic Usage

1. **Start the System**
   ```bash
   # Start model servers
   python -m moe.servers.start_servers
   
   # Launch main system
   python -m moe.cli start
   ```

2. **Simple Queries**
   ```bash
   # Ask a question
   python -m moe.cli chat "What's the latest in quantum computing?"
   
   # Research task
   python -m moe.cli research "Analyze recent developments in AI"
   ```

3. **API Integration**
   ```python
   from moe.client import MoEClient
   
   async def main():
       client = MoEClient()
       response = await client.execute_task(
           task_type="research",
           content={
               "query": "Latest AI developments",
               "depth": "comprehensive",
               "include": ["academic", "news"]
           }
       )
       print(response)
       await client.close()
   ```

## Alt Text Generation

The system includes multiple Flask implementations for generating accessible image descriptions:

### Camina Implementation (`flask_alt_camina.py`)
High-quality alt text generation with advanced features:
- File upload system with progress tracking
- Real-time streaming responses
- Support for multiple image formats
- Dark mode support
- ARIA-enhanced accessibility
- Keyboard navigation

```bash
# Start Camina server
python flask_alt_camina.py
# Server runs on http://localhost:5100
```

### Normal Implementation (`flask_alt_normal.py`)
Standard alt text generation with base64 encoding:
- Direct base64 image processing
- Streaming response support
- Accessible interface
- Dark mode support
- Error handling and validation

```bash
# Start Normal server
python flask_alt_normal.py
# Server runs on http://localhost:5101
```

Both implementations include:
- HTML interface with ARIA attributes
- Real-time progress indicators
- Comprehensive error handling
- Support for PNG, JPEG, GIF, and WEBP formats
- Keyboard navigation improvements

## Available Tools

### Research & Analysis
- Academic Research (Semantic Scholar, arXiv)
- News Aggregation (NYT, Guardian)
- Data Analysis
- Pattern Recognition

### Content & Media
- Text-to-Speech (ElevenLabs)
- Image Generation & Analysis
- Document Processing
- YouTube Transcript Analysis

### Integration & APIs
- Social Media Integration
- Weather Services
- Government Data
- Analytics Tools

## Architecture

```
MoE System
├── Primary Agent (Mistral-22B)
│   └── Natural language understanding & task orchestration
├── Domain Specialists (Mistral-7B)
│   ├── Research
│   ├── Content
│   └── Analysis
├── Task Executors (LLaMA-3.2-3B)
│   └── Direct tool interaction & execution
└── System Observer (DeepSeek-R1-14B)
    └── Performance monitoring & optimization
```

## Configuration

### API Keys
Store your API keys in `.env`:
```bash
ELEVENLABS_API_KEY=your_key_here
NYT_API_KEY=your_key_here
SEMANTIC_SCHOLAR_KEY=your_key_here
CAMINA_API_KEY=your_key_here  # For Camina alt text generation
```

### Custom Tools
Create new tools in `moe/tools/`:
```python
from moe.tools.base import BaseTool

class YourTool(BaseTool):
    async def execute(self, params):
        # Implementation
        pass
```

## Documentation

- [Detailed Documentation](docs/)
- [API Reference](docs/api/)
- [Tool Guide](docs/tools/)
- [Examples](docs/examples/)
- [Changelog](CHANGELOG.md)

## Development Status

Current Version: 0.8.5

- Core System: 75% Complete
- Intelligence Layer: 60% Complete
- Tool Integration: 80% Complete
- Schema Integration: 90% Complete
- Alt Text Generation: 100% Complete

See [progress.md](progress.md) for detailed implementation status.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `pytest`
5. Submit a pull request

## License

MIT License - see [LICENSE](LICENSE)

## Acknowledgments

- Built with [Ollama](https://github.com/ollama/ollama)
- Powered by Mistral, LLaMA, and DeepSeek models
- Inspired by modern event-driven architectures 