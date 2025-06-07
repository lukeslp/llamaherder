# Code Snippets from toollama/setup.py

File: `toollama/setup.py`  
Language: Python  
Extracted: 2025-06-07 05:08:15  

## Snippet 1
Lines 1-8

```Python
"""Setup file for the MoE system."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
```

## Snippet 2
Lines 16-50

```Python
description="A Mixture of Experts system for AI model coordination",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/luketools/toollama",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.4.4",
            "pytest-asyncio>=0.23.3",
            "pytest-cov>=4.1.0",
            "mypy>=1.8.0",
            "black>=23.12.1",
            "isort>=5.13.2",
            "flake8>=7.0.0",
        ],
        "docs": [
            "mkdocs>=1.5.3",
            "mkdocs-material>=9.5.3",
            "mkdocstrings>=0.24.0",
        ],
    },
```

