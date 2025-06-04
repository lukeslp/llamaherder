###############################################################################
# media.py - Media File Processing Utilities for CleanupX
#
# This module provides classes and functions for analyzing, processing, and
# documenting media files (audio/video) in the CleanupX system. It includes
# metadata extraction, renaming, and markdown documentation generation.
#
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
# --------------
# Uses ffprobe to extract duration, resolution, format, and size from a media
# file. Returns a dictionary with the extracted metadata or error information.
###############################################################################
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
        if process.returncode == 0:
            info = json.loads(process.stdout)
            if "format" in info and "duration" in info["format"]:
                result["duration"] = format_duration(float(info["format"]["duration"]))
            for stream in info.get("streams", []):
                if stream.get("codec_type") == "video":
                    result["width"] = stream.get("width")
                    result["height"] = stream.get("height")
                    break
        else:
            result["error"] = f"ffprobe failed: {process.stderr}"
    except Exception as e:
        logger.error(f"Error analyzing media file {file_path}: {e}")
        result["error"] = str(e)
    return result

###############################################################################
# format_duration
# ---------------
# Converts a duration in seconds to a human-readable HH:MM:SS or MM:SS string.
###############################################################################
def format_duration(seconds: float) -> str:
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    else:
        return f"{minutes:02d}:{seconds:02d}"

###############################################################################
# process_media_file (legacy/simple version)
# ------------------------------------------
# Processes a media file using get_media_info and writes a markdown summary.
# Returns a dictionary with processing results and error info if any.
###############################################################################
def process_media_file(file_path: Union[str, Path], logger: logging.Logger) -> Dict[str, Any]:
    file_path = Path(file_path)
    result = {
        "processed": False,
        "error": None,
        "info": None
    }
    try:
        info = get_media_info(file_path)
        if info and not info.get("error"):
            result["processed"] = True
            result["info"] = info
            md_path = file_path.parent / f"{file_path.stem}_description.md"
            with open(md_path, 'w') as f:
                f.write(f"# {file_path.name}\n\n")
                f.write("## Media Information\n\n")
                if info["duration"]:
                    f.write(f"- Duration: {info['duration']}\n")
                if info["width"] and info["height"]:
                    f.write(f"- Resolution: {info['width']}x{info['height']}\n")
                f.write(f"- Format: {info['format']}\n")
                f.write(f"- Size: {info['size']} bytes\n")
        else:
            result["error"] = info.get("error") if info else "Failed to analyze media file"
    except Exception as e:
        logger.error(f"Error processing media file {file_path}: {e}")
        result["error"] = str(e)
    return result

###############################################################################
# MediaProcessor
# --------------
# Main processor class for media files. Handles metadata extraction, renaming,
# and markdown documentation. Inherits from BaseProcessor.
###############################################################################
class MediaProcessor(BaseProcessor):
    def __init__(self):
        """
        Initialize the media processor with supported extensions and size limit.
        """
        super().__init__()
        self.supported_extensions = MEDIA_EXTENSIONS
        self.max_size_mb = 100.0

    ###########################################################################
    # process
    # -------
    # Orchestrates the processing of a media file: checks type/size, extracts
    # metadata, renames file, and generates markdown documentation.
    ###########################################################################
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
            if not self.can_process(file_path):
                result['error'] = f"Unsupported file type: {file_path.suffix}"
                return result
            if not self.check_file_size(file_path):
                result['error'] = f"File size exceeds maximum ({self.max_size_mb}MB)"
                return result
            description = self._extract_metadata(file_path, cache)
            if not description:
                result['error'] = "Failed to extract metadata"
                return result
            result['description'] = description
            result['metadata_extracted'] = True
            new_name = self._generate_media_filename(file_path, description)
            if not new_name:
                result['error'] = "Failed to generate new filename"
                return result
            new_path = super().rename_file(file_path, new_name, rename_log)
            if new_path:
                result['new_path'] = str(new_path)
                result['renamed'] = True
            self._generate_markdown(file_path, description)
            return result
        except Exception as e:
            logger.error(f"Error processing media file {file_path}: {e}")
            result['error'] = str(e)
            return result
        finally:
            gc.collect()

    ###########################################################################
    # _extract_metadata
    # -----------------
    # Extracts and caches metadata for a media file, including dimensions,
    # duration, type, title, size, and modification date.
    ###########################################################################
    def _extract_metadata(
        self,
        file_path: Path,
        cache: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        try:
            cache_key = str(file_path)
            if cache_key in cache:
                logger.info(f"Using cached description for {file_path.name}")
                return cache[cache_key]
            dimensions = get_media_dimensions(file_path)
            duration = get_media_duration(file_path)
            file_stats = file_path.stat()
            file_size_mb = file_stats.st_size / (1024 * 1024)
            modified_time = datetime.fromtimestamp(file_stats.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
            data = {
                "dimensions": dimensions,
                "duration": duration,
                "format_duration": format_duration(duration),
                "type": file_path.suffix[1:].upper() if file_path.suffix else "Unknown",
                "title": strip_media_suffixes(file_path.stem),
                "file_size": f"{file_size_mb:.2f} MB",
                "modified_date": modified_time,
                "description": f"Media file with dimensions {dimensions} and duration {format_duration(duration)}"
            }
            cache[cache_key] = data
            save_cache(cache)
            return data
        except Exception as e:
            logger.error(f"Error extracting metadata from {file_path}: {e}")
            return None

    ###########################################################################
    # _generate_media_filename
    # -----------------------
    # Constructs a new filename for the media file, embedding dimensions and/or
    # duration as appropriate for the file type.
    ###########################################################################
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
            if ext.lower() in ['.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv']:
                if dimensions and dimensions != 'Unknown' and duration:
                    duration_str = format_duration(duration).replace(':', '_')
                    return f"{original_stem}_{dimensions}_{duration_str}{ext}"
                elif dimensions and dimensions != 'Unknown':
                    return f"{original_stem}_{dimensions}{ext}"
                elif duration:
                    duration_str = format_duration(duration).replace(':', '_')
                    return f"{original_stem}_{duration_str}{ext}"
            elif ext.lower() in ['.mp3', '.wav', '.ogg', '.flac', '.aac']:
                if duration:
                    duration_str = format_duration(duration).replace(':', '_')
                    return f"{original_stem}_{duration_str}{ext}"
            return f"{original_stem}{ext}"
        except Exception as e:
            logger.error(f"Error generating media filename for {file_path}: {e}")
            return None

    ###########################################################################
    # _generate_markdown
    # ------------------
    # Generates a markdown file summarizing the media file's metadata and
    # description. Ensures the metadata directory exists.
    ###########################################################################
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
            if description.get('dimensions') and description.get('dimensions') != 'Unknown':
                content.append(f"- **Dimensions:** {description.get('dimensions')}")
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
        except Exception as e:
            logger.error(f"Error generating markdown for {file_path}: {e}")

###############################################################################
# process_media_file (backward compatibility)
# -------------------------------------------
# Legacy interface for processing a media file. Returns a tuple of original
# path, new path (if renamed), and metadata dictionary.
###############################################################################
def process_media_file(
    file_path: Union[str, Path],
    cache: Dict[str, Any],
    rename_log: Optional[Dict] = None
) -> Tuple[Path, Optional[Path], Optional[Dict[str, Any]]]:
    processor = MediaProcessor()
    result = processor.process(file_path, cache, rename_log)
    new_path = None
    if result.get('new_path'):
        new_path = Path(result['new_path'])
    return Path(file_path), new_path, result.get('description')
