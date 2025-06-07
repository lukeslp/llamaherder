#!/usr/bin/env python3
"""Release Preparation Script for LlamaHerder"""

import os
import re
import sys
from pathlib import Path
from datetime import datetime

def get_current_version():
    """Get current version from pyproject.toml"""
    with open('pyproject.toml', 'r') as f:
        content = f.read()
    match = re.search(r'version = ["\']([^"\']+)["\']', content)
    return match.group(1) if match else None

def update_version(new_version):
    """Update version in pyproject.toml"""
    with open('pyproject.toml', 'r') as f:
        content = f.read()
    
    content = re.sub(
        r'version = ["\'][^"\']+["\']',
        f'version = "{new_version}"',
        content
    )
    
    with open('pyproject.toml', 'w') as f:
        f.write(content)

def main():
    print("🦙 LlamaHerder Release Preparation")
    print("=================================")
    
    if not Path('pyproject.toml').exists():
        print("❌ pyproject.toml not found. Run from project root.")
        sys.exit(1)
    
    current_version = get_current_version()
    print(f"Current version: {current_version}")
    
    print("\nVersion bump options:")
    print("1) Patch (0.1.0 -> 0.1.1)")
    print("2) Minor (0.1.0 -> 0.2.0)")
    print("3) Major (0.1.0 -> 1.0.0)")
    print("4) Custom version")
    
    choice = input("Select option (1-4): ").strip()
    
    if choice == '1':
        parts = current_version.split('.')
        parts[2] = str(int(parts[2]) + 1)
        new_version = '.'.join(parts)
    elif choice == '2':
        parts = current_version.split('.')
        parts[1] = str(int(parts[1]) + 1)
        parts[2] = '0'
        new_version = '.'.join(parts)
    elif choice == '3':
        parts = current_version.split('.')
        parts[0] = str(int(parts[0]) + 1)
        parts[1] = '0'
        parts[2] = '0'
        new_version = '.'.join(parts)
    elif choice == '4':
        new_version = input("Enter new version: ").strip()
    else:
        print("❌ Invalid choice")
        sys.exit(1)
    
    print(f"New version: {new_version}")
    
    if input("Update version? (y/N): ").lower().startswith('y'):
        update_version(new_version)
        print("✅ Version updated")
        
        # Create release notes template
        release_notes = f"""# Release v{new_version}

## Changes
- Feature 1
- Bug fix 1

## Installation
```bash
pip install herd-ai=={new_version}
```
"""
        
        with open(f'release_notes_v{new_version}.md', 'w') as f:
            f.write(release_notes)
        
        print(f"✅ Created release_notes_v{new_version}.md")
        print("\nNext steps:")
        print("1. Edit release notes")
        print("2. Test: ./scripts/publish_to_test_pypi.sh")
        print("3. Publish: ./scripts/publish_to_pypi.sh")

if __name__ == '__main__':
    main() 