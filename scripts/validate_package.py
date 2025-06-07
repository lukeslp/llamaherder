#!/usr/bin/env python3
"""
Package Validation Script for LlamaHerder

This script validates the built package without relying on twine
"""

import os
import sys
import zipfile
import tarfile
from pathlib import Path

def print_status(message):
    print(f"ℹ️  {message}")

def print_success(message):
    print(f"✅ {message}")

def print_error(message):
    print(f"❌ {message}")

def validate_wheel(wheel_path):
    """Validate wheel file"""
    print_status(f"Validating wheel: {wheel_path}")
    
    try:
        with zipfile.ZipFile(wheel_path, 'r') as wheel:
            files = wheel.namelist()
            
            # Check for required files
            has_metadata = any('METADATA' in f for f in files)
            has_wheel = any('WHEEL' in f for f in files)
            has_record = any('RECORD' in f for f in files)
            has_python_files = any(f.endswith('.py') for f in files)
            
            if not has_metadata:
                print_error("Missing METADATA file")
                return False
            
            if not has_wheel:
                print_error("Missing WHEEL file")
                return False
                
            if not has_record:
                print_error("Missing RECORD file")
                return False
                
            if not has_python_files:
                print_error("No Python files found")
                return False
            
            print_success("Wheel file is valid")
            return True
            
    except Exception as e:
        print_error(f"Error validating wheel: {e}")
        return False

def validate_sdist(sdist_path):
    """Validate source distribution"""
    print_status(f"Validating sdist: {sdist_path}")
    
    try:
        with tarfile.open(sdist_path, 'r:gz') as tar:
            files = tar.getnames()
            
            # Check for required files
            has_setup_cfg = any('setup.cfg' in f for f in files)
            has_pyproject = any('pyproject.toml' in f for f in files)
            has_python_files = any(f.endswith('.py') for f in files)
            has_license = any('LICENSE' in f for f in files)
            has_readme = any('README' in f for f in files)
            
            if not (has_setup_cfg or has_pyproject):
                print_error("Missing setup.cfg or pyproject.toml")
                return False
                
            if not has_python_files:
                print_error("No Python files found")
                return False
                
            if not has_license:
                print_error("Missing LICENSE file")
                return False
                
            if not has_readme:
                print_error("Missing README file")
                return False
            
            print_success("Source distribution is valid")
            return True
            
    except Exception as e:
        print_error(f"Error validating sdist: {e}")
        return False

def main():
    print("🦙 LlamaHerder Package Validation")
    print("=================================")
    
    dist_dir = Path('dist')
    if not dist_dir.exists():
        print_error("dist/ directory not found. Run 'python -m build' first.")
        sys.exit(1)
    
    # Find wheel and sdist files
    wheel_files = list(dist_dir.glob('*.whl'))
    sdist_files = list(dist_dir.glob('*.tar.gz'))
    
    if not wheel_files:
        print_error("No wheel files found in dist/")
        sys.exit(1)
        
    if not sdist_files:
        print_error("No source distribution files found in dist/")
        sys.exit(1)
    
    all_valid = True
    
    # Validate wheel files
    for wheel_file in wheel_files:
        if not validate_wheel(wheel_file):
            all_valid = False
    
    # Validate sdist files
    for sdist_file in sdist_files:
        if not validate_sdist(sdist_file):
            all_valid = False
    
    if all_valid:
        print_success("\n🎉 All packages are valid!")
        print_status("Ready for publishing to PyPI")
        return 0
    else:
        print_error("\n❌ Package validation failed")
        return 1

if __name__ == '__main__':
    sys.exit(main()) 