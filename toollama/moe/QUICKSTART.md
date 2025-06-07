# MoE System Quick Start Guide

This guide will help you get the MoE (Mixture of Experts) system up and running quickly.

## Prerequisites

1. **Python Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Linux/macOS
   .\venv\Scripts\activate   # On Windows
   pip install -r requirements.txt
   ```

2. **Ollama**
   Make sure Ollama is installed and running on your system. The system requires:
   - mistral-small:22b (for Caminaå)
   - mistral:7b (for Belters and Drummers)
   - deepseek-r1:7b (for DeepSeek Reasoner)

## Quick Start Commands

The `moe.py` script provides a simple interface to manage the entire system:

1. **Build Models**
   ```bash
   ./moe.py build
   ```
   This will build all required models using Ollama.

2. **Start the System**
   ```bash
   ./moe.py start
   ```
   This launches all server components:
   - Caminaå (Coordinator) on port 6000
   - Belters (File Manipulation) on port 6001
   - Drummers (Information Gathering) on port 6002
   - DeepSeek (Background Reasoning) on port 6003

3. **Check System Status**
   ```bash
   ./moe.py status
   ```
   Shows running servers and available models.

4. **Stop the System**
   ```bash
   ./moe.py stop
   ```
   Gracefully stops all running servers.

5. **Run Tests**
   ```bash
   ./moe.py test
   ```
   Runs the test suite to verify system functionality.

## Server Endpoints

Once running, the following endpoints are available:

- Caminaå: http://localhost:6000/chat
- Belters: http://localhost:6001/chat
- Drummers: http://localhost:6002/chat
- DeepSeek: http://localhost:6003/chat

## Example Usage

1. **Start Everything**
   ```bash
   ./moe.py build   # First time only
   ./moe.py start
   ```

2. **Send a Test Request**
   ```bash
   curl -X POST http://localhost:6000/chat \
        -H "Content-Type: application/json" \
        -d '{"content": "Hello, Caminaå!", "task_id": "test123"}'
   ```

3. **Monitor Status**
   ```bash
   ./moe.py status
   ```

4. **Shutdown**
   ```bash
   ./moe.py stop
   ```

## Troubleshooting

1. **Server Won't Start**
   - Check if ports are already in use
   - Ensure Ollama is running
   - Verify model availability with `ollama list`

2. **Model Build Fails**
   - Check Ollama status
   - Ensure sufficient disk space
   - Verify internet connection for model downloads

3. **Request Failures**
   - Check server logs
   - Verify all servers are running with `./moe.py status`
   - Ensure correct JSON format in requests

## Directory Structure

```
moe/
├── models/              # Model definitions and configurations
├── servers/            # Server implementations
├── tools/              # Utility functions and tools
├── tests/              # Test suite
├── scripts/            # Management scripts
├── config/             # Configuration files
└── moe.py             # Main management script
```

## Next Steps

- Review the full documentation in README.md
- Check project_plan.md for development roadmap
- Explore the test suite in tests/
- Review configuration options in config/

For more detailed information, see the full documentation in README.md. 