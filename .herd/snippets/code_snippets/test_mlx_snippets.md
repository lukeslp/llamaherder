# Code Snippets from toollama/API/--storage/test_mlx.py

File: `toollama/API/--storage/test_mlx.py`  
Language: Python  
Extracted: 2025-06-07 05:17:02  

## Snippet 1
Lines 1-7

```Python
#!/usr/bin/env python
import sys
print(f"Python version: {sys.version}")

try:
    import mlx
    print(f"MLX is installed: {mlx}")
```

## Snippet 2
Lines 8-14

```Python
# Try to get version from package metadata if available
    try:
        import importlib.metadata
        mlx_version = importlib.metadata.version("mlx")
        print(f"MLX version (from metadata): {mlx_version}")
    except:
        print("Could not get MLX version from metadata")
```

## Snippet 3
Lines 15-42

```Python
except ImportError as e:
    print(f"MLX import error: {e}")

try:
    import torch
    print(f"PyTorch version: {torch.__version__}")
except ImportError as e:
    print(f"PyTorch import error: {e}")

try:
    import transformers
    print(f"Transformers version: {transformers.__version__}")
except ImportError as e:
    print(f"Transformers import error: {e}")

try:
    import mlx_lm
    print(f"MLX-LM is installed: {mlx_lm}")
    # Try to get version from package metadata
    try:
        import importlib.metadata
        mlx_lm_version = importlib.metadata.version("mlx-lm")
        print(f"MLX-LM version (from metadata): {mlx_lm_version}")
    except:
        print("Could not get MLX-LM version from metadata")

    # Check available modules and functions
    print("\nAvailable MLX-LM modules:")
```

## Snippet 4
Lines 47-66

```Python
except ImportError as e:
    print(f"MLX-LM import error: {e}")

# Let's try a simpler approach to run MLX with a tiny model
print("\nAttempting to create a simple MLX model:")
try:
    import mlx.core as mx

    # Create a small matrix multiplication example to verify MLX works
    a = mx.array([[1, 2], [3, 4]])
    b = mx.array([[5, 6], [7, 8]])
    c = mx.matmul(a, b)
    print(f"Simple matrix multiplication with MLX:")
    print(f"A: {a}")
    print(f"B: {b}")
    print(f"A × B: {c}")
    print("MLX computation successful!")
except Exception as e:
    print(f"MLX computation error: {e}")
```

## Snippet 5
Lines 67-69

```Python
print("\nChecking if we can download models using huggingface_hub:")
try:
    from huggingface_hub import snapshot_download
```

## Snippet 6
Lines 70-73

```Python
print("huggingface_hub is available for downloading models")
    print("You can download models using:")
    print("  from huggingface_hub import snapshot_download")
    print("  snapshot_download(repo_id='mlx-community/Llama-3.2-3B-Instruct-4bit')")
```

