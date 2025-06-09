#!/bin/bash

# =====================================================
# Camina Chat API Models Testing Script
# =====================================================
# This script tests the models endpoint for all providers
# to verify that duplicate models are filtered out.
# 
# Author: Luke Steuber
# Date: February 26, 2024
# =====================================================

# Set up variables
API_HOST="localhost"
API_PORT="8435"
API_BASE_URL="http://$API_HOST:$API_PORT/v2"
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

# Function to test the models endpoint and count unique IDs
test_models_endpoint() {
    local provider=$1
    local output_file="$OUTPUT_DIR/models_${provider}_test.json"
    
    echo -e "${YELLOW}Testing GET $API_BASE_URL/models/$provider${NC}"
    
    # Get the models and save to file
    curl -s -X GET "$API_BASE_URL/models/$provider" > "$output_file"
    
    local status=$?
    print_result $status "GET /models/$provider"
    
    # Count the number of models
    local model_count=$(grep -o '"id":' "$output_file" | wc -l)
    echo -e "${YELLOW}Number of models returned: $model_count${NC}"
    
    # Count unique IDs
    local unique_count=$(grep -o '"id": "[^"]*"' "$output_file" | sort | uniq | wc -l)
    echo -e "${YELLOW}Number of unique model IDs: $unique_count${NC}"
    
    # Check if there are duplicates
    if [ "$model_count" -eq "$unique_count" ]; then
        echo -e "${GREEN}No duplicate models found.${NC}"
    else
        echo -e "${RED}Found $(($model_count - $unique_count)) duplicate models!${NC}"
        
        # List the duplicates
        echo -e "${YELLOW}Duplicate model IDs:${NC}"
        grep -o '"id": "[^"]*"' "$output_file" | sort | uniq -c | sort -nr | grep -v "^ *1 " | sed 's/^ *\([0-9]*\) "id": "\([^"]*\)"/\1 occurrences of \2/'
    fi
    
    return $status
}

# Start testing
print_header "Testing Models Endpoint"

# Test Mistral models
print_header "Testing Mistral Models"
test_models_endpoint "mistral"

# Test Anthropic models for comparison
print_header "Testing Anthropic Models"
test_models_endpoint "anthropic"

# Test Ollama models
print_header "Testing Ollama Models"
test_models_endpoint "ollama"

# Summary
print_header "Test Summary"
echo -e "${BOLD}Test results have been saved to the '$OUTPUT_DIR' directory.${NC}"
echo -e "\n${GREEN}Testing completed!${NC}\n" 