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

# Try to import dotenv for .env loading. Install if necessary but don't fail if unavailable
try:
    from dotenv import load_dotenv
    # Load environment variables from .env file
    env_path = Path('.env')
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)
        print(f"Loaded environment variables from {env_path.absolute()}")
except ImportError:
    warnings.warn(
        "python-dotenv package not found. Environment variables from .env won't be loaded. "
        "Install with 'pip install python-dotenv' for .env file support.",
        ImportWarning,
        stacklevel=2
    )

console = Console()

def main():
    """
    Main entry point for the Herd AI CLI.
    Detects whether called as 'herd' or legacy 'llamacleaner' and runs accordingly.
    Now supports direct CLI flags for all main actions.
    """
    # Set up command detection
    command = Path(sys.argv[0]).stem if len(sys.argv) > 0 else ""
    is_legacy_mode = command == "llamacleaner" or "llamacleaner" in __file__
    if is_legacy_mode:
        warnings.warn(
            "The 'llamacleaner' command is deprecated and will be removed in a future version. "
            "Please use 'herd' instead.", 
            DeprecationWarning, 
            stacklevel=2
        )
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
                def log_action(*args, **kwargs): pass
                def undo_last_action(*args, **kwargs): console.print("[yellow]Undo functionality not available in legacy version[/yellow]")
                def list_undo_actions(*args, **kwargs): return []
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
                def log_action(*args, **kwargs): pass
                def undo_last_action(*args, **kwargs): console.print("[yellow]Undo functionality not available[/yellow]")
                def list_undo_actions(*args, **kwargs): return []
                
    # --- Argument Parsing ---
    parser = argparse.ArgumentParser(description="Herd AI - Document & Code Intelligence")
    parser.add_argument('--dir', '-d', type=str, default=os.getcwd(), help='Project directory (default: current directory)')
    parser.add_argument('--snippets', action='store_true', help='Extract code snippets from code files')
    parser.add_argument('--docs', action='store_true', help='Generate documentation from code files')
    parser.add_argument('--images', action='store_true', help='Process and optimize images')
    parser.add_argument('--rename', action='store_true', help='Rename files based on content analysis')
    parser.add_argument('--idealize', action='store_true', help='Rewrite or enhance content for clarity and accessibility')
    parser.add_argument('--citations', action='store_true', help='Extract and format citations from documents')
    parser.add_argument('--dedupe', action='store_true', help='Deduplicate files based on content similarity')
    parser.add_argument('--scramble', action='store_true', help='Randomize filenames for privacy/testing')
    parser.add_argument('--sample', action='store_true', help='Generate sample files for testing')
    parser.add_argument('--clear-cache', action='store_true', help='Remove cached analysis data')
    parser.add_argument('--process-all', action='store_true', help='Run all processing tasks in sequence (can choose which to include)')
    parser.add_argument('--undo', action='store_true', help='Undo the last operation')
    parser.add_argument('--gui', action='store_true', help='Launch the Herd AI GUI web application')
    parser.add_argument('--provider', type=str, choices=AI_PROVIDERS, default=DEFAULT_AI_PROVIDER,
                       help=f'AI provider to use (default: {DEFAULT_AI_PROVIDER})')
    parser.add_argument('--batch-size', type=int, default=50, help='Batch size for processing (default: 50)')
    parser.add_argument('--api-key', type=str, help='API key for selected provider (if needed)')
    parser.add_argument('--recursive', '-r', action='store_true', help='Process subdirectories recursively')
    parser.add_argument('--non-interactive', '-n', action='store_true', help='Run in non-interactive mode')
    parser.add_argument('--output', '-o', type=str, help='Output directory for processed files')
    parser.add_argument('--generate-md', action='store_true', help='Generate Markdown files for images')
    parser.add_argument('--force', action='store_true', help='Force reprocessing even if files exist')
    parser.add_argument('--exec', action='store_true', help='Launch the code executor CLI (Python/Bash sandbox)')
    args = parser.parse_args()
    
    # Update environment with API key if provided
    if args.provider == "xai" and args.api_key:
        os.environ["XAI_API_KEY"] = args.api_key
    
    root = Path(args.dir).resolve()
    
    # Handle GUI launch if requested
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
                # Two levels up (for deeply nested imports)
                Path("../..") / "herd_gui.py",
            ]
            
            gui_path = None
            for path in possible_paths:
                if path.exists():
                    gui_path = path
                    break
            
            if not gui_path:
                console.print("[bold red]Error: Could not find herd_gui.py[/bold red]")
                console.print("[yellow]Searched in the following locations:[/yellow]")
                for path in possible_paths:
                    console.print(f"  - {path.resolve()}")
                sys.exit(1)
            
            # Launch the GUI using subprocess
            console.print(f"[cyan]Found GUI at: {gui_path}[/cyan]")
            console.print(f"[cyan]Starting web server at http://localhost:4343[/cyan]")
            subprocess.run([sys.executable, str(gui_path)])
            return
        except Exception as e:
            console.print(f"[bold red]Error launching GUI: {e}[/bold red]")
            traceback.print_exc()
            sys.exit(1)
    
    # Handle undo operation if requested
    if args.undo:
        console.print(f"[cyan]Attempting to undo the last operation in {root}[/cyan]")
        undo_last_action(root)
        return
    
    # If any action flag is present, run the corresponding function(s) and exit
    ran_any = False
    
    # Process all tasks if requested
    if args.process_all:
        console.print(f"[bold cyan]Processing All Tasks for {root} using {args.provider}[/bold cyan]")
        run_process_all(root, args)
        ran_any = True
    
    # Prompt for recursive option if not explicitly set in flags
    recursive = args.recursive
    if not args.non_interactive and not args.process_all and not ran_any:
        recursive = Confirm.ask("Process subdirectories recursively?", default=True)
    
    # Confirmation helper
    def confirm_action(action_desc: str) -> bool:
        if args.non_interactive:
            return True
        return Confirm.ask(f"Proceed with {action_desc} in {root}?", default=True)

    if args.snippets:
        if confirm_action("extracting code snippets"):
            console.print(f"[cyan]Extracting code snippets from {root} using {args.provider}[/cyan]")
            process_snippets(root, recursive=recursive, exclude_ext=set(), batch_size=args.batch_size, provider=args.provider)
            ran_any = True
        else:
            console.print("[yellow]Skipped code snippet extraction.[/yellow]")
        
    if args.docs:
        if confirm_action("generating documentation"):
            console.print(f"[cyan]Generating documentation from {root} using {args.provider}[/cyan]")
            generate_docs(root, recursive=recursive, provider=args.provider)
            ran_any = True
        else:
            console.print("[yellow]Skipped documentation generation.[/yellow]")
        
    if args.images:
        if confirm_action("processing images"):
            console.print(f"[cyan]Processing images in {root} using {args.provider}[/cyan]")
            
            # Set defaults for image processing
            generate_md = args.generate_md
            force_reprocess = args.force
            rename_images = True
            override_md = True
            
            # If interactive mode, prompt for options
            if not args.non_interactive:
                generate_md = Confirm.ask("Generate Markdown documentation for each image?", default=True)
                force_reprocess = Confirm.ask("Force reprocessing even if .md or cache exists?", default=True)
                rename_images = Confirm.ask("Rename files based on content analysis?", default=True)
                override_md = Confirm.ask("Override existing markdown file check?", default=True)
            
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
        else:
            console.print("[yellow]Skipped image processing.[/yellow]")
        
    if args.rename:
        if confirm_action("renaming files"):
            console.print(f"[cyan]Renaming files in {root} using {args.provider}[/cyan]")
            process_renames(root, recursive=recursive, exclude_ext=set(), provider=args.provider)
            ran_any = True
        else:
            console.print("[yellow]Skipped file renaming.[/yellow]")
        
    if args.idealize:
        if confirm_action("idealizing content"):
            console.print(f"[cyan]Idealizing content in {root} using {args.provider}[/cyan]")
            process_ideal(root, recursive=recursive, provider=args.provider)
            ran_any = True
        else:
            console.print("[yellow]Skipped content idealization.[/yellow]")
        
    if args.citations:
        if confirm_action("extracting citations"):
            console.print(f"[cyan]Extracting citations from {root} using {args.provider}[/cyan]")
            process_file_or_directory(root, recursive=recursive, provider=args.provider)
            ran_any = True
        else:
            console.print("[yellow]Skipped citation extraction.[/yellow]")
        
    if args.dedupe:
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
        
    if args.scramble:
        if confirm_action("scrambling filenames"):
            console.print(f"[cyan]Scrambling filenames in {root}[/cyan]")
            scramble_directory(root)
            ran_any = True
        else:
            console.print("[yellow]Skipped filename scrambling.[/yellow]")
        
    if args.sample:
        if confirm_action("generating sample files"):
            console.print(f"[cyan]Generating sample files in {root}[/cyan]")
            generate_sample_files(root)
            ran_any = True
        else:
            console.print("[yellow]Skipped sample file generation.[/yellow]")
        
    if args.clear_cache:
        if confirm_action("clearing cache"):
            console.print(f"[cyan]Clearing cache in {root}[/cyan]")
            clear_cache(root)
            ran_any = True
        else:
            console.print("[yellow]Skipped cache clearing.[/yellow]")
        
    # If no action flag is present, launch the interactive CLI
    if not ran_any:
        console.print(f"Starting Herd AI from {root}")
        cli_main(str(root))

    # Handle code executor CLI if requested
    if getattr(args, 'exec', False):
        try:
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
        except Exception as e:
            console.print(f"[bold red]Error launching code executor: {e}[/bold red]")
            import traceback
            traceback.print_exc()
            sys.exit(1)

def run_process_all(root, args):
    """Run all processing tasks in sequence, allowing user to toggle which to include"""
    tasks = {
        "dedupe": {"enabled": True, "description": "Deduplicate files"},
        "rename": {"enabled": True, "description": "Rename files based on content"},
        "snippets": {"enabled": True, "description": "Extract code snippets"},
        "citations": {"enabled": True, "description": "Extract and format citations"},
        "idealize": {"enabled": True, "description": "Rewrite for clarity and accessibility"},
        "images": {"enabled": True, "description": "Process and optimize images"},
        "docs": {"enabled": True, "description": "Generate documentation"}
    }
    
    # If in interactive mode, let the user choose which tasks to run
    if not args.non_interactive:
        console.print("[bold cyan]Process All Tasks[/bold cyan]")
        console.print("Select which tasks to run:")
        
        for task_name, task_info in tasks.items():
            tasks[task_name]["enabled"] = Confirm.ask(
                f"Include {task_info['description']}?", 
                default=True
            )
    
    # Check if any tasks are enabled
    if not any(task["enabled"] for task in tasks.values()):
        console.print("[yellow]No tasks selected. Exiting process-all.[/yellow]")
        return
    
    # Prompt for recursive processing
    recursive = args.recursive
    if not args.non_interactive:
        recursive = Confirm.ask("Process subdirectories recursively?", default=True)
    
    # Confirm before running all tasks
    if not args.non_interactive:
        proceed = Confirm.ask("Proceed with the selected tasks?", default=True)
        if not proceed:
            console.print("[yellow]Process-all cancelled by user.[/yellow]")
            return
    
    # Set up undo log
    undo_log_path = root / ".herd" / "undo_log.json"
    undo_log_path.parent.mkdir(exist_ok=True, parents=True)
    
    # Run the enabled tasks
    console.print("[bold cyan]Starting comprehensive processing...[/bold cyan]")
    
    # Deduplicate first if enabled
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
    
    # Rename files if enabled
    if tasks["rename"]["enabled"]:
        console.print("[cyan]Step 2: Renaming files based on content[/cyan]")
        process_renames(root, recursive=recursive, exclude_ext=set(), provider=args.provider)
        log_action(root, "rename", {"recursive": recursive, "provider": args.provider})
    
    # Process snippets if enabled
    if tasks["snippets"]["enabled"]:
        console.print("[cyan]Step 3: Extracting code snippets[/cyan]")
        process_snippets(root, recursive=recursive, exclude_ext=set(), batch_size=args.batch_size, provider=args.provider)
        log_action(root, "snippets", {"recursive": recursive, "provider": args.provider})
    
    # Extract citations if enabled
    if tasks["citations"]["enabled"]:
        console.print("[cyan]Step 4: Extracting citations[/cyan]")
        process_file_or_directory(root, recursive=recursive, provider=args.provider)
        log_action(root, "citations", {"recursive": recursive, "provider": args.provider})
    
    # Idealize content if enabled
    if tasks["idealize"]["enabled"]:
        console.print("[cyan]Step 5: Idealizing content[/cyan]")
        process_ideal(root, recursive=recursive, provider=args.provider)
        log_action(root, "idealize", {"recursive": recursive, "provider": args.provider})
    
    # Process images if enabled
    if tasks["images"]["enabled"]:
        console.print("[cyan]Step 6: Processing images[/cyan]")
        
        # Determine options for image processing
        generate_md = True
        force_reprocess = True
        rename_images = True
        override_md = True
        
        # If interactive mode, prompt for image processing options
        if not args.non_interactive:
            generate_md = Confirm.ask("Generate Markdown documentation for each image?", default=True)
            force_reprocess = Confirm.ask("Force reprocessing even if .md or cache exists?", default=True)
            rename_images = Confirm.ask("Rename files based on content analysis?", default=True)
            override_md = Confirm.ask("Override existing markdown file check?", default=True)
        
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
    
    # Generate documentation if enabled
    if tasks["docs"]["enabled"]:
        console.print("[cyan]Step 7: Generating documentation[/cyan]")
        generate_docs(root, recursive=recursive, provider=args.provider)
        log_action(root, "docs", {"recursive": recursive, "provider": args.provider})
    
    console.print("[bold green]Comprehensive processing completed![/bold green]")
    console.print("Use 'herd --undo' to revert the last operation if needed.")

# Entry point for CLI usage
if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        console.print(f"[bold red]Error running Herd AI: {e}[/bold red]")
        console.print("\n[yellow]Detailed traceback:[/yellow]")
        traceback.print_exc()
        sys.exit(1)