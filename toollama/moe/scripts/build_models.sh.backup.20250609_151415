#!/bin/bash
# Script to build all MoE models using Ollama

# Set up error handling
set -e
trap 'echo "Error on line $LINENO"' ERR

# Color output helpers
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Building MoE Models...${NC}\n"

# Function to build a model
build_model() {
    local name=$1
    local modelfile=$2
    echo -e "${YELLOW}Building ${name}...${NC}"
    if ollama create "$name" -f "$modelfile"; then
        echo -e "${GREEN}Successfully built ${name}${NC}"
    else
        echo -e "${RED}Failed to build ${name}${NC}"
        return 1
    fi
    echo
}

# Get the project root directory
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Build Caminaå (Coordinator)
build_model "camina-moe" "${PROJECT_ROOT}/models/caminaa/Modelfile.camina.moe"

# Build Belters (File Manipulation)
build_model "belter-base" "${PROJECT_ROOT}/models/belters/Modelfile.belters.moe"

# Build Drummers (Information Gathering)
build_model "drummer-base" "${PROJECT_ROOT}/models/drummers/Modelfile.drummers.moe"

# Build DeepSeek (Background Reasoning)
build_model "deepseek-observer" "${PROJECT_ROOT}/models/deepseek/Modelfile.deepseek.moe"

echo -e "${GREEN}All models built successfully!${NC}"

# List all available models
echo -e "\n${YELLOW}Available Models:${NC}"
ollama list 