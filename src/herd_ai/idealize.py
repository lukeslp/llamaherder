###############################################################################
# herd_ai/idealize.py
#
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
# Processes a single file for idealization:
# - Validates file type and content
# - Uses LLM to generate an idealized version
# - Writes the idealized file to a designated directory
# - Backs up the original file
# - Logs the operation for undo functionality
# Returns a dictionary with the result status and paths.
###############################################################################
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

    def log(msg: str) -> None:
        if log_callback:
            log_callback(msg)
        else:
            console.print(msg)
    
    if provider is None and herd_config:
        saved_provider = herd_config.get_provider()
        if saved_provider:
            provider = saved_provider
            log(f"[cyan]Loading provider from config: {saved_provider}[/cyan]")
    provider = provider or DEFAULT_AI_PROVIDER
    
    log(f"[bold cyan]Using AI provider: {provider}[/bold cyan]")

    try:
        base_dir = omni_paths.get("base_dir", file_path.parent / ".herd")
        backup_dir = omni_paths.get("backup_dir", base_dir / "backup")
        ideal_dir = omni_paths.get("idealized_dir", base_dir / "idealized")
        backup_dir.mkdir(parents=True, exist_ok=True)
        ideal_dir.mkdir(parents=True, exist_ok=True)

        exts = TEXT_EXTENSIONS.union(DOCUMENT_EXTENSIONS)
        if file_path.suffix.lower() not in exts:
            result["error"] = "Unsupported file type"
            log(f"[yellow]Skipping non-text/document file: {file_path}[/]")
            return result

        content = get_file_text(file_path)
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

        if not resp or not resp.strip():
            result["error"] = "No response from LLM"
            log(f"[yellow]No response from LLM for: {file_path.name}[/]")
            return result

        name_prompt = (
            "Suggest a concise filename (lowercase, underscores, max 8 words) "
            "for the following idealized content. Exclude any extension:\n\n"
            f"{resp[:1000] if len(resp) > 1000 else resp}"
        )

        name_raw = process_with_ai(file_path, name_prompt, provider=provider)
        filename = clean_filename(name_raw) if name_raw else f"ideal_{file_path.stem}"
        ideal_path = ideal_dir / f"{filename}{file_path.suffix}"

        if ideal_path.exists():
            i = 1
            while (ideal_dir / f"{filename}_{i}{file_path.suffix}").exists():
                i += 1
            ideal_path = ideal_dir / f"{filename}_{i}{file_path.suffix}"

        ideal_path.write_text(resp, encoding="utf-8")
        result["idealized"] = True
        result["new_path"] = str(ideal_path)
        log(f"[green]Created idealized version: {ideal_path.name}[/]")

        backup_path = backup_dir / file_path.name

        if backup_path.exists():
            i = 1
            while backup_path.with_suffix(f".bak{i}{backup_path.suffix}").exists():
                i += 1
            backup_path = backup_path.with_suffix(f".bak{i}{backup_path.suffix}")

        try:
            shutil.copy2(file_path, backup_path)
            result["backed_up"] = True
            log(f"[green]Backed up original to: {backup_path.name}[/]")

            try:
                undo_log = omni_paths.get("undo_log", base_dir / "undo_log.json")
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
            except Exception as e:
                log(f"[yellow]Warning: Could not log action: {e}[/]")
        except Exception as e:
            result["error"] = f"Error backing up: {str(e)}"
            log(f"[red]Error backing up {file_path.name}: {e}[/]")

        return result
    except Exception as e:
        result["error"] = str(e)
        log(f"[red]Error processing {file_path.name}: {e}[/]")
        return result

###############################################################################
# batch_process_files
#
# Processes a list of files in batches for idealization. Tracks statistics
# for total, idealized, backed up, and error counts. Uses process_single_file.
###############################################################################
def batch_process_files(
    files: List[Path],
    omni_paths: Dict[str, Any],
    log_callback: Optional[Callable[[str], None]] = None,
    batch_size: int = 10,
    provider: Optional[str] = None
) -> Dict[str, Any]:
    def log(msg: str) -> None:
        if log_callback:
            log_callback(msg)
        else:
            console.print(msg)

    if provider is None and herd_config:
        saved_provider = herd_config.get_provider()
        if saved_provider:
            provider = saved_provider
            log(f"[cyan]Loading provider from config: {saved_provider}[/cyan]")
    provider = provider or DEFAULT_AI_PROVIDER
    
    log(f"[bold cyan]Using AI provider: {provider}[/bold cyan]")

    if not files:
        log("[yellow]No files to process for idealization.[/]")
        return {"total": 0, "idealized": 0, "errors": 0}

    stats = {
        "total": len(files),
        "idealized": 0,
        "backed_up": 0,
        "errors": 0
    }

    batches = [files[i:i+batch_size] for i in range(0, len(files), batch_size)]
    log(f"[cyan]Processing {len(files)} files in {len(batches)} batches[/]")

    for batch_idx, batch in enumerate(batches, 1):
        log(f"[cyan]Processing batch {batch_idx}/{len(batches)} ({len(batch)} files)[/]")
        for file_idx, file_path in enumerate(batch, 1):
            log(f"[cyan]Processing file {file_idx}/{len(batch)} in batch {batch_idx}: {file_path.name}[/]")
            result = process_single_file(file_path, omni_paths, log_callback, provider=provider)
            if result["idealized"]:
                stats["idealized"] += 1
            if result["backed_up"]:
                stats["backed_up"] += 1
            if result["error"]:
                stats["errors"] += 1

    return stats

###############################################################################
# group_similar_files
#
# Groups files by content similarity using difflib's SequenceMatcher.
# Returns a list of groups, each group being a list of Path objects.
###############################################################################
def group_similar_files(files: List[Path]) -> List[List[Path]]:
    from difflib import SequenceMatcher

    groups = []
    used = set()

    for i, file1 in enumerate(files):
        if file1 in used:
            continue

        group = [file1]
        used.add(file1)
        content1 = get_file_text(file1)

        for file2 in files[i+1:]:
            if file2 in used:
                continue

            content2 = get_file_text(file2)
            similarity = SequenceMatcher(None, content1, content2).quick_ratio()

            if similarity > 0.7:
                group.append(file2)
                used.add(file2)

        if len(group) >= 1:
            groups.append(group)

    return groups

###############################################################################
# process_ideal
#
# Main entry point for idealization. Handles both files and directories:
# - For files: processes directly if supported
# - For directories: finds candidate files, processes in batches, and reports
#   statistics. Handles recursive search and extension exclusion.
###############################################################################
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
        omni_paths: Dictionary of relevant paths for the operation
        log_callback: Optional function to log messages
        provider: AI provider to use (e.g., "ollama", "xai", "gemini")
    """
    if exclude_ext is None:
        exclude_ext = set()

    if omni_paths is None:
        omni_paths = {}

    base_dir = omni_paths.get("base_dir", file_or_dir.parent / ".herd")
    if isinstance(base_dir, str):
        base_dir = Path(base_dir)

    backup_dir = omni_paths.get("backup_dir", base_dir / "backup")
    ideal_dir = omni_paths.get("idealized_dir", base_dir / "idealized")
    undo_log = omni_paths.get("undo_log", base_dir / "undo_log.json")

    for dir_path in [base_dir, backup_dir, ideal_dir]:
        if isinstance(dir_path, Path):
            dir_path.mkdir(parents=True, exist_ok=True)

    def log(msg: str) -> None:
        if log_callback:
            log_callback(msg)
        else:
            console.print(msg)

    if file_or_dir.is_file():
        exts = TEXT_EXTENSIONS.union(DOCUMENT_EXTENSIONS)
        if file_or_dir.suffix.lower() not in exts:
            log(f"[yellow]Skipping non-text/document file: {file_or_dir}[/]")
            return

        if file_or_dir.suffix.lower() in exclude_ext:
            log(f"[yellow]Skipping excluded extension: {file_or_dir}[/]")
            return

        log(f"[cyan]Processing single file: {file_or_dir}[/]")
        result = process_single_file(file_or_dir, omni_paths, log_callback, provider=provider)

        if result["idealized"]:
            log(f"[green]Created idealized version at {result['new_path']}[/]")
        elif result["error"]:
            log(f"[red]Error processing file: {result['error']}[/]")
        return

    if file_or_dir.is_dir():
        log(f"[bold cyan]Starting Idealization on directory: {file_or_dir}[/bold cyan]")

        exts = TEXT_EXTENSIONS.union(DOCUMENT_EXTENSIONS)
        walker = file_or_dir.rglob('*') if recursive else file_or_dir.glob('*')
        candidates = [
            p for p in walker 
            if p.is_file() 
            and p.suffix.lower() in exts
            and p.suffix.lower() not in exclude_ext
        ]

        if not candidates:
            log("[yellow]No files found for idealization.[/]")
            return

        log(f"[cyan]Found {len(candidates)} files for idealization[/]")

        stats = batch_process_files(candidates, omni_paths, log_callback, provider=provider)

        log(f"[cyan]Idealization Results:[/cyan]")
        log(f"[cyan]Total Files:[/cyan] [green]{stats.get('total', 0)}[/green]")
        log(f"[cyan]Idealized:[/cyan] [green]{stats.get('idealized', 0)}[/green]")
        log(f"[cyan]Backed Up:[/cyan] [green]{stats.get('backed_up', 0)}[/green]")
        log(f"[cyan]Errors:[/cyan] [green]{stats.get('errors', 0)}[/green]")
        log(f"[bold green]Idealization complete! Processed {stats.get('total', 0)} files with {stats.get('idealized', 0)} idealizations.[/bold green]")
        log(f"[green]Idealized files saved to: {ideal_dir}[/green]")
        log(f"[green]Original files backed up to: {backup_dir}[/green]")

        return

    log(f"[red]Not a file or directory: {file_or_dir}[/]")

###############################################################################
# idealize_directory
#
# Wrapper function for backward compatibility with CLI module.
# Processes all text files in a directory and creates idealized versions.
###############################################################################
def idealize_directory(
    directory: Path,
    recursive: bool = False,
    exclude_ext: Optional[Set[str]] = None,
    log_callback: Optional[Callable[[str], None]] = None,
    provider: Optional[str] = None
) -> Dict[str, Any]:
    """
    Process all text files in a directory and create idealized versions.
    Wrapper around process_ideal for backward compatibility.
    Args:
        directory: Directory to process
        recursive: Whether to process subdirectories
        exclude_ext: Set of file extensions to exclude
        log_callback: Optional callback for logging
        provider: AI provider to use
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
        if isinstance(directory, str):
            directory = Path(directory)
        # Log the start of processing
        if log_callback:
            log_callback(f"[bold cyan]Idealizing content in directory: {directory}[/bold cyan]")
        # Setup paths
        base_dir = directory / ".herd"
        backup_dir = base_dir / "backup"
        ideal_dir = base_dir / "idealized"
        undo_log = base_dir / "undo_log.json"
        # Ensure directories exist
        for dir_path in [base_dir, backup_dir, ideal_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
        # Setup omni_paths
        omni_paths = {
            "base_dir": base_dir,
            "backup_dir": backup_dir,
            "idealized_dir": ideal_dir,
            "undo_log": undo_log
        }
        # Check if directory exists
        if not directory.exists():
            msg = f"Directory not found: {directory}"
            if log_callback:
                log_callback(f"[red]{msg}[/red]")
            result["error"] = msg
            return result
        # Find candidate files
        exts = TEXT_EXTENSIONS.union(DOCUMENT_EXTENSIONS)
        walker = directory.rglob('*') if recursive else directory.glob('*')
        candidates = [
            p for p in walker 
            if p.is_file() 
            and p.suffix.lower() in exts
            and (exclude_ext is None or p.suffix.lower() not in exclude_ext)
            and not p.name.startswith('.')
            and not any(part.startswith('.') for part in p.parts)
        ]
        # Check if any files were found
        if not candidates:
            msg = "No files found for idealization"
            if log_callback:
                log_callback(f"[yellow]{msg}[/yellow]")
            result["success"] = True
            result["message"] = msg
            result["output_dir"] = str(ideal_dir)
            result["backup_dir"] = str(backup_dir)
            return result
        # Log the number of files found
        if log_callback:
            log_callback(f"[cyan]Found {len(candidates)} files for idealization[/cyan]")
        # Process the files
        stats = batch_process_files(candidates, omni_paths, log_callback, provider=provider)
        # Generate table for console output
        if log_callback:
            log_callback(f"[cyan]Idealization Results:[/cyan]")
            log_callback(f"[cyan]Total Files:[/cyan] [green]{stats.get('total', 0)}[/green]")
            log_callback(f"[cyan]Idealized:[/cyan] [green]{stats.get('idealized', 0)}[/green]")
            log_callback(f"[cyan]Backed Up:[/cyan] [green]{stats.get('backed_up', 0)}[/green]")
            log_callback(f"[cyan]Errors:[/cyan] [green]{stats.get('errors', 0)}[/green]")
            log_callback(f"[bold green]Idealization complete! Processed {stats.get('total', 0)} files with {stats.get('idealized', 0)} idealizations.[/bold green]")
            log_callback(f"[green]Idealized files saved to: {ideal_dir}[/green]")
            log_callback(f"[green]Original files backed up to: {backup_dir}[/green]")
        result["success"] = True
        result["files_processed"] = stats.get('total', 0)
        result["files_idealized"] = stats.get('idealized', 0)
        result["output_dir"] = str(ideal_dir)
        result["backup_dir"] = str(backup_dir)
        return result
    except Exception as e:
        error_msg = f"Error in idealize_directory: {str(e)}"
        if log_callback:
            log_callback(f"[red]{error_msg}[/red]")
        result["error"] = error_msg
        return result 