#!/bin/bash

# PyPI Publishing Script for LlamaHerder
# This script handles the complete publishing process to PyPI

set -e  # Exit on any error

echo "🦙 LlamaHerder PyPI Publishing Script"
echo "===================================="

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

# Check if required tools are installed
print_status "Checking required tools..."

if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is required but not installed."
    exit 1
fi

if ! command -v git &> /dev/null; then
    print_error "Git is required but not installed."
    exit 1
fi

print_success "Required tools are available"

# Install/upgrade build tools
print_status "Installing/upgrading build tools..."
python3 -m pip install --upgrade pip build twine

# Check git status
print_status "Checking git status..."
if [ -n "$(git status --porcelain)" ]; then
    print_warning "You have uncommitted changes. Please commit or stash them first."
    git status --short
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Get current version from pyproject.toml
CURRENT_VERSION=$(python3 -c "import tomllib; print(tomllib.load(open('pyproject.toml', 'rb'))['project']['version'])" 2>/dev/null || python3 -c "import tomli; print(tomli.load(open('pyproject.toml', 'rb'))['project']['version'])")
print_status "Current version: $CURRENT_VERSION"

# Ask for version bump
echo "Version bump options:"
echo "1) Patch (0.1.0 -> 0.1.1)"
echo "2) Minor (0.1.0 -> 0.2.0)"
echo "3) Major (0.1.0 -> 1.0.0)"
echo "4) Custom version"
echo "5) Keep current version ($CURRENT_VERSION)"

read -p "Select option (1-5): " VERSION_OPTION

case $VERSION_OPTION in
    1)
        NEW_VERSION=$(python3 -c "
import re
version = '$CURRENT_VERSION'
parts = version.split('.')
parts[2] = str(int(parts[2]) + 1)
print('.'.join(parts))
")
        ;;
    2)
        NEW_VERSION=$(python3 -c "
import re
version = '$CURRENT_VERSION'
parts = version.split('.')
parts[1] = str(int(parts[1]) + 1)
parts[2] = '0'
print('.'.join(parts))
")
        ;;
    3)
        NEW_VERSION=$(python3 -c "
import re
version = '$CURRENT_VERSION'
parts = version.split('.')
parts[0] = str(int(parts[0]) + 1)
parts[1] = '0'
parts[2] = '0'
print('.'.join(parts))
")
        ;;
    4)
        read -p "Enter new version: " NEW_VERSION
        ;;
    5)
        NEW_VERSION=$CURRENT_VERSION
        ;;
    *)
        print_error "Invalid option"
        exit 1
        ;;
esac

print_status "New version will be: $NEW_VERSION"

# Update version in pyproject.toml if changed
if [ "$NEW_VERSION" != "$CURRENT_VERSION" ]; then
    print_status "Updating version in pyproject.toml..."
    python3 -c "
import re
with open('pyproject.toml', 'r') as f:
    content = f.read()
content = re.sub(r'version = \".*?\"', f'version = \"$NEW_VERSION\"', content)
with open('pyproject.toml', 'w') as f:
    f.write(content)
"
    print_success "Version updated to $NEW_VERSION"
fi

# Clean previous builds
print_status "Cleaning previous builds..."
rm -rf build/ dist/ *.egg-info/
print_success "Build directories cleaned"

# Run tests (if available)
if [ -f "pytest.ini" ] || [ -d "tests" ]; then
    print_status "Running tests..."
    python3 -m pytest || {
        print_error "Tests failed. Aborting publish."
        exit 1
    }
    print_success "Tests passed"
fi

# Build the package
print_status "Building package..."
python3 -m build

if [ $? -ne 0 ]; then
    print_error "Build failed"
    exit 1
fi

print_success "Package built successfully"

# Check the built package
print_status "Checking package..."
python3 scripts/validate_package.py

if [ $? -ne 0 ]; then
    print_error "Package validation failed"
    exit 1
fi

print_success "Package validation passed"

# Show what will be uploaded
print_status "Files to be uploaded:"
ls -la dist/

# Ask for confirmation
echo
print_warning "You are about to publish to PyPI!"
print_status "Package: herd-ai"
print_status "Version: $NEW_VERSION"
print_status "Files: $(ls dist/ | tr '\n' ' ')"
echo

read -p "Are you sure you want to publish to PyPI? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    print_status "Publishing cancelled"
    exit 0
fi

# Upload to PyPI
print_status "Uploading to PyPI..."
python3 -m twine upload dist/*

if [ $? -eq 0 ]; then
    print_success "Successfully published to PyPI!"
    
    # Commit version change if it was updated
    if [ "$NEW_VERSION" != "$CURRENT_VERSION" ]; then
        print_status "Committing version change..."
        git add pyproject.toml
        git commit -m "Bump version to $NEW_VERSION"
        
        # Create git tag
        print_status "Creating git tag..."
        git tag -a "v$NEW_VERSION" -m "Release version $NEW_VERSION"
        
        print_status "Pushing changes and tags..."
        git push origin main
        git push origin "v$NEW_VERSION"
        
        print_success "Git tag v$NEW_VERSION created and pushed"
    fi
    
    echo
    print_success "🎉 Package published successfully!"
    print_status "You can install it with: pip install herd-ai==$NEW_VERSION"
    print_status "PyPI page: https://pypi.org/project/herd-ai/"
    
else
    print_error "Failed to publish to PyPI"
    exit 1
fi 