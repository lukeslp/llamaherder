#!/usr/bin/env python3
###############################################################################
# Herd AI - setup.py
# -----------------------------------------------------------------------------
# PyPI setup script for the Herd AI package.
#
# This script configures the packaging, distribution, and installation of the
# Herd AI project. It reads metadata, dependencies, and entry points, and
# ensures the package is ready for publishing to PyPI or installation via pip.
#
# Major Functions:
#   - Reads the package version from src/herd_ai/__init__.py
#   - Reads the long description from README.md (for PyPI display)
#   - Configures setuptools with all required metadata, dependencies, and
#     entry points for CLI tools.
#
# Arguments:
#   - None (run as a script or via pip/setuptools)
#
# Credentials:
#   - None required for running this script.
#
# Usage:
#   python setup.py install
#   pip install .
###############################################################################

from setuptools import setup, find_packages
import os
import re

###############################################################################
# get_version
# -----------------------------------------------------------------------------
# Reads the __version__ string from src/herd_ai/__init__.py.
#
# Returns:
#   - version (str): The version string, e.g., "0.2.0"
###############################################################################
with open(os.path.join("src", "herd_ai", "__init__.py"), "r", encoding="utf-8") as f:
    version_match = re.search(
        r"^__version__\s*=\s*['\"]([^'\"]*)['\"]",
        f.read(),
        re.MULTILINE
    )
    version = version_match.group(1) if version_match else "0.2.0"

###############################################################################
# get_long_description
# -----------------------------------------------------------------------------
# Reads the long description from README.md for PyPI.
#
# Returns:
#   - long_description (str): The full README content, or a fallback string.
###############################################################################
try:
    with open("README.md", "r", encoding="utf-8") as f:
        long_description = f.read()
except FileNotFoundError:
    long_description = "Herd AI - Document Analysis & Code Management Tools"

###############################################################################
# setuptools.setup
# -----------------------------------------------------------------------------
# Main setup configuration for the Herd AI package.
#
# Arguments:
#   - name: Package name for PyPI.
#   - version: Version string.
#   - description: Short summary.
#   - long_description: Full description for PyPI.
#   - long_description_content_type: Format of the long description.
#   - author: Author name.
#   - author_email: Author contact email.
#   - url: Project homepage.
#   - package_dir: Source directory mapping.
#   - packages: List of packages to include.
#   - classifiers: PyPI classifiers for discoverability.
#   - python_requires: Minimum Python version.
#   - install_requires: List of required dependencies.
#   - entry_points: CLI entry points for console scripts.
#   - keywords: Search keywords.
#   - project_urls: Additional project links.
#   - include_package_data: Whether to include package data files.
#   - package_data: Patterns for data files to include.
###############################################################################
setup(
    name="herd-ai",
    version=version,
    description="AI-powered document analysis and code management tools",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Luke Steuber",
    author_email="lsteuber@gmail.com",
    url="https://github.com/yourusername/herd-ai",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Documentation",
        "Topic :: Text Processing :: Markup",
    ],
    python_requires=">=3.8",
    install_requires=[
        "rich>=10.0.0",
        "requests>=2.25.0",
        "Pillow>=8.0.0",
        "pyyaml>=5.4.0",
        "pyperclip>=1.8.0",
    ],
    entry_points={
        "console_scripts": [
            "herd=herd_ai.__main__:run_as_module",
            "llamacleaner=herd_ai.__main__:run_as_module",  # For backward compatibility
        ],
    },
    keywords="ai, document analysis, code management, documentation, llm",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/herd-ai/issues",
        "Source": "https://github.com/yourusername/herd-ai",
        "Documentation": "https://github.com/yourusername/herd-ai/blob/main/README.md",
    },
    include_package_data=True,
    package_data={
        "herd_ai": ["**/*.yml", "**/*.yaml"],
    },
)