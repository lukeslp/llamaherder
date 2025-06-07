# Code Snippets from toollama/API/api-tools/tools/python/schema_utils.py

File: `toollama/API/api-tools/tools/python/schema_utils.py`  
Language: Python  
Extracted: 2025-06-07 05:20:41  

## Snippet 1
Lines 2-12

```Python
Schema validation and utility functions for OpenAPI schemas.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Union

import yaml
from jsonschema import validate
```

## Snippet 2
Lines 16-22

```Python
def __init__(self, schema_dir: Union[str, Path]):
        """Initialize the validator with a schema directory.

        Args:
            schema_dir: Path to the directory containing OpenAPI schemas
        """
        self.schema_dir = Path(schema_dir)
```

## Snippet 3
Lines 26-32

```Python
def validate_schema(self, schema_path: Union[str, Path]) -> bool:
        """Validate a single OpenAPI schema file.

        Args:
            schema_path: Path to the schema file

        Returns:
```

## Snippet 4
Lines 40-44

```Python
if schema_path.suffix in ['.yaml', '.yml']:
                spec = yaml.safe_load(f)
            else:
                spec = json.load(f)
```

## Snippet 5
Lines 45-48

```Python
# Basic validation that it's a valid JSON Schema
        validate(instance={}, schema=spec)
        return True
```

## Snippet 6
Lines 49-55

```Python
def validate_all(self) -> Dict[str, bool]:
        """Validate all schema files in the schema directory.

        Returns:
            Dict mapping schema paths to validation results
        """
        results = {}
```

## Snippet 7
Lines 56-62

```Python
for schema_file in self.schema_dir.glob('**/*.{yaml,yml,json}'):
            try:
                results[str(schema_file)] = self.validate_schema(schema_file)
            except Exception as e:
                results[str(schema_file)] = str(e)
        return results
```

## Snippet 8
Lines 63-74

```Python
def deduplicate_schemas(schema_dir: Union[str, Path],
                       output_dir: Optional[Union[str, Path]] = None) -> List[Path]:
    """Find and remove duplicate schema files based on content.

    Args:
        schema_dir: Directory containing schema files
        output_dir: Optional directory to write unique schemas to

    Returns:
        List of paths to duplicate files that were found
    """
    schema_dir = Path(schema_dir)
```

## Snippet 9
Lines 75-82

```Python
if output_dir:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

    # Map content hashes to file paths
    content_map = {}
    duplicates = []
```

## Snippet 10
Lines 83-87

```Python
for schema_file in schema_dir.glob('**/*.{yaml,yml,json}'):
        with open(schema_file) as f:
            content = f.read()
            content_hash = hash(content)
```

## Snippet 11
Lines 88-91

```Python
if content_hash in content_map:
                duplicates.append(schema_file)
            else:
                content_map[content_hash] = schema_file
```

## Snippet 12
Lines 99-112

```Python
def normalize_schema(schema_path: Union[str, Path],
                    output_path: Optional[Union[str, Path]] = None) -> dict:
    """Normalize a schema file by sorting keys and standardizing format.

    Args:
        schema_path: Path to input schema file
        output_path: Optional path to write normalized schema

    Returns:
        Normalized schema as dict
    """
    schema_path = Path(schema_path)

    with open(schema_path) as f:
```

## Snippet 13
Lines 113-117

```Python
if schema_path.suffix in ['.yaml', '.yml']:
            schema = yaml.safe_load(f)
        else:
            schema = json.load(f)
```

## Snippet 14
Lines 125-127

```Python
if output_path:
        output_path = Path(output_path)
        with open(output_path, 'w') as f:
```

## Snippet 15
Lines 128-132

```Python
if output_path.suffix in ['.yaml', '.yml']:
                yaml.dump(normalized, f, sort_keys=True)
            else:
                json.dump(normalized, f, sort_keys=True, indent=2)
```

