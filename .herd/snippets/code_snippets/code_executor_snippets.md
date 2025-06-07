# Code Snippets from toollama/API/api-tools/tools/code/runner/code_executor.py

File: `toollama/API/api-tools/tools/code/runner/code_executor.py`  
Language: Python  
Extracted: 2025-06-07 05:24:56  

## Snippet 1
Lines 1-8

```Python
import os
import sys
import json
import asyncio
import tempfile
import subprocess
from typing import Dict, Any, Optional
```

## Snippet 2
Lines 12-15

```Python
def __init__(self):
        self.python_path = sys.executable
        self.temp_dir = tempfile.gettempdir()
```

## Snippet 3
Lines 16-40

```Python
async def run_python_code(self, code: str) -> str:
        """Run Python code in a restricted environment"""
        try:
            # Create a temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(code)
                temp_path = f.name

            # Run with restricted permissions
            process = await asyncio.create_subprocess_exec(
                self.python_path,
                temp_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=self.temp_dir,
                env={
                    'PATH': os.environ.get('PATH', ''),
                    'PYTHONPATH': '',  # Restrict imports
                    'PYTHONHOME': '',  # Restrict Python environment
                }
            )

            stdout, stderr = await process.communicate()
            os.unlink(temp_path)  # Clean up temp file
```

## Snippet 4
Lines 51-54

```Python
async def run_bash_command(self, command: str) -> str:
        """Run a bash command with restricted permissions"""
        try:
            # Basic command validation
```

## Snippet 5
Lines 55-73

```Python
if any(unsafe in command.lower() for unsafe in ['sudo', 'rm -rf', '>', '>>', '|', '&', ';']):
                return "Error: Command contains unsafe operations"

            # Run with restricted shell
            process = await asyncio.create_subprocess_exec(
                'sh',
                '-c',
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=self.temp_dir,
                env={
                    'PATH': '/usr/bin:/bin',  # Restrict available commands
                    'HOME': self.temp_dir,
                }
            )

            stdout, stderr = await process.communicate()
```

