# Code Snippets from src/herd_ai/image_processor.py

File: `src/herd_ai/image_processor.py`  
Language: Python  
Extracted: 2025-06-07 05:09:33  

## Snippet 1
Lines 9-70

```Python
# Markdown documentation for each image. It supports batch processing, caching,
# and conversion of various image formats, with a focus on accessibility and
# integration with LLM workflows.
###############################################################################

import os
import logging
import base64
import tempfile
import io
import gc
import json
import re
import shutil
import time
import sys
import argparse
from pathlib import Path
from typing import Dict, Optional, Tuple, Union, Any, List, Set, Callable

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, MofNCompleteColumn, TimeElapsedColumn
from rich.table import Table
from rich.prompt import Prompt

###############################################################################
# PIL Import and Fallback Handling
###############################################################################
try:
    from PIL import Image, ExifTags, ImageFile
    ImageFile.LOAD_TRUNCATED_IMAGES = True
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

###############################################################################
# Configuration and Utility Imports with Fallbacks
###############################################################################
try:
    try:
        from herd_ai.config import IMAGE_EXTENSIONS, DEFAULT_AI_PROVIDER, IMAGE_ALT_TEXT_TEMPLATE
        from herd_ai.utils.file import extract_text_from_image, get_image_dimensions, embed_alt_text_into_image
        from herd_ai.utils.ai_provider import process_with_ai
        from herd_ai.utils.file import clean_filename, get_cache_key
    except ImportError:
        try:
            from llamacleaner.config import IMAGE_EXTENSIONS, DEFAULT_AI_PROVIDER, IMAGE_ALT_TEXT_TEMPLATE
            from llamacleaner.utils.file import extract_text_from_image, get_image_dimensions, embed_alt_text_into_image
            from llamacleaner.utils.ai_provider import process_with_ai
            from llamacleaner.utils.file import clean_filename, get_cache_key
        except ImportError:
            from config import IMAGE_EXTENSIONS, DEFAULT_AI_PROVIDER, IMAGE_ALT_TEXT_TEMPLATE
            from utils.file import extract_text_from_image, get_image_dimensions, embed_alt_text_into_image
            from utils.ai_provider import process_with_ai
            from utils.file import clean_filename, get_cache_key
except Exception as e:
    print(f"Error importing modules in image_processor.py: {e}")
    print("Make sure you're running from the project directory or the package is installed.")
    IMAGE_EXTENSIONS = set([".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp", ".svg", ".tiff", ".tif"])
    DEFAULT_AI_PROVIDER = "xai"
    IMAGE_ALT_TEXT_TEMPLATE = (
```

## Snippet 2
Lines 72-77

```Python
"Write comprehensive alt text for this image, as though for a blind engineer who needs "
        "to understand every detail of the information including text. "
        "Also suggest a 6-10 word descriptive filename based on the content of the image. "
        "Format your response in this exact JSON structure:\n"
        "{\n"
        "  \"description\": \"Detailed description of the image\",\n"
```

## Snippet 3
Lines 93-96

```Python
def get_cache_key(path_str):
        import hashlib
        return hashlib.md5(path_str.encode('utf-8')).hexdigest()
```

## Snippet 4
Lines 97-108

```Python
logger = logging.getLogger(__name__)
console = Console()

ALT_CACHE_FILE = "alt_text_cache.json"
SUPPORTED_CONVERT_EXTS = {'.heic', '.heif', '.webp', '.gif'}

try:
    from herd_ai.utils import config as herd_config
except ImportError:
    herd_config = None

###############################################################################
```

## Snippet 5
Lines 109-122

```Python
# Add pyheif import check at the top
###############################################################################
try:
    import pyheif
    PYHEIF_AVAILABLE = True
except ImportError:
    PYHEIF_AVAILABLE = False

###############################################################################
# ImageProcessor Class
#
# Handles single image and directory processing, including AI-based alt text
# generation, file renaming, alt text embedding, and Markdown documentation.
###############################################################################
```

## Snippet 6
Lines 125-130

```Python
if provider is None and herd_config:
            provider = herd_config.get_provider()
        self.max_size_mb = max_size_mb
        self.alt_cache: Dict[str, Any] = {}
        self.omni_paths = omni_paths or {}
        self.provider = provider or DEFAULT_AI_PROVIDER
```

## Snippet 7
Lines 136-139

```Python
Determine if a file can be processed based on its extension.
        """
        return file_path.suffix.lower() in IMAGE_EXTENSIONS
```

## Snippet 8
Lines 142-147

```Python
Convert and optimize an image for AI processing.
        Handles RGBA/LA images, resizes large images, and outputs JPEG bytes.
        Returns a tuple of (image_data, error_message).
        """
        try:
            with Image.open(image_path) as img:
```

## Snippet 9
Lines 150-154

```Python
if img.mode == 'RGBA':
                        background.paste(img, mask=img.split()[3])
                    else:
                        background.paste(img, mask=img.split()[1])
                    img = background
```

## Snippet 10
Lines 157-160

```Python
if img.size[0] * img.size[1] > 4000000:
                    img.thumbnail((2000, 2000), Image.Resampling.LANCZOS)
                buffer = io.BytesIO()
                save_kwargs = {}
```

## Snippet 11
Lines 164-169

```Python
elif img.format == 'PNG':
                    save_kwargs['optimize'] = True
                else:
                    save_kwargs['quality'] = 85
                img.save(buffer, format='JPEG', **save_kwargs)
                return buffer.getvalue(), None
```

## Snippet 12
Lines 180-197

```Python
def process_single_image(
        self,
        file_path: Path,
        omni_paths: Dict[str, Any],
        log_callback: Optional[Callable[[str], None]] = None
    ) -> Dict[str, Any]:
        result = {
            "file": str(file_path),
            "alt_text_generated": False,
            "dimensions": None,
            "renamed": False,
            "error": None,
            "new_path": None,
            "markdown_path": None,
            "embedded_metadata": [],  # Track which metadata fields were embedded
            "provider": self.provider,
            "model": None,
        }
```

## Snippet 13
Lines 199-202

```Python
if log_callback:
                log_callback(msg)
            else:
                console.print(msg)
```

## Snippet 14
Lines 204-206

```Python
log(f"[yellow]PIL/Pillow not available for image processing: {file_path}[/]")
            result["error"] = "PIL/Pillow not available"
            return result
```

## Snippet 15
Lines 223-225

```Python
if len(api_key) > 8:
                            masked_key = f"{api_key[:4]}...{api_key[-4:]}"
                        log(f"[cyan]Using X.AI API key: {masked_key}[/cyan]")
```

## Snippet 16
Lines 228-233

```Python
log(f"[cyan]Using AI provider: {self.provider}[/cyan]")
            # Always get model name
            try:
                from herd_ai.config import get_model_for_file
                model = get_model_for_file(file_path, self.provider)
                result["model"] = model
```

## Snippet 17
Lines 235-237

```Python
except Exception as e:
                log(f"[yellow]Could not determine model: {e}[/]")
            image_data, error = self.convert_image_for_processing(file_path)
```

## Snippet 18
Lines 238-245

```Python
if error:
                log(f"[yellow]{error}[/]")
                result["error"] = error
                return result
            ocr = extract_text_from_image(file_path) or ""
            prompt = (
                "You will receive both OCR-extracted text and a base64-encoded image. "
                "Return a JSON object with the following keys:\n"
```

## Snippet 19
Lines 248-251

```Python
"- categories: A list of categories/tags for the image\n"
                "- suggested_filename: A concise, descriptive filename (5-8 words max, lowercase with underscores)\n\n"
                f"OCR Text: {ocr[:1000]}\n"
                f"Current filename: {file_path.name}\n"
```

## Snippet 20
Lines 255-258

```Python
if len(b64) < 500000:
                    prompt += f"Image Base64: {b64}"
                else:
                    prompt += "Image Base64: [Image too large, using OCR text only]"
```

## Snippet 21
Lines 265-267

```Python
log(f"[red]X.AI processing failed or returned invalid data for {file_path.name}[/red]")
                    result["error"] = "X.AI processing failed or returned invalid data"
                    return result
```

## Snippet 22
Lines 274-280

```Python
if raw.get("error", False):
                        log(f"[yellow]AI provider returned an error: {raw.get('text', 'Unknown error')}[/]")
                        result["error"] = raw.get("text", "AI provider error")
                        data = {}
                    else:
                        raw = raw.get("text", "")
```

## Snippet 23
Lines 285-288

```Python
elif not isinstance(raw, dict):
                    try:
                        data = json.loads(raw)
                    except json.JSONDecodeError as e:
```

## Snippet 24
Lines 290-293

```Python
if raw and "{" in raw and "}" in raw:
                            try:
                                start = raw.find("{")
                                end = raw.rfind("}") + 1
```

## Snippet 25
Lines 294-296

```Python
if start >= 0 and end > start:
                                    json_str = raw[start:end]
                                    data = json.loads(json_str)
```

## Snippet 26
Lines 305-311

```Python
elif 'text' in raw:
                        try:
                            data = json.loads(raw.get('text', ''))
                        except json.JSONDecodeError:
                            data = {}
                    else:
                        data = raw
```

## Snippet 27
Lines 321-325

```Python
if alt:
                log(f"[green]Generated alt text: {alt[:50]}...[/]")
                result["embedded_metadata"].append("alt_text")
            else:
                log(f"[yellow]No alt text generated[/]")
```

## Snippet 28
Lines 328-332

```Python
if name_raw:
                log(f"[green]Suggested filename: {name_raw}[/]")
            else:
                log(f"[yellow]No filename suggested[/]")
            self.alt_cache[get_cache_key(str(file_path))] = alt
```

## Snippet 29
Lines 335-341

```Python
log(f"[green]Generated alt text for {file_path.name}[/]")
                try:
                    embed_alt_text_into_image(file_path, alt)
                    log(f"[green]Embedded alt text in {file_path.name}[/]")
                    result["embedded_metadata"].append("alt_text (EXIF)")
                except Exception as e:
                    log(f"[yellow]Error embedding alt text in {file_path.name}: {e}[/]")
```

## Snippet 30
Lines 346-349

```Python
if name_raw and len(name_raw.strip()) > 3:
                new_stem = clean_filename(name_raw)
                new_name = f"{new_stem}{file_path.suffix.lower()}"
                new_path = file_path.with_name(new_name)
```

## Snippet 31
Lines 350-352

```Python
if not new_path.exists() and new_name != file_path.name and new_stem != file_path.stem:
                    try:
                        file_path.rename(new_path)
```

## Snippet 32
Lines 359-361

```Python
else:
                    base, ext = os.path.splitext(new_name)
                    counter = 1
```

## Snippet 33
Lines 362-364

```Python
while True:
                        candidate = f"{base}_{counter}{ext}"
                        candidate_path = file_path.with_name(candidate)
```

## Snippet 34
Lines 365-367

```Python
if not candidate_path.exists():
                            try:
                                file_path.rename(candidate_path)
```

## Snippet 35
Lines 372-374

```Python
except Exception as e:
                                log(f"[yellow]Error renaming {file_path.name}: {e}[/]")
                            break
```

## Snippet 36
Lines 376-384

```Python
md_content = [
                f"# {file_path.stem}",
                "",
                f"**Alt Text:** {alt}",
                "",
                f"**Description:** {desc}",
                "",
                "## Categories"
            ]
```

## Snippet 37
Lines 385-401

```Python
for c in cats:
                md_content.append(f"- {c}")
            md_content.extend([
                "",
                "## Metadata",
                f"- Dimensions before: {before_dims}",
                f"- Dimensions after: {after_dims}",
                f"- File path: {file_path}",
                f"- AI Provider: {self.provider}",
                f"- Process date: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(Path(file_path).stat().st_mtime))}"
            ])
            md_path = file_path.with_suffix('.md')
            try:
                md_path.write_text("\n".join(md_content), encoding='utf-8')
                result["markdown_path"] = str(md_path)
                log(f"[green]Created markdown file: {md_path.name}[/]")
            except Exception as e:
```

## Snippet 38
Lines 403-407

```Python
table = Table(title=f"Summary for {file_path.name}")
            table.add_column("Field", style="bold cyan")
            table.add_column("Value", style="white")
            table.add_row("Dimensions", str(after_dims))
            table.add_row("AI Provider", self.provider)
```

## Snippet 39
Lines 412-415

```Python
if result["renamed"]:
                table.add_row("Renamed To", Path(result["new_path"]).name)
            console.print(table)
            return result
```

## Snippet 40
Lines 416-421

```Python
except Exception as e:
            error_msg = f"Error processing image {file_path}: {str(e)}"
            log(f"[red]{error_msg}[/]")
            result["error"] = error_msg
            return result
```

## Snippet 41
Lines 429-443

```Python
def process_directory(
        self,
        directory: Path,
        recursive: bool = False,
        batch_size: int = 10,
        force: bool = False,
        rename: bool = False,
        override_md: bool = False,
        test: bool = False,
        log_callback: Optional[Callable[[str], None]] = None,
        provider: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process all images in a directory.
```

## Snippet 42
Lines 444-453

```Python
Wrapper around process_images_cli for backward compatibility with CLI module.

        Args:
            directory: Directory to process
            recursive: Whether to process subdirectories
            batch_size: Number of images to process at once
            force: Whether to force reprocessing of images with existing alt text
            rename: Whether to rename images based on content
            override_md: Whether to override existing markdown files
            test: Whether to test metadata before and after embedding
```

## Snippet 43
Lines 457-468

```Python
Returns:
            Dictionary with processing statistics and success status
        """
        result = {
            "success": False,
            "files_processed": 0,
            "output_dir": None,
            "message": None,
            "error": None
        }

        try:
```

## Snippet 44
Lines 477-483

```Python
force = Prompt.ask("[bright_yellow]Force reprocessing even if .md or cache exists?[/bright_yellow] (y/n)", default="n").lower() == "y"
                rename = Prompt.ask("[bright_yellow]Rename files based on content analysis?[/bright_yellow] (y/n)", default="n").lower() == "y"
                override_md = Prompt.ask("[bright_yellow]Override existing markdown file check and reprocess images?[/bright_yellow] (y/n)", default="n").lower() == "y"
                test = Prompt.ask("[bright_yellow]Check metadata before and after embedding alt text?[/bright_yellow] (y/n)", default="n").lower() == "y"

                log_callback(f"[bright_blue]Options: force={force}, rename={rename}, override_md={override_md}, test={test}[/bright_blue]")
```

## Snippet 45
Lines 491-495

```Python
if log_callback:
                    log_callback(f"[red]{error_msg}[/red]")
                result["error"] = error_msg
                return result
```

## Snippet 46
Lines 496-520

```Python
# Setup paths
            base_dir = directory / ".herd"
            images_dir = base_dir / "images"

            # Ensure directories exist
            base_dir.mkdir(parents=True, exist_ok=True)
            images_dir.mkdir(parents=True, exist_ok=True)

            stats = process_images_cli(
                directory=directory,
                recursive=recursive,
                force=force,
                rename=rename,
                override_md=override_md,
                test=test,
                log_callback=log_callback,
                provider=provider
            )

            # Return detailed results
            result["success"] = True
            result["files_processed"] = stats.get("total", 0)
            result["files_processed_success"] = stats.get("processed", 0)
            result["files_with_errors"] = stats.get("errors", 0)
            result["output_dir"] = str(images_dir)
```

## Snippet 47
Lines 521-524

```Python
result["message"] = f"Processed {stats.get('processed', 0)}/{stats.get('total', 0)} images"

            return result
```

## Snippet 48
Lines 527-531

```Python
if log_callback:
                log_callback(f"[red]{error_msg}[/red]")
            result["error"] = error_msg
            return result
```

## Snippet 49
Lines 538-541

```Python
def convert_to_jpeg(image_path: Path) -> Optional[Path]:
    try:
        from PIL import Image
        temp_path = Path(tempfile.gettempdir()) / f"temp_{image_path.stem}.jpg"
```

## Snippet 50
Lines 546-556

```Python
try:
                heif_file = pyheif.read(str(image_path))
                img = Image.frombytes(
                    heif_file.mode, heif_file.size, heif_file.data,
                    "raw", heif_file.mode, heif_file.stride,
                )
                img.save(temp_path, "JPEG", quality=95)
                return temp_path
            except Exception as e:
                print(f"Error converting HEIC/HEIF: {e}")
                return None
```

## Snippet 51
Lines 559-564

```Python
if img.mode in ('RGBA', 'LA'):
                background = Image.new('RGBA', img.size, (255, 255, 255))
                img = Image.alpha_composite(background.convert(img.mode), img)
            img = img.convert("RGB")
            img.save(temp_path, "JPEG", quality=95)
            return temp_path
```

## Snippet 52
Lines 565-570

```Python
elif image_path.suffix.lower() == '.gif':
            img = Image.open(image_path)
            img.seek(0)
            img = img.convert("RGB")
            img.save(temp_path, "JPEG", quality=95)
            return temp_path
```

## Snippet 53
Lines 571-574

```Python
except Exception as e:
        print(f"Error in convert_to_jpeg: {e}")
        return None
```

## Snippet 54
Lines 581-585

```Python
if os.path.exists(ALT_CACHE_FILE):
        with open(ALT_CACHE_FILE, "r", encoding="utf-8") as fp:
            return json.load(fp)
    return {}
```

## Snippet 55
Lines 586-592

```Python
def save_alt_cache(cache: Dict[str, Any]):
    with open(ALT_CACHE_FILE, "w", encoding="utf-8") as fp:
        json.dump(cache, fp, indent=2, ensure_ascii=False)

###############################################################################
# process_images_cli
#
```

## Snippet 56
Lines 596-605

```Python
def process_images_cli(
    directory: Path,
    recursive: bool = False,
    force: bool = False,
    rename: bool = False,
    override_md: bool = False,
    test: bool = False,
    log_callback: Optional[Any] = None,
    provider: str = None
):
```

## Snippet 57
Lines 622-625

```Python
if api_key:
                    log_callback(f"[cyan]Using X.AI API key from environment variable[/cyan]")
                else:
                    log_callback(f"[yellow]Warning: No X.AI API key found. Processing may fail.[/yellow]")
```

## Snippet 58
Lines 627-629

```Python
if len(api_key) > 8:
                    masked_key = f"{api_key[:4]}...{api_key[-4:]}"
                log_callback(f"[cyan]Using X.AI API key from config: {masked_key}[/cyan]")
```

## Snippet 59
Lines 642-647

```Python
cache = load_alt_cache()
    stats = {
        "total": 0, "processed": 0, "skipped": 0, "renamed": 0, "errors": 0,
        "converted": 0, "optimized": 0
    }
    images = []
```

## Snippet 60
Lines 656-658

```Python
if log_callback:
            log_callback("[yellow]No images found in directory.[/]")
        return stats
```

## Snippet 61
Lines 659-662

```Python
for img_path in images:
        try:
            md_path = img_path.with_suffix('.md')
            cache_key = f"{img_path}:{os.path.getmtime(img_path)}"
```

## Snippet 62
Lines 664-667

```Python
if log_callback:
                    log_callback(f"[yellow]Skipping {img_path.name}: .md exists[/]")
                stats["skipped"] += 1
                continue
```

## Snippet 63
Lines 669-672

```Python
if log_callback:
                    log_callback(f"[yellow]Skipping {img_path.name}: in cache[/]")
                stats["skipped"] += 1
                continue
```

## Snippet 64
Lines 676-678

```Python
if jpeg_path:
                    to_process = jpeg_path
                    stats["converted"] += 1
```

## Snippet 65
Lines 680-683

```Python
if 'get_model_for_file' in globals() and log_callback:
                try:
                    from herd_ai.config import get_model_for_file
                    model = get_model_for_file(to_process, provider)
```

## Snippet 66
Lines 687-693

```Python
start_time = time.time()
            result = processor.process_single_image(
                to_process,
                {"base_dir": directory},
                log_callback
            )
            processing_time = time.time() - start_time
```

## Snippet 67
Lines 696-699

```Python
if result.get("error"):
                stats["errors"] += 1
            else:
                stats["processed"] += 1
```

## Snippet 68
Lines 702-710

```Python
cache[cache_key] = {
                "alt_text": result.get("alt_text_generated"),
                "dimensions": result.get("dimensions"),
                "renamed": result.get("renamed"),
                "error": result.get("error"),
                "provider": provider,
                "processing_time": processing_time
            }
            save_alt_cache(cache)
```

## Snippet 69
Lines 712-715

```Python
if log_callback:
                log_callback(f"[red]Error processing {img_path}: {e}[/red]")
            stats["errors"] += 1
            continue
```

## Snippet 70
Lines 716-726

```Python
if log_callback:
        log_callback(f"[bold green]Image processing complete. Summary:[/bold green]")
        log_callback(f"[green]Total images: {stats['total']}[/green]")
        log_callback(f"[green]Processed: {stats['processed']}[/green]")
        log_callback(f"[green]Converted: {stats['converted']}[/green]")
        log_callback(f"[green]Skipped: {stats['skipped']}[/green]")
        log_callback(f"[green]Renamed: {stats['renamed']}[/green]")
        log_callback(f"[green]Errors: {stats['errors']}[/green]")
        log_callback(f"[green]Provider used: {provider}[/green]")
    return stats
```

## Snippet 71
Lines 732-735

```Python
def main():
    parser = argparse.ArgumentParser(description="Process images to generate alt text and markdown files.")
    parser.add_argument("--dir", required=True, help="Directory containing images to process")
    parser.add_argument("--recursive", "-r", action="store_true", help="Process subdirectories recursively")
```

## Snippet 72
Lines 736-742

```Python
parser.add_argument("--force", "-f", action="store_true", help="Force reprocessing even if .md or cache exists")
    parser.add_argument("--rename", "-n", action="store_true", help="Rename files based on content analysis")
    parser.add_argument("--override_md", "-m", action="store_true", help="Override existing markdown file check and reprocess images")
    parser.add_argument("--test", "-t", action="store_true", help="Check metadata before and after embedding alt text")
    parser.add_argument("--provider", "-p", help=f"AI provider to use (default: {DEFAULT_AI_PROVIDER})")
    args = parser.parse_args()
    directory = Path(args.dir)
```

## Snippet 73
Lines 743-749

```Python
if not directory.exists() or not directory.is_dir():
        print(f"[red]Invalid directory: {directory}[/red]")
        sys.exit(1)
    process_images_cli(directory, recursive=args.recursive, force=args.force,
                      rename=args.rename, override_md=args.override_md,
                      test=args.test, provider=args.provider)
```

## Snippet 74
Lines 754-767

```Python
def process_directory(
    directory: Path,
    recursive: bool = False,
    batch_size: int = 10,
    force: bool = False,
    rename: bool = False,
    override_md: bool = False,
    test: bool = False,
    log_callback: Optional[Callable[[str], None]] = None,
    provider: Optional[str] = None
) -> Dict[str, Any]:
    """
    Process all images in a directory.
```

## Snippet 75
Lines 768-777

```Python
Wrapper around process_images_cli for backward compatibility with CLI module.

    Args:
        directory: Directory to process
        recursive: Whether to process subdirectories
        batch_size: Number of images to process at once
        force: Whether to force reprocessing of images with existing alt text
        rename: Whether to rename images based on content
        override_md: Whether to override existing markdown files
        test: Whether to test metadata before and after embedding
```

## Snippet 76
Lines 781-792

```Python
Returns:
        Dictionary with processing statistics
    """
    result = {
        "success": False,
        "files_processed": 0,
        "output_dir": None,
        "message": None,
        "error": None
    }

    try:
```

## Snippet 77
Lines 801-807

```Python
force = Prompt.ask("[bright_yellow]Force reprocessing even if .md or cache exists?[/bright_yellow] (y/n)", default="n").lower() == "y"
            rename = Prompt.ask("[bright_yellow]Rename files based on content analysis?[/bright_yellow] (y/n)", default="n").lower() == "y"
            override_md = Prompt.ask("[bright_yellow]Override existing markdown file check and reprocess images?[/bright_yellow] (y/n)", default="n").lower() == "y"
            test = Prompt.ask("[bright_yellow]Check metadata before and after embedding alt text?[/bright_yellow] (y/n)", default="n").lower() == "y"

            log_callback(f"[bright_blue]Options: force={force}, rename={rename}, override_md={override_md}, test={test}[/bright_blue]")
```

## Snippet 78
Lines 808-819

```Python
# Process the directory
        stats = process_images_cli(
            directory,
            recursive=recursive,
            force=force,
            rename=rename,
            override_md=override_md,
            test=test,
            log_callback=log_callback,
            provider=provider
        )
```

## Snippet 79
Lines 823-825

```Python
# Set up result for return
        result["success"] = True
        result["files_processed"] = stats.get("processed", 0)
```

## Snippet 80
Lines 829-831

```Python
except Exception as e:
        import traceback
        error_msg = f"{e}\n{traceback.format_exc()}"
```

## Snippet 81
Lines 832-837

```Python
if log_callback:
            log_callback(f"[bold red]Error processing directory: {e}[/]")
        result["success"] = False
        result["error"] = str(e)
        result["traceback"] = error_msg
```

## Snippet 82
Lines 841-851

```Python
def batch_extract_alt_text(
    directory: Path,
    output_format: str = "text",
    recursive: bool = False,
    log_callback: Optional[Callable[[str], None]] = None
) -> str:
    """
    Extract alt text from multiple images in a directory.

    Args:
        directory: Directory containing images
```

## Snippet 83
Lines 856-858

```Python
Returns:
        String with extracted alt text in requested format
    """
```

## Snippet 84
Lines 859-865

```Python
if log_callback:
        log_callback(f"[bold cyan]Extracting alt text from images in: {directory}[/]")

    processor = ImageProcessor()
    image_files = []

    # Find all image files
```

## Snippet 85
Lines 876-879

```Python
for img_file in image_files:
        try:
            from herd_ai.utils.file import read_alt_text
            alt_text = read_alt_text(img_file)
```

## Snippet 86
Lines 880-884

```Python
if alt_text:
                results.append({
                    "file": str(img_file),
                    "alt_text": alt_text
                })
```

## Snippet 87
Lines 895-897

```Python
for r in results:
            safe_alt_text = r["alt_text"].replace('"', '""')
            output += f'"{r["file"]}","{safe_alt_text}"\n'
```

## Snippet 88
Lines 900-903

```Python
for r in results:
            output += f"## {Path(r['file']).name}\n\n"
            output += f"![{r['alt_text']}]({r['file']})\n\n"
            output += f"**Alt Text:** {r['alt_text']}\n\n"
```

## Snippet 89
Lines 912-917

```Python
List available output formats for alt text extraction.

    Returns:
        List of format names
    """
    return ["text", "json", "csv", "markdown"]
```

