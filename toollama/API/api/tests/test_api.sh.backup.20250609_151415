#!/bin/bash

# =====================================================
# Camina Chat API Testing Script
# =====================================================
# This script tests all endpoints of the Camina Chat API
# including Anthropic, Mistral, Ollama, OpenAI, Cohere, X.AI (Grok), Coze, Perplexity, and MLX providers.
# 
# Author: Luke Steuber
# Date: February 25, 2024
# Updated: February 25, 2025 - Added Perplexity provider tests
# Updated: February 26, 2025 - Added MLX provider tests
# =====================================================

# Set up variables
API_HOST="localhost"
API_PORT="8435"
API_BASE_URL="http://api.assisted.space/v2"
TEST_IMAGE="test_image.png"
OUTPUT_DIR="test_results"

# Create output directory if it doesn't exist
mkdir -p "$OUTPUT_DIR"

# Text formatting (ANSI color codes)
BOLD="\033[1m"
GREEN="\033[0;32m"
RED="\033[0;31m"
YELLOW="\033[0;33m"
BLUE="\033[0;34m"
NC="\033[0m" # No Color

# Function to print section headers
print_header() {
  echo -e "\n${BOLD}${BLUE}$1${NC}"
  echo -e "${BLUE}=================================================${NC}\n"
}

# Function to print test results
print_result() {
  if [ $1 -eq 0 ]; then
    echo -e "${GREEN}✓ $2${NC}"
  else
    echo -e "${RED}✗ $2${NC}"
  fi
}

# Function to test an endpoint
test_endpoint() {
  local endpoint=$1
  local method=${2:-"GET"}
  local data=${3:-""}
  local output_file="${OUTPUT_DIR}/${endpoint//\//_}.json"
  
  echo -e "${YELLOW}Testing ${method} ${API_BASE_URL}${endpoint}${NC}"
  
  if [ "$method" = "GET" ]; then
    curl -s -X GET "${API_BASE_URL}${endpoint}" | tee "$output_file"
  else
    curl -s -X POST "${API_BASE_URL}${endpoint}" \
      -H "Content-Type: application/json" \
      -d "$data" | tee "$output_file"
  fi
  
  local status=$?
  echo # Add newline
  print_result $status "${method} ${endpoint}"
  return $status
}

# Function to create a test image if it doesn't exist
create_test_image() {
  if [ ! -f "$TEST_IMAGE" ]; then
    echo "Creating test image..."
    # Create a simple test image using ImageMagick if available
    if command -v convert &> /dev/null; then
      convert -size 400x200 xc:white \
        -fill red -draw "rectangle 50,50 150,150" \
        -fill blue -draw "circle 250,100 300,150" \
        -pointsize 20 -fill black -draw "text 150,180 'Test Image'" \
        "$TEST_IMAGE"
      echo "Test image created successfully"
    else
      echo "ImageMagick not found. Please install it or create a test image manually."
      exit 1
    fi
  fi
}

# Create test image
create_test_image

# Run tests
print_header "Testing Camina Chat API"

# Test 1: API Info Endpoint
print_header "1. Testing API Info Endpoint"
test_endpoint "/"

# Test 2: Health Check Endpoint
print_header "2. Testing Health Check Endpoint"
test_endpoint "/health"

# Test 3: Models Endpoint - MLX
print_header "3. Testing Models Endpoint - MLX"
test_endpoint "/models/mlx"

# Test 4: Chat Endpoint - MLX (Non-streaming)
print_header "4. Testing Chat Endpoint - MLX (Non-streaming)"
test_endpoint "/chat/mlx" "POST" '{
  "model": "qwen:7b",
  "prompt": "Hello, how are you today?",
  "max_tokens": 100,
  "stream": false
}'

# Test 5: Chat Endpoint - MLX (Streaming)
print_header "5. Testing Chat Endpoint - MLX (Streaming)"
echo -e "${YELLOW}Testing POST ${API_BASE_URL}/chat/mlx (streaming)${NC}"
curl -N -X POST "${API_BASE_URL}/chat/mlx" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen:7b",
    "prompt": "Write a short poem about AI",
    "max_tokens": 100,
    "stream": true
  }' | tee "${OUTPUT_DIR}/_chat_mlx_stream.json"
echo # Add newline
print_result $? "POST /chat/mlx (streaming)"

# Test 6: Tool Calling - MLX
print_header "6. Testing Tool Calling - MLX"
test_endpoint "/tools/mlx" "POST" '{
  "model": "qwen:7b",
  "prompt": "What is the weather in Seattle?",
  "tools": [
    {
      "type": "function",
      "function": {
        "name": "get_weather",
        "description": "Get the current weather in a location",
        "parameters": {
          "type": "object",
          "properties": {
            "location": {
              "type": "string",
              "description": "The city and state, e.g. San Francisco, CA"
            },
            "unit": {
              "type": "string",
              "enum": ["celsius", "fahrenheit"],
              "description": "The unit of temperature to use"
            }
          },
          "required": ["location"]
        }
      }
    }
  ],
  "max_tokens": 200
}'

# Test 7: Clear Conversation - MLX
print_header "7. Testing Clear Conversation - MLX"
test_endpoint "/chat/mlx/clear" "POST" '{}'

# Print summary
print_header "Test Summary"
echo -e "${BOLD}All test results have been saved to the '${OUTPUT_DIR}' directory.${NC}"
echo -e "${BOLD}Check the JSON files for detailed responses.${NC}"
echo -e "\n${BOLD}Test Coverage Highlights:${NC}"
echo "• API endpoints for MLX provider"
echo "• Chat capabilities (streaming and non-streaming)"
echo "• Tool calling functionality"
echo "• Conversation management"
echo -e "\n${GREEN}Testing completed!${NC}\n" 