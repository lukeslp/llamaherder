# Code Snippets from toollama/API/api-tools/tools/python/analyze_schemas.py

File: `toollama/API/api-tools/tools/python/analyze_schemas.py`  
Language: Python  
Extracted: 2025-06-07 05:20:40  

## Snippet 1
Lines 1-21

```Python
#!/usr/bin/env python3
"""
Script to analyze and categorize OpenAPI schemas.
"""

import json
import logging
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

import yaml
from schema_utils import SchemaValidator

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
```

## Snippet 2
Lines 23-40

```Python
"""Analyzer for OpenAPI schemas."""

    # Schema categories and their keywords
    CATEGORIES = {
        'api_integration': {
            'keywords': ['api', 'endpoint', 'service', 'integration'],
            'paths': True  # Has API paths
        },
        'data_model': {
            'keywords': ['model', 'schema', 'type', 'object'],
            'components': True  # Has reusable components
        },
        'utility': {
            'keywords': ['util', 'helper', 'common', 'shared'],
            'generic': True  # Generic/utility schemas
        }
    }
```

## Snippet 3
Lines 41-49

```Python
def __init__(self, schema_dir: Path):
        """Initialize the analyzer.

        Args:
            schema_dir: Directory containing schemas to analyze
        """
        self.schema_dir = Path(schema_dir)
        self.validator = SchemaValidator(schema_dir)
```

## Snippet 4
Lines 50-59

```Python
def analyze_schema(self, schema_path: Path) -> Tuple[str, Dict]:
        """Analyze a single schema file.

        Args:
            schema_path: Path to schema file

        Returns:
            Tuple of (category, analysis_results)
        """
        with open(schema_path) as f:
```

## Snippet 5
Lines 60-64

```Python
if schema_path.suffix in ['.yaml', '.yml']:
                schema = yaml.safe_load(f)
            else:
                schema = json.load(f)
```

## Snippet 6
Lines 65-73

```Python
# Analyze schema structure
        has_paths = 'paths' in schema
        has_components = 'components' in schema

        # Extract keywords from schema content
        content_str = json.dumps(schema).lower()

        # Determine category
        scores = defaultdict(int)
```

## Snippet 7
Lines 78-81

```Python
if criteria.get('components') and has_components:
                scores[category] += 2

            # Check keywords
```

## Snippet 8
Lines 87-100

```Python
category = max(scores.items(), key=lambda x: x[1])[0] if scores else 'unknown'

        # Collect analysis results
        results = {
            'category': category,
            'has_paths': has_paths,
            'has_components': has_components,
            'component_types': list(schema.get('components', {}).keys()),
            'endpoint_count': len(schema.get('paths', {})),
            'size_bytes': schema_path.stat().st_size
        }

        return category, results
```

## Snippet 9
Lines 101-108

```Python
def analyze_all(self) -> Dict[str, List[Dict]]:
        """Analyze all schemas in the directory.

        Returns:
            Dict mapping categories to lists of schema analysis results
        """
        results = defaultdict(list)
```

## Snippet 10
Lines 109-120

```Python
for schema_file in self.schema_dir.glob('**/*.{yaml,yml,json}'):
            try:
                category, analysis = self.analyze_schema(schema_file)
                results[category].append({
                    'file': str(schema_file),
                    **analysis
                })
            except Exception as e:
                logger.error(f"Error analyzing {schema_file}: {e}")

        return dict(results)
```

## Snippet 11
Lines 121-131

```Python
def suggest_organization(self) -> Dict[str, Set[Path]]:
        """Suggest how to organize schemas based on analysis.

        Returns:
            Dict mapping target directories to sets of schema files
        """
        organization = defaultdict(set)

        # Analyze all schemas
        analysis_results = self.analyze_all()
```

## Snippet 12
Lines 139-142

```Python
if schema['has_components']:
                        organization['components/models'].add(schema_path)
                    else:
                        organization['schemas'].add(schema_path)
```

## Snippet 13
Lines 144-147

```Python
if 'responses' in schema['component_types']:
                        organization['components/responses'].add(schema_path)
                    else:
                        organization['components'].add(schema_path)
```

## Snippet 14
Lines 153-167

```Python
def generate_report(self, output_path: Optional[Path] = None) -> str:
        """Generate a markdown report of the analysis.

        Args:
            output_path: Optional path to write report

        Returns:
            Report content as string
        """
        analysis = self.analyze_all()

        # Build report
        lines = ['# Schema Analysis Report\n']

        # Summary
```

## Snippet 15
Lines 168-173

```Python
total_schemas = sum(len(schemas) for schemas in analysis.values())
        lines.append(f"## Summary\n")
        lines.append(f"Total schemas analyzed: {total_schemas}\n")

        # Categories
        lines.append(f"## Categories\n")
```

## Snippet 16
Lines 174-179

```Python
for category, schemas in analysis.items():
            lines.append(f"### {category.replace('_', ' ').title()}\n")
            lines.append(f"Total: {len(schemas)}\n")
            lines.append("| File | Endpoints | Component Types | Size |\n")
            lines.append("|------|-----------|-----------------|------|\n")
```

## Snippet 17
Lines 180-183

```Python
for schema in schemas:
                components = ', '.join(schema['component_types']) or 'None'
                size_kb = schema['size_bytes'] / 1024
                lines.append(
```

## Snippet 18
Lines 193-197

```Python
if output_path:
            output_path.write_text(report)

        return report
```

## Snippet 19
Lines 198-213

```Python
def main():
    import argparse

    parser = argparse.ArgumentParser(description='Analyze OpenAPI schemas')
    parser.add_argument('schema_dir', type=Path, help='Directory containing schemas')
    parser.add_argument('--report', type=Path, help='Path to write analysis report')

    args = parser.parse_args()

    try:
        analyzer = SchemaAnalyzer(args.schema_dir)
        report = analyzer.generate_report(args.report)
        print(report)

        # Print organization suggestions
        print("\nSuggested Organization:")
```

## Snippet 20
Lines 219-222

```Python
except Exception as e:
        logger.error(f"Error analyzing schemas: {e}")
        raise
```

