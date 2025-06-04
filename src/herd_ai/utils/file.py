###############################################################################
# Herd AI - File Handling and Metadata Utilities
#
# This module provides accessible, robust, and extensible utilities for:
#   - File and directory management
#   - File metadata extraction
#   - Text extraction from various file types (PDF, DOCX, images, plain text)
#   - Image metadata and accessibility enhancements (alt text embedding)
#   - File extension and size utilities
#
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
    import fitz  # PyMuPDF for PDF text extraction
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
# ---------------
# Ensures that a directory exists at the given path. If it does not exist,
# it is created (including parent directories as needed). Returns the Path object.
###############################################################################
def ensure_directory(path: Union[str, Path]) -> Path:
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p

###############################################################################
# get_file_extension
# ------------------
# Returns the lowercase file extension (including the dot) for a given file path.
###############################################################################
def get_file_extension(path: Union[str, Path]) -> str:
    return Path(path).suffix.lower()

###############################################################################
# get_file_metadata
# -----------------
# Returns a dictionary containing metadata about a file, including:
#   - path: full path as string
#   - name: file name
#   - extension: file extension
#   - size: file size in bytes
#   - modified: last modified time (epoch)
###############################################################################
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
# --------------
# Cleans a filename by:
#   - Lowercasing
#   - Replacing non-alphanumeric characters with underscores
#   - Collapsing multiple underscores
#   - Removing leading/trailing underscores
###############################################################################
def clean_filename(name: str) -> str:
    name = name.strip().lower()
    name = re.sub(r'[^a-z0-9]+', '_', name)
    name = re.sub(r'_+', '_', name)
    return name.strip('_')

###############################################################################
# is_ignored_file
# ---------------
# Determines if a file should be ignored based on its name or extension.
# Returns True if the file is hidden, a known system file, or a special marker.
###############################################################################
def is_ignored_file(file_path: Union[str, Path]) -> bool:
    path = Path(file_path)
    if path.name.startswith('.'):
        return True
    ignored_names = {
        'thumbs.db', 'desktop.ini', '.ds_store', 'icon\r', '.localized',
        '.gitignore', '.gitkeep', 'readme.md', 'license'
    }
    if path.name.lower() in ignored_names:
        return True
    if path.name.startswith(".renamed_"):
        return True
    return False

###############################################################################
# extract_text_from_pdf
# ---------------------
# Extracts text from a PDF file. If force_ocr is True or text extraction fails,
# falls back to OCR using pytesseract and pdf2image.
###############################################################################
def extract_text_from_pdf(file_path: Path, force_ocr: bool = False) -> str:
    try:
        if not force_ocr and fitz:
            text = ""
            with fitz.open(file_path) as pdf:
                for page_num in range(len(pdf)):
                    text += pdf.load_page(page_num).get_text()
            if text.strip():
                return text
        if PILImage and pytesseract:
            from pdf2image import convert_from_path
            from tempfile import TemporaryDirectory
            text = ""
            with TemporaryDirectory() as tmp:
                images = convert_from_path(file_path, output_folder=tmp)
                for img in images:
                    text += pytesseract.image_to_string(img) + "\n"
            return text
    except Exception as e:
        logger.error(f"Error extracting text from PDF {file_path}: {e}")
    return ""

###############################################################################
# extract_text_from_docx
# ----------------------
# Extracts text from a DOCX file using docx2txt if available.
###############################################################################
def extract_text_from_docx(file_path: Path) -> str:
    try:
        if docx2txt:
            return docx2txt.process(str(file_path))
        return ""
    except Exception as e:
        logger.error(f"Error extracting text from DOCX {file_path}: {e}")
        return ""

###############################################################################
# extract_text_from_txt_like
# --------------------------
# Extracts text from a plain text file, trying UTF-8 and falling back to Latin-1.
###############################################################################
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
# -----------------------
# Extracts text from an image file using OCR (pytesseract).
###############################################################################
def extract_text_from_image(image_path: Path) -> str:
    if not PILImage or not pytesseract:
        logger.warning("OCR libraries not available. Skipping OCR.")
        return ""
    try:
        img = PILImage.open(image_path)
        return pytesseract.image_to_string(img)
    except Exception as e:
        logger.error(f"Error extracting text from image {image_path}: {e}")
        return ""

###############################################################################
# get_file_text
# -------------
# Extracts text from a file based on its extension/type.
# Supports PDF, DOCX, images, and plain text files.
###############################################################################
def get_file_text(path: Path) -> str:
    ext = path.suffix.lower()
    if ext == '.pdf':
        return extract_text_from_pdf(path)
    if ext in {'.docx', '.doc'}:
        return extract_text_from_docx(path)
    if ext in {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.gif'}:
        return extract_text_from_image(path)
    return extract_text_from_txt_like(path)

###############################################################################
# get_file_size_mb
# ----------------
# Returns the file size in megabytes for the given file path.
###############################################################################
def get_file_size_mb(file_path: Union[str, Path]) -> float:
    try:
        path = Path(file_path)
        size_bytes = path.stat().st_size
        return size_bytes / (1024 * 1024)
    except Exception as e:
        logger.error(f"Error getting file size for {file_path}: {e}")
        return 0.0

###############################################################################
# count_by_extension
# ------------------
# Counts files by their extension in a directory (optionally recursive)
###############################################################################
def count_by_extension(directory: Path) -> Dict[str, int]:
    counts = {}
    for file_path in directory.rglob('*'):
        if file_path.is_file() and not is_ignored_file(file_path):
            ext = file_path.suffix.lower()
            counts[ext] = counts.get(ext, 0) + 1
    return counts

###############################################################################
# read_project_stats
# -----------------
# Reads statistics about a project directory including file counts and sizes
###############################################################################
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
    
    # Choose glob function based on recursion preference
    glob_func = directory.rglob if recursive else directory.glob
    
    for file_path in glob_func('*'):
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
            if file_size > stats['biggest_file_size']:
                stats['biggest_file'] = str(file_path)
                stats['biggest_file_size'] = file_size
                
            # Track newest file
            if file_mtime > stats['newest_file_time']:
                stats['newest_file'] = str(file_path)
                stats['newest_file_time'] = file_mtime
    
    return stats

###############################################################################
# get_file_count_by_type
# ---------------------
# Counts files by type category (document, code, image, etc.) in a directory
###############################################################################
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
    counts = {category: 0 for category in type_categories}
    counts['other'] = 0  # For files that don't match any category
    
    # Choose glob function based on recursion preference
    glob_func = directory.rglob if recursive else directory.glob
    
    # Count files by type
    for file_path in glob_func('*'):
        if file_path.is_file() and not is_ignored_file(file_path):
            ext = file_path.suffix.lower()
            
            # Categorize the file
            categorized = False
            for category, extensions in type_categories.items():
                if ext in extensions:
                    counts[category] += 1
                    categorized = True
                    break
            
            # If not categorized, count as 'other'
            if not categorized:
                counts['other'] += 1
    
    return counts

###############################################################################
# get_cache_key
# -------------
# Generates a cache key for a file path based on the file path and modification time
###############################################################################
def get_cache_key(path_str: str) -> str:
    return hashlib.md5(path_str.encode('utf-8')).hexdigest()

###############################################################################
# get_image_dimensions
# --------------------
# Returns the (width, height) of an image file.
# Tries PIL first, then falls back to ImageMagick's 'identify' command.
###############################################################################
def get_image_dimensions(path: Path) -> Union[Tuple[int, int], None]:
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

###############################################################################
# embed_alt_text_into_image
# -------------------------
# Embeds alt text into an image's metadata for accessibility.
###############################################################################
def embed_alt_text_into_image(path: Path, alt_text: str) -> None:
    try:
        if not PILImage:
            logger.warning("PIL/Pillow not available for embedding alt text")
            return
        
        img = PILImage.open(path)
        if img.mode in ('RGBA', 'LA'):
            # Handle transparency
            img = img.convert('RGB')
        
        # Save the alt text in EXIF UserComment
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
    except Exception as e:
        logger.error(f"Error embedding alt text in {path}: {e}")

###############################################################################
# read_alt_text
# ------------
# Reads alt text from an image's metadata.
###############################################################################
def read_alt_text(path: Path) -> Optional[str]:
    """
    Extract alt text from an image file's metadata.
    
    Args:
        path: Path to the image file
        
    Returns:
        The alt text as a string if found, None otherwise
    """
    try:
        if not PILImage:
            logger.warning("PIL/Pillow not available for reading alt text")
            return None
        
        img = PILImage.open(path)
        exif_data = img.getexif()
        
        # UserComment tag (0x9286)
        if 0x9286 in exif_data:
            user_comment = exif_data[0x9286]
            # Check if it's bytes with ASCII header
            if isinstance(user_comment, bytes):
                if user_comment.startswith(b'ASCII\0\0\0'):
                    return user_comment[8:].decode('utf-8', errors='ignore')
                else:
                    return user_comment.decode('utf-8', errors='ignore')
            else:
                return str(user_comment)
        
        # Check XMP metadata if available
        if 'xmp' in img.info:
            xmp = img.info['xmp']
            if isinstance(xmp, bytes):
                xmp_str = xmp.decode('utf-8', errors='ignore')
                # Look for alt text in XMP metadata
                alt_match = re.search(r'<dc:description>(.*?)</dc:description>', xmp_str)
                if alt_match:
                    return alt_match.group(1)
        
        return None
    except Exception as e:
        logger.error(f"Error reading alt text from {path}: {e}")
        return None

###############################################################################
# write_alt_text
# -------------
# Writes alt text to an image's metadata.
###############################################################################
def write_alt_text(path: Path, alt_text: str) -> bool:
    """
    Write alt text to an image file's metadata.
    
    Args:
        path: Path to the image file
        alt_text: The alt text to embed
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # This is a wrapper around embed_alt_text_into_image for API consistency
        embed_alt_text_into_image(path, alt_text)
        return True
    except Exception as e:
        logger.error(f"Error writing alt text to {path}: {e}")
        return False