#!/bin/bash

# Simple test script for Coze alt text generation

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

# Function to test Coze file upload endpoint
test_coze_upload_endpoint() {
    local output_file="$OUTPUT_DIR/upload_coze.json"
    
    echo -e "${YELLOW}Testing Coze file upload using direct API call to api.coze.com${NC}"
    
    # Extract temporary file for the upload
    local temp_file=$(mktemp /tmp/coze_test_XXXXXX.png)
    cp "$TEST_IMAGE" "$temp_file"
    
    # Use the exact same endpoint and auth token as in flask_chat_coze.py
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

# Function to test API server connection
test_coze_alt_text_api() {
    local model="7462296933429346310"
    local prompt="Describe this image in detail. What do you see?"
    local output_file="$OUTPUT_DIR/_alt_coze_api.json"
    
    echo -e "${YELLOW}Testing Coze Alt Text Generation with API Server (model: $model)${NC}"
    
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

# Function to test direct server connection
test_coze_direct_server() {
    local output_file="$OUTPUT_DIR/_coze_direct_server.json"
    
    echo -e "${YELLOW}Testing Coze direct server connection${NC}"
    
    # Test direct connection to the flask_chat_coze server
    curl -s "http://localhost:5088/" | tee "$output_file"
    
    local status=$?
    print_result $status "Direct connection to Coze server"
    return $status
}

# Run the tests
print_header "Testing Coze Alt Text Generation"
test_coze_alt_text_api

# Summary
print_header "Test Summary"
echo -e "${BOLD}All test results have been saved to the '$OUTPUT_DIR' directory.${NC}"
echo -e "${BOLD}Check the JSON files for detailed responses.${NC}"
echo -e "\n${GREEN}Testing completed!${NC}\n" 