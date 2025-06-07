# Code Snippets from src/herd_ai/utils/scrambler.py

File: `src/herd_ai/utils/scrambler.py`  
Language: Python  
Extracted: 2025-06-07 05:09:42  

## Snippet 1
Lines 10-24

```Python
# No credentials are required for these utilities.
#
###############################################################################

import random
import string
from pathlib import Path
import zipfile
import gzip
from typing import Callable, Optional

###############################################################################
# scramble_directory
#
# Randomly renames all non-hidden, non-special files in the specified directory.
```

## Snippet 2
Lines 43-47

```Python
def scramble_directory(
    target_dir: Path,
    log_callback: Optional[Callable[[str], None]] = None
) -> int:
    files = [
```

## Snippet 3
Lines 52-54

```Python
if log_callback:
            log_callback("No files found in directory.")
        return 0
```

## Snippet 4
Lines 63-69

```Python
while new_path.exists():
                random_name = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
                new_name = f"{random_name}{file_path.suffix}"
                new_path = file_path.parent / new_name
            try:
                file_path.rename(new_path)
                rename_log.append((str(file_path), str(new_path)))
```

## Snippet 5
Lines 75-78

```Python
log_path = target_dir / "scramble_rename_log.txt"
    try:
        with open(log_path, 'w', encoding='utf-8') as f:
            f.write("Original Name,New Name\n")
```

## Snippet 6
Lines 112-123

```Python
def generate_sample_files(
    target_dir: Path,
    files_per_ext: int = 3,
    log_callback: Optional[Callable[[str], None]] = None
) -> int:
    sample_extensions = [
        ".jpg", ".png", ".gif", ".heic", ".docx", ".pptx", ".zip", ".gz",
        ".txt", ".pdf", ".csv", ".json", ".xml", ".mp3", ".mp4", ".avi",
        ".mkv", ".html", ".css", ".js", ".py", ".rb", ".java", ".c",
        ".cpp", ".sh", ".bat", ".iso"
    ]
    total_files = len(sample_extensions) * files_per_ext
```

## Snippet 7
Lines 126-132

```Python
generated_files = []
    sample_image_bytes = {
        ".jpg": b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00\xff\xd9',
        ".png": b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\nIDAT\x08\xd7c\x00\x01\x00\x00\x05\x00\x01\r\n,\x89\x00\x00\x00\x00IEND\xaeB`\x82',
        ".gif": b'GIF89a\x01\x00\x01\x00\x80\xff\x00\xff\xff\xff\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;',
        ".heic": b'\x00\x00\x00\x18ftypheic\x00\x00\x00\x00heic'
    }
```

## Snippet 8
Lines 135-141

```Python
Helper function to create a single sample file with the given extension.

        Args:
            new_path (Path): Full path to the new file.
            ext (str): File extension (including dot).
        """
        try:
```

## Snippet 9
Lines 142-144

```Python
if ext in sample_image_bytes:
                with open(new_path, "wb") as f:
                    f.write(sample_image_bytes[ext])
```

## Snippet 10
Lines 151-154

```Python
elif ext == ".pdf":
                pdf_content = b"%PDF-1.4\n%Dummy PDF content\n%%EOF"
                with open(new_path, "wb") as f:
                    f.write(pdf_content)
```

## Snippet 11
Lines 156-158

```Python
content = f"Dummy binary content for {ext} file.".encode('utf-8')
                with open(new_path, "wb") as f:
                    f.write(content)
```

## Snippet 12
Lines 170-175

```Python
while new_path.exists():
                random_name = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
                new_name = f"{random_name}{ext}"
                new_path = target_dir / new_name
            create_sample_file(new_path, ext)
            generated_files.append(str(new_path))
```

