# Code Snippets from toollama/API/--storage/simple_pil_test.py

File: `toollama/API/--storage/simple_pil_test.py`  
Language: Python  
Extracted: 2025-06-07 05:16:50  

## Snippet 1
Lines 1-12

```Python
#!/usr/bin/env python
from PIL import Image
import io
import base64

# Create a simple image
img = Image.new('RGB', (100, 100), color='red')
print(f"Created image: {img.size}, {img.mode}")

# Save to bytes
buffer = io.BytesIO()
img.save(buffer, format='PNG')
```

## Snippet 2
Lines 13-19

```Python
print(f"Saved image to buffer, size: {buffer.tell()} bytes")

# Encode to base64
encoded = base64.b64encode(buffer.getvalue()).decode('utf-8')
print(f"Encoded to base64, length: {len(encoded)}")

print("All tests passed!")
```

