# Code Snippets from src/herd_ai/utils/media.py

File: `src/herd_ai/utils/media.py`  
Language: Python  
Extracted: 2025-06-07 05:09:58  

## Snippet 1
Lines 8-34

```Python
# Accessibility: All generated markdown is structured for screen readers.
#                File renaming and metadata extraction are robust and logged.
###############################################################################

import os
import logging
import subprocess
import gc
import json
from pathlib import Path
from typing import Dict, Optional, Tuple, Union, Any
from datetime import datetime

from cleanupx.config import MEDIA_EXTENSIONS
from cleanupx.utils.common import (
    get_media_dimensions,
    get_media_duration,
    format_duration,
    strip_media_suffixes
)
from cleanupx.processors.base import BaseProcessor
from cleanupx.utils.cache import save_cache, ensure_metadata_dir, get_description_path

logger = logging.getLogger(__name__)

###############################################################################
# get_media_info
```

## Snippet 2
Lines 39-60

```Python
def get_media_info(file_path: Union[str, Path]) -> Optional[Dict[str, Any]]:
    file_path = Path(file_path)
    result = {
        "duration": None,
        "width": None,
        "height": None,
        "format": None,
        "size": None,
        "error": None
    }
    try:
        result["size"] = file_path.stat().st_size
        result["format"] = file_path.suffix.lower()
        cmd = [
            "ffprobe",
            "-v", "quiet",
            "-print_format", "json",
            "-show_format",
            "-show_streams",
            str(file_path)
        ]
        process = subprocess.run(cmd, capture_output=True, text=True)
```

## Snippet 3
Lines 72-76

```Python
except Exception as e:
        logger.error(f"Error analyzing media file {file_path}: {e}")
        result["error"] = str(e)
    return result
```

## Snippet 4
Lines 82-85

```Python
def format_duration(seconds: float) -> str:
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)
```

## Snippet 5
Lines 86-90

```Python
if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    else:
        return f"{minutes:02d}:{seconds:02d}"
```

## Snippet 6
Lines 97-105

```Python
def process_media_file(file_path: Union[str, Path], logger: logging.Logger) -> Dict[str, Any]:
    file_path = Path(file_path)
    result = {
        "processed": False,
        "error": None,
        "info": None
    }
    try:
        info = get_media_info(file_path)
```

## Snippet 7
Lines 106-112

```Python
if info and not info.get("error"):
            result["processed"] = True
            result["info"] = info
            md_path = file_path.parent / f"{file_path.stem}_description.md"
            with open(md_path, 'w') as f:
                f.write(f"# {file_path.name}\n\n")
                f.write("## Media Information\n\n")
```

## Snippet 8
Lines 121-125

```Python
except Exception as e:
        logger.error(f"Error processing media file {file_path}: {e}")
        result["error"] = str(e)
    return result
```

## Snippet 9
Lines 133-142

```Python
def __init__(self):
        """
        Initialize the media processor with supported extensions and size limit.
        """
        super().__init__()
        self.supported_extensions = MEDIA_EXTENSIONS
        self.max_size_mb = 100.0

    ###########################################################################
    # process
```

## Snippet 10
Lines 147-162

```Python
def process(
        self,
        file_path: Union[str, Path],
        cache: Dict[str, Any],
        rename_log: Optional[Dict] = None
    ) -> Dict:
        file_path = Path(file_path)
        result = {
            'original_path': str(file_path),
            'new_path': None,
            'description': None,
            'metadata_extracted': False,
            'renamed': False,
            'error': None
        }
        try:
```

## Snippet 11
Lines 163-165

```Python
if not self.can_process(file_path):
                result['error'] = f"Unsupported file type: {file_path.suffix}"
                return result
```

## Snippet 12
Lines 166-169

```Python
if not self.check_file_size(file_path):
                result['error'] = f"File size exceeds maximum ({self.max_size_mb}MB)"
                return result
            description = self._extract_metadata(file_path, cache)
```

## Snippet 13
Lines 170-175

```Python
if not description:
                result['error'] = "Failed to extract metadata"
                return result
            result['description'] = description
            result['metadata_extracted'] = True
            new_name = self._generate_media_filename(file_path, description)
```

## Snippet 14
Lines 176-179

```Python
if not new_name:
                result['error'] = "Failed to generate new filename"
                return result
            new_path = super().rename_file(file_path, new_name, rename_log)
```

## Snippet 15
Lines 180-184

```Python
if new_path:
                result['new_path'] = str(new_path)
                result['renamed'] = True
            self._generate_markdown(file_path, description)
            return result
```

## Snippet 16
Lines 185-191

```Python
except Exception as e:
            logger.error(f"Error processing media file {file_path}: {e}")
            result['error'] = str(e)
            return result
        finally:
            gc.collect()
```

## Snippet 17
Lines 198-204

```Python
def _extract_metadata(
        self,
        file_path: Path,
        cache: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        try:
            cache_key = str(file_path)
```

## Snippet 18
Lines 208-216

```Python
dimensions = get_media_dimensions(file_path)
            duration = get_media_duration(file_path)
            file_stats = file_path.stat()
            file_size_mb = file_stats.st_size / (1024 * 1024)
            modified_time = datetime.fromtimestamp(file_stats.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
            data = {
                "dimensions": dimensions,
                "duration": duration,
                "format_duration": format_duration(duration),
```

## Snippet 19
Lines 222-225

```Python
}
            cache[cache_key] = data
            save_cache(cache)
            return data
```

## Snippet 20
Lines 226-229

```Python
except Exception as e:
            logger.error(f"Error extracting metadata from {file_path}: {e}")
            return None
```

## Snippet 21
Lines 236-245

```Python
def _generate_media_filename(
        self,
        file_path: Path,
        description: Dict[str, Any]
    ) -> Optional[str]:
        try:
            original_stem = strip_media_suffixes(file_path.stem)
            ext = file_path.suffix.lower()
            dimensions = description.get('dimensions')
            duration = description.get('duration')
```

## Snippet 22
Lines 247-249

```Python
if dimensions and dimensions != 'Unknown' and duration:
                    duration_str = format_duration(duration).replace(':', '_')
                    return f"{original_stem}_{dimensions}_{duration_str}{ext}"
```

## Snippet 23
Lines 252-254

```Python
elif duration:
                    duration_str = format_duration(duration).replace(':', '_')
                    return f"{original_stem}_{duration_str}{ext}"
```

## Snippet 24
Lines 256-258

```Python
if duration:
                    duration_str = format_duration(duration).replace(':', '_')
                    return f"{original_stem}_{duration_str}{ext}"
```

## Snippet 25
Lines 270-286

```Python
def _generate_markdown(
        self,
        file_path: Path,
        description: Dict[str, Any]
    ):
        try:
            ensure_metadata_dir(file_path.parent)
            md_path = get_description_path(file_path)
            content = [
                f"# {description.get('title', file_path.stem)}",
                "",
                "## Media Information",
                f"- **Original Filename:** {file_path.name}",
                f"- **Media Type:** {description.get('type', 'Unknown')}",
                f"- **File Size:** {description.get('file_size', 'Unknown')}",
                f"- **Modified Date:** {description.get('modified_date', 'Unknown')}"
            ]
```

## Snippet 26
Lines 289-298

```Python
if description.get('duration'):
                content.append(f"- **Duration:** {description.get('format_duration', format_duration(description.get('duration')))}")
            content.extend([
                "",
                "## Description",
                description.get('description', 'No description available')
            ])
            with open(md_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(content))
            logger.info(f"Generated markdown description: {md_path}")
```

## Snippet 27
Lines 308-315

```Python
def process_media_file(
    file_path: Union[str, Path],
    cache: Dict[str, Any],
    rename_log: Optional[Dict] = None
) -> Tuple[Path, Optional[Path], Optional[Dict[str, Any]]]:
    processor = MediaProcessor()
    result = processor.process(file_path, cache, rename_log)
    new_path = None
```

## Snippet 28
Lines 316-318

```Python
if result.get('new_path'):
        new_path = Path(result['new_path'])
    return Path(file_path), new_path, result.get('description')
```

