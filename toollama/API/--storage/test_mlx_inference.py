#!/usr/bin/env python
"""
Test script to run inference with the downloaded Llama model using MLX.
"""

import os
import sys
import time
import mlx.core as mx
from mlx_lm import load, generate

def run_inference_test(model_path, prompt, max_tokens=100):
    """
    Run inference test with the downloaded model
    
    Args:
        model_path: Path to the model directory
        prompt: Text prompt for generation
        max_tokens: Maximum number of tokens to generate
    """
    print(f"Loading model from {model_path}...")
    try:
        # Load the model
        model, tokenizer = load(model_path)
        
        print(f"Model loaded successfully")
        print(f"Tokenizing prompt: '{prompt}'")
        
        # Tokenize the prompt
        tokens = tokenizer.encode(prompt)
        print(f"Prompt tokenized to {len(tokens)} tokens")
        
        # Prepare for generation
        print(f"Running inference (generating up to {max_tokens} tokens)...")
        start_time = time.time()
        
        # Generate text
        outputs = generate(model, tokenizer, prompt, max_tokens=max_tokens)
        
        # Calculate generation time
        end_time = time.time()
        generation_time = end_time - start_time
        
        print(f"\n--- Generated Text ({generation_time:.2f} seconds) ---")
        print(outputs)
        print(f"--- End of Generated Text ---")
        
        return True
    except Exception as e:
        print(f"Error during inference: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # Default model path (as downloaded by download_model.py)
    default_model_path = os.path.expanduser("~/.cache/mlx-community/Llama-3.2-3B-Instruct-4bit")
    
    # Default prompt
    default_prompt = "Explain the concept of neural networks in simple terms."
    
    # Use command line arguments if provided
    if len(sys.argv) > 1:
        model_path = sys.argv[1]
    else:
        model_path = default_model_path
        
    if len(sys.argv) > 2:
        prompt = sys.argv[2]
    else:
        prompt = default_prompt
    
    # Run the inference test
    success = run_inference_test(model_path, prompt)
    
    if success:
        print("\nMLX inference test completed successfully!")
        print("The model is working correctly with MLX.")
    else:
        print("\nMLX inference test failed.")
        print("Please check the error messages above for more information.") 