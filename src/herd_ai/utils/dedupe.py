#!/usr/bin/env python3
"""
===============================================================================
 Herd AI File Deduplication Utility
===============================================================================

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

class DedupeProcessor:
    """
    ===========================================================================
    Base Processor for File Deduplication
    ===========================================================================
    Provides generic deduplication logic for files, including extension and size
    checks, and hash calculation.
    """
    def __init__(self):
        self.supported_extensions = set()
        self.max_size_mb = 1000.0
        self.cache = {}

    def can_process(self, file_path: Path) -> bool:
        """
        Determine if a file is eligible for processing by this processor.
        Checks file existence, extension, and size.
        """
        if not file_path.is_file():
            return False
        if self.supported_extensions and file_path.suffix.lower() not in self.supported_extensions:
            return False
        try:
            size_mb = file_path.stat().st_size / (1024 * 1024)
            if size_mb > self.max_size_mb:
                logger.warning(f"File {file_path} exceeds maximum size limit ({self.max_size_mb}MB)")
                return False
        except Exception as e:
            logger.error(f"Error checking size for {file_path}: {e}")
            return False
        return True

    def process(self, file_path: Union[str, Path], cache: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process a file for deduplication.
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
            if not self.can_process(file_path):
                result['error'] = f"Cannot process {file_path}"
                return result
            file_size = file_path.stat().st_size
            result['size'] = file_size
            file_hash = get_file_hash(file_path)
            if file_hash:
                result['hash'] = file_hash
            else:
                result['error'] = f"Failed to calculate hash for {file_path}"
            if cache is not None and file_hash:
                cache_key = str(file_path)
                cache[cache_key] = {'hash': file_hash, 'size': file_size}
            return result
        except Exception as e:
            logger.error(f"Error processing {file_path}: {e}")
            result['error'] = str(e)
            return result

class ImageDedupeProcessor(DedupeProcessor):
    """
    ===========================================================================
    Image File Deduplication Processor
    ===========================================================================
    Extends DedupeProcessor to add image-specific metadata (resolution).
    """
    def __init__(self):
        super().__init__()
        self.supported_extensions = IMAGE_EXTENSIONS

    def process(self, file_path: Union[str, Path], cache: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process an image file for deduplication, including resolution info.
        """
        file_path = Path(file_path)
        result = super().process(file_path, cache)
        if not result.get('error') and PIL_AVAILABLE:
            try:
                with Image.open(file_path) as img:
                    result['resolution'] = img.size
            except Exception as e:
                logger.error(f"Error getting image resolution for {file_path}: {e}")
        return result

class TextDedupeProcessor(DedupeProcessor):
    """
    ===========================================================================
    Text File Deduplication Processor
    ===========================================================================
    Extends DedupeProcessor to add text-specific metadata and similarity logic.
    """
    def __init__(self):
        super().__init__()
        self.supported_extensions = TEXT_EXTENSIONS
        self.max_size_mb = 10.0
        self.similarity_threshold = 0.7

    def process(self, file_path: Union[str, Path], cache: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process a text file for deduplication, including content, paragraphs,
        lines, and a normalized content hash for similarity checks.
        """
        file_path = Path(file_path)
        result = super().process(file_path, cache)
        if not result.get('error'):
            try:
                with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                    content = f.read()
                result['content'] = content
                result['paragraphs'] = split_into_paragraphs(content)
                result['lines'] = content.splitlines()
                result['content_hash'] = calculate_text_hash(content)
                if cache is not None:
                    cache_key = str(file_path)
                    if cache_key in cache:
                        cache[cache_key].update({
                            'content_hash': result['content_hash'],
                            'paragraphs': len(result['paragraphs'])
                        })
            except Exception as e:
                logger.error(f"Error processing text file {file_path}: {e}")
                result['error'] = str(e)
        return result

class DuplicateDetector:
    """
    ===========================================================================
    DuplicateDetector
    ===========================================================================
    Scans a directory for duplicate files of various types (images, text, general).
    Provides methods for scanning, deleting duplicates, and merging similar text.
    """
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

    def scan_directory(self) -> Dict[str, Any]:
        """
        =========================================================================
        Scan Directory for Duplicates
        =========================================================================
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
        file_pattern = '**/*' if self.recursive else '*'
        files = list(self.directory.glob(file_pattern))
        files = [f for f in files if f.is_file() and not is_ignored_file(f)]
        if not files:
            logger.info(f"No files found in {self.directory}")
            return self._generate_empty_results()
        logger.info(f"Found {len(files)} files to process")
        for file_path in files:
            try:
                size = file_path.stat().st_size
                self.size_groups[size].append(file_path)
            except Exception as e:
                logger.error(f"Error getting size for {file_path}: {e}")
        total_groups = 0
        processed_files = 0
        for size, file_group in self.size_groups.items():
            if len(file_group) < 2:
                continue
            image_files = [f for f in file_group if f.suffix.lower() in IMAGE_EXTENSIONS]
            text_files = [f for f in file_group if f.suffix.lower() in TEXT_EXTENSIONS]
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
        logger.info(f"Found {total_groups} groups of duplicates among {processed_files} files")
        return self._generate_results()

    def _find_exact_duplicates(self, files: List[Path]) -> Dict[str, List[Path]]:
        """
        =========================================================================
        Find Exact Duplicates
        =========================================================================
        Groups files by identical content hash and size.
        Returns a dict of {hash_key: [file_paths]} for groups with >1 file.
        """
        if not files:
            return {}
        hash_groups = defaultdict(list)
        for file_path in files:
            file_hash = get_file_hash(file_path)
            if file_hash:
                key = f"{file_path.stat().st_size}_{file_hash}"
                hash_groups[key].append(file_path)
        return {k: v for k, v in hash_groups.items() if len(v) > 1}

    def _find_image_duplicates(self, files: List[Path]) -> Dict[str, List[Path]]:
        """
        =========================================================================
        Find Duplicate Images
        =========================================================================
        Groups images by file size and resolution.
        Returns a dict of {size_res_key: [file_paths]} for groups with >1 file.
        """
        if not files or not PIL_AVAILABLE:
            return {}
        image_groups = defaultdict(list)
        for file_path in files:
            try:
                file_size = file_path.stat().st_size
                with Image.open(file_path) as img:
                    resolution = img.size
                    key = f"{file_size}_{resolution[0]}x{resolution[1]}"
                    image_groups[key].append(file_path)
            except Exception as e:
                logger.error(f"Error processing image {file_path}: {e}")
        return {k: v for k, v in image_groups.items() if len(v) > 1}

    def _find_similar_text_files(self, files: List[Path]) -> List[List[Dict[str, Any]]]:
        """
        =========================================================================
        Find Similar Text Files
        =========================================================================
        Groups text files by content similarity above a threshold.
        Returns a list of groups, each group being a list of file metadata dicts.
        """
        if not files:
            return []
        text_files = []
        for file_path in files:
            result = self.text_processor.process(file_path, self.cache)
            if not result.get('error'):
                text_files.append(result)
        similar_groups = []
        processed = set()
        for i, file1 in enumerate(text_files):
            if file1['original_path'] in processed:
                continue
            current_group = [file1]
            processed.add(file1['original_path'])
            for j, file2 in enumerate(text_files):
                if i == j or file2['original_path'] in processed:
                    continue
                similarity = calculate_text_similarity(file1, file2)
                if similarity >= self.text_processor.similarity_threshold:
                    current_group.append(file2)
                    processed.add(file2['original_path'])
            if len(current_group) > 1:
                similar_groups.append(current_group)
        return similar_groups

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
        for key, files in self.exact_duplicates.items():
            if len(files) <= 1:
                continue
            size = files[0].stat().st_size
            group = {
                'key': key,
                'files': [str(f) for f in files],
                'size': size,
                'count': len(files)
            }
            result['exact_duplicates'].append(group)
            result['total_duplicates'] += len(files) - 1
            result['potential_space_saving'] += size * (len(files) - 1)
        for key, files in self.image_duplicates.items():
            if len(files) <= 1:
                continue
            size = files[0].stat().st_size
            resolution = key.split('_')[1] if '_' in key else 'unknown'
            group = {
                'key': key,
                'files': [str(f) for f in files],
                'size': size,
                'resolution': resolution,
                'count': len(files)
            }
            result['image_duplicates'].append(group)
            result['total_duplicates'] += len(files) - 1
            result['potential_space_saving'] += size * (len(files) - 1)
        for group in self.similar_text_groups:
            if len(group) <= 1:
                continue
            group_info = {
                'files': [f['original_path'] for f in group],
                'count': len(group)
            }
            result['similar_text_groups'].append(group_info)
        return result

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
        for key, files in self.exact_duplicates.items():
            if len(files) <= 1:
                continue
            files_to_delete = files[1:] if keep_first else files
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
        for key, files in self.image_duplicates.items():
            if len(files) <= 1:
                continue
            files_to_delete = files[1:] if keep_first else files
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
        return result

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
        if output_dir:
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
        else:
            output_dir = self.directory / "merged_docs"
            output_dir.mkdir(parents=True, exist_ok=True)
        for i, group in enumerate(self.similar_text_groups):
            if len(group) <= 1:
                continue
            try:
                paths = [Path(f['original_path']) for f in group]
                base_names = [p.stem for p in paths]
                merged_name = f"merged_{'_'.join(base_names[:3])}"
                if len(base_names) > 3:
                    merged_name += f"_and_{len(base_names) - 3}_more"
                merged_name += ".md"
                merged_path = output_dir / merged_name
                merged_content = self._generate_merged_content(group)
                with open(merged_path, 'w', encoding='utf-8') as f:
                    f.write(merged_content)
                result['merged_files'].append(str(merged_path))
                result['total_merged'] += 1
            except Exception as e:
                error = {'files': [f['original_path'] for f in group], 'error': str(e)}
                result['errors'].append(error)
                logger.error(f"Error merging similar files: {e}")
        return result

    def _generate_merged_content(self, files: List[Dict[str, Any]]) -> str:
        """
        =========================================================================
        Generate Merged Content for Similar Text Files
        =========================================================================
        Produces a markdown document with common and unique content from a group.
        """
        content = [
            f"# Merged content from {len(files)} similar files\n",
            "## Source Files\n"
        ]
        for file in files:
            file_path = Path(file['original_path'])
            mod_time = datetime.fromtimestamp(file_path.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S')
            content.append(f"* {file_path.name} (Last modified: {mod_time})")
        content.append("\n---\n")
        common_paragraphs = find_common_paragraphs([f['paragraphs'] for f in files])
        content.extend([
            "## Common Content\n",
            "\n".join(common_paragraphs) if common_paragraphs else "*No significant common content was found.*"
        ])
        content.append("\n---\n")
        content.append("## Unique Content\n")
        for file in files:
            file_path = Path(file['original_path'])
            unique_content = find_unique_paragraphs(file['paragraphs'], common_paragraphs)
            content.append(f"### From {file_path.name}\n")
            content.append("\n".join(unique_content) if unique_content else "*No unique content in this file.*")
            content.append("\n---\n")
        return "\n".join(content)

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
            for block in iter(lambda: f.read(block_size), b''):
                hasher.update(block)
        return hasher.hexdigest()
    except Exception as e:
        logger.error(f"Error calculating hash for {file_path}: {e}")
        return None

def get_image_info(file_path: Path) -> Tuple[Optional[int], Optional[Tuple[int, int]]]:
    """
    ============================================================================
    Get Image File Info
    ============================================================================
    Returns the file size and resolution (if available) for an image file.
    """
    try:
        file_size = file_path.stat().st_size
    except Exception as e:
        logger.error(f"Error getting file size for {file_path}: {e}")
        return None, None
    if not PIL_AVAILABLE:
        return file_size, None
    try:
        with Image.open(file_path) as img:
            resolution = img.size
    except Exception as e:
        logger.error(f"Error opening image {file_path}: {e}")
        resolution = None
    return file_size, resolution

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

def split_into_paragraphs(text: str) -> List[str]:
    """
    ============================================================================
    Split Text into Paragraphs
    ============================================================================
    Splits text into paragraphs using blank lines as delimiters.
    """
    raw_paragraphs = re.split(r'\n\s*\n', text)
    return [p.strip() for p in raw_paragraphs if p.strip()]

def calculate_text_similarity(file1: Dict[str, Any], file2: Dict[str, Any]) -> float:
    """
    ============================================================================
    Calculate Text File Similarity
    ============================================================================
    Computes a similarity score between two text files using line, paragraph,
    and word overlap metrics.
    """
    if file1.get('content_hash') == file2.get('content_hash'):
        return 1.0
    matcher = difflib.SequenceMatcher(None, file1.get('lines', []), file2.get('lines', []))
    line_similarity = matcher.ratio()
    paragraph_matches = 0
    for p1 in file1.get('paragraphs', []):
        for p2 in file2.get('paragraphs', []):
            para_matcher = difflib.SequenceMatcher(None, p1, p2)
            if para_matcher.ratio() > 0.8:
                paragraph_matches += 1
                break
    max_paragraphs = max(len(file1.get('paragraphs', [])), len(file2.get('paragraphs', [])))
    paragraph_similarity = paragraph_matches / max_paragraphs if max_paragraphs > 0 else 0
    words1 = set(re.findall(r'\b\w+\b', file1.get('content', '').lower()))
    words2 = set(re.findall(r'\b\w+\b', file2.get('content', '').lower()))
    if not words1 or not words2:
        word_similarity = 0
    else:
        intersection = words1.intersection(words2)
        word_similarity = len(intersection) / max(len(words1), len(words2))
    return (line_similarity * 0.5) + (paragraph_similarity * 0.3) + (word_similarity * 0.2)

def is_ignored_file(file_path: Path) -> bool:
    """
    ============================================================================
    Check if File Should Be Ignored
    ============================================================================
    Returns True if the file is hidden or in a known ignored directory.
    """
    if file_path.name.startswith('.'):
        return True
    ignored_dirs = {'.git', '__pycache__', 'node_modules', 'venv', 'env', '.herd', '.llamacleaner'}
    parts = file_path.parts
    for part in parts:
        if part in ignored_dirs:
            return True
    return False

def find_common_paragraphs(all_paragraphs: List[List[str]]) -> List[str]:
    """
    ============================================================================
    Find Common Paragraphs Across Files
    ============================================================================
    Returns a list of paragraphs that are common (by similarity) to all files.
    """
    if not all_paragraphs or not all_paragraphs[0]:
        return []
    reference_paragraphs = all_paragraphs[0]
    common = []
    for paragraph in reference_paragraphs:
        is_common = True
        for other_paragraphs in all_paragraphs[1:]:
            found = False
            for other_paragraph in other_paragraphs:
                matcher = difflib.SequenceMatcher(None, paragraph, other_paragraph)
                if matcher.ratio() > 0.8:
                    found = True
                    break
            if not found:
                is_common = False
                break
        if is_common and len(paragraph.split()) > 5:
            common.append(paragraph)
    return common

def find_unique_paragraphs(paragraphs: List[str], common_paragraphs: List[str]) -> List[str]:
    """
    ============================================================================
    Find Unique Paragraphs
    ============================================================================
    Returns paragraphs that are not present in the list of common paragraphs.
    """
    unique = []
    for paragraph in paragraphs:
        is_unique = True
        for common_paragraph in common_paragraphs:
            matcher = difflib.SequenceMatcher(None, paragraph, common_paragraph)
            if matcher.ratio() > 0.8:
                is_unique = False
                break
        if is_unique and len(paragraph.split()) > 5:
            unique.append(paragraph)
    return unique

def format_size(size_bytes: int) -> str:
    """
    ============================================================================
    Format File Size
    ============================================================================
    Converts a file size in bytes to a human-readable string.
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024 or unit == 'GB':
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024

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
    Scans a directory for duplicate files, optionally deletes duplicates and/or
    merges similar text files. Can run interactively or non-interactively.
    Returns a dictionary with the results of the operation.
    """
    directory = Path(directory)
    if output_dir:
        output_dir = Path(output_dir)
    detector = DuplicateDetector(directory, recursive)
    results = detector.scan_directory()
    exact_dupes_count = sum(len(g['files']) - 1 for g in results['exact_duplicates'])
    image_dupes_count = sum(len(g['files']) - 1 for g in results['image_duplicates'])
    similar_text_count = sum(g['count'] - 1 for g in results['similar_text_groups'])
    total_dupes = exact_dupes_count + image_dupes_count
    print(f"\n=== Deduplication Results for {directory} ===")
    print(f"Found {total_dupes} exact duplicates and {similar_text_count} similar text files")
    if total_dupes > 0:
        print(f"Potential space saving: {format_size(results['potential_space_saving'])}")
    if not interactive:
        if delete_duplicates and total_dupes > 0:
            deletion_result = detector.delete_duplicates(keep_first=True)
            results['deletion_result'] = deletion_result
            print(f"Deleted {deletion_result['total_deleted']} files, saving {format_size(deletion_result['total_space_saved'])}")
        if merge_similar and similar_text_count > 0:
            merge_result = detector.merge_similar_text(output_dir)
            results['merge_result'] = merge_result
            print(f"Merged {merge_result['total_merged']} groups of similar text files")
        return results
    if total_dupes > 0 or similar_text_count > 0:
        show_details = input("\nShow detailed duplicate information? [y/N]: ").strip().lower() == 'y'
        if show_details:
            if results['exact_duplicates']:
                print("\n== Exact Duplicates ==")
                for i, group in enumerate(results['exact_duplicates'], 1):
                    print(f"\nGroup {i}: {group['count']} files, {format_size(group['size'])} each")
                    for file_path in group['files']:
                        print(f"  - {file_path}")
            if results['image_duplicates']:
                print("\n== Image Duplicates ==")
                for i, group in enumerate(results['image_duplicates'], 1):
                    print(f"\nGroup {i}: {group['count']} files, {format_size(group['size'])} each, Resolution: {group['resolution']}")
                    for file_path in group['files']:
                        print(f"  - {file_path}")
            if results['similar_text_groups']:
                print("\n== Similar Text Files ==")
                for i, group in enumerate(results['similar_text_groups'], 1):
                    print(f"\nGroup {i}: {group['count']} files")
                    for file_path in group['files']:
                        print(f"  - {file_path}")
        if total_dupes > 0:
            delete_action = input("\nDelete duplicate files (keeping the first one in each group)? [y/N]: ").strip().lower() == 'y'
            if delete_action:
                deletion_result = detector.delete_duplicates(keep_first=True)
                results['deletion_result'] = deletion_result
                print(f"\nDeleted {deletion_result['total_deleted']} files, saving {format_size(deletion_result['total_space_saved'])}")
                if deletion_result['errors']:
                    print(f"Encountered {len(deletion_result['errors'])} errors while deleting files")
                    for error in deletion_result['errors']:
                        print(f"  - {error['file']}: {error['error']}")
        if similar_text_count > 0:
            merge_action = input("\nMerge similar text files? [y/N]: ").strip().lower() == 'y'
            if merge_action:
                output_prompt = input("Enter output directory for merged files (leave blank for default): ").strip()
                output_path = Path(output_prompt) if output_prompt else None
                merge_result = detector.merge_similar_text(output_path)
                results['merge_result'] = merge_result
                print(f"\nMerged {merge_result['total_merged']} groups of similar text files")
                if merge_result['errors']:
                    print(f"Encountered {len(merge_result['errors'])} errors while merging files")
                    for error in merge_result['errors']:
                        print(f"  - Error merging {len(error['files'])} files: {error['error']}")
    else:
        print("No duplicate or similar files found.")
    return results

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
    parser.add_argument('--output', '-o', type=str, help='Output directory for merged files')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    args = parser.parse_args()
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

if __name__ == "__main__":
    main()