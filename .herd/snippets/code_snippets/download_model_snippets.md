# Code Snippets from toollama/API/download_model.py

File: `toollama/API/download_model.py`  
Language: Python  
Extracted: 2025-06-07 05:10:23  

## Snippet 1
Lines 3-8

```Python
Script to download the Llama 3.2 3B Instruct 4bit model for MLX
"""
from huggingface_hub import snapshot_download
import os
import sys
```

## Snippet 2
Lines 9-14

```Python
def download_mlx_model(repo_id, local_dir=None):
    """
    Download a model from the Hugging Face Hub

    Args:
        repo_id: Repository ID on the Hugging Face Hub
```

## Snippet 3
Lines 17-23

```Python
Returns:
        Path to the downloaded model
    """
    print(f"Downloading model from {repo_id}...")

    try:
        # If local_dir is not provided, use the default HF cache location
```

## Snippet 4
Lines 24-40

```Python
if local_dir is None:
            # Create a directory in user's cache folder
            local_dir = os.path.expanduser(f"~/.cache/mlx-community/{repo_id.split('/')[-1]}")

        # Make sure the directory exists
        os.makedirs(local_dir, exist_ok=True)

        # Download the model
        path = snapshot_download(
            repo_id=repo_id,
            local_dir=local_dir,
            local_dir_use_symlinks=False  # Ensure actual files are downloaded
        )

        print(f"Model downloaded successfully to: {path}")
        return path
```

## Snippet 5
Lines 41-44

```Python
except Exception as e:
        print(f"Error downloading model: {e}")
        return None
```

## Snippet 6
Lines 50-57

```Python
if len(sys.argv) > 1:
        repo_id = sys.argv[1]
    else:
        repo_id = default_repo_id

    # Download the model
    model_path = download_mlx_model(repo_id)
```

