# API Interaction Examples

These minimal examples demonstrate how Herd AI's unified `ai_provider` wrapper interacts with different providers.

```python
from pathlib import Path
from herd_ai.utils.ai_provider import process_with_ai, process_image

# Send a text prompt and get a simple response
resp = process_with_ai("notes.txt", "Summarize this file", provider="openai")
print(resp["text"])

# Stream responses from Ollama
stream_resp = process_with_ai(
    "chat.txt",
    "Explain reinforcement learning",
    provider="ollama",
    stream=True
)
for chunk in stream_resp["stream"]:
    print(chunk)

# Analyze an image using Gemini
image_result = process_image(
    Path("image.jpg"),
    "Describe the scene",
    provider="gemini"
)
print(image_result)
```

Documentation by [Luke Steuber](https://lukesteuber.com) – MIT License
