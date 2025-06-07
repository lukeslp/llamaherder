# Code Snippets from src/herd_ai/utils/file.py

File: `src/herd_ai/utils/file.py`  
Language: Python  
Extracted: 2025-06-07 05:09:50  

## Snippet 1
Lines 11-22

```Python
# All functions are designed for use in accessible, automated, and interactive
# document and code intelligence workflows.
###############################################################################

import hashlib
import subprocess
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, Union
import logging

try:
```

## Snippet 2
Lines 24-38

```Python
except ImportError:
    fitz = None

try:
    import docx2txt  # For DOCX text extraction
except ImportError:
    docx2txt = None

try:
    from PIL import Image as PILImage
    import pytesseract  # For OCR on images and PDFs
except ImportError:
    PILImage = None
    pytesseract = None
```

## Snippet 3
Lines 39-62

```Python
# --- Herd AI Utility Imports (robust, fallback style) ---
try:
    from herd_ai.utils import dedupe, analysis, config as herd_config, scrambler, undo_log
except ImportError:
    try:
        from llamacleaner.utils import dedupe, analysis, config as herd_config, scrambler, undo_log
    except ImportError:
        try:
            import utils.dedupe as dedupe
            import utils.analysis as analysis
            import utils.config as herd_config
            import utils.scrambler as scrambler
            import utils.undo_log as undo_log
        except ImportError:
            dedupe = None
            analysis = None
            herd_config = None
            scrambler = None
            undo_log = None

logger = logging.getLogger(__name__)

###############################################################################
# ensure_directory
```

## Snippet 4
Lines 67-73

```Python
def ensure_directory(path: Union[str, Path]) -> Path:
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p

###############################################################################
# get_file_extension
```

## Snippet 5
Lines 77-81

```Python
def get_file_extension(path: Union[str, Path]) -> str:
    return Path(path).suffix.lower()

###############################################################################
# get_file_metadata
```

## Snippet 6
Lines 90-102

```Python
def get_file_metadata(path: Union[str, Path]) -> Dict[str, Any]:
    p = Path(path)
    stat = p.stat()
    return {
        'path': str(p),
        'name': p.name,
        'extension': p.suffix,
        'size': stat.st_size,
        'modified': stat.st_mtime,
    }

###############################################################################
# clean_filename
```

## Snippet 7
Lines 110-117

```Python
def clean_filename(name: str) -> str:
    name = name.strip().lower()
    name = re.sub(r'[^a-z0-9]+', '_', name)
    name = re.sub(r'_+', '_', name)
    return name.strip('_')

###############################################################################
# is_ignored_file
```

## Snippet 8
Lines 124-129

```Python
if path.name.startswith('.'):
        return True
    ignored_names = {
        'thumbs.db', 'desktop.ini', '.ds_store', 'icon\r', '.localized',
        '.gitignore', '.gitkeep', 'readme.md', 'license'
    }
```

## Snippet 9
Lines 132-135

```Python
if path.name.startswith(".renamed_"):
        return True
    return False
```

## Snippet 10
Lines 144-146

```Python
if not force_ocr and fitz:
            text = ""
            with fitz.open(file_path) as pdf:
```

## Snippet 11
Lines 151-156

```Python
if PILImage and pytesseract:
            from pdf2image import convert_from_path
            from tempfile import TemporaryDirectory
            text = ""
            with TemporaryDirectory() as tmp:
                images = convert_from_path(file_path, output_folder=tmp)
```

## Snippet 12
Lines 160-163

```Python
except Exception as e:
        logger.error(f"Error extracting text from PDF {file_path}: {e}")
    return ""
```

## Snippet 13
Lines 171-173

```Python
if docx2txt:
            return docx2txt.process(str(file_path))
        return ""
```

## Snippet 14
Lines 174-177

```Python
except Exception as e:
        logger.error(f"Error extracting text from DOCX {file_path}: {e}")
        return ""
```

## Snippet 15
Lines 183-194

```Python
def extract_text_from_txt_like(file_path: Path) -> str:
    try:
        return file_path.read_text(encoding="utf-8", errors="ignore")
    except UnicodeDecodeError:
        try:
            return file_path.read_text(encoding="latin-1", errors="ignore")
        except Exception as e:
            logger.error(f"Error reading text file {file_path}: {e}")
            return ""

###############################################################################
# extract_text_from_image
```

## Snippet 16
Lines 199-208

```Python
if not PILImage or not pytesseract:
        logger.warning("OCR libraries not available. Skipping OCR.")
        return ""
    try:
        img = PILImage.open(image_path)
        return pytesseract.image_to_string(img)
    except Exception as e:
        logger.error(f"Error extracting text from image {image_path}: {e}")
        return ""
```

## Snippet 17
Lines 221-224

```Python
if ext in {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.gif'}:
        return extract_text_from_image(path)
    return extract_text_from_txt_like(path)
```

## Snippet 18
Lines 230-235

```Python
def get_file_size_mb(file_path: Union[str, Path]) -> float:
    try:
        path = Path(file_path)
        size_bytes = path.stat().st_size
        return size_bytes / (1024 * 1024)
    except Exception as e:
```

## Snippet 19
Lines 257-282

```Python
def read_project_stats(directory: Path, recursive: bool = True) -> Dict[str, Any]:
    """
    Analyzes a project directory and returns statistics about files and their types.

    Args:
        directory: The project directory to analyze
        recursive: Whether to analyze subdirectories recursively

    Returns:
        Dictionary containing project statistics:
            - total_files: Total number of files
            - total_size: Total size in bytes of all files
            - extensions: Dictionary counting files by extension
            - biggest_file: Path to the largest file
            - newest_file: Path to the most recently modified file
    """
    stats = {
        'total_files': 0,
        'total_size': 0,
        'extensions': {},
        'biggest_file': None,
        'biggest_file_size': 0,
        'newest_file': None,
        'newest_file_time': 0
    }
```

## Snippet 20
Lines 287-303

```Python
if file_path.is_file() and not is_ignored_file(file_path):
            # Update file count
            stats['total_files'] += 1

            # Get file metadata
            file_stat = file_path.stat()
            file_size = file_stat.st_size
            file_mtime = file_stat.st_mtime

            # Update total size
            stats['total_size'] += file_size

            # Track by extension
            ext = file_path.suffix.lower()
            stats['extensions'][ext] = stats['extensions'].get(ext, 0) + 1

            # Track biggest file
```

## Snippet 21
Lines 320-344

```Python
def get_file_count_by_type(directory: Path, recursive: bool = True) -> Dict[str, int]:
    """
    Categorizes and counts files by their type based on file extensions.

    Args:
        directory: The directory to analyze
        recursive: Whether to analyze subdirectories recursively

    Returns:
        Dictionary with file type categories as keys and counts as values
    """
    # Define file type categories based on extensions
    type_categories = {
        'document': {'.pdf', '.docx', '.doc', '.rtf', '.txt', '.md', '.odt'},
        'code': {'.py', '.js', '.html', '.css', '.java', '.c', '.cpp', '.h', '.cs', '.php', '.go', '.rs', '.rb', '.swift'},
        'image': {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp', '.svg', '.ico'},
        'audio': {'.mp3', '.wav', '.ogg', '.flac', '.aac', '.m4a'},
        'video': {'.mp4', '.avi', '.mov', '.wmv', '.mkv', '.flv', '.webm'},
        'archive': {'.zip', '.rar', '.7z', '.tar', '.gz', '.bz2'},
        'data': {'.csv', '.json', '.xml', '.yaml', '.yml', '.sql', '.db'},
        'presentation': {'.ppt', '.pptx', '.key', '.odp'},
        'spreadsheet': {'.xls', '.xlsx', '.ods', '.csv'},
    }

    # Initialize counts
```

## Snippet 22
Lines 359-363

```Python
if ext in extensions:
                    counts[category] += 1
                    categorized = True
                    break
```

## Snippet 23
Lines 375-379

```Python
def get_cache_key(path_str: str) -> str:
    return hashlib.md5(path_str.encode('utf-8')).hexdigest()

###############################################################################
# get_image_dimensions
```

## Snippet 24
Lines 385-400

```Python
if PILImage:
        try:
            with PILImage.open(path) as img:
                return img.width, img.height
        except Exception:
            pass
    try:
        result = subprocess.run(
            ['identify', '-format', '%w %h', str(path)],
            capture_output=True, text=True, check=True
        )
        w, h = result.stdout.strip().split()
        return int(w), int(h)
    except Exception:
        return None
```

## Snippet 25
Lines 418-429

```Python
if 'exif' not in img.info:
            img.info['exif'] = {}

        # Convert to EXIF format (must be bytes with appropriate header)
        exif_data = img.getexif()
        user_comment = alt_text.encode('utf-8')
        ascii_header = b'ASCII\0\0\0'
        exif_data[0x9286] = ascii_header + user_comment  # 0x9286 is UserComment

        # Save with updated EXIF data
        img.save(path, exif=exif_data)
        logger.info(f"Alt text embedded in {path}")
```

## Snippet 26
Lines 438-445

```Python
def read_alt_text(path: Path) -> Optional[str]:
    """
    Extract alt text from an image file's metadata.

    Args:
        path: Path to the image file

    Returns:
```

## Snippet 27
Lines 461-464

```Python
if user_comment.startswith(b'ASCII\0\0\0'):
                    return user_comment[8:].decode('utf-8', errors='ignore')
                else:
                    return user_comment.decode('utf-8', errors='ignore')
```

## Snippet 28
Lines 479-482

```Python
except Exception as e:
        logger.error(f"Error reading alt text from {path}: {e}")
        return None
```

## Snippet 29
Lines 488-496

```Python
def write_alt_text(path: Path, alt_text: str) -> bool:
    """
    Write alt text to an image file's metadata.

    Args:
        path: Path to the image file
        alt_text: The alt text to embed

    Returns:
```

## Snippet 30
Lines 500-502

```Python
# This is a wrapper around embed_alt_text_into_image for API consistency
        embed_alt_text_into_image(path, alt_text)
        return True
```

## Snippet 31
Lines 503-505

```Python
except Exception as e:
        logger.error(f"Error writing alt text to {path}: {e}")
        return False
```

