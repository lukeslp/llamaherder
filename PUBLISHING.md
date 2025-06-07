# Publishing Guide for LlamaHerder

This guide covers how to publish LlamaHerder to PyPI using both automated workflows and manual scripts.

## Prerequisites

### 1. PyPI Account Setup
1. Create accounts on [PyPI](https://pypi.org) and [Test PyPI](https://test.pypi.org)
2. Enable 2FA on both accounts
3. Generate API tokens:
   - PyPI: Account settings → API tokens → Add API token
   - Test PyPI: Account settings → API tokens → Add API token

### 2. Local Setup
```bash
# Install required tools
pip install build twine

# Copy and configure PyPI credentials
cp .pypirc.template ~/.pypirc
# Edit ~/.pypirc with your API tokens
```

### 3. GitHub Setup (for automated publishing)
Add these secrets to your GitHub repository:
- `PYPI_API_TOKEN`: Your PyPI API token
- `TEST_PYPI_API_TOKEN`: Your Test PyPI API token

## Publishing Methods

### Method 1: Automated Publishing (Recommended)

#### For Test Releases
1. Create a development tag:
   ```bash
   git tag v0.1.0-dev
   git push origin v0.1.0-dev
   ```
2. GitHub Actions will automatically publish to Test PyPI

#### For Production Releases
1. Create a GitHub release:
   - Go to GitHub → Releases → Create a new release
   - Tag: `v0.1.0` (semantic versioning)
   - Title: `Release v0.1.0`
   - Description: Release notes
2. GitHub Actions will automatically publish to PyPI

### Method 2: Manual Publishing

#### Prepare Release
```bash
# Run the preparation script
python scripts/prepare_release.py

# Or manually update version in pyproject.toml
```

#### Test Publishing
```bash
# Publish to Test PyPI first
./scripts/publish_to_test_pypi.sh

# Test installation
pip install --index-url https://test.pypi.org/simple/ herd-ai==0.1.0.dev20231207120000
```

#### Production Publishing
```bash
# Publish to PyPI
./scripts/publish_to_pypi.sh
```

## Version Management

### Semantic Versioning
We follow [Semantic Versioning](https://semver.org/):
- `MAJOR.MINOR.PATCH` (e.g., 1.0.0)
- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Version Bump Examples
```bash
# Current: 0.1.0
# Patch: 0.1.1 (bug fixes)
# Minor: 0.2.0 (new features)
# Major: 1.0.0 (breaking changes)
```

## Release Checklist

### Pre-Release
- [ ] All tests pass
- [ ] Documentation is updated
- [ ] CHANGELOG.md is updated
- [ ] Version is bumped in pyproject.toml
- [ ] All changes are committed and pushed

### Test Release
- [ ] Publish to Test PyPI
- [ ] Test installation from Test PyPI
- [ ] Verify package functionality

### Production Release
- [ ] Create GitHub release with proper tag
- [ ] Verify PyPI publication
- [ ] Test installation from PyPI
- [ ] Update documentation if needed

## Troubleshooting

### Common Issues

#### 1. "File already exists" error
```bash
# Clean build directories
rm -rf build/ dist/ *.egg-info/
```

#### 2. Authentication errors
```bash
# Check your ~/.pypirc file
# Ensure API tokens are correct
# Verify 2FA is enabled
```

#### 3. Package validation errors
```bash
# Check package with twine
python -m build
twine check dist/*
```

#### 4. Import errors after installation
```bash
# Ensure all dependencies are in pyproject.toml
# Test in a clean virtual environment
```

### Manual Commands

#### Build package
```bash
python -m build
```

#### Check package
```bash
twine check dist/*
```

#### Upload to Test PyPI
```bash
twine upload --repository testpypi dist/*
```

#### Upload to PyPI
```bash
twine upload dist/*
```

## GitHub Actions Workflows

### CI Workflow (`.github/workflows/ci.yml`)
- Runs on every push and PR
- Tests across multiple Python versions and platforms
- Validates package building

### Publish Workflow (`.github/workflows/publish.yml`)
- Triggers on GitHub releases
- Publishes to PyPI automatically
- Creates release artifacts

### Security Workflow (`.github/workflows/security.yml`)
- Weekly security scans
- Dependency vulnerability checks

## Best Practices

1. **Always test first**: Use Test PyPI before production
2. **Version consistency**: Ensure version is updated everywhere
3. **Clean builds**: Remove old build artifacts
4. **Test installation**: Verify package works after publishing
5. **Documentation**: Keep README and docs updated
6. **Security**: Use API tokens, not passwords
7. **Automation**: Prefer GitHub Actions for consistency

## Support

For issues with publishing:
1. Check this guide first
2. Review GitHub Actions logs
3. Check PyPI project page
4. Consult [PyPI documentation](https://packaging.python.org/)

## Links

- [PyPI Project Page](https://pypi.org/project/herd-ai/)
- [Test PyPI Project Page](https://test.pypi.org/project/herd-ai/)
- [GitHub Repository](https://github.com/lukeslp/llamaherder)
- [PyPI Publishing Guide](https://packaging.python.org/tutorials/packaging-projects/) 