#!/bin/bash

# LlamaHerder Installation Script
# This script installs the LlamaHerder package with all dependencies

set -e  # Exit on any error

echo "🦙 LlamaHerder Installation Script"
echo "=================================="

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    echo "Please install Python 3.8 or later and try again."
    exit 1
fi

# Check Python version
python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo "🐍 Found Python $python_version"

# Check if pip is available
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is required but not installed."
    echo "Please install pip and try again."
    exit 1
fi

echo "📦 Installing LlamaHerder package..."

# Install in development mode with all dependencies
pip3 install -e ".[all]"

echo "✅ Installation complete!"
echo ""
echo "🚀 You can now run:"
echo "   herd --help          # Show CLI help"
echo "   herd --gui           # Launch web interface"
echo "   herd                 # Interactive menu"
echo ""
echo "🔧 For development:"
echo "   pre-commit install   # Install git hooks"
echo "   pytest               # Run tests"
echo ""
echo "📚 Documentation: https://github.com/lukeslp/llamaherder#readme" 