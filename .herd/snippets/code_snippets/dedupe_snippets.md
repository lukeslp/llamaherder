# Code Snippets from src/herd_ai/utils/dedupe.py

File: `src/herd_ai/utils/dedupe.py`  
Language: Python  
Extracted: 2025-06-07 05:10:05  

## Snippet 1
Lines 1-6

```Python
#!/usr/bin/env python3
"""
===============================================================================
 Herd AI File Deduplication Utility
===============================================================================
```

## Snippet 2
Lines 7-28

```Python
This module provides a comprehensive utility for deduplicating files in a directory.
It supports:
    - Image deduplication (by file size and resolution)
    - General file deduplication (by file size and content hash)
    - Text file deduplication (by content similarity, with optional merging)

The module can be used programmatically or via an interactive CLI.

===============================================================================
"""

import os
import sys
import logging
import hashlib
import re
import difflib
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from typing import Dict, List, Set, Tuple, Optional, Union, Any
```

## Snippet 3
Lines 29-78

```Python
# --- Herd AI Utility Imports (robust, fallback style) ---
try:
    from herd_ai.utils import analysis, config as herd_config, file, scrambler, undo_log
except ImportError:
    try:
        from llamacleaner.utils import analysis, config as herd_config, file, scrambler, undo_log
    except ImportError:
        try:
            import utils.analysis as analysis
            import utils.config as herd_config
            import utils.file as file
            import utils.scrambler as scrambler
            import utils.undo_log as undo_log
        except ImportError:
            analysis = None
            herd_config = None
            file = None
            scrambler = None
            undo_log = None

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

IMAGE_EXTENSIONS = {
    '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp', '.heic', '.svg',
    '.avif', '.jfif', '.pjpeg', '.pjp', '.ico', '.cur'
}

TEXT_EXTENSIONS = {
    '.txt', '.md', '.markdown', '.rst', '.log', '.csv', '.json', '.xml',
    '.yml', '.yaml', '.html', '.htm', '.css', '.conf', '.ini', '.cfg',
    '.py', '.js', '.java', '.c', '.cpp', '.h', '.hpp', '.cs', '.php', '.rb',
    '.go', '.swift', '.kt', '.ts', '.jsx', '.tsx', '.vue', '.sh', '.bat', '.ps1'
}

CODE_EXTENSIONS = {
    '.py', '.js', '.java', '.c', '.cpp', '.h', '.hpp', '.cs', '.php', '.rb',
    '.go', '.swift', '.kt', '.ts', '.jsx', '.tsx', '.vue', '.sh', '.bat', '.ps1'
}

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    logger.warning("PIL/Pillow not installed. Image resolution detection disabled.")
```

## Snippet 4
Lines 79-81

```Python
class DedupeProcessor:
    """
    ===========================================================================
```

## Snippet 5
Lines 87-91

```Python
def __init__(self):
        self.supported_extensions = set()
        self.max_size_mb = 1000.0
        self.cache = {}
```

## Snippet 6
Lines 99-102

```Python
if self.supported_extensions and file_path.suffix.lower() not in self.supported_extensions:
            return False
        try:
            size_mb = file_path.stat().st_size / (1024 * 1024)
```

## Snippet 7
Lines 114-123

```Python
Returns a dictionary with file path, hash, size, and error (if any).
        """
        file_path = Path(file_path)
        result = {
            'original_path': str(file_path),
            'hash': None,
            'size': None,
            'error': None
        }
        try:
```

## Snippet 8
Lines 124-129

```Python
if not self.can_process(file_path):
                result['error'] = f"Cannot process {file_path}"
                return result
            file_size = file_path.stat().st_size
            result['size'] = file_size
            file_hash = get_file_hash(file_path)
```

## Snippet 9
Lines 130-132

```Python
if file_hash:
                result['hash'] = file_hash
            else:
```

## Snippet 10
Lines 134-137

```Python
if cache is not None and file_hash:
                cache_key = str(file_path)
                cache[cache_key] = {'hash': file_hash, 'size': file_size}
            return result
```

## Snippet 11
Lines 138-142

```Python
except Exception as e:
            logger.error(f"Error processing {file_path}: {e}")
            result['error'] = str(e)
            return result
```

## Snippet 12
Lines 143-149

```Python
class ImageDedupeProcessor(DedupeProcessor):
    """
    ===========================================================================
    Image File Deduplication Processor
    ===========================================================================
    Extends DedupeProcessor to add image-specific metadata (resolution).
    """
```

## Snippet 13
Lines 150-153

```Python
def __init__(self):
        super().__init__()
        self.supported_extensions = IMAGE_EXTENSIONS
```

## Snippet 14
Lines 160-164

```Python
if not result.get('error') and PIL_AVAILABLE:
            try:
                with Image.open(file_path) as img:
                    result['resolution'] = img.size
            except Exception as e:
```

## Snippet 15
Lines 168-174

```Python
class TextDedupeProcessor(DedupeProcessor):
    """
    ===========================================================================
    Text File Deduplication Processor
    ===========================================================================
    Extends DedupeProcessor to add text-specific metadata and similarity logic.
    """
```

## Snippet 16
Lines 175-180

```Python
def __init__(self):
        super().__init__()
        self.supported_extensions = TEXT_EXTENSIONS
        self.max_size_mb = 10.0
        self.similarity_threshold = 0.7
```

## Snippet 17
Lines 188-195

```Python
if not result.get('error'):
            try:
                with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                    content = f.read()
                result['content'] = content
                result['paragraphs'] = split_into_paragraphs(content)
                result['lines'] = content.splitlines()
                result['content_hash'] = calculate_text_hash(content)
```

## Snippet 18
Lines 198-202

```Python
if cache_key in cache:
                        cache[cache_key].update({
                            'content_hash': result['content_hash'],
                            'paragraphs': len(result['paragraphs'])
                        })
```

## Snippet 19
Lines 203-205

```Python
except Exception as e:
                logger.error(f"Error processing text file {file_path}: {e}")
                result['error'] = str(e)
```

## Snippet 20
Lines 208-212

```Python
class DuplicateDetector:
    """
    ===========================================================================
    DuplicateDetector
    ===========================================================================
```

## Snippet 21
Lines 216-228

```Python
def __init__(self, directory: Union[str, Path], recursive: bool = True):
        self.directory = Path(directory)
        self.recursive = recursive
        self.cache = {}
        self.image_processor = ImageDedupeProcessor()
        self.text_processor = TextDedupeProcessor()
        self.general_processor = DedupeProcessor()
        self.all_files = []
        self.size_groups = defaultdict(list)
        self.exact_duplicates = {}
        self.similar_text_groups = []
        self.image_duplicates = {}
```

## Snippet 22
Lines 229-231

```Python
def scan_directory(self) -> Dict[str, Any]:
        """
        =========================================================================
```

## Snippet 23
Lines 234-243

```Python
Scans the target directory for files, groups by size, and detects duplicates
        using hashing, image resolution, and text similarity.
        Returns a structured dictionary of results.
        """
        logger.info(f"Scanning directory: {self.directory}")
        self.all_files = []
        self.size_groups = defaultdict(list)
        self.exact_duplicates = {}
        self.similar_text_groups = []
        self.image_duplicates = {}
```

## Snippet 24
Lines 247-249

```Python
if not files:
            logger.info(f"No files found in {self.directory}")
            return self._generate_empty_results()
```

## Snippet 25
Lines 251-255

```Python
for file_path in files:
            try:
                size = file_path.stat().st_size
                self.size_groups[size].append(file_path)
            except Exception as e:
```

## Snippet 26
Lines 264-275

```Python
other_files = [f for f in file_group if f.suffix.lower() not in IMAGE_EXTENSIONS
                                                 and f.suffix.lower() not in TEXT_EXTENSIONS]
            image_dupes = self._find_image_duplicates(image_files)
            self.image_duplicates.update(image_dupes)
            text_dupes = self._find_exact_duplicates(text_files)
            self.exact_duplicates.update(text_dupes)
            similar_groups = self._find_similar_text_files(text_files)
            self.similar_text_groups.extend(similar_groups)
            other_dupes = self._find_exact_duplicates(other_files)
            self.exact_duplicates.update(other_dupes)
            total_groups += (len(image_dupes) + len(text_dupes) + len(other_dupes) + len(similar_groups))
            processed_files += len(file_group)
```

## Snippet 27
Lines 279-284

```Python
def _find_exact_duplicates(self, files: List[Path]) -> Dict[str, List[Path]]:
        """
        =========================================================================
        Find Exact Duplicates
        =========================================================================
        Groups files by identical content hash and size.
```

## Snippet 28
Lines 287-289

```Python
if not files:
            return {}
        hash_groups = defaultdict(list)
```

## Snippet 29
Lines 292-294

```Python
if file_hash:
                key = f"{file_path.stat().st_size}_{file_hash}"
                hash_groups[key].append(file_path)
```

## Snippet 30
Lines 297-302

```Python
def _find_image_duplicates(self, files: List[Path]) -> Dict[str, List[Path]]:
        """
        =========================================================================
        Find Duplicate Images
        =========================================================================
        Groups images by file size and resolution.
```

## Snippet 31
Lines 305-307

```Python
if not files or not PIL_AVAILABLE:
            return {}
        image_groups = defaultdict(list)
```

## Snippet 32
Lines 308-316

```Python
for file_path in files:
            try:
                file_size = file_path.stat().st_size
                with Image.open(file_path) as img:
                    resolution = img.size
                    key = f"{file_size}_{resolution[0]}x{resolution[1]}"
                    image_groups[key].append(file_path)
            except Exception as e:
                logger.error(f"Error processing image {file_path}: {e}")
```

## Snippet 33
Lines 319-326

```Python
def _find_similar_text_files(self, files: List[Path]) -> List[List[Dict[str, Any]]]:
        """
        =========================================================================
        Find Similar Text Files
        =========================================================================
        Groups text files by content similarity above a threshold.
        Returns a list of groups, each group being a list of file metadata dicts.
        """
```

## Snippet 34
Lines 327-329

```Python
if not files:
            return []
        text_files = []
```

## Snippet 35
Lines 337-340

```Python
if file1['original_path'] in processed:
                continue
            current_group = [file1]
            processed.add(file1['original_path'])
```

## Snippet 36
Lines 342-344

```Python
if i == j or file2['original_path'] in processed:
                    continue
                similarity = calculate_text_similarity(file1, file2)
```

## Snippet 37
Lines 345-347

```Python
if similarity >= self.text_processor.similarity_threshold:
                    current_group.append(file2)
                    processed.add(file2['original_path'])
```

## Snippet 38
Lines 352-367

```Python
def _generate_results(self) -> Dict[str, Any]:
        """
        =========================================================================
        Generate Results Summary
        =========================================================================
        Compiles the results of duplicate detection into a structured dictionary.
        """
        result = {
            'directory': str(self.directory),
            'scan_time': datetime.now().isoformat(),
            'exact_duplicates': [],
            'image_duplicates': [],
            'similar_text_groups': [],
            'total_duplicates': 0,
            'potential_space_saving': 0
        }
```

## Snippet 39
Lines 369-373

```Python
if len(files) <= 1:
                continue
            size = files[0].stat().st_size
            group = {
                'key': key,
```

## Snippet 40
Lines 382-384

```Python
if len(files) <= 1:
                continue
            size = files[0].stat().st_size
```

## Snippet 41
Lines 397-399

```Python
if len(group) <= 1:
                continue
            group_info = {
```

## Snippet 42
Lines 406-423

```Python
def _generate_empty_results(self) -> Dict[str, Any]:
        """
        =========================================================================
        Generate Empty Results
        =========================================================================
        Returns a results dictionary indicating no files were found.
        """
        return {
            'directory': str(self.directory),
            'scan_time': datetime.now().isoformat(),
            'exact_duplicates': [],
            'image_duplicates': [],
            'similar_text_groups': [],
            'total_duplicates': 0,
            'potential_space_saving': 0,
            'error': 'No files found in directory'
        }
```

## Snippet 43
Lines 424-437

```Python
def delete_duplicates(self, keep_first: bool = True) -> Dict[str, Any]:
        """
        =========================================================================
        Delete Duplicate Files
        =========================================================================
        Deletes duplicate files, optionally keeping the first file in each group.
        Returns a dictionary with deletion results and errors.
        """
        result = {
            'deleted_files': [],
            'errors': [],
            'total_deleted': 0,
            'total_space_saved': 0
        }
```

## Snippet 44
Lines 442-452

```Python
for file_path in files_to_delete:
                try:
                    size = file_path.stat().st_size
                    file_path.unlink()
                    result['deleted_files'].append(str(file_path))
                    result['total_deleted'] += 1
                    result['total_space_saved'] += size
                except Exception as e:
                    error = {'file': str(file_path), 'error': str(e)}
                    result['errors'].append(error)
                    logger.error(f"Error deleting {file_path}: {e}")
```

## Snippet 45
Lines 457-467

```Python
for file_path in files_to_delete:
                try:
                    size = file_path.stat().st_size
                    file_path.unlink()
                    result['deleted_files'].append(str(file_path))
                    result['total_deleted'] += 1
                    result['total_space_saved'] += size
                except Exception as e:
                    error = {'file': str(file_path), 'error': str(e)}
                    result['errors'].append(error)
                    logger.error(f"Error deleting {file_path}: {e}")
```

## Snippet 46
Lines 470-482

```Python
def merge_similar_text(self, output_dir: Optional[Path] = None) -> Dict[str, Any]:
        """
        =========================================================================
        Merge Similar Text Files
        =========================================================================
        Merges groups of similar text files into consolidated markdown documents.
        Returns a dictionary with merge results and errors.
        """
        result = {
            'merged_files': [],
            'errors': [],
            'total_merged': 0
        }
```

## Snippet 47
Lines 483-488

```Python
if output_dir:
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
        else:
            output_dir = self.directory / "merged_docs"
            output_dir.mkdir(parents=True, exist_ok=True)
```

## Snippet 48
Lines 490-492

```Python
if len(group) <= 1:
                continue
            try:
```

## Snippet 49
Lines 496-504

```Python
if len(base_names) > 3:
                    merged_name += f"_and_{len(base_names) - 3}_more"
                merged_name += ".md"
                merged_path = output_dir / merged_name
                merged_content = self._generate_merged_content(group)
                with open(merged_path, 'w', encoding='utf-8') as f:
                    f.write(merged_content)
                result['merged_files'].append(str(merged_path))
                result['total_merged'] += 1
```

## Snippet 50
Lines 511-513

```Python
def _generate_merged_content(self, files: List[Dict[str, Any]]) -> str:
        """
        =========================================================================
```

## Snippet 51
Lines 514-518

```Python
Generate Merged Content for Similar Text Files
        =========================================================================
        Produces a markdown document with common and unique content from a group.
        """
        content = [
```

## Snippet 52
Lines 522-524

```Python
for file in files:
            file_path = Path(file['original_path'])
            mod_time = datetime.fromtimestamp(file_path.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S')
```

## Snippet 53
Lines 534-537

```Python
for file in files:
            file_path = Path(file['original_path'])
            unique_content = find_unique_paragraphs(file['paragraphs'], common_paragraphs)
            content.append(f"### From {file_path.name}\n")
```

## Snippet 54
Lines 542-551

```Python
def get_file_hash(file_path: Path, block_size: int = 65536) -> Optional[str]:
    """
    ============================================================================
    Calculate File Hash
    ============================================================================
    Returns the SHA-256 hash of the file at the given path.
    """
    try:
        hasher = hashlib.sha256()
        with open(file_path, 'rb') as f:
```

## Snippet 55
Lines 559-563

```Python
def get_image_info(file_path: Path) -> Tuple[Optional[int], Optional[Tuple[int, int]]]:
    """
    ============================================================================
    Get Image File Info
    ============================================================================
```

## Snippet 56
Lines 564-568

```Python
Returns the file size and resolution (if available) for an image file.
    """
    try:
        file_size = file_path.stat().st_size
    except Exception as e:
```

## Snippet 57
Lines 571-580

```Python
if not PIL_AVAILABLE:
        return file_size, None
    try:
        with Image.open(file_path) as img:
            resolution = img.size
    except Exception as e:
        logger.error(f"Error opening image {file_path}: {e}")
        resolution = None
    return file_size, resolution
```

## Snippet 58
Lines 581-592

```Python
def calculate_text_hash(text: str) -> str:
    """
    ============================================================================
    Calculate Normalized Text Hash
    ============================================================================
    Returns an MD5 hash of the normalized text content (lowercased, whitespace
    collapsed, and punctuation removed).
    """
    normalized = re.sub(r'\s+', ' ', text.lower())
    normalized = re.sub(r'[#*_`\[\]\(\)\{\}]', '', normalized)
    return hashlib.md5(normalized.encode('utf-8')).hexdigest()
```

## Snippet 59
Lines 593-600

```Python
def split_into_paragraphs(text: str) -> List[str]:
    """
    ============================================================================
    Split Text into Paragraphs
    ============================================================================
    Splits text into paragraphs using blank lines as delimiters.
    """
    raw_paragraphs = re.split(r'\n\s*\n', text)
```

## Snippet 60
Lines 603-610

```Python
def calculate_text_similarity(file1: Dict[str, Any], file2: Dict[str, Any]) -> float:
    """
    ============================================================================
    Calculate Text File Similarity
    ============================================================================
    Computes a similarity score between two text files using line, paragraph,
    and word overlap metrics.
    """
```

## Snippet 61
Lines 611-615

```Python
if file1.get('content_hash') == file2.get('content_hash'):
        return 1.0
    matcher = difflib.SequenceMatcher(None, file1.get('lines', []), file2.get('lines', []))
    line_similarity = matcher.ratio()
    paragraph_matches = 0
```

## Snippet 62
Lines 619-621

```Python
if para_matcher.ratio() > 0.8:
                paragraph_matches += 1
                break
```

## Snippet 63
Lines 626-632

```Python
if not words1 or not words2:
        word_similarity = 0
    else:
        intersection = words1.intersection(words2)
        word_similarity = len(intersection) / max(len(words1), len(words2))
    return (line_similarity * 0.5) + (paragraph_similarity * 0.3) + (word_similarity * 0.2)
```

## Snippet 64
Lines 633-635

```Python
def is_ignored_file(file_path: Path) -> bool:
    """
    ============================================================================
```

## Snippet 65
Lines 640-643

```Python
if file_path.name.startswith('.'):
        return True
    ignored_dirs = {'.git', '__pycache__', 'node_modules', 'venv', 'env', '.herd', '.llamacleaner'}
    parts = file_path.parts
```

## Snippet 66
Lines 649-655

```Python
def find_common_paragraphs(all_paragraphs: List[List[str]]) -> List[str]:
    """
    ============================================================================
    Find Common Paragraphs Across Files
    ============================================================================
    Returns a list of paragraphs that are common (by similarity) to all files.
    """
```

## Snippet 67
Lines 656-659

```Python
if not all_paragraphs or not all_paragraphs[0]:
        return []
    reference_paragraphs = all_paragraphs[0]
    common = []
```

## Snippet 68
Lines 666-668

```Python
if matcher.ratio() > 0.8:
                    found = True
                    break
```

## Snippet 69
Lines 669-671

```Python
if not found:
                is_common = False
                break
```

## Snippet 70
Lines 676-683

```Python
def find_unique_paragraphs(paragraphs: List[str], common_paragraphs: List[str]) -> List[str]:
    """
    ============================================================================
    Find Unique Paragraphs
    ============================================================================
    Returns paragraphs that are not present in the list of common paragraphs.
    """
    unique = []
```

## Snippet 71
Lines 688-690

```Python
if matcher.ratio() > 0.8:
                is_unique = False
                break
```

## Snippet 72
Lines 695-701

```Python
def format_size(size_bytes: int) -> str:
    """
    ============================================================================
    Format File Size
    ============================================================================
    Converts a file size in bytes to a human-readable string.
    """
```

## Snippet 73
Lines 707-718

```Python
def dedupe_files(
    directory: Union[str, Path],
    recursive: bool = True,
    interactive: bool = True,
    delete_duplicates: bool = False,
    merge_similar: bool = False,
    output_dir: Optional[Union[str, Path]] = None
) -> Dict[str, Any]:
    """
    ============================================================================
    Main Deduplication Function
    ============================================================================
```

## Snippet 74
Lines 719-723

```Python
Scans a directory for duplicate files, optionally deletes duplicates and/or
    merges similar text files. Can run interactively or non-interactively.
    Returns a dictionary with the results of the operation.
    """
    directory = Path(directory)
```

## Snippet 75
Lines 724-727

```Python
if output_dir:
        output_dir = Path(output_dir)
    detector = DuplicateDetector(directory, recursive)
    results = detector.scan_directory()
```

## Snippet 76
Lines 737-739

```Python
if delete_duplicates and total_dupes > 0:
            deletion_result = detector.delete_duplicates(keep_first=True)
            results['deletion_result'] = deletion_result
```

## Snippet 77
Lines 741-743

```Python
if merge_similar and similar_text_count > 0:
            merge_result = detector.merge_similar_text(output_dir)
            results['merge_result'] = merge_result
```

## Snippet 78
Lines 769-771

```Python
if delete_action:
                deletion_result = detector.delete_duplicates(keep_first=True)
                results['deletion_result'] = deletion_result
```

## Snippet 79
Lines 789-792

```Python
else:
        print("No duplicate or similar files found.")
    return results
```

## Snippet 80
Lines 793-806

```Python
def main():
    """
    ============================================================================
    Main CLI Entry Point
    ============================================================================
    Parses command-line arguments and runs the deduplication process.
    """
    import argparse
    parser = argparse.ArgumentParser(description="Herd AI File Deduplication Utility")
    parser.add_argument('--dir', '-d', type=str, default=os.getcwd(), help='Directory to scan (default: current directory)')
    parser.add_argument('--recursive', '-r', action='store_true', help='Scan subdirectories')
    parser.add_argument('--non-interactive', '-n', action='store_true', help='Non-interactive mode')
    parser.add_argument('--delete', action='store_true', help='Delete duplicates (keeping the first in each group)')
    parser.add_argument('--merge', action='store_true', help='Merge similar text files')
```

## Snippet 81
Lines 810-820

```Python
if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    dedupe_files(
        directory=args.dir,
        recursive=args.recursive,
        interactive=not args.non_interactive,
        delete_duplicates=args.delete,
        merge_similar=args.merge,
        output_dir=args.output
    )
```

