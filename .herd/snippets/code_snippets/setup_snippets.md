# Code Snippets from /Volumes/Galactus/_DEV/herd/setup.py

File: `/Volumes/Galactus/_DEV/herd/setup.py`  
Language: Python  
Extracted: 2025-05-01 13:07:19  

## Snippet 1
Lines 4-13

```Python
Setup script for PyPI package
"""

from setuptools import setup, find_packages
import os
import re

# Read version from src/herd_ai/__init__.py
with open(os.path.join("src", "herd_ai", "__init__.py"), "r", encoding="utf-8") as f:
    version_match = re.search(r"^__version__\s*=\s*['\"]([^'\"]*)['\"]", f.read(), re.MULTILINE)
```

## Snippet 2
Lines 16-29

```Python
# Read long description from README.md
try:
    with open("README.md", "r", encoding="utf-8") as f:
        long_description = f.read()
except FileNotFoundError:
    long_description = "Herd AI - Document Analysis & Code Management Tools"

setup(
    name="herd-ai",
    version=version,
    description="AI-powered document analysis and code management tools",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Luke Steuber",
```

## Snippet 3
Lines 30-69

```Python
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
```

