# Code Snippets from src/herd_ai/rename.py

File: `src/herd_ai/rename.py`  
Language: Python  
Extracted: 2025-06-07 05:09:28  

## Snippet 1
Lines 1-24

```Python
# =============================================================================
# herd_ai.rename
#
# File renaming functionality using LLM (Large Language Model) suggestions.
# Provides batch and single-file renaming, using AI to generate meaningful
# filenames based on file content. Includes logging, undo support, and
# flexible provider/model selection.
# =============================================================================

import json
from json import JSONDecodeError
from pathlib import Path
import logging
import time
from typing import List, Set, Dict, Callable, Any, Optional, Union, Tuple
import os

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, MofNCompleteColumn, TimeElapsedColumn
from rich.panel import Panel
from rich.table import Table

# =============================================================================
# Import configuration, file utilities, and AI provider modules.
```

## Snippet 2
Lines 25-54

```Python
# Tries several import paths for compatibility with different project layouts.
# =============================================================================
try:
    try:
        from herd_ai.config import PROCESS_EXTENSIONS, RENAME_TEMPLATE, DEFAULT_AI_PROVIDER, IMAGE_EXTENSIONS
        from herd_ai.utils.file import get_file_text, clean_filename
        from herd_ai.utils.ai_provider import process_with_ai
        from herd_ai.utils import config as herd_config
    except ImportError:
        try:
            from llamacleaner.config import PROCESS_EXTENSIONS, RENAME_TEMPLATE, DEFAULT_AI_PROVIDER, IMAGE_EXTENSIONS
            from llamacleaner.utils.file import get_file_text, clean_filename
            from llamacleaner.utils.ai_provider import process_with_ai
            from llamacleaner.utils import config as herd_config
        except ImportError:
            from config import PROCESS_EXTENSIONS, RENAME_TEMPLATE, DEFAULT_AI_PROVIDER, IMAGE_EXTENSIONS
            from utils.file import get_file_text, clean_filename
            from utils.ai_provider import process_with_ai
            from utils import config as herd_config
except Exception as e:
    print(f"Error importing modules in rename.py: {e}")
    print("Make sure you're running from the project directory or the package is installed.")
    raise

logger = logging.getLogger(__name__)
console = Console()

# =============================================================================
# generate_description
#
```

## Snippet 3
Lines 58-63

```Python
def generate_description(path: Path, provider: Optional[str] = None) -> str:
    """
    Generate a short description of a file's content.

    Args:
        path: Path to the file
```

## Snippet 4
Lines 66-82

```Python
Returns:
        str: A short description of the file content
    """
    try:
        try:
            try:
                from herd_ai.utils.file import extract_text_from_pdf, extract_text_from_docx
            except ImportError:
                try:
                    from llamacleaner.utils.file import extract_text_from_pdf, extract_text_from_docx
                except ImportError:
                    from utils.file import extract_text_from_pdf, extract_text_from_docx
        except Exception as e:
            print(f"Error importing file utilities: {e}")
            raise

        ext = path.suffix.lower()
```

## Snippet 5
Lines 104-108

```Python
def rename_file(path: Path, suggestion: str, omni_paths: Dict[str, Any]) -> bool:
    new_base = clean_filename(suggestion)
    new_name = new_base + path.suffix.lower()
    target = path.with_name(new_name)
```

## Snippet 6
Lines 109-112

```Python
if target.exists():
        console.print(f"[yellow]Skipping rename; target exists: {target}[/]")
        return False
```

## Snippet 7
Lines 113-116

```Python
if path.name == new_name:
        console.print(f"[yellow]Skipping rename; name unchanged: {path.name}[/]")
        return False
```

## Snippet 8
Lines 126-139

```Python
if isinstance(undo_log, Path) and undo_log.exists():
                with open(undo_log, "r") as ul:
                    try:
                        log = json.load(ul)
                    except JSONDecodeError:
                        log = []
            else:
                log = []
            log.append({
                "type": "rename",
                "old": str(path),
                "new": str(target),
                "timestamp": time.time()
            })
```

## Snippet 9
Lines 140-143

```Python
if isinstance(undo_log, Path):
                undo_log.parent.mkdir(exist_ok=True, parents=True)
                with open(undo_log, "w") as ul:
                    json.dump(log, ul, indent=2)
```

## Snippet 10
Lines 144-146

```Python
except Exception as e:
            logger.error(f"Error logging rename action: {e}")
        return True
```

## Snippet 11
Lines 147-150

```Python
except Exception as e:
        console.print(f"[red]Error renaming {path.name}: {e}[/]")
        return False
```

## Snippet 12
Lines 158-164

```Python
def batch_process_files(
    files: List[Path],
    omni_paths: Dict[str, Any],
    log_callback: Optional[Callable[[str], None]] = None,
    batch_size: int = 10,
    provider: str = None
) -> Tuple[int, int]:
```

## Snippet 13
Lines 174-178

```Python
if log_callback:
            log_callback(msg)
        else:
            logger.info(msg)
```

## Snippet 14
Lines 179-184

```Python
if not files:
        log("[yellow]No files to process.[/]")
        return 0, 0

    log(f"[bold cyan]Using AI provider: {provider}[/bold cyan]")
```

## Snippet 15
Lines 192-195

```Python
if api_key:
                log(f"[cyan]Using X.AI API key from environment variable[/cyan]")
            else:
                log(f"[bold yellow]Warning: No X.AI API key found. Processing may fail.[/bold yellow]")
```

## Snippet 16
Lines 197-200

```Python
if len(api_key) > 8:
                masked_key = f"{api_key[:4]}...{api_key[-4:]}"
            log(f"[cyan]Using X.AI API key from config: {masked_key}[/cyan]")
```

## Snippet 17
Lines 212-218

```Python
if filepath.suffix.lower() not in PROCESS_EXTENSIONS:
                log(f"[yellow]Skipping unsupported file type: {filepath}[/]")
                continue
            model = "default"
            try:
                from herd_ai.config import get_model_for_file
                model = get_model_for_file(filepath, provider)
```

## Snippet 18
Lines 239-243

```Python
log(f"[cyan]Sending prompt to {provider} (model: {model}) for {filepath.name}[/cyan]")
            ai_start_time = time.time()
            try:
                raw = process_with_ai(filepath, prompt, provider=provider, custom_system_prompt=RENAME_TEMPLATE)
                # Handle dict responses by extracting the 'text' field
```

## Snippet 19
Lines 244-248

```Python
if isinstance(raw, dict):
                    text_response = raw.get("text", "")
                else:
                    text_response = raw or ""
                ai_processing_time = time.time() - ai_start_time
```

## Snippet 20
Lines 259-261

```Python
if not suggestion or suggestion.lower().startswith("please") or len(suggestion) > 100:
                log(f"[yellow]Invalid suggestion: {suggestion}[/]")
                continue
```

## Snippet 21
Lines 270-280

```Python
if processing_times:
        avg_time = sum(processing_times) / len(processing_times)
        min_time = min(processing_times)
        max_time = max(processing_times)
        log(f"[bold cyan]Processing Statistics:[/bold cyan]")
        log(f"[cyan]Total processing time: {total_time:.2f}s[/cyan]")
        log(f"[cyan]Average processing time: {avg_time:.2f}s per file[/cyan]")
        log(f"[cyan]Fastest processing time: {min_time:.2f}s[/cyan]")
        log(f"[cyan]Slowest processing time: {max_time:.2f}s[/cyan]")
    return success_count, len(files)
```

## Snippet 22
Lines 287-294

```Python
def process_renames(
    file_or_dir: Path,
    recursive: bool = False,
    log_callback: Optional[Callable[[str], None]] = None,
    exclude_ext: Set[str] = None,
    omni_paths: Dict[str, Any] = None,
    provider: str = None
) -> None:
```

## Snippet 23
Lines 308-312

```Python
if log_callback:
            log_callback(msg)
        else:
            logger.info(msg)
```

## Snippet 24
Lines 318-320

```Python
if file_or_dir.suffix.lower() in exclude_ext:
            log(f"[yellow]Skipping excluded extension: {file_or_dir}[/]")
            return
```

## Snippet 25
Lines 328-330

```Python
else:
                log(f"[yellow]No files were renamed.[/]")
            return
```

## Snippet 26
Lines 334-339

```Python
if file_or_dir.is_dir():
        start_dir_time = time.time()
        log(f"[bold cyan]Scanning directory: {file_or_dir}[/bold cyan]")
        log(f"[bold cyan]Using AI provider: {provider}[/bold cyan]")
        try:
            from herd_ai.config import get_model_for_file
```

## Snippet 27
Lines 353-356

```Python
if api_key:
                    log(f"[cyan]Using X.AI API key from environment variable[/cyan]")
                else:
                    log(f"[bold yellow]Warning: No X.AI API key found. Processing may fail.[/bold yellow]")
```

## Snippet 28
Lines 358-360

```Python
if len(api_key) > 8:
                    masked_key = f"{api_key[:4]}...{api_key[-4:]}"
                log(f"[cyan]Using X.AI API key from config: {masked_key}[/cyan]")
```

## Snippet 29
Lines 372-374

```Python
if not files:
            log(f"[yellow]No applicable files found in {file_or_dir}[/]")
            return
```

## Snippet 30
Lines 402-404

```Python
if saved_provider:
            provider = saved_provider
            logger.info(f"Loading provider from config: {saved_provider}")
```

## Snippet 31
Lines 405-410

```Python
provider = provider or DEFAULT_AI_PROVIDER
    logger.info(f"Processing rename with provider: {provider}")
    model = "default"
    try:
        from herd_ai.config import get_model_for_file
        model = get_model_for_file(file_path, provider)
```

## Snippet 32
Lines 412-417

```Python
except ImportError:
        pass
    try:
        ai_start_time = time.time()
        raw = process_with_ai(file_path, prompt, provider=provider, custom_system_prompt=custom_system_prompt)
        # Handle dict responses by extracting the 'text' field
```

## Snippet 33
Lines 418-422

```Python
if isinstance(raw, dict):
            text_response = raw.get("text", "")
        else:
            text_response = raw or ""
        ai_time = time.time() - ai_start_time
```

## Snippet 34
Lines 440-457

```Python
if __name__ == "__main__":
    import time
    try:
        try:
            from herd_ai.utils.ai_provider import process_with_ai
        except ImportError:
            try:
                from llamacleaner.utils.ai_provider import process_with_ai
            except ImportError:
                from utils.ai_provider import process_with_ai
    except logging.exception as e:
        print(f"Error importing ai_provider module: {e}")
        raise

    print("[TEST] Starting minimal AI provider test...")
    start = time.time()
    response = process_with_ai(
        Path("test_file.py"),
```

