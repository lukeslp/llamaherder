#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}Testing LM Studio Provider${NC}"
echo "----------------------------------------"

# Test LM Studio chat completion (streaming)
curl -X POST http://localhost:8435/v2/chat/lmstudio \
  -H "Content-Type: application/json" \
  -d '{
    "model": "mistral-7b-instruct",
    "prompt": "What is the capital of France?",
    "max_tokens": 100,
    "stream": true
  }'

echo -e "\n\n${GREEN}Testing MLX Provider${NC}"
echo "----------------------------------------"

# Test MLX chat completion (streaming)
curl -X POST http://localhost:8435/v2/chat/mlx \
  -H "Content-Type: application/json" \
  -d '{
    "model": "mistral-7b",
    "prompt": "What is the capital of France?",
    "max_tokens": 100,
    "stream": true
  }'

echo -e "\n\n${GREEN}Testing Non-Streaming Endpoints${NC}"
echo "----------------------------------------"

# Test LM Studio non-streaming
curl -X POST http://localhost:8435/v2/chat/lmstudio \
  -H "Content-Type: application/json" \
  -d '{
    "model": "mistral-7b-instruct",
    "prompt": "What is the capital of France?",
    "max_tokens": 100,
    "stream": false
  }'

echo -e "\n\n"

# Test MLX non-streaming
curl -X POST http://localhost:8435/v2/chat/mlx \
  -H "Content-Type: application/json" \
  -d '{
    "model": "mistral-7b",
    "prompt": "What is the capital of France?",
    "max_tokens": 100,
    "stream": false
  }'

echo -e "\n\n${GREEN}Testing Model Listing${NC}"
echo "----------------------------------------"

# List available models for both providers
curl -X GET "http://localhost:8435/v2/models/lmstudio"
echo -e "\n\n"
curl -X GET "http://localhost:8435/v2/models/mlx" 