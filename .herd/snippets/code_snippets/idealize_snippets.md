# Code Snippets from src/herd_ai/idealize.py

File: `src/herd_ai/idealize.py`  
Language: Python  
Extracted: 2025-06-07 05:09:37  

## Snippet 1
Lines 4-21

```Python
# Provides functionality for creating canonical, "idealized" versions of content
# files using LLMs. Handles single files and directories, including backup,
# logging, and batch processing. Integrates with project config and utilities.
###############################################################################

import json
from json import JSONDecodeError
from pathlib import Path
import time
import shutil
from typing import List, Set, Dict, Any, Optional, Callable, Union, Tuple

from rich.console import Console
from rich.table import Table
from rich.progress import Progress, TextColumn, BarColumn, MofNCompleteColumn, TimeElapsedColumn, SpinnerColumn
from rich.panel import Panel

###############################################################################
```

## Snippet 2
Lines 22-54

```Python
# Import configuration and utility functions, with fallbacks for different
# project layouts and direct execution.
###############################################################################
try:
    try:
        from herd_ai.config import TEXT_EXTENSIONS, DOCUMENT_EXTENSIONS, DEFAULT_AI_PROVIDER
        from herd_ai.utils.file import get_file_text, clean_filename
        from herd_ai.utils.ai_provider import process_with_ai
        from herd_ai.utils import config as herd_config
    except ImportError:
        try:
            from llamacleaner.config import TEXT_EXTENSIONS, DOCUMENT_EXTENSIONS, DEFAULT_AI_PROVIDER
            from llamacleaner.utils.file import get_file_text, clean_filename
            from llamacleaner.utils.ai_provider import process_with_ai
            from llamacleaner.utils import config as herd_config
        except ImportError:
            from config import TEXT_EXTENSIONS, DOCUMENT_EXTENSIONS, DEFAULT_AI_PROVIDER
            from utils.file import get_file_text, clean_filename
            from utils.ai_provider import process_with_ai
            from utils import config as herd_config
except Exception as e:
    print(f"Error importing modules in idealize.py: {e}")
    print("Make sure you're running from the project directory or the package is installed.")
    TEXT_EXTENSIONS = {".txt", ".md", ".rst", ".log", ".json", ".xml", ".yaml", ".yml", ".ini", ".cfg", ".conf"}
    DOCUMENT_EXTENSIONS = {".pdf", ".docx", ".doc", ".rtf", ".odt"}
    DEFAULT_AI_PROVIDER = "xai"
    herd_config = None

console = Console()

###############################################################################
# process_single_file
#
```

## Snippet 3
Lines 63-76

```Python
def process_single_file(
    file_path: Path,
    omni_paths: Dict[str, Any],
    log_callback: Optional[Callable[[str], None]] = None,
    provider: Optional[str] = None
) -> Dict[str, Any]:
    result = {
        "file": str(file_path),
        "idealized": False,
        "backed_up": False,
        "error": None,
        "new_path": None
    }
```

## Snippet 4
Lines 78-82

```Python
if log_callback:
            log_callback(msg)
        else:
            console.print(msg)
```

## Snippet 5
Lines 85-87

```Python
if saved_provider:
            provider = saved_provider
            log(f"[cyan]Loading provider from config: {saved_provider}[/cyan]")
```

## Snippet 6
Lines 88-99

```Python
provider = provider or DEFAULT_AI_PROVIDER

    log(f"[bold cyan]Using AI provider: {provider}[/bold cyan]")

    try:
        base_dir = omni_paths.get("base_dir", file_path.parent / ".herd")
        backup_dir = omni_paths.get("backup_dir", base_dir / "backup")
        ideal_dir = omni_paths.get("idealized_dir", base_dir / "idealized")
        backup_dir.mkdir(parents=True, exist_ok=True)
        ideal_dir.mkdir(parents=True, exist_ok=True)

        exts = TEXT_EXTENSIONS.union(DOCUMENT_EXTENSIONS)
```

## Snippet 7
Lines 100-105

```Python
if file_path.suffix.lower() not in exts:
            result["error"] = "Unsupported file type"
            log(f"[yellow]Skipping non-text/document file: {file_path}[/]")
            return result

        content = get_file_text(file_path)
```

## Snippet 8
Lines 106-127

```Python
if not content.strip():
            result["error"] = "Empty file"
            log(f"[yellow]Empty file: {file_path}[/]")
            return result

        system_prompt = (
            "You are an expert content editor specializing in enhancement and optimization. "
            "Your task is to create an idealized version of the provided content. "
            "Clean it up, fix errors, improve clarity, and enhance the overall quality. "
            "Maintain the original meaning and intent, but make it more concise, clear, and polished. "
            "Respond only with the improved content, no explanations needed."
        )

        prompt = (
            f"Create an idealized version of this content from: {file_path.name}\n\n"
            f"```\n{content}\n```\n\n"
            "Clean it up, fix errors, improve clarity, and enhance the overall quality."
        )

        log(f"[cyan]Generating idealized content for: {file_path.name}[/]")
        resp = process_with_ai(file_path, prompt, provider=provider, custom_system_prompt=system_prompt)
```

## Snippet 9
Lines 128-134

```Python
if not resp or not resp.strip():
            result["error"] = "No response from LLM"
            log(f"[yellow]No response from LLM for: {file_path.name}[/]")
            return result

        name_prompt = (
            "Suggest a concise filename (lowercase, underscores, max 8 words) "
```

## Snippet 10
Lines 145-148

```Python
while (ideal_dir / f"{filename}_{i}{file_path.suffix}").exists():
                i += 1
            ideal_path = ideal_dir / f"{filename}_{i}{file_path.suffix}"
```

## Snippet 11
Lines 149-155

```Python
ideal_path.write_text(resp, encoding="utf-8")
        result["idealized"] = True
        result["new_path"] = str(ideal_path)
        log(f"[green]Created idealized version: {ideal_path.name}[/]")

        backup_path = backup_dir / file_path.name
```

## Snippet 12
Lines 162-168

```Python
try:
            shutil.copy2(file_path, backup_path)
            result["backed_up"] = True
            log(f"[green]Backed up original to: {backup_path.name}[/]")

            try:
                undo_log = omni_paths.get("undo_log", base_dir / "undo_log.json")
```

## Snippet 13
Lines 169-187

```Python
if undo_log.exists():
                    with open(undo_log, "r", encoding="utf-8") as ul:
                        try:
                            log_data = json.load(ul)
                        except JSONDecodeError:
                            log_data = []
                else:
                    log_data = []

                log_data.append({
                    "type": "idealize",
                    "original": str(file_path),
                    "backup": str(backup_path),
                    "idealized": str(ideal_path),
                    "timestamp": time.time()
                })

                with open(undo_log, "w", encoding="utf-8") as ul:
                    json.dump(log_data, ul, indent=2)
```

## Snippet 14
Lines 190-194

```Python
except Exception as e:
            result["error"] = f"Error backing up: {str(e)}"
            log(f"[red]Error backing up {file_path.name}: {e}[/]")

        return result
```

## Snippet 15
Lines 195-199

```Python
except Exception as e:
        result["error"] = str(e)
        log(f"[red]Error processing {file_path.name}: {e}[/]")
        return result
```

## Snippet 16
Lines 206-212

```Python
def batch_process_files(
    files: List[Path],
    omni_paths: Dict[str, Any],
    log_callback: Optional[Callable[[str], None]] = None,
    batch_size: int = 10,
    provider: Optional[str] = None
) -> Dict[str, Any]:
```

## Snippet 17
Lines 214-218

```Python
if log_callback:
            log_callback(msg)
        else:
            console.print(msg)
```

## Snippet 18
Lines 221-223

```Python
if saved_provider:
            provider = saved_provider
            log(f"[cyan]Loading provider from config: {saved_provider}[/cyan]")
```

## Snippet 19
Lines 232-238

```Python
stats = {
        "total": len(files),
        "idealized": 0,
        "backed_up": 0,
        "errors": 0
    }
```

## Snippet 20
Lines 262-267

```Python
def group_similar_files(files: List[Path]) -> List[List[Path]]:
    from difflib import SequenceMatcher

    groups = []
    used = set()
```

## Snippet 21
Lines 269-275

```Python
if file1 in used:
            continue

        group = [file1]
        used.add(file1)
        content1 = get_file_text(file1)
```

## Snippet 22
Lines 277-282

```Python
if file2 in used:
                continue

            content2 = get_file_text(file2)
            similarity = SequenceMatcher(None, content1, content2).quick_ratio()
```

## Snippet 23
Lines 283-286

```Python
if similarity > 0.7:
                group.append(file2)
                used.add(file2)
```

## Snippet 24
Lines 300-314

```Python
def process_ideal(
    file_or_dir: Path,
    recursive: bool = False,
    exclude_ext: Optional[Set[str]] = None,
    omni_paths: Optional[Dict[str, Any]] = None,
    log_callback: Optional[Callable[[str], None]] = None,
    provider: Optional[str] = None
) -> None:
    """
    Process a file or directory to create idealized versions.

    Args:
        file_or_dir: Path to file or directory to process
        recursive: If True and file_or_dir is a directory, process subdirectories
        exclude_ext: Set of extensions to exclude
```

## Snippet 25
Lines 322-325

```Python
if omni_paths is None:
        omni_paths = {}

    base_dir = omni_paths.get("base_dir", file_or_dir.parent / ".herd")
```

## Snippet 26
Lines 326-332

```Python
if isinstance(base_dir, str):
        base_dir = Path(base_dir)

    backup_dir = omni_paths.get("backup_dir", base_dir / "backup")
    ideal_dir = omni_paths.get("idealized_dir", base_dir / "idealized")
    undo_log = omni_paths.get("undo_log", base_dir / "undo_log.json")
```

## Snippet 27
Lines 338-342

```Python
if log_callback:
            log_callback(msg)
        else:
            console.print(msg)
```

## Snippet 28
Lines 345-348

```Python
if file_or_dir.suffix.lower() not in exts:
            log(f"[yellow]Skipping non-text/document file: {file_or_dir}[/]")
            return
```

## Snippet 29
Lines 349-355

```Python
if file_or_dir.suffix.lower() in exclude_ext:
            log(f"[yellow]Skipping excluded extension: {file_or_dir}[/]")
            return

        log(f"[cyan]Processing single file: {file_or_dir}[/]")
        result = process_single_file(file_or_dir, omni_paths, log_callback, provider=provider)
```

## Snippet 30
Lines 358-361

```Python
elif result["error"]:
            log(f"[red]Error processing file: {result['error']}[/]")
        return
```

## Snippet 31
Lines 378-386

```Python
log(f"[cyan]Found {len(candidates)} files for idealization[/]")

        stats = batch_process_files(candidates, omni_paths, log_callback, provider=provider)

        log(f"[cyan]Idealization Results:[/cyan]")
        log(f"[cyan]Total Files:[/cyan] [green]{stats.get('total', 0)}[/green]")
        log(f"[cyan]Idealized:[/cyan] [green]{stats.get('idealized', 0)}[/green]")
        log(f"[cyan]Backed Up:[/cyan] [green]{stats.get('backed_up', 0)}[/green]")
        log(f"[cyan]Errors:[/cyan] [green]{stats.get('errors', 0)}[/green]")
```

## Snippet 32
Lines 387-392

```Python
log(f"[bold green]Idealization complete! Processed {stats.get('total', 0)} files with {stats.get('idealized', 0)} idealizations.[/bold green]")
        log(f"[green]Idealized files saved to: {ideal_dir}[/green]")
        log(f"[green]Original files backed up to: {backup_dir}[/green]")

        return
```

## Snippet 33
Lines 401-409

```Python
def idealize_directory(
    directory: Path,
    recursive: bool = False,
    exclude_ext: Optional[Set[str]] = None,
    log_callback: Optional[Callable[[str], None]] = None,
    provider: Optional[str] = None
) -> Dict[str, Any]:
    """
    Process all text files in a directory and create idealized versions.
```

## Snippet 34
Lines 410-414

```Python
Wrapper around process_ideal for backward compatibility.
    Args:
        directory: Directory to process
        recursive: Whether to process subdirectories
        exclude_ext: Set of file extensions to exclude
```

## Snippet 35
Lines 417-429

```Python
Returns:
        Dictionary with processing statistics
    """
    result = {
        "success": False,
        "files_processed": 0,
        "files_idealized": 0,
        "output_dir": None,
        "backup_dir": None,
        "error": None
    }
    try:
        # Ensure directory is a Path object
```

## Snippet 36
Lines 433-440

```Python
if log_callback:
            log_callback(f"[bold cyan]Idealizing content in directory: {directory}[/bold cyan]")
        # Setup paths
        base_dir = directory / ".herd"
        backup_dir = base_dir / "backup"
        ideal_dir = base_dir / "idealized"
        undo_log = base_dir / "undo_log.json"
        # Ensure directories exist
```

## Snippet 37
Lines 441-449

```Python
for dir_path in [base_dir, backup_dir, ideal_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
        # Setup omni_paths
        omni_paths = {
            "base_dir": base_dir,
            "backup_dir": backup_dir,
            "idealized_dir": ideal_dir,
            "undo_log": undo_log
        }
```

## Snippet 38
Lines 453-456

```Python
if log_callback:
                log_callback(f"[red]{msg}[/red]")
            result["error"] = msg
            return result
```

## Snippet 39
Lines 471-477

```Python
if log_callback:
                log_callback(f"[yellow]{msg}[/yellow]")
            result["success"] = True
            result["message"] = msg
            result["output_dir"] = str(ideal_dir)
            result["backup_dir"] = str(backup_dir)
            return result
```

## Snippet 40
Lines 484-489

```Python
if log_callback:
            log_callback(f"[cyan]Idealization Results:[/cyan]")
            log_callback(f"[cyan]Total Files:[/cyan] [green]{stats.get('total', 0)}[/green]")
            log_callback(f"[cyan]Idealized:[/cyan] [green]{stats.get('idealized', 0)}[/green]")
            log_callback(f"[cyan]Backed Up:[/cyan] [green]{stats.get('backed_up', 0)}[/green]")
            log_callback(f"[cyan]Errors:[/cyan] [green]{stats.get('errors', 0)}[/green]")
```

## Snippet 41
Lines 493-498

```Python
result["success"] = True
        result["files_processed"] = stats.get('total', 0)
        result["files_idealized"] = stats.get('idealized', 0)
        result["output_dir"] = str(ideal_dir)
        result["backup_dir"] = str(backup_dir)
        return result
```

## Snippet 42
Lines 501-504

```Python
if log_callback:
            log_callback(f"[red]{error_msg}[/red]")
        result["error"] = error_msg
        return result
```

