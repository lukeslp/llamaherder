#!/bin/bash

# Publishing Help Script for LlamaHerder
# Shows all available publishing commands and workflows

echo "🦙 LlamaHerder Publishing Commands"
echo "=================================="
echo
echo "📋 Available Scripts:"
echo "  ./scripts/prepare_release.py     - Prepare a new release (version bump, changelog)"
echo "  ./scripts/validate_package.py    - Validate built packages"
echo "  ./scripts/publish_to_test_pypi.sh - Publish to Test PyPI for testing"
echo "  ./scripts/publish_to_pypi.sh     - Publish to production PyPI"
echo "  ./scripts/publish_help.sh        - Show this help message"
echo
echo "🔄 Publishing Workflow:"
echo "  1. Prepare release:    python scripts/prepare_release.py"
echo "  2. Test publish:       ./scripts/publish_to_test_pypi.sh"
echo "  3. Test installation:  pip install --index-url https://test.pypi.org/simple/ herd-ai"
echo "  4. Production publish: ./scripts/publish_to_pypi.sh"
echo
echo "🤖 Automated Publishing (GitHub Actions):"
echo "  • Test PyPI: Create tag with 'dev' suffix (e.g., v0.1.0-dev)"
echo "  • Production: Create GitHub release with version tag (e.g., v0.1.0)"
echo
echo "🔧 Manual Commands:"
echo "  Build package:         python -m build"
echo "  Validate package:      python scripts/validate_package.py"
echo "  Upload to Test PyPI:   twine upload --repository testpypi dist/*"
echo "  Upload to PyPI:        twine upload dist/*"
echo
echo "📚 Documentation:"
echo "  • Full guide: PUBLISHING.md"
echo "  • PyPI page: https://pypi.org/project/herd-ai/"
echo "  • Test PyPI: https://test.pypi.org/project/herd-ai/"
echo
echo "⚠️  Prerequisites:"
echo "  • PyPI account with API tokens"
echo "  • ~/.pypirc configured (see .pypirc.template)"
echo "  • All tests passing"
echo "  • Documentation updated" 