#!/bin/bash

# =====================================================
# Camina Chat API Testing Script
# =====================================================
# This script tests all endpoints of the Camina Chat API
# including Anthropic, Mistral, Ollama, OpenAI, X.AI, Cohere, Coze, and Perplexity providers.
# 
# Author: Luke Steuber
# Date: February 25, 2024
# Updated: February 26, 2024 - Added Ollama provider tests
# Updated: February 28, 2024 - Added OpenAI provider tests
# Updated: February 24, 2025 - Updated for all model compatibility with alt text generation
# Updated: August 15, 2024 - Added Cohere provider tests
# Updated: August 20, 2024 - Added Coze provider tests
# Updated: February 25, 2025 - Added Perplexity provider tests
# =====================================================

# Set up variables
API_HOST="localhost"
API_PORT="8435"
API_BASE_URL="http://$API_HOST:$API_PORT/v2"
TEST_IMAGE="test_image.png"
OUTPUT_DIR="test_results"

# Text formatting
BOLD="\033[1m"
GREEN="\033[0;32m"
RED="\033[0;31m"
YELLOW="\033[0;33m"
BLUE="\033[0;34m"
NC="\033[0m" # No Color

# Create output directory if it doesn't exist
mkdir -p "$OUTPUT_DIR"

# Create a test image if it doesn't exist
if [ ! -f "$TEST_IMAGE" ]; then
    echo -e "${YELLOW}Creating test image...${NC}"
    # Use Python to create a simple test image
    python3 -c "
from PIL import Image, ImageDraw, ImageFont
import sys

try:
    # Create a new image with a white background
    img = Image.new('RGB', (400, 200), color='white')
    draw = ImageDraw.Draw(img)
    
    # Draw some shapes
    draw.rectangle([50, 50, 150, 150], fill='red', outline='black')
    draw.ellipse([200, 50, 300, 150], fill='blue', outline='black')
    
    # Add text
    draw.text((150, 160), 'Test Image', fill='black')
    
    # Save the image
    img.save('$TEST_IMAGE')
    print('Test image created successfully')
except Exception as e:
    print(f'Error creating test image: {e}')
    sys.exit(1)
"
    if [ $? -ne 0 ]; then
        echo -e "${RED}Failed to create test image. Make sure PIL is installed.${NC}"
        echo -e "${YELLOW}You can install it with: pip install Pillow${NC}"
        exit 1
    fi
fi

# Function to print section headers
print_header() {
    echo -e "\n${BOLD}${BLUE}$1${NC}"
    echo -e "${BLUE}$(printf '=%.0s' {1..50})${NC}\n"
}

# Function to print test results
print_result() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✓ $2${NC}"
    else
        echo -e "${RED}✗ $2${NC}"
    fi
}

# Function to test an endpoint and save the response
test_endpoint() {
    local endpoint=$1
    local method=${2:-GET}
    local data=${3:-""}
    local output_file="$OUTPUT_DIR/$(echo $endpoint | tr '/' '_').json"
    
    echo -e "${YELLOW}Testing $method $API_BASE_URL$endpoint${NC}"
    
    if [ "$method" = "GET" ]; then
        curl -s -X $method "$API_BASE_URL$endpoint" | tee "$output_file"
    else
        curl -s -X $method -H "Content-Type: application/json" -d "$data" "$API_BASE_URL$endpoint" | tee "$output_file"
    fi
    
    local status=$?
    print_result $status "$method $endpoint"
    return $status
}

# Function to test file upload endpoint
test_upload_endpoint() {
    local endpoint=$1
    local provider=$2
    local model=$3
    local prompt=${4:-"Generate descriptive alt text for this image"}
    local output_file="$OUTPUT_DIR/$(echo $endpoint | tr '/' '_')_${provider}.json"
    
    echo -e "${YELLOW}Testing POST $API_BASE_URL$endpoint (provider: $provider, model: $model)${NC}"
    
    curl -s -X POST \
        -F "image=@$TEST_IMAGE" \
        -F "prompt=$prompt" \
        -F "model=$model" \
        -F "stream=false" \
        "$API_BASE_URL$endpoint/$provider" | tee "$output_file"
    
    local status=$?
    print_result $status "POST $endpoint/$provider"
    return $status
}

# Function to test Coze file upload endpoint
test_coze_upload_endpoint() {
    local output_file="$OUTPUT_DIR/upload_coze.json"
    
    echo -e "${YELLOW}Testing Coze file upload using direct API call to api.coze.com${NC}"
    
    # Extract temporary file for the upload
    local temp_file=$(mktemp /tmp/coze_test_XXXXXX.png)
    cp "$TEST_IMAGE" "$temp_file"
    
    # Use the exact same endpoint and auth token as in flask_chat_coze.py
    # Note: In a production environment, this token should be stored securely
    # and not hardcoded in the script
    local COZE_AUTH_TOKEN="pat_x43jhhVkypZ7CrKwnFwLGLdHOAegoEQqnhFO4kIqomnw6a3Zp4EaorAYfn6EMLz4"
    local COZE_BOT_ID="7462296933429346310"
    
    # Upload file using exact same endpoint as in flask_chat_coze.py
    echo -e "${YELLOW}Uploading file directly to Coze API...${NC}"
    local upload_response=$(curl -s -X POST \
        -H "Authorization: Bearer $COZE_AUTH_TOKEN" \
        -F "file=@$temp_file" \
        "https://api.coze.com/v1/files/upload")
    
    echo "$upload_response" > "$output_file"
    
    # Print the response for debugging
    echo -e "${YELLOW}Response from Coze API: ${NC}${upload_response}"
    
    # Extract file_id according to documented response format (same as flask_chat_coze.py)
    # Response format: {"code": 0, "data": {"id": "xxx", ...}, "msg": ""}
    local file_id=""
    
    # Check if response contains the expected structure
    if [[ "$upload_response" == *"\"code\":0"* ]]; then
        # Extract id from data object
        file_id=$(echo "$upload_response" | grep -o '"id":"[^"]*"' | head -1 | sed 's/"id":"//;s/"//')
    fi
    
    # Cleanup temp file
    rm -f "$temp_file"
    
    if [ -z "$file_id" ]; then
        echo -e "${RED}Failed to extract file_id from response${NC}"
        print_result 1 "POST to api.coze.com/v1/files/upload"
        return 1
    fi
    
    echo -e "${GREEN}Successfully uploaded file to Coze. File ID: $file_id${NC}"
    print_result 0 "POST to api.coze.com/v1/files/upload"
    
    echo "$file_id"  # Return the file_id
    return 0
}

# Function to test Coze alt text generation using file ID
test_coze_alt_text() {
    local model=$1
    local prompt=${2:-"Generate descriptive alt text for this image"}
    local output_file="$OUTPUT_DIR/_alt_coze.json"
    
    echo -e "${YELLOW}Testing Coze Alt Text Generation with model: $model${NC}"
    
    # First upload the file to get a file_id using the direct API
    local full_output=$(test_coze_upload_endpoint)
    local upload_status=$?
    
    # Extract only the last line as the file_id
    local file_id=$(echo "$full_output" | tail -n 1)
    
    if [ $upload_status -ne 0 ]; then
        echo -e "${RED}Failed to upload file for Coze alt text generation${NC}"
        print_result 1 "Coze Alt Text Generation"
        return 1
    fi
    
    # Now use the file_id to request alt text generation
    echo -e "${YELLOW}Testing POST $API_BASE_URL/chat/coze with file_id=${file_id}${NC}"
    
    # Make sure we escape quotes properly to avoid control character issues
    local request_data="{\"model\":\"$model\",\"prompt\":\"$prompt\",\"max_tokens\":500,\"stream\":false,\"file_id\":\"$file_id\"}"
    
    # Show the exact request we're sending
    echo -e "${YELLOW}Request data: ${NC}"
    echo "$request_data"
    
    curl -s -X POST \
        -H "Content-Type: application/json" \
        -d "$request_data" \
        "$API_BASE_URL/chat/coze" | tee "$output_file"
    
    local status=$?
    print_result $status "POST /chat/coze (with file_id for alt text)"
    return $status
}

# Function to test streaming endpoint
test_streaming_endpoint() {
    local endpoint=$1
    local provider=$2
    local model=$3
    local data=$4
    local output_file="$OUTPUT_DIR/$(echo $endpoint | tr '/' '_')_${provider}_stream.txt"
    
    echo -e "${YELLOW}Testing POST $API_BASE_URL$endpoint/$provider (streaming)${NC}"
    
    curl -s -X POST \
        -H "Content-Type: application/json" \
        -d "$data" \
        "$API_BASE_URL$endpoint/$provider" | tee "$output_file"
    
    local status=$?
    print_result $status "POST $endpoint/$provider (streaming)"
    return $status
}

# Start testing
print_header "Starting API Tests"

# Test 1: API Info Endpoint
print_header "1. Testing API Info Endpoint"
test_endpoint "/"

# Test 2: Health Check Endpoint
print_header "2. Testing Health Check Endpoint"
test_endpoint "/health"

# Test 3: Models Endpoint - Anthropic
print_header "3. Testing Models Endpoint - Anthropic"
test_endpoint "/models/anthropic"

# Test 4: Models Endpoint - Mistral
print_header "4. Testing Models Endpoint - Mistral"
test_endpoint "/models/mistral"

# Test 4b: Models Endpoint - Cohere
print_header "4b. Testing Models Endpoint - Cohere"
test_endpoint "/models/cohere"

# Test 4c: Models Endpoint - Coze
print_header "4c. Testing Models Endpoint - Coze"
test_endpoint "/models/coze"

# Test 5: Models Endpoint - Ollama
print_header "5. Testing Models Endpoint - Ollama"
test_endpoint "/models/ollama"

# Test 6: Models Endpoint - OpenAI
print_header "6. Testing Models Endpoint - OpenAI"
test_endpoint "/models/openai"

# Test 6b: Models Endpoint - X.AI
print_header "6b. Testing Models Endpoint - X.AI"
test_endpoint "/models/xai"

# Test 6c: Models Endpoint - Perplexity
print_header "6c. Testing Models Endpoint - Perplexity"
test_endpoint "/models/perplexity"

# Test 7: Chat Endpoint - Anthropic (non-streaming)
print_header "7. Testing Chat Endpoint - Anthropic (non-streaming)"
test_endpoint "/chat/anthropic" "POST" '{
    "model": "claude-3-haiku-20240307",
    "prompt": "Hello, how are you today?",
    "max_tokens": 100,
    "stream": false
}'

# Test 8: Chat Endpoint - Mistral (non-streaming)
print_header "8. Testing Chat Endpoint - Mistral (non-streaming)"
test_endpoint "/chat/mistral" "POST" '{
    "model": "mistral-tiny",
    "prompt": "Hello, how are you today?",
    "max_tokens": 100,
    "stream": false
}'

# Test 9: Chat Endpoint - Ollama (non-streaming)
print_header "9. Testing Chat Endpoint - Ollama (non-streaming)"
test_endpoint "/chat/ollama" "POST" '{
    "model": "llama3.2:1b",
    "prompt": "Hello, how are you today?",
    "max_tokens": 100,
    "stream": false
}'

# Test 10: Chat Endpoint - OpenAI (non-streaming)
print_header "10. Testing Chat Endpoint - OpenAI (non-streaming)"
test_endpoint "/chat/openai" "POST" '{
    "model": "gpt-3.5-turbo-0125",
    "prompt": "Hello, how are you today?",
    "max_tokens": 100,
    "stream": false
}'

# Test 10b: Chat Endpoint - Cohere (non-streaming)
print_header "10b. Testing Chat Endpoint - Cohere (non-streaming)"
test_endpoint "/chat/cohere" "POST" '{
    "model": "command-light",
    "prompt": "Hello, how are you today?",
    "max_tokens": 100,
    "stream": false
}'

# Test 10c: Chat Endpoint - X.AI (non-streaming)
print_header "10c. Testing Chat Endpoint - X.AI (non-streaming)"
test_endpoint "/chat/xai" "POST" '{
    "model": "grok-2-1212",
    "prompt": "Hello, how are you today?",
    "max_tokens": 100,
    "stream": false,
    "image_data": null
}'

# Test 10d: Chat Endpoint - Coze (non-streaming)
print_header "10d. Testing Chat Endpoint - Coze (non-streaming)"
test_endpoint "/chat/coze" "POST" '{
    "model": "7462296933429346310",
    "prompt": "Hello, how are you today?",
    "max_tokens": 100,
    "stream": false
}'

# Test 10e: Chat Endpoint - Perplexity (non-streaming)
print_header "10e. Testing Chat Endpoint - Perplexity (non-streaming)"
test_endpoint "/chat/perplexity" "POST" '{
    "model": "sonar",
    "prompt": "Hello, how are you today?",
    "max_tokens": 100,
    "stream": false
}'

# Test 11: Chat Endpoint - Anthropic (streaming)
print_header "11. Testing Chat Endpoint - Anthropic (streaming)"
test_streaming_endpoint "/chat" "anthropic" "claude-3-haiku-20240307" '{
    "model": "claude-3-haiku-20240307",
    "prompt": "Write a short poem about AI",
    "max_tokens": 100,
    "stream": true
}'

# Test 12: Chat Endpoint - Mistral (streaming)
print_header "12. Testing Chat Endpoint - Mistral (streaming)"
test_streaming_endpoint "/chat" "mistral" "mistral-tiny" '{
    "model": "mistral-tiny",
    "prompt": "Write a short poem about AI",
    "max_tokens": 100,
    "stream": true
}'

# Test 13: Chat Endpoint - Ollama (streaming)
print_header "13. Testing Chat Endpoint - Ollama (streaming)"
test_streaming_endpoint "/chat" "ollama" "llama3.2:1b" '{
    "model": "llama3.2:1b",
    "prompt": "Write a short poem about AI",
    "max_tokens": 100,
    "stream": true
}'

# Test 14: Chat Endpoint - OpenAI (streaming)
print_header "14. Testing Chat Endpoint - OpenAI (streaming)"
test_streaming_endpoint "/chat" "openai" "gpt-3.5-turbo-0125" '{
    "model": "gpt-3.5-turbo-0125",
    "prompt": "Write a short poem about AI",
    "max_tokens": 100,
    "stream": true
}'

# Test 14b: Chat Endpoint - Cohere (streaming)
print_header "14b. Testing Chat Endpoint - Cohere (streaming)"
test_streaming_endpoint "/chat" "cohere" "command-light" '{
    "model": "command-light",
    "prompt": "Write a short poem about AI",
    "max_tokens": 100,
    "stream": true
}'

# Test 14c: Chat Endpoint - X.AI (streaming)
print_header "14c. Testing Chat Endpoint - X.AI (streaming)"
test_streaming_endpoint "/chat" "xai" "grok-2-1212" '{
    "model": "grok-2-1212",
    "prompt": "Write a short poem about AI",
    "max_tokens": 100,
    "stream": true,
    "image_data": null
}'

# Test 14d: Chat Endpoint - Coze (streaming)
print_header "14d. Testing Chat Endpoint - Coze (streaming)"
test_streaming_endpoint "/chat" "coze" "7462296933429346310" '{
    "model": "7462296933429346310",
    "prompt": "Write a short poem about AI",
    "max_tokens": 100,
    "stream": true
}'

# Test 14e: Chat Endpoint - Perplexity (streaming)
print_header "14e. Testing Chat Endpoint - Perplexity (streaming)"
test_streaming_endpoint "/chat" "perplexity" "sonar" '{
    "model": "sonar",
    "prompt": "Write a short poem about AI",
    "max_tokens": 100,
    "stream": true
}'

# Test 15: Alt Text Generation - Anthropic
print_header "15. Testing Alt Text Generation - Anthropic"
test_upload_endpoint "/alt" "anthropic" "claude-3-haiku-20240307"

# Test 16: Alt Text Generation - Mistral
print_header "16. Testing Alt Text Generation - Mistral"
test_upload_endpoint "/alt" "mistral" "pixtral-large-2411"

# Test 17: Alt Text Generation - Ollama (Vision model)
print_header "17. Testing Alt Text Generation - Ollama (Vision model)"
test_upload_endpoint "/alt" "ollama" "coolhand/altllama:13b" "Describe this image in detail. What do you see?"

# Test 17B: Alt Text Generation - Ollama (Non-vision model)
print_header "17B. Testing Alt Text Generation - Ollama (Non-vision model)"
test_upload_endpoint "/alt" "ollama" "llama3.2:1b" "Generate alt text for this image. Describe what you think it might contain."

# Test 18: Alt Text Generation - OpenAI
print_header "18. Testing Alt Text Generation - OpenAI"
test_upload_endpoint "/alt" "openai" "gpt-4o-mini" "Generate detailed alt text for this image"

# Test 18b: Alt Text Generation - Cohere
print_header "18b. Testing Alt Text Generation - Cohere"
echo -e "${YELLOW}Note: Cohere does not support vision capabilities. Skipping alt text generation test for Cohere.${NC}"
echo -e "${BLUE}Cohere vision test skipped${NC}" | tee "$OUTPUT_DIR/_alt_cohere_skipped.txt"
print_result 0 "Skipped: Cohere vision test (provider does not support vision)"

# Test 18c: Alt Text Generation - X.AI
print_header "18c. Testing Alt Text Generation - X.AI"
# Define a custom function for testing X.AI alt text generation with a different approach
test_xai_alt_text() {
    echo -e "${YELLOW}Testing POST $API_BASE_URL/alt/xai (provider: xai, model: grok-2-vision-1212)${NC}"
    
    # Convert image to base64 inline to avoid form-data upload issues
    local image_base64=$(base64 -i "$TEST_IMAGE")
    local output_file="$OUTPUT_DIR/_alt_xai.json"
    
    # Send request with image data in the JSON payload instead of form upload
    curl -s -X POST \
        -H "Content-Type: application/json" \
        -d "{
            \"model\": \"grok-2-vision-1212\",
            \"prompt\": \"Describe what's in this image in detail\",
            \"image_data\": \"$image_base64\"
        }" \
        "$API_BASE_URL/alt/xai" | tee "$output_file"
    
    local status=$?
    print_result $status "POST /alt/xai"
    return $status
}

test_xai_alt_text

# Test 18d: Alt Text Generation - Coze
print_header "18d. Testing Alt Text Generation - Coze"
test_coze_alt_text "7462296933429346310" "Describe this image in detail. Generate descriptive alt text for accessibility purposes."

# Test 19: Tool Calling - Anthropic
print_header "19. Testing Tool Calling - Anthropic"
test_endpoint "/tools/anthropic" "POST" '{
    "model": "claude-3-opus-20240229",
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

# Test 20: Tool Calling - Mistral
print_header "20. Testing Tool Calling - Mistral"
test_endpoint "/tools/mistral" "POST" '{
    "model": "mistral-small",
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

# Test 21: Tool Calling - Ollama
print_header "21. Testing Tool Calling - Ollama"
test_endpoint "/tools/ollama" "POST" '{
    "model": "llama3.2:1b",
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

# Test 22: Tool Calling - OpenAI
print_header "22. Testing Tool Calling - OpenAI"
test_endpoint "/tools/openai" "POST" '{
    "model": "gpt-4-0125-preview",
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

# Test 22b: Tool Calling - Cohere
print_header "22b. Testing Tool Calling - Cohere"
test_endpoint "/tools/cohere" "POST" '{
    "model": "command-r-plus-08-2024",
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

# Test 22c: Tool Calling - X.AI
print_header "22c. Testing Tool Calling - X.AI"
test_endpoint "/tools/xai" "POST" '{
    "model": "grok-2-1212",
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
    "max_tokens": 200,
    "image_data": null
}'

# Test 22d: Tool Calling - Coze
print_header "22d. Testing Tool Calling - Coze"
test_endpoint "/tools/coze" "POST" '{
    "model": "7462296933429346310",
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

# Test 22e: Tool Calling - Perplexity
print_header "22e. Testing Tool Calling - Perplexity"
test_endpoint "/tools/perplexity" "POST" '{
    "model": "sonar",
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

# Test 23: Clear Conversation - Anthropic
print_header "23. Testing Clear Conversation - Anthropic"
test_endpoint "/chat/anthropic/clear" "POST" '{}'

# Test 24: Clear Conversation - Mistral
print_header "24. Testing Clear Conversation - Mistral"
test_endpoint "/chat/mistral/clear" "POST" '{}'

# Test 25: Clear Conversation - Ollama
print_header "25. Testing Clear Conversation - Ollama"
test_endpoint "/chat/ollama/clear" "POST" '{}'

# Test 26: Clear Conversation - OpenAI
print_header "26. Testing Clear Conversation - OpenAI"
test_endpoint "/chat/openai/clear" "POST" '{}'

# Test 26b: Clear Conversation - Cohere
print_header "26b. Testing Clear Conversation - Cohere"
test_endpoint "/chat/cohere/clear" "POST" '{}'

# Test 26c: Clear Conversation - X.AI
print_header "26c. Testing Clear Conversation - X.AI"
test_endpoint "/chat/xai/clear" "POST" '{}'

# Test 26d: Clear Conversation - Coze
print_header "26d. Testing Clear Conversation - Coze"
test_endpoint "/chat/coze/clear" "POST" '{}'

# Test 26e: Clear Conversation - Perplexity
print_header "26e. Testing Clear Conversation - Perplexity"
test_endpoint "/chat/perplexity/clear" "POST" '{}'

# Summary
print_header "Test Summary"
echo -e "${BOLD}All test results have been saved to the '$OUTPUT_DIR' directory.${NC}"
echo -e "${BOLD}Check the JSON files for detailed responses.${NC}"
echo -e "\n${BOLD}Test Coverage Highlights:${NC}"
echo -e "• API endpoints for all providers (Anthropic, Mistral, Ollama, OpenAI, X.AI, Cohere, Coze)"
echo -e "• Chat capabilities (streaming and non-streaming)"
echo -e "• Alt text generation with both vision and non-vision models"
echo -e "• Tool calling functionality"
echo -e "• Conversation management\n"
echo -e "\n${GREEN}Testing completed!${NC}\n" 