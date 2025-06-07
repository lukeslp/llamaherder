#!/usr/bin/env python
"""
Script to download the Llama 3.2 3B Instruct 4bit model for MLX
"""
from huggingface_hub import snapshot_download
import os
import sys

def download_mlx_model(repo_id, local_dir=None):
    """
    Download a model from the Hugging Face Hub
    
    Args:
        repo_id: Repository ID on the Hugging Face Hub
        local_dir: Local directory to save the model (if None, uses ~/.cache/huggingface/hub)
    
    Returns:
        Path to the downloaded model
    """
    print(f"Downloading model from {repo_id}...")
    
    try:
        # If local_dir is not provided, use the default HF cache location
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
        
    except Exception as e:
        print(f"Error downloading model: {e}")
        return None

if __name__ == "__main__":
    # Default model to download
    default_repo_id = "mlx-community/Llama-3.2-3B-Instruct-4bit"
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        repo_id = sys.argv[1]
    else:
        repo_id = default_repo_id
        
    # Download the model
    model_path = download_mlx_model(repo_id)
    
    if model_path:
        print("\nModel files:")
        for root, dirs, files in os.walk(model_path):
            for file in files:
                print(f"  - {os.path.join(root, file)}")
        
        print("\nTo use this model with the MLX API, ensure the model path is configured in your API settings.")
    else:
        print("Failed to download the model.") 