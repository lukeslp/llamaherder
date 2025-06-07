# Local LLM Providers

This document explains how to use the LM Studio and MLX providers for local LLM inference.

## LM Studio Provider

The LM Studio provider connects to a running LM Studio API server to interact with local LLMs.

### Setup

1. Install LM Studio from [https://lmstudio.ai/](https://lmstudio.ai/)
2. Start LM Studio and navigate to the 'Developer' tab
3. Click 'Start Server' to start the API server (default port is 1234)
4. Load a model by clicking on it in the model list

### Configuration

The LM Studio provider is configured to connect to `http://192.168.0.32:8001`. You can modify this URL in the `api/services/providers/lmstudio.py` file if needed.

```python
self.base_url = "http://192.168.0.32:8001"  # Change this to your LM Studio server URL
```

### Usage

You can use the LM Studio provider with the following endpoints:

- `GET /v2/models/lmstudio`: List available models
- `POST /v2/chat/lmstudio`: Chat with a loaded model

Example curl request:

```bash
curl -X POST http://localhost:8435/v2/chat/lmstudio \
  -H "Content-Type: application/json" \
  -d '{
    "model": "mistral-7b-instruct",
    "prompt": "What is the capital of France?",
    "max_tokens": 100,
    "stream": true
  }'
```

### Important Notes

- You must load a model in LM Studio before using it for chat
- The provider will return a helpful error message if no models are loaded
- All available models are listed via the models endpoint, but they must be loaded before use

## MLX Provider

The MLX provider allows you to use MLX models running locally on Apple Silicon hardware.

### Setup

1. Install MLX and MLX-LM:
   ```bash
   pip install mlx mlx-lm
   ```
2. You can either use MLX directly via command line, or run an API server (like Ollama) for MLX models

### Configuration

The MLX provider is configured to first try connecting to an API server at `http://localhost:3000`, and if that fails, it will fall back to using the command line tools.

```python
self.base_url = "http://localhost:3000"  # Change this to your MLX API server if needed
```

### Usage

You can use the MLX provider with the following endpoints:

- `GET /v2/models/mlx`: List available models
- `POST /v2/chat/mlx`: Chat with a local MLX model

Example curl request:

```bash
curl -X POST http://localhost:8435/v2/chat/mlx \
  -H "Content-Type: application/json" \
  -d '{
    "model": "mistral:7b",
    "prompt": "What is the capital of France?",
    "max_tokens": 100,
    "stream": true
  }'
```

### Available Models

The following MLX models are available by default:

- `qwen:7b`: Qwen2 7B optimized for Apple Silicon
- `mistral:7b`: Mistral 7B optimized for instruction following
- `nemo:7b`: Mistral Nemo optimized for instruction following
- `deepseek:7b`: DeepSeek R1 optimized for reasoning
- `mistral-small:24b`: Mistral Small 24B optimized for instruction following
- `deepseek:32b`: DeepSeek R1 optimized for reasoning

## Testing

You can test both providers using the included test script:

```bash
./test_providers.sh
```

This script will test:
1. Streaming chat completions for both providers
2. Non-streaming chat completions for both providers
3. Model listing for both providers 