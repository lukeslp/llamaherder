# Code Snippets from src/herd_ai/herd.py

File: `src/herd_ai/herd.py`  
Language: Python  
Extracted: 2025-06-07 05:09:30  

## Snippet 1
Lines 1-45

```Python
#!/usr/bin/env python3
"""
Herd AI - Document Analysis & Code Management Tools

A unified toolset that lets you:
  - Batch-rename files using AI based on content
  - Extract and consolidate the most important code snippets
  - Generate project documentation summaries
  - Extract citations and build a bibliography
  - Analyze and summarize local documents
  - Process and optimize images with accessibility features
  - Deduplicate files based on content similarity
  - Process all tasks in one comprehensive operation

Usage examples:
  herd --dir /path/to/project --rename
  herd --dir /path/to/project --snippets --batch-size 10
  herd --dir /path/to/project --docs
  herd --dir /path/to/project --cite
  herd --dir /path/to/project --analyze
  herd --dir /path/to/project --stats --export-summary
  herd --dir /path/to/project --images
  herd --dir /path/to/project --dedupe
  herd --dir /path/to/project --clear-cache
  herd --dir /path/to/project --provider xai --images
  herd --dir /path/to/project --process-all
  herd --dir /path/to/project --undo
  herd --gui
  herd --exec
"""

# This file provides backward compatibility and the new CLI entry point.
# It imports and uses the refactored, modular implementation.

import sys
import os
import json
from pathlib import Path
import warnings
import traceback
import argparse
import subprocess
from rich.prompt import Prompt, Confirm
from rich.console import Console
```

## Snippet 2
Lines 46-50

```Python
# Try to import dotenv for .env loading. Install if necessary but don't fail if unavailable
try:
    from dotenv import load_dotenv
    # Load environment variables from .env file
    env_path = Path('.env')
```

## Snippet 3
Lines 54-56

```Python
except ImportError:
    warnings.warn(
        "python-dotenv package not found. Environment variables from .env won't be loaded. "
```

## Snippet 4
Lines 73-79

```Python
if is_legacy_mode:
        warnings.warn(
            "The 'llamacleaner' command is deprecated and will be removed in a future version. "
            "Please use 'herd' instead.",
            DeprecationWarning,
            stacklevel=2
        )
```

## Snippet 5
Lines 80-117

```Python
# Add the parent directory to sys.path for direct imports
    current_dir = Path(__file__).parent.resolve()
    parent_dir = current_dir.parent.resolve()
    sys.path.insert(0, str(parent_dir))
    sys.path.insert(0, str(current_dir))
    os.environ['PYTHONPATH'] = str(parent_dir) + os.pathsep + str(current_dir) + os.pathsep + os.environ.get('PYTHONPATH', '')
    # Import CLI entry points
    try:
        from herd_ai.cli import main as cli_main
        from herd_ai.snippets import process_snippets
        from herd_ai.rename import process_renames
        from herd_ai.idealize import process_ideal
        from herd_ai.docs import generate_docs
        from herd_ai.citations import process_file_or_directory
        from herd_ai.image_processor import process_images_cli, process_directory as process_images
        from herd_ai.utils.scrambler import scramble_directory, generate_sample_files
        from herd_ai.utils.cache import clear_cache
        from herd_ai.utils.dedupe import dedupe_files
        from herd_ai.config import AI_PROVIDERS, DEFAULT_AI_PROVIDER
        from herd_ai.utils.undo_log import log_action, undo_last_action, list_undo_actions
    except ImportError:
        try:
            # Fallback to llamacleaner legacy imports
            from llamacleaner.cli import main as cli_main
            from llamacleaner.snippets import process_snippets
            from llamacleaner.rename import process_renames
            from llamacleaner.idealize import process_ideal
            from llamacleaner.docs import generate_docs
            from llamacleaner.citations import process_file_or_directory
            from llamacleaner.image_processor import process_images_cli, process_directory as process_images
            from llamacleaner.utils.scrambler import scramble_directory, generate_sample_files
            from llamacleaner.utils.cache import clear_cache
            from llamacleaner.utils.dedupe import dedupe_files
            from llamacleaner.config import AI_PROVIDERS, DEFAULT_AI_PROVIDER
            # Fallback - undo log might not exist in legacy version
            try:
                from llamacleaner.utils.undo_log import log_action, undo_last_action, list_undo_actions
            except ImportError:
```

## Snippet 6
Lines 121-138

```Python
except ImportError:
            # Final fallback to direct relative imports
            sys.path.insert(0, str(current_dir.parent.parent))
            from herd_ai.cli import main as cli_main
            from herd_ai.snippets import process_snippets
            from herd_ai.rename import process_renames
            from herd_ai.idealize import process_ideal
            from herd_ai.docs import generate_docs
            from herd_ai.citations import process_file_or_directory
            from herd_ai.image_processor import process_images_cli, process_directory as process_images
            from herd_ai.utils.scrambler import scramble_directory, generate_sample_files
            from herd_ai.utils.cache import clear_cache
            from herd_ai.utils.dedupe import dedupe_files
            from herd_ai.config import AI_PROVIDERS, DEFAULT_AI_PROVIDER
            # Fallback - undo log might not exist in direct imports
            try:
                from herd_ai.utils.undo_log import log_action, undo_last_action, list_undo_actions
            except ImportError:
```

## Snippet 7
Lines 143-149

```Python
# --- Argument Parsing ---
    parser = argparse.ArgumentParser(description="Herd AI - Document & Code Intelligence")
    parser.add_argument('--dir', '-d', type=str, default=os.getcwd(), help='Project directory (default: current directory)')
    parser.add_argument('--snippets', action='store_true', help='Extract code snippets from code files')
    parser.add_argument('--docs', action='store_true', help='Generate documentation from code files')
    parser.add_argument('--images', action='store_true', help='Process and optimize images')
    parser.add_argument('--rename', action='store_true', help='Rename files based on content analysis')
```

## Snippet 8
Lines 150-152

```Python
parser.add_argument('--idealize', action='store_true', help='Rewrite or enhance content for clarity and accessibility')
    parser.add_argument('--citations', action='store_true', help='Extract and format citations from documents')
    parser.add_argument('--dedupe', action='store_true', help='Deduplicate files based on content similarity')
```

## Snippet 9
Lines 154-160

```Python
parser.add_argument('--sample', action='store_true', help='Generate sample files for testing')
    parser.add_argument('--clear-cache', action='store_true', help='Remove cached analysis data')
    parser.add_argument('--process-all', action='store_true', help='Run all processing tasks in sequence (can choose which to include)')
    parser.add_argument('--undo', action='store_true', help='Undo the last operation')
    parser.add_argument('--gui', action='store_true', help='Launch the Herd AI GUI web application')
    parser.add_argument('--provider', type=str, choices=AI_PROVIDERS, default=DEFAULT_AI_PROVIDER,
                       help=f'AI provider to use (default: {DEFAULT_AI_PROVIDER})')
```

## Snippet 10
Lines 172-176

```Python
if args.provider == "xai" and args.api_key:
        os.environ["XAI_API_KEY"] = args.api_key

    root = Path(args.dir).resolve()
```

## Snippet 11
Lines 178-191

```Python
if args.gui:
        try:
            console.print("[bold cyan]Launching Herd AI GUI[/bold cyan]")

            # Try multiple possible paths to find herd_gui.py
            possible_paths = [
                # Path relative to workspace root
                Path(root) / "herd_gui.py",
                # Path relative to the herd.py file location
                Path(__file__).resolve().parent.parent.parent / "herd_gui.py",
                # Direct path from current directory
                Path("herd_gui.py"),
                # One level up
                Path("..") / "herd_gui.py",
```

## Snippet 12
Lines 202-204

```Python
if not gui_path:
                console.print("[bold red]Error: Could not find herd_gui.py[/bold red]")
                console.print("[yellow]Searched in the following locations:[/yellow]")
```

## Snippet 13
Lines 205-208

```Python
for path in possible_paths:
                    console.print(f"  - {path.resolve()}")
                sys.exit(1)
```

## Snippet 14
Lines 209-213

```Python
# Launch the GUI using subprocess
            console.print(f"[cyan]Found GUI at: {gui_path}[/cyan]")
            console.print(f"[cyan]Starting web server at http://localhost:4343[/cyan]")
            subprocess.run([sys.executable, str(gui_path)])
            return
```

## Snippet 15
Lines 214-218

```Python
except Exception as e:
            console.print(f"[bold red]Error launching GUI: {e}[/bold red]")
            traceback.print_exc()
            sys.exit(1)
```

## Snippet 16
Lines 220-227

```Python
if args.undo:
        console.print(f"[cyan]Attempting to undo the last operation in {root}[/cyan]")
        undo_last_action(root)
        return

    # If any action flag is present, run the corresponding function(s) and exit
    ran_any = False
```

## Snippet 17
Lines 236-239

```Python
if not args.non_interactive and not args.process_all and not ran_any:
        recursive = Confirm.ask("Process subdirectories recursively?", default=True)

    # Confirmation helper
```

## Snippet 18
Lines 265-270

```Python
# Set defaults for image processing
            generate_md = args.generate_md
            force_reprocess = args.force
            rename_images = True
            override_md = True
```

## Snippet 19
Lines 278-287

```Python
# Process images with user preferences
            process_images_cli(
                root,
                recursive=recursive,
                force=force_reprocess,
                rename=rename_images,
                override_md=override_md,
                provider=args.provider
            )
            ran_any = True
```

## Snippet 20
Lines 316-330

```Python
if confirm_action("deduplicating files"):
            interactive = not args.non_interactive
            console.print(f"[cyan]Deduplicating files in {root}[/cyan]")
            dedupe_files(
                directory=root,
                recursive=recursive,
                interactive=interactive,
                delete_duplicates=False,  # Always ask the user first in CLI mode
                merge_similar=False,      # Always ask the user first in CLI mode
                output_dir=args.output
            )
            ran_any = True
        else:
            console.print("[yellow]Skipped deduplication.[/yellow]")
```

## Snippet 21
Lines 332-338

```Python
if confirm_action("scrambling filenames"):
            console.print(f"[cyan]Scrambling filenames in {root}[/cyan]")
            scramble_directory(root)
            ran_any = True
        else:
            console.print("[yellow]Skipped filename scrambling.[/yellow]")
```

## Snippet 22
Lines 340-346

```Python
if confirm_action("generating sample files"):
            console.print(f"[cyan]Generating sample files in {root}[/cyan]")
            generate_sample_files(root)
            ran_any = True
        else:
            console.print("[yellow]Skipped sample file generation.[/yellow]")
```

## Snippet 23
Lines 348-354

```Python
if confirm_action("clearing cache"):
            console.print(f"[cyan]Clearing cache in {root}[/cyan]")
            clear_cache(root)
            ran_any = True
        else:
            console.print("[yellow]Skipped cache clearing.[/yellow]")
```

## Snippet 24
Lines 356-359

```Python
if not ran_any:
        console.print(f"Starting Herd AI from {root}")
        cli_main(str(root))
```

## Snippet 25
Lines 363-374

```Python
# Robust import for code_executor
            try:
                from herd_ai.utils.code_executor import interactive_cli
            except ImportError:
                try:
                    from llamacleaner.code_executor import interactive_cli
                except ImportError:
                    from herd_ai.utils.code_executor import interactive_cli
            import asyncio
            console.print("[bold cyan]Launching Code Executor CLI...[/bold cyan]")
            asyncio.run(interactive_cli())
            return
```

## Snippet 26
Lines 375-380

```Python
except Exception as e:
            console.print(f"[bold red]Error launching code executor: {e}[/bold red]")
            import traceback
            traceback.print_exc()
            sys.exit(1)
```

## Snippet 27
Lines 381-387

```Python
def run_process_all(root, args):
    """Run all processing tasks in sequence, allowing user to toggle which to include"""
    tasks = {
        "dedupe": {"enabled": True, "description": "Deduplicate files"},
        "rename": {"enabled": True, "description": "Rename files based on content"},
        "snippets": {"enabled": True, "description": "Extract code snippets"},
        "citations": {"enabled": True, "description": "Extract and format citations"},
```

## Snippet 28
Lines 394-397

```Python
if not args.non_interactive:
        console.print("[bold cyan]Process All Tasks[/bold cyan]")
        console.print("Select which tasks to run:")
```

## Snippet 29
Lines 398-403

```Python
for task_name, task_info in tasks.items():
            tasks[task_name]["enabled"] = Confirm.ask(
                f"Include {task_info['description']}?",
                default=True
            )
```

## Snippet 30
Lines 405-408

```Python
if not any(task["enabled"] for task in tasks.values()):
        console.print("[yellow]No tasks selected. Exiting process-all.[/yellow]")
        return
```

## Snippet 31
Lines 411-414

```Python
if not args.non_interactive:
        recursive = Confirm.ask("Process subdirectories recursively?", default=True)

    # Confirm before running all tasks
```

## Snippet 32
Lines 417-420

```Python
if not proceed:
            console.print("[yellow]Process-all cancelled by user.[/yellow]")
            return
```

## Snippet 33
Lines 421-427

```Python
# Set up undo log
    undo_log_path = root / ".herd" / "undo_log.json"
    undo_log_path.parent.mkdir(exist_ok=True, parents=True)

    # Run the enabled tasks
    console.print("[bold cyan]Starting comprehensive processing...[/bold cyan]")
```

## Snippet 34
Lines 429-441

```Python
if tasks["dedupe"]["enabled"]:
        console.print("[cyan]Step 1: Deduplicating files[/cyan]")
        interactive = not args.non_interactive
        dedupe_files(
            directory=root,
            recursive=recursive,
            interactive=interactive,
            delete_duplicates=False,
            merge_similar=False,
            output_dir=args.output
        )
        log_action(root, "dedupe", {"recursive": recursive})
```

## Snippet 35
Lines 443-447

```Python
if tasks["rename"]["enabled"]:
        console.print("[cyan]Step 2: Renaming files based on content[/cyan]")
        process_renames(root, recursive=recursive, exclude_ext=set(), provider=args.provider)
        log_action(root, "rename", {"recursive": recursive, "provider": args.provider})
```

## Snippet 36
Lines 449-453

```Python
if tasks["snippets"]["enabled"]:
        console.print("[cyan]Step 3: Extracting code snippets[/cyan]")
        process_snippets(root, recursive=recursive, exclude_ext=set(), batch_size=args.batch_size, provider=args.provider)
        log_action(root, "snippets", {"recursive": recursive, "provider": args.provider})
```

## Snippet 37
Lines 455-459

```Python
if tasks["citations"]["enabled"]:
        console.print("[cyan]Step 4: Extracting citations[/cyan]")
        process_file_or_directory(root, recursive=recursive, provider=args.provider)
        log_action(root, "citations", {"recursive": recursive, "provider": args.provider})
```

## Snippet 38
Lines 461-465

```Python
if tasks["idealize"]["enabled"]:
        console.print("[cyan]Step 5: Idealizing content[/cyan]")
        process_ideal(root, recursive=recursive, provider=args.provider)
        log_action(root, "idealize", {"recursive": recursive, "provider": args.provider})
```

## Snippet 39
Lines 470-475

```Python
# Determine options for image processing
        generate_md = True
        force_reprocess = True
        rename_images = True
        override_md = True
```

## Snippet 40
Lines 483-500

```Python
# Process images with appropriate options
        process_images_cli(
            root,
            recursive=recursive,
            force=force_reprocess,
            rename=rename_images,
            override_md=override_md,
            provider=args.provider
        )
        log_action(root, "images", {
            "recursive": recursive,
            "provider": args.provider,
            "generate_md": generate_md,
            "force": force_reprocess,
            "rename": rename_images,
            "override_md": override_md
        })
```

## Snippet 41
Lines 502-507

```Python
if tasks["docs"]["enabled"]:
        console.print("[cyan]Step 7: Generating documentation[/cyan]")
        generate_docs(root, recursive=recursive, provider=args.provider)
        log_action(root, "docs", {"recursive": recursive, "provider": args.provider})

    console.print("[bold green]Comprehensive processing completed![/bold green]")
```

## Snippet 42
Lines 511-518

```Python
if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        console.print(f"[bold red]Error running Herd AI: {e}[/bold red]")
        console.print("\n[yellow]Detailed traceback:[/yellow]")
        traceback.print_exc()
        sys.exit(1)
```

