#!/bin/bash

# Test PyPI Publishing Script for LlamaHerder
# This script publishes to Test PyPI for testing before production release

set -e  # Exit on any error

echo "🦙 LlamaHerder Test PyPI Publishing Script"
echo "========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ]; then
    print_error "pyproject.toml not found. Please run this script from the project root."
    exit 1
fi

# Install/upgrade build tools
print_status "Installing/upgrading build tools..."
python3 -m pip install --upgrade pip build twine

# Get current version
CURRENT_VERSION=$(python3 -c "import tomllib; print(tomllib.load(open('pyproject.toml', 'rb'))['project']['version'])" 2>/dev/null || python3 -c "import tomli; print(tomli.load(open('pyproject.toml', 'rb'))['project']['version'])")
print_status "Current version: $CURRENT_VERSION"

# Create a test version with timestamp
TIMESTAMP=$(date +"%Y%m%d%H%M%S")
TEST_VERSION="${CURRENT_VERSION}.dev${TIMESTAMP}"

print_status "Test version will be: $TEST_VERSION"

# Update version temporarily
print_status "Updating version for test release..."
python3 -c "
import re
with open('pyproject.toml', 'r') as f:
    content = f.read()
content = re.sub(r'version = \".*?\"', f'version = \"$TEST_VERSION\"', content)
with open('pyproject.toml', 'w') as f:
    f.write(content)
"

# Clean previous builds
print_status "Cleaning previous builds..."
rm -rf build/ dist/ *.egg-info/

# Build the package
print_status "Building package..."
python3 -m build

if [ $? -ne 0 ]; then
    print_error "Build failed"
    # Restore original version
    python3 -c "
import re
with open('pyproject.toml', 'r') as f:
    content = f.read()
content = re.sub(r'version = \".*?\"', f'version = \"$CURRENT_VERSION\"', content)
with open('pyproject.toml', 'w') as f:
    f.write(content)
"
    exit 1
fi

print_success "Package built successfully"

# Check the built package
print_status "Checking package..."
python3 scripts/validate_package.py

if [ $? -ne 0 ]; then
    print_error "Package validation failed"
    # Restore original version
    python3 -c "
import re
with open('pyproject.toml', 'r') as f:
    content = f.read()
content = re.sub(r'version = \".*?\"', f'version = \"$CURRENT_VERSION\"', content)
with open('pyproject.toml', 'w') as f:
    f.write(content)
"
    exit 1
fi

print_success "Package validation passed"

# Upload to Test PyPI
print_status "Uploading to Test PyPI..."
python3 -m twine upload --repository testpypi dist/*

if [ $? -eq 0 ]; then
    print_success "Successfully published to Test PyPI!"
    echo
    print_status "🎉 Test package published successfully!"
    print_status "You can test install it with:"
    print_status "pip install --index-url https://test.pypi.org/simple/ herd-ai==$TEST_VERSION"
    print_status "Test PyPI page: https://test.pypi.org/project/herd-ai/"
    echo
    print_warning "Remember: This is a test release. Use the main publish script for production."
else
    print_error "Failed to publish to Test PyPI"
fi

# Restore original version
print_status "Restoring original version..."
python3 -c "
import re
with open('pyproject.toml', 'r') as f:
    content = f.read()
content = re.sub(r'version = \".*?\"', f'version = \"$CURRENT_VERSION\"', content)
with open('pyproject.toml', 'w') as f:
    f.write(content)
"

print_success "Original version restored" 