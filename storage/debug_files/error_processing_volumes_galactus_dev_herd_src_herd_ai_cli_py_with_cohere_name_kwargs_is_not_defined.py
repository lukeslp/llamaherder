# =============================================================================
# Herd AI - CLI Module
#
# This module provides the command line interface for the entire suite of 
# Herd AI tools. It handles command parsing, user interaction, and delegates
# to the appropriate module for each operation.
# =============================================================================

import os
import sys
import time
import json
from pathlib import Path
import argparse
import logging
from rich.console import Console
from rich.panel import Panel
from rich.layout import Layout
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, MofNCompleteColumn, TimeRemainingColumn
from rich.prompt import Prompt, IntPrompt
from rich.live import Live
from rich import box
from rich.align import Align
from rich.text import Text
from rich.padding import Padding
from rich.style import Style
from rich.columns import Columns
import re
from rich.console import Group
import subprocess
import traceback

# For arrow key navigation
try:
    import readchar
    HAS_READCHAR = True
except ImportError:
    HAS_READCHAR = False

# Configure logging
logger = logging.getLogger(__name__)
console = Console()

# =============================================================================
# Import configuration and utility functions
# =============================================================================
try:
    from herd_ai.utils.file import (
        get_file_text, 
        is_ignored_file, 
        read_project_stats,
        get_file_extension,
        read_alt_text,
        write_alt_text,
        get_file_count_by_type
    )
    from herd_ai.utils.ai_provider import (
        process_with_ai, 
        process_image, 
        validate_provider, 
        check_local_provider,
        list_models
    )
    from herd_ai.utils.scrambler import scramble_directory, generate_sample_files
    from herd_ai.utils.dedupe import dedupe_files
    from herd_ai.rename import process_renames
    from herd_ai.citations import process_directory as process_citations
    from herd_ai.snippets import (
        process_directory as process_snippets,
        search_snippets,
        export_snippets,
        import_snippet,
        list_snippet_formats
    )
    from herd_ai.idealize import idealize_directory
    from herd_ai.docs import generate_docs, export_document_summary
    from herd_ai.config import AI_PROVIDERS, DEFAULT_AI_PROVIDER, OLLAMA_TEXT_MODEL
    from herd_ai.utils import config as herd_config
    from herd_ai.image_processor import (
        process_directory as process_images,
        batch_extract_alt_text,
        list_alt_text_formats
    )
    from herd_ai.herd import run_process_all
    from herd_ai.utils.undo_log import undo_last_action
except Exception as e:
    print(f"Error importing modules: {e}")
    print("Make sure you're running from the project directory or the package is installed.")
    sys.exit(1)

# --- Create a pre-rendered version of the banner to avoid formatting issues ---
HERD_LOGO = """
                            ██╗  ██╗███████╗██████╗ ██████╗  
                            ██║  ██║██╔════╝██╔══██╗██╔══██╗ 
                            ███████║█████╗  ██████╔╝██║  ██║ 
                            ██╔══██║██╔══╝  ██╔══██╗██║  ██║  
                            ██║  ██║███████╗██║  ██║██████╔╝  
                            ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═════╝     
            ,   #                                                     _
            (\\_(^>                            _.                    >(')__,
            (_(__)           ||          _.||~~ {^--^}.-._._.---.__.-;(_~_/
                ||   (^..^)   ||  (\\(__)/)  ||   {6 6 }.')' (. )' ).-`  ||
            __||____(oo)____||___`(QQ)'___||___( v  )._('.) ( .' )____||__
            --||----"- "----||----)  (----||----`-.''(.' .( ' ) .)----||--
            __||__@(    )___||___(o  o)___||______#`(.'( . ( (',)_____||__
            --||----"--"----||----`--'----||-------'\\_.).(_.). )------||--
                ||            ||       `||~|||~~|""||  `W W    W W      ||
            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  
                    Document & Code Intelligence v0.7

"""

# Styling constants - Enhanced with more vivid colors
STYLES = {
    "header": Style(color="bright_green", bold=True),
    "subheader": Style(color="magenta", italic=True),
    "success": Style(color="bright_green", bold=True),
    "error": Style(color="bright_red", bold=True),
    "warning": Style(color="yellow", bold=True),
    "info": Style(color="bright_blue"),
    "highlight": Style(color="bright_cyan", bold=True, underline=True),
    "dim": Style(color="grey70", italic=True),
    "action": Style(color="bright_magenta", bold=True),
    "progress": Style(color="bright_green"),
    "menu_selected": Style(color="bright_green", bold=True, reverse=True),
    "menu_unselected": Style(color="bright_cyan"),
    "button": Style(color="white", bgcolor="blue", bold=True),
    "title": Style(color="bright_yellow", bold=True),
    "panel_border": Style(color="bright_blue"),
}

def get_config_module():
    """Get the config module using the same import pattern as above"""
    try:
        try:
            from herd_ai import config
            return config
        except ImportError:
            try:
                from llamacleaner import config
                return config
            except ImportError:
                import config
                return config
    except Exception as e:
        print(f"Error importing config module: {e}")
        sys.exit(1)

def setup_paths(root: Path, omni_paths=None):
    """Configure paths for the LlamaCleaner operations"""
    if omni_paths is None:
        omni_paths = {}
    
    # Create .herd in the target directory
    base_dir = root / ".herd"
    base_dir.mkdir(exist_ok=True)
    
    # Set base_dir in omni_paths if not already present
    if "base_dir" not in omni_paths:
        omni_paths["base_dir"] = base_dir
    
    # Create required directories if they don't exist in omni_paths
    dir_paths = {
        "backup_dir": "backup",
        "snippets_dir": "snippets",
        "idealized_dir": "idealized",
        "citations_dir": "citations",
        "cache_dir": "cache",
        "images_dir": "images",
        "analysis_dir": "analysis"
    }
    
    # Ensure all directories exist
    for key, subdir in dir_paths.items():
        if key not in omni_paths:
            omni_paths[key] = base_dir / subdir
        
        # Convert string paths to Path objects
        if isinstance(omni_paths[key], str):
            omni_paths[key] = Path(omni_paths[key])
            
        # Create directory
        omni_paths[key].mkdir(exist_ok=True, parents=True)
        logger.debug(f"Created directory: {omni_paths[key]}")
    
    # Set up file paths
    file_paths = {
        "log": "log.txt",
        "undo_log": "undo_log.json",
        "citations_md": "citations.md",
        "citations_bib": "citations.bib",
        "api_creds": "api_credentials.txt"
    }
    
    # Create files if they don't exist
    for key, filename in file_paths.items():
        if key not in omni_paths:
            omni_paths[key] = base_dir / filename
        
        # Convert string paths to Path objects
        if isinstance(omni_paths[key], str):
            omni_paths[key] = Path(omni_paths[key])
            
        # Make sure parent directory exists
        omni_paths[key].parent.mkdir(exist_ok=True, parents=True)
        
        # Touch the file to create it if it doesn't exist
        if not omni_paths[key].exists():
            omni_paths[key].touch()
    
    return file_paths, omni_paths

def clear_cache(directory: Path = None):
    """
    Clear the cache directory for the specified project path.
    
    Args:
        directory: The project root directory. Cache will be cleaned from .herd/cache
    
    Returns:
        Dictionary with operation results
    """
    if directory is None:
        directory = Path.cwd()
    
    # Set up paths to ensure the cache directory exists
    _, paths = setup_paths(directory)
    cache_dir = paths["cache_dir"]  # Get cache_dir from omni_paths
    
    # Count files before deletion for reporting
    files_removed = 0
    space_saved = 0
    
    try:
        # Get size information before deletion
        for file in cache_dir.glob("**/*"):
            if file.is_file():
                try:
                    space_saved += file.stat().st_size
                    files_removed += 1
                except:
                    pass
        
        # Remove all files in the cache directory
        for file in cache_dir.glob("**/*"):
            if file.is_file():
                try:
                    file.unlink()
                except Exception as e:
                    logger.error(f"Error removing {file}: {e}")
    
        console.print(f"[green]Cleared {files_removed} cached files, freeing {space_saved / (1024*1024):.2f} MB[/green]")
        return {
            "success": True,
            "files_removed": files_removed,
            "space_saved": space_saved,
            "message": f"Cleared {files_removed} cached files, freeing {space_saved / (1024*1024):.2f} MB"
        }
    except Exception as e:
        error_msg = f"Error clearing cache: {e}"
        console.print(f"[red]{error_msg}[/red]")
        return {
            "success": False,
            "error": str(e),
            "message": error_msg
        }

# --- Menu Action Definitions ---
PRIMARY_ACTIONS = [
    {
        "name": " • Process All Tasks",
        "fn": run_process_all,
        "type": "process_all",
        "args": [],
        "log": False,
        "description": "Run all major processing tasks in sequence (dedupe, rename, snippets, citations, idealize, images, docs)"
    },
    {
        "name": " • Process Files",
        "fn": process_renames,
        "type": "file",
        "args": [True, set()],
        "log": True,
        "description": "Analyze and process all non-media files (text, code, docs)"
    },
    {
        "name": " • Process Images",
        "fn": process_images,
        "type": "dir",
        "args": [True],
        "log": True,
        "description": "Analyze and optimize images for accessibility and metadata"
    },
    {
        "name": " • Extract Snippets",
        "fn": process_snippets,
        "type": "file",
        "args": [True, 100, set()],
        "log": True,
        "description": "Extract code snippets from source files"
    },
    {
        "name": " • Generate Docs",
        "fn": generate_docs,
        "type": "dir",
        "args": [True],
        "log": False,
        "description": "Build documentation from code files"
    },
    {
        "name": " • Extract Citations",
        "fn": process_citations,
        "type": "dir",
        "args": [True],
        "log": False,
        "description": "Collect and format citations from documents"
    },
    {
        "name": " • Idealize Content",
        "fn": idealize_directory,
        "type": "file",
        "args": [True, set()],
        "log": True,
        "description": "Rewrite or enhance content for clarity and accessibility"
    },
    {
        "name": " • Analysis Report",
        "fn": None,  # Special handler for the report function
        "type": "analysis_report",
        "args": [],
        "log": False,
        "description": "Analyze documents, show stats, and export summary report"
    },
]

UTILITY_ACTIONS = [
    {
        "name": " • Scramble Files",
        "fn": scramble_directory,
        "type": "scrambler",
        "args": [],
        "log": True,
        "description": "Randomize filenames for privacy/testing"
    },
    {
        "name": " • Sample Files",
        "fn": generate_sample_files,
        "type": "scrambler_sample",
        "args": [],
        "log": True,
        "description": "Generate sample files for testing"
    },
    {
        "name": " • Deduplicate Files",
        "fn": dedupe_files,
        "type": "func",
        "args": [None, True, True, False, False, None],
        "log": True,
        "description": "Find and remove duplicate files based on content"
    },
    {
        "name": " • Launch GUI",
        "fn": None,  # Special handler for GUI launch
        "type": "gui",
        "args": [],
        "log": False,
        "description": "Launch the Herd AI GUI web application"
    },
    {
        "name": " • Clear Cache",
        "fn": clear_cache,
        "type": "func",
        "args": [None],
        "log": False,
        "description": "Remove cached analysis data"
    },
    {
        "name": " • Undo Last Operation",
        "fn": undo_last_action,
        "type": "undo",
        "args": [],
        "log": False,
        "description": "Undo the most recent operation (rename, dedupe, images, etc.)"
    },
]

# Special actions not shown in the numbered menu
SPECIAL_ACTIONS = {
    "g": {
        "name": "Launch GUI",
        "fn": None,  # Special handler
        "type": "gui",
        "args": [],
        "log": False,
        "description": "Launch the Herd AI GUI web application"
    },
    "s": {
        "name": "Settings",
        "fn": None,  # Special handler
        "type": "settings",
        "args": [],
        "log": False,
        "description": "Change working directory and other preferences"
    },
    "h": {
        "name": "Help",
        "fn": None,  # Special handler
        "type": "help",
        "args": [],
        "log": False,
        "description": "Show detailed descriptions of all tasks"
    },
    "q": {
        "name": "Quit",
        "fn": None,  # Special handler
        "type": "quit",
        "args": [],
        "log": False,
        "description": "Exit the program"
    }
}

# --- Enhanced Menu Rendering ---
def create_header_with_menu(selected=None, project_path=None, provider=None):
    # Create info strings
    info_lines = []
    if project_path:
        info_lines.append(f"📁 Project: {project_path}")
    if provider:
        info_lines.append(f"🤖 AI Provider: {provider}")
    
    # Combine logo and info into a styled header
    logo_text = Text.from_ansi(HERD_LOGO)
    logo_text.stylize("bold cyan", 0, 432)  # Apply styling to logo part
    logo_text.stylize("bold green", 432, 1080)  # Apply styling to llama part
    logo_text.stylize("bold magenta", 1080, 1110)  # Apply styling to "Document & Code Intelligence"
    logo_text.stylize("bold cyan", 1110, 1114)  # Apply styling to version
    
    # Create a header section with logo and info
    header_parts = [logo_text]
    for line in info_lines:
        info_text = Text(line)
        info_text.highlight_words(["Project:", "AI Provider:"], "dim")
        info_text.highlight_regex(r"(?<=: ).+", "bright_yellow")
        header_parts.append(info_text)
        
    header_content = Group(*header_parts)
    
    # Menu table
    menu_table = Table(box=box.SIMPLE, show_header=True, padding=(0, 2), expand=True)
    menu_table.add_column("[bold bright_yellow]Primary Tasks[/bold bright_yellow]", justify="left")
    menu_table.add_column("[bold bright_magenta]Utilities[/bold bright_magenta]", justify="right")
    
    # Calculate rows needed (combine primary and utility actions into rows)
    rows = []
    for i in range(max(len(PRIMARY_ACTIONS), len(UTILITY_ACTIONS))):
        left_idx = i + 1
        right_idx = i + 1 + len(PRIMARY_ACTIONS)
        
        # Primary task (left)
        if i < len(PRIMARY_ACTIONS):
            left_style = "[reverse][bold bright_green]" if left_idx == selected else "[bright_cyan]"
            left_end_style = "[/reverse]" if left_idx == selected else ""
            left_action = f"{left_style}{left_idx}{PRIMARY_ACTIONS[i]['name'].strip()}{left_end_style}"
        else:
            left_action = ""
            
        # Utility task (right)
        if i < len(UTILITY_ACTIONS):
            right_style = "[reverse][bold bright_green]" if right_idx == selected else "[bright_cyan]"
            right_end_style = "[/reverse]" if right_idx == selected else ""
            right_action = f"{right_style}{right_idx}{UTILITY_ACTIONS[i]['name'].strip()}{right_end_style}"
        else:
            right_action = ""
            
        menu_table.add_row(left_action, right_action)
        
    # Special commands
    special_cmds = []
    for key, action in SPECIAL_ACTIONS.items():
        special_cmds.append(f"[bright_cyan]{key}[/bright_cyan]=[bold bright_yellow]{action['name']}[/bold bright_yellow]")
    
    # Different instruction text based on whether readchar is available
    if HAS_READCHAR:
        special_cmd_text = f"[dim]Use [bright_cyan]↑/↓[/bright_cyan] arrows or numbers (1-{len(PRIMARY_ACTIONS) + len(UTILITY_ACTIONS)}) or {' '.join(special_cmds)}[/dim]"
    else:
        special_cmd_text = f"[dim]Select action with numbers (1-{len(PRIMARY_ACTIONS) + len(UTILITY_ACTIONS)}), [bright_cyan]n[/bright_cyan]/[bright_cyan]p[/bright_cyan] to navigate, or {' '.join(special_cmds)}[/dim]"

    # Create header panel
    header_panel = Panel(
        header_content,
        border_style="bright_blue",
        box=box.DOUBLE,
        padding=(1, 1)
    )
    
    # Stack the header and menu vertically
    return Panel(
        Group(
            header_panel,
            menu_table,
            Align.center(Text.from_markup(special_cmd_text), vertical="top")
        ),
        title="[bold bright_yellow]HERD AI Control Panel[/bold bright_yellow]",
        subtitle="[dim italic]Document & Code Intelligence[/dim italic]",
        border_style="bright_blue",
        box=box.ROUNDED,
        padding=(1, 2),
        width=100  # Constrain width to 100 characters
    )

def print_progress_bar(current, total, description=""):
    """Create a rich progress bar with spinner"""
    with Progress(
        SpinnerColumn(),
        TextColumn("[bright_blue]{task.description}[/bright_blue]"),
        BarColumn(complete_style="bright_green", finished_style="green"),
        TextColumn("[bright_yellow]{task.percentage:>3.0f}%[/bright_yellow]"),
        TimeRemainingColumn(),
        console=console
    ) as progress:
        task = progress.add_task(description, total=total)
        progress.update(task, completed=current)

def rich_interface(root: Path, omni_paths=None, provider=None):
    """Interactive rich UI for HERD AI operations with enhanced styling"""
    # Set up paths
    _, omni_paths = setup_paths(root, omni_paths)
    session_root = [root]  # Use a list for mutability in nested scope
    
    # Load provider from config if not specified and config module is available
    if provider is None and herd_config:
        provider = herd_config.get_provider()
        if provider is None:
            # Fall back to DEFAULT_AI_PROVIDER from config
            config = get_config_module()
            provider = config.DEFAULT_AI_PROVIDER
            
    session_provider = [provider if provider else DEFAULT_AI_PROVIDER]  # Use a list for mutability in nested scope
    
    # Log the provider being used
    logger.info(f"Using AI provider: {session_provider[0]}")

    # Define log callback with rich styling
    def log_callback(msg: str):
        # Strip existing rich tags for clean styling
        plain_msg = re.sub(r"\[/?[a-zA-Z0-9_\s]+?\]", "", msg)
        # Remove any potentially unmatched closing tags
        plain_msg = plain_msg.replace("[/]", "")
        console.print(plain_msg)

    # Main application loop
    selected_action = 1  # Start with first item selected

    try:
        while True:
            console.clear()
            console.print(create_header_with_menu(selected_action, session_root[0], session_provider[0]))
            
            # Get user input
            action_count = len(PRIMARY_ACTIONS) + len(UTILITY_ACTIONS)
            special_keys = list(SPECIAL_ACTIONS.keys())
            
            # If readchar is available, use arrow key navigation
            if HAS_READCHAR:
                console.print(f"[bright_green]Action[/bright_green] (Use arrows ↑/↓ to navigate, Enter to select, or type 1-{action_count})")

                # Wait for key press
                key = readchar.readkey()

                # Handle arrow keys
                if key == readchar.key.UP and selected_action > 1:
                    selected_action -= 1
                    continue
                elif key == readchar.key.DOWN and selected_action < action_count:
                    selected_action += 1
                    continue
                elif key == readchar.key.ENTER:
                    # Fall through to processing the currently-selected action
                    pass

                # Handle quit immediately
                elif key.lower() == "q":
                    console.print("[bold bright_red]Exiting HERD AI. Goodbye![/bold bright_red]")
                    sys.exit(0)

                # Handle special commands (like 's' for settings, 'h' for help, etc.)
                elif key in special_keys:
                    action_type = SPECIAL_ACTIONS[key]["type"]
                    if action_type == "settings":
                        handle_settings_menu(session_root, session_provider, console)
                        continue  # Re-render menu after settings
                    if action_type == "help":
                        # Show help information (reuse fallback logic)
                        console.clear()
                        # Create styled tables without using markup
                        # Primary tasks table
                        primary_table = Table(box=box.SIMPLE, show_header=True)
                        primary_table.add_column("#", style="bright_cyan", justify="right", width=3)
                        primary_table.add_column("Task", style="bright_green")
                        primary_table.add_column("Description", style="dim")
                        primary_title = Text("Primary Tasks")
                        primary_title.stylize("bold bright_yellow")
                        primary_table.title = primary_title
                        for i, action in enumerate(PRIMARY_ACTIONS, 1):
                            primary_table.add_row(str(i), action["name"].strip(), action["description"])
                        utility_table = Table(box=box.SIMPLE, show_header=True)
                        utility_table.add_column("#", style="bright_cyan", justify="right", width=3)
                        utility_table.add_column("Task", style="bright_green")
                        utility_table.add_column("Description", style="dim")
                        utility_title = Text("Utilities")
                        utility_title.stylize("bold bright_magenta")
                        utility_table.title = utility_title
                        for i, action in enumerate(UTILITY_ACTIONS, len(PRIMARY_ACTIONS) + 1):
                            utility_table.add_row(str(i), action["name"].strip(), action["description"])
                        special_table = Table(box=box.SIMPLE, show_header=True)
                        special_table.add_column("Key", style="bright_cyan", justify="center", width=3)
                        special_table.add_column("Command", style="bright_green")
                        special_table.add_column("Description", style="dim")
                        special_title = Text("Special Commands")
                        special_title.stylize("bold bright_yellow")
                        special_table.title = special_title
                        for key2, action in SPECIAL_ACTIONS.items():
                            special_table.add_row(key2, action["name"], action["description"])
                        special_table.add_row("n", "Next item", "Move selection to next menu item")
                        special_table.add_row("p", "Previous item", "Move selection to previous menu item")
                        help_columns = Columns([primary_table, utility_table], align="left", expand=True)
                        panel_title = Text("HERD AI Help: Available Tasks")
                        panel_title.stylize("bold bright_yellow")
                        panel_subtitle = Text("Press Enter to return to menu")
                        panel_subtitle.stylize("dim italic")
                        console.print(Panel(
                            Group(
                                help_columns,
                                Padding(special_table, (1, 0, 0, 0))
                            ),
                            title=panel_title,
                            subtitle=panel_subtitle,
                            border_style="bright_blue",
                            box=box.ROUNDED,
                            padding=(1, 1),
                            width=100
                        ))
                        Prompt.ask("", default="")
                        continue
                    if action_type == "quit":
                        console.print("[bold bright_red]Exiting HERD AI. Goodbye![/bold bright_red]")
                        sys.exit(0)
                    # Add more special actions as needed
                    continue

                # Any other special command (like 'h' for help)
                elif key in special_keys:
                    choice = key

                else:
                    # Try interpreting as a number
                    try:
                        if '1' <= key <= '9' or key == '0':
                            num = int(key)
                            if 1 <= num <= action_count:
                                selected_action = num
                            continue
                        else:
                            continue
                    except Exception:
                        continue
                    try:
                        if '1' <= key <= '9' or key == '0':
                            num = int(key)
                            if 1 <= num <= action_count:
                                selected_action = num
                            continue
                        elif key == 'q':
                            break
                        else:
                            continue
                    except:
                        continue
            else:
                # Fall back to traditional prompt if readchar isn't available
                choices = [str(i) for i in range(1, action_count + 1)] + special_keys + ["n", "p"]
                prompt_text = f"[bright_green]Action[/bright_green] ([bright_cyan]1-{action_count}[/bright_cyan], [bright_cyan]n[/bright_cyan]=next, [bright_cyan]p[/bright_cyan]=prev, {', '.join(f'[bright_cyan]{k}[/bright_cyan]' for k in special_keys)})"
                choice = Prompt.ask(
                    prompt_text,
                    choices=choices,
                    default=str(selected_action)
                )
                
                # Handle navigation commands
                if choice == "n":  # Next item
                    if selected_action < action_count:
                        selected_action += 1
                    continue
                elif choice == "p":  # Previous item
                    if selected_action > 1:
                        selected_action -= 1
                    continue
                
                # Handle special actions
                if choice in special_keys:
                    action_type = SPECIAL_ACTIONS[choice]["type"]
                    
                    if action_type == "quit":
                        console.print("[bold bright_red]Exiting HERD AI. Goodbye![/bold bright_red]")
                        sys.exit(0)
                    
                    if action_type == "settings":
                        # Handle settings as a special case
                        handle_settings_menu(session_root, session_provider, console)
                        continue
                    
                    if action_type == "help":
                        # Show help information
                        console.clear()
                        
                        # Create styled tables without using markup
                        # Primary tasks table
                        primary_table = Table(box=box.SIMPLE, show_header=True)
                        primary_table.add_column("#", style="bright_cyan", justify="right", width=3)
                        primary_table.add_column("Task", style="bright_green")
                        primary_table.add_column("Description", style="dim")
                        
                        # Add a title
                        primary_title = Text("Primary Tasks")
                        primary_title.stylize("bold bright_yellow")
                        primary_table.title = primary_title
                        
                        # Add primary actions
                        for i, action in enumerate(PRIMARY_ACTIONS, 1):
                            primary_table.add_row(str(i), action["name"].strip(), action["description"])
                        
                        # Utility tasks table
                        utility_table = Table(box=box.SIMPLE, show_header=True)
                        utility_table.add_column("#", style="bright_cyan", justify="right", width=3)
                        utility_table.add_column("Task", style="bright_green")
                        utility_table.add_column("Description", style="dim")
                        
                        # Add a title
                        utility_title = Text("Utilities")
                        utility_title.stylize("bold bright_magenta")
                        utility_table.title = utility_title
                        
                        # Add utility actions
                        for i, action in enumerate(UTILITY_ACTIONS, len(PRIMARY_ACTIONS) + 1):
                            utility_table.add_row(str(i), action["name"].strip(), action["description"])
                        
                        # Special commands table
                        special_table = Table(box=box.SIMPLE, show_header=True)
                        special_table.add_column("Key", style="bright_cyan", justify="center", width=3)
                        special_table.add_column("Command", style="bright_green")
                        special_table.add_column("Description", style="dim")
                        
                        # Add a title
                        special_title = Text("Special Commands")
                        special_title.stylize("bold bright_yellow")
                        special_table.title = special_title
                        
                        # Add special actions and navigation commands
                        for key, action in SPECIAL_ACTIONS.items():
                            special_table.add_row(key, action["name"], action["description"])
                        special_table.add_row("n", "Next item", "Move selection to next menu item")
                        special_table.add_row("p", "Previous item", "Move selection to previous menu item")
                        
                        # Create the help panel with tables
                        help_columns = Columns([primary_table, utility_table], align="left", expand=True)
                        
                        # Create panel with title and subtitle
                        panel_title = Text("HERD AI Help: Available Tasks")
                        panel_title.stylize("bold bright_yellow")
                        
                        panel_subtitle = Text("Press Enter to return to menu")
                        panel_subtitle.stylize("dim italic")
                        
                        console.print(Panel(
                            Group(
                                help_columns,
                                Padding(special_table, (1, 0, 0, 0))
                            ),
                            title=panel_title,
                            subtitle=panel_subtitle,
                            border_style="bright_blue",
                            box=box.ROUNDED,
                            padding=(1, 1),
                            width=100  # Constrain width
                        ))
                        
                        Prompt.ask("", default="")
                        continue
                    
                    # Handle other special actions as needed
                    continue
                
                # Handle number selection
                try:
                    selected_action = int(choice)
                    # Continue to process
                except ValueError:
                    console.print(f"[bold bright_red]Invalid option: {choice}[/bold bright_red]")
                    continue
            
            # Process the selected action
            action_idx = selected_action - 1
            if action_idx < 0 or action_idx >= len(PRIMARY_ACTIONS) + len(UTILITY_ACTIONS):
                console.print(f"[bold bright_red]Invalid action index: {action_idx}[/bold bright_red]")
                selected_action = 1  # Reset to first item
                continue
                
            action = PRIMARY_ACTIONS[action_idx] if action_idx < len(PRIMARY_ACTIONS) else UTILITY_ACTIONS[action_idx - len(PRIMARY_ACTIONS)]
            action_name = action["name"]
            action_fn = action["fn"]
            action_type = action["type"]
            action_args = action["args"]
            use_log = action["log"]
            
            # Update header to show current action
            header = create_header_with_menu(selected_action, session_root[0], session_provider[0])
            console.print(header)
            
            # Update content area to show we're starting the action
            console.print(Panel(
                f"[bright_cyan]Running {action_name}...[/bright_cyan]",
                title="[bold bright_green]Output[/bold bright_green]",
                border_style="bright_blue",
                box=box.ROUNDED,
                padding=(1, 2)
            ))
            
            # Handle GUI special action
            if action_type == "gui":
                try:
                    console.print("[bold cyan]Launching Herd AI GUI[/bold cyan]")
                    
                    # Try multiple possible paths to find herd_gui.py
                    import subprocess
                    from pathlib import Path
                    
                    possible_paths = [
                        # Path relative to workspace root
                        Path(session_root[0]) / "herd_gui.py",
                        # Path relative to this file location
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
                        Prompt.ask("[bright_yellow]Press Enter to return to menu[/bright_yellow]")
                        continue
                    
                    # Launch the GUI using subprocess
                    console.print(f"[cyan]Found GUI at: {gui_path}[/cyan]")
                    console.print(f"[cyan]Starting web server at http://localhost:4343[/cyan]")
                    console.print("[yellow]GUI will launch in a separate window. Close this terminal when done.[/yellow]")
                    
                    subprocess.run([sys.executable, str(gui_path)])
                    continue
                    
                except Exception as e:
                    console.print(f"[bold red]Error launching GUI: {e}[/bold red]")
                    traceback.print_exc()
                    Prompt.ask("[bright_yellow]Press Enter to return to menu[/bright_yellow]")
                    continue
            
            console.clear()
            console.print(header)
            
            # Process action
            try:
                # FUNCTION-BASED OPERATIONS
                if action_type == "func":
                    console.print(f"[dim]Executing [bright_cyan]{action_name}[/bright_cyan]...[/dim]")
                    
                    try:
                        if action_name == " • Deduplicate Files":
                            # Special handling for dedupe with enhanced UI
                            directory = session_root[0]
                            recursive = Prompt.ask("[bright_yellow]Process subdirectories recursively?[/bright_yellow] (y/n)", default="y").lower() == "y"
                            
                            console.print(f"[bright_cyan]Scanning for duplicates in {directory}...[/bright_cyan]")
                            with console.status("[bright_cyan]Scanning files...[/bright_cyan]", spinner="dots"):
                                # Initialize and scan
                                detector = DuplicateDetector(directory, recursive)
                                results = detector.scan_directory()
                            
                            # Get duplicate counts
                            exact_dupes_count = sum(len(g['files']) - 1 for g in results['exact_duplicates'])
                            image_dupes_count = sum(len(g['files']) - 1 for g in results['image_duplicates'])
                            similar_text_count = sum(g['count'] - 1 for g in results['similar_text_groups'])
                            total_dupes = exact_dupes_count + image_dupes_count
                            
                            # Display results
                            if total_dupes > 0 or similar_text_count > 0:
                                space_saved = format_size(results['potential_space_saving'])
                                console.print(Panel(
                                    f"[bright_green]Found {total_dupes} exact duplicate files[/bright_green]\n"
                                    f"[bright_green]Found {similar_text_count} similar text files[/bright_green]\n"
                                    f"[bright_yellow]Potential space savings: {space_saved}[/bright_yellow]",
                                    title="[bold bright_yellow]Deduplication Results[/bold bright_yellow]",
                                    border_style="bright_blue",
                                    box=box.ROUNDED,
                                    padding=(1, 2)
                                ))
                                
                                # Show details if requested
                                show_details = Prompt.ask("[bright_yellow]Show detailed duplicate information?[/bright_yellow] (y/n)", default="n").lower() == "y"
                                
                                if show_details:
                                    if results['exact_duplicates']:
                                        console.print("[bold bright_green]== Exact Duplicates ==[/bold bright_green]")
                                        for i, group in enumerate(results['exact_duplicates'], 1):
                                            console.print(f"[bright_cyan]Group {i}: {group['count']} files, {format_size(group['size'])} each[/bright_cyan]")
                                            for file_path in group['files']:
                                                console.print(f"  [dim]- {file_path}[/dim]")
                                    
                                    if results['image_duplicates']:
                                        console.print("[bold bright_green]== Image Duplicates ==[/bold bright_green]")
                                        for i, group in enumerate(results['image_duplicates'], 1):
                                            console.print(f"[bright_cyan]Group {i}: {group['count']} files, {format_size(group['size'])} each, Resolution: {group['resolution']}[/bright_cyan]")
                                            for file_path in group['files']:
                                                console.print(f"  [dim]- {file_path}[/dim]")
                                    
                                    if results['similar_text_groups']:
                                        console.print("[bold bright_green]== Similar Text Files ==[/bold bright_green]")
                                        for i, group in enumerate(results['similar_text_groups'], 1):
                                            console.print(f"[bright_cyan]Group {i}: {group['count']} files[/bright_cyan]")
                                            for file_path in group['files']:
                                                console.print(f"  [dim]- {file_path}[/dim]")
                                
                                # Prompt for actions if duplicates found
                                if total_dupes > 0:
                                    delete_action = Prompt.ask("[bright_yellow]Delete duplicate files (keeping the first one in each group)?[/bright_yellow] (y/n)", default="n").lower() == "y"
                                    
                                    if delete_action:
                                        with console.status("[bright_cyan]Deleting duplicates...[/bright_cyan]", spinner="dots"):
                                            deletion_result = detector.delete_duplicates(keep_first=True)
                                        
                                        space_saved = format_size(deletion_result['total_space_saved'])
                                        console.print(f"[bold bright_green]Deleted {deletion_result['total_deleted']} files, saving {space_saved}[/bold bright_green]")
                                        
                                        if deletion_result['errors']:
                                            console.print(f"[bold yellow]Encountered {len(deletion_result['errors'])} errors while deleting files[/bold yellow]")
                                            for error in deletion_result['errors']:
                                                console.print(f"  [dim]- {error['file']}: {error['error']}[/dim]")
                                
                                if similar_text_count > 0:
                                    merge_action = Prompt.ask("[bright_yellow]Merge similar text files?[/bright_yellow] (y/n)", default="n").lower() == "y"
                                    
                                    if merge_action:
                                        output_prompt = Prompt.ask("[bright_yellow]Enter output directory for merged files (leave blank for default)[/bright_yellow]", default="")
                                        output_path = Path(output_prompt) if output_prompt else None
                                        
                                        with console.status("[bright_cyan]Merging similar files...[/bright_cyan]", spinner="dots"):
                                            merge_result = detector.merge_similar_text(output_path)
                                        
                                        console.print(f"[bold bright_green]Merged {merge_result['total_merged']} groups of similar text files[/bold bright_green]")
                                        
                                        if merge_result['errors']:
                                            console.print(f"[bold yellow]Encountered {len(merge_result['errors'])} errors while merging files[/bold yellow]")
                                            for error in merge_result['errors']:
                                                console.print(f"  [dim]- Error merging {len(error['files'])} files: {error['error']}[/dim]")
                            else:
                                console.print("[bright_yellow]No duplicate or similar files found in the selected directory.[/bright_yellow]")
                                
                        else:
                            # Regular function execution for other actions
                            result = action_fn(*action_args)
                            console.print(f"[bright_green]{action_name} completed successfully[/bright_green]")
                    except Exception as e:
                        console.print(f"[bold bright_red]Error in {action_name}: {e}[/bold bright_red]")
                
                # DIRECTORY-BASED OPERATIONS
                elif action_type == "dir":
                    console.print(f"[dim]Processing directory [bright_cyan]{session_root[0]}[/bright_cyan]...[/dim]")
                    
                    try:
                        # Call appropriate function based on action
                        if action_name == " • Generate Docs":
                            # Ensure directory exists
                            docs_dir = omni_paths.get('base_dir') / "docs"
                            docs_dir.mkdir(parents=True, exist_ok=True)
                            
                            console.print(f"[bright_cyan]Generating documentation for {session_root[0]}...[/bright_cyan]")
                            result = action_fn(session_root[0], recursive=action_args[0], provider=session_provider[0], log_callback=log_callback)
                            
                            if result.get('success', False):
                                if result.get('readme_path'):
                                    console.print(f"[bold bright_green]✅ Documentation generated successfully![/bold bright_green]")
                                    console.print(f"[bright_green]Generated README.md at: {result['readme_path']}[/bright_green]")
                                    console.print(f"[bright_green]Processed {result.get('files_processed', 0)} files.[/bright_green]")
                                else:
                                    console.print(f"[bright_yellow]⚠️ No README.md was generated: {result.get('message', 'No applicable files found')}[/bright_yellow]")
                            else:
                                console.print(f"[bold yellow]⚠️ Documentation generation completed with issues: {result.get('error', 'Unknown error')}[/bold yellow]")
                                if 'error' in result:
                                    console.print(f"[yellow]Error details: {result['error']}[/yellow]")
                        elif action_name == " • Extract Citations":
                            # Prompt for output formats
                            format_input = Prompt.ask(
                                "[bright_yellow]Which output format(s) do you want?[/bright_yellow] (md, json, txt, bib, mla, chicago, ieee) [comma-separated, default: md]",
                                default="md"
                            )
                            outputs = [f.strip() for f in format_input.split(",") if f.strip() in ("md", "json", "txt", "bib", "mla", "chicago", "ieee")]
                            if not outputs:
                                outputs = ["md"]
                            
                            # Prompt for citation styles
                            style_input = Prompt.ask(
                                "[bright_yellow]Which citation style(s) do you want?[/bright_yellow] (apa, mla, chicago, ieee, vancouver) [comma-separated, default: apa]",
                                default="apa"
                            )
                            styles = [s.strip() for s in style_input.split(",") if s.strip() in ("apa", "mla", "chicago", "ieee", "vancouver")]
                            if not styles:
                                styles = ["apa"]
                            
                            console.print(f"[dim]Extracting citations in {', '.join(styles)} style(s) with {', '.join(outputs)} output format(s)[/dim]")
                            
                            try:
                                result = action_fn(session_root[0], recursive=action_args[0], styles=styles, outputs=outputs, provider=session_provider[0], log_callback=log_callback)
                                if result.get('success', False):
                                    console.print(f"[bold bright_green]✅ Citations extracted successfully![/bold bright_green]")
                                    console.print(f"[bright_green]Found {result.get('unique_citations', 0)} unique citations across {result.get('files_processed', 0)} files.[/bright_green]")
                                    if 'outputs' in result and result['outputs']:
                                        console.print("[bright_blue]Output files:[/bright_blue]")
                                        for style, files in result.get('outputs', {}).items():
                                            for fmt, path in files.items():
                                                console.print(f"  [bright_yellow]{style.upper()} ({fmt})[/bright_yellow]: {path}")
                                else:
                                    console.print(f"[bold yellow]⚠️ Citation extraction completed with issues: {result.get('error', 'Unknown error')}[/bold yellow]")
                            except Exception as e:
                                console.print(f"[bold bright_red]❌ Error extracting citations: {e}[/bold bright_red]")
                        elif action_name == " • Process Images":
                            # Only process this section once - we'll use a function here
                            try:
                                # Import the correct function
                                from herd_ai.image_processor import process_directory as process_images
                                
                                # Use existing parameters and call the function directly
                                result = action_fn(session_root[0], recursive=action_args[0], provider=session_provider[0], log_callback=log_callback)
                                
                                console.print(f"[bold bright_green]✅ Image processing completed successfully![/bold bright_green]")
                                console.print(f"[bright_green]Processed {result.get('files_processed', 0)} images.[/bright_green]")
                                console.print(f"[bright_green]Output directory: {result.get('output_dir', 'Unknown')}[/bright_green]")
                            except Exception as e:
                                console.print(f"[bold bright_red]❌ Error processing images: {e}[/bold bright_red]")
                        else:
                            # Generic fallback
                            result = action_fn(session_root[0], *action_args, provider=session_provider[0])
                            console.print("[bright_green]Operation completed successfully.[/bright_green]")
                    except Exception as e:
                        console.print(f"[bold bright_red]Error in {action_name}: {e}[/bold bright_red]")
                
                # ANALYSIS REPORT
                elif action_type == "analysis_report":
                    console.print(f"[bright_cyan]Generating Analysis Report for {session_root[0]}...[/bright_cyan]")
                    
                    try:
                        # Ensure analysis directory exists
                        analysis_dir = omni_paths.get('analysis_dir')
                        if not analysis_dir:
                            analysis_dir = omni_paths.get('base_dir') / "analysis"
                        analysis_dir.mkdir(exist_ok=True, parents=True)
                        
                        # Define output path
                        output_path = analysis_dir / "report.md"
                        
                        # Track progress and success
                        progress_steps = 3
                        completed_steps = 0
                        step_results = []
                        
                        # Run analyze_documents
                        with console.status("[bright_cyan]Analyzing documents...[/bright_cyan]", spinner="dots"):
                            try:
                                analyze_documents(session_root[0], recursive=True, force=False)
                                step_results.append(True)
                                completed_steps += 1
                                console.print("[bright_green]✅ Document analysis complete[/bright_green]")
                            except Exception as e:
                                step_results.append(False)
                                console.print(f"[bright_red]❌ Document analysis failed: {e}[/bright_red]")
                        
                        # Generate document summary
                        with console.status("[bright_cyan]Generating document summary...[/bright_cyan]", spinner="dots"):
                            try:
                                stats = generate_document_summary(session_root[0], recursive=True, force=False, provider=session_provider[0])
                                step_results.append(True)
                                completed_steps += 1
                                console.print("[bright_green]✅ Summary generation complete[/bright_green]")
                            except Exception as e:
                                stats = None
                                step_results.append(False)
                                console.print(f"[bright_red]❌ Summary generation failed: {e}[/bright_red]")
                        
                        # Export the summary
                        with console.status(f"[bright_cyan]Exporting report to {output_path}...[/bright_cyan]", spinner="dots"):
                            try:
                                export_document_summary(session_root[0], output_path, provider=session_provider[0])
                                step_results.append(True)
                                completed_steps += 1
                                console.print(f"[bright_green]✅ Report exported to {output_path}[/bright_green]")
                            except Exception as e:
                                step_results.append(False)
                                console.print(f"[bright_red]❌ Report export failed: {e}[/bright_red]")
                        
                        # Show overall progress
                        print_progress_bar(completed_steps, progress_steps, "Analysis Report Progress")
                        
                        # Show summary statistics if available
                        if stats:
                            console.print(Panel(
                                f"[bright_green]Analysis Summary:[/bright_green]\n\n"
                                f"📚 Documents: [bold bright_yellow]{stats.get('count', 0)}[/bold bright_yellow]\n"
                                f"📝 Total Words: [bold bright_yellow]{stats.get('total_words', 0):,}[/bold bright_yellow]\n"
                                f"📊 Average Words Per Document: [bold bright_yellow]{stats.get('avg_words', 0):.1f}[/bold bright_yellow]\n"
                                f"🔄 Word Frequency: Top words include [bold bright_yellow]{', '.join(stats.get('top_words', [])[:5])}[/bold bright_yellow]\n",
                                title="[bold bright_yellow]Document Analysis Report[/bold bright_yellow]",
                                border_style="bright_blue",
                                box=box.ROUNDED,
                                padding=(1, 2)
                            ))
                        
                        # Overall status message
                        if all(step_results):
                            console.print(Panel(
                                f"[bold bright_green]✅ Analysis Report Successfully Generated[/bold bright_green]\n\n"
                                f"Report saved to: [bright_yellow]{output_path}[/bright_yellow]\n"
                                f"Completed {completed_steps}/{progress_steps} steps successfully.",
                                border_style="bright_green",
                                box=box.ROUNDED
                            ))
                        else:
                            console.print(Panel(
                                f"[bold bright_yellow]⚠️ Analysis Report Partially Completed[/bold bright_yellow]\n\n"
                                f"Report location: [bright_yellow]{output_path}[/bright_yellow]\n"
                                f"Completed {completed_steps}/{progress_steps} steps successfully.",
                                border_style="yellow",
                                box=box.ROUNDED
                            ))
                    except Exception as e:
                        console.print(Panel(
                            f"[bold bright_red]❌ Error Generating Analysis Report[/bold bright_red]\n\n"
                            f"Error: {e}",
                            border_style="bright_red",
                            box=box.ROUNDED
                        ))
                
                # SCRAMBLER ACTIONS
                elif action_type == "scrambler":
                    # Prompt for directory
                    target_dir = Prompt.ask("[bright_yellow]Enter the directory to scramble filenames[/bright_yellow]", default=str(session_root[0]))
                    target_dir = Path(target_dir.strip())
                    if not target_dir.exists() or not target_dir.is_dir():
                        console.print(f"[bold bright_red]Invalid directory: {target_dir}[/bold bright_red]")
                        time.sleep(2)
                        selected_action = None
                        continue
                    console.print(f"[dim]Scrambling filenames in [bright_cyan]{target_dir}[/bright_cyan]...[/dim]")
                    count = scramble_directory(target_dir, log_callback=log_callback)
                    console.print(f"[bright_green]Scrambled {count} files in {target_dir}[/bright_green]")
                elif action_type == "scrambler_sample":
                    target_dir = Prompt.ask("[bright_yellow]Enter the directory to generate sample files[/bright_yellow]", default=str(session_root[0]))
                    target_dir = Path(target_dir.strip())
                    if not target_dir.exists() or not target_dir.is_dir():
                        console.print(f"[bold bright_red]Invalid directory: {target_dir}[/bold bright_red]")
                        time.sleep(2)
                        selected_action = None
                        continue
                    files_per_ext = Prompt.ask("[bright_yellow]How many sample files per file type?[/bright_yellow]", default="3")
                    try:
                        files_per_ext = int(files_per_ext)
                    except Exception:
                        files_per_ext = 3
                    console.print(f"[dim]Generating sample files in [bright_cyan]{target_dir}[/bright_cyan]...[/dim]")
                    count = generate_sample_files(target_dir, files_per_ext=files_per_ext, log_callback=log_callback)
                    console.print(f"[bright_green]Generated {count} sample files in {target_dir}[/bright_green]")
                
                # FILE OPERATIONS
                elif action_type == "file":
                    console.print(f"[dim]Scanning for files in {session_root[0]}...[/dim]")
                    all_files = list(session_root[0].rglob("*") if action_args[0] else session_root[0].glob("*"))
                    console.print(f"[dim]Found {len(all_files)} total files before filtering[/dim]")
                    
                    targets = [
                        f for f in all_files 
                        if f.is_file() 
                        and not f.name.startswith('.')
                        and not f.name.startswith('|_')
                        and not any(part.startswith('.') or part.startswith('|_') for part in f.parts)
                    ]
                    console.print(f"[dim]After basic filtering: {len(targets)} files[/dim]")
                    
                    config = get_config_module()
                    if action_name == " • Process Files":
                        targets = [f for f in targets if f.suffix.lower() in config.SUPPORTED_EXTENSIONS]
                        console.print(f"[dim]Extensions being processed: {', '.join(sorted(config.SUPPORTED_EXTENSIONS))}[/dim]")
                    elif action_name == " • Extract Snippets":
                        targets = [f for f in targets if f.suffix.lower() in config.CODE_EXTENSIONS]
                        console.print(f"[dim]Extensions being processed: {', '.join(sorted(config.CODE_EXTENSIONS))}[/dim]")
                    elif action_name == " • Idealize Content":
                        targets = [f for f in targets if f.suffix.lower() in config.TEXT_EXTENSIONS.union(config.DOCUMENT_EXTENSIONS)]
                        console.print(f"[dim]Extensions being processed: {', '.join(sorted(config.TEXT_EXTENSIONS.union(config.DOCUMENT_EXTENSIONS)))}[/dim]")
                    elif action_name == " • Process Images":
                        targets = [f for f in targets if f.suffix.lower() in config.IMAGE_EXTENSIONS]
                        console.print(f"[dim]Extensions being processed: {', '.join(sorted(config.IMAGE_EXTENSIONS))}[/dim]")
                    
                    console.print(f"[bright_blue]Found {len(targets)} files to process[/bright_blue]")
                    
                    if not targets:
                        console.print(f"[bold yellow]No applicable files found for {action_name}[/bold yellow]")
                        time.sleep(2)
                        selected_action = None
                        continue
                        
                    processed = 0
                    total = len(targets)
                    
                    for idx, filepath in enumerate(targets, 1):
                        if use_log:
                            try:
                                rel_path = filepath.relative_to(session_root[0])
                            except ValueError:
                                rel_path = filepath
                            console.print(f"[dim]Processing → [bright_cyan]{rel_path}[/bright_cyan][/dim]")
                            
                        try:
                            if action_name == " • Process Files":
                                action_fn(filepath, recursive=action_args[0], exclude_ext=action_args[1], 
                                          provider=session_provider[0], omni_paths=omni_paths, log_callback=log_callback if use_log else None)
                            elif action_name == " • Extract Snippets":
                                console.print(f"[bright_cyan]Extracting code snippets from {session_root[0]}...[/bright_cyan]")
                                
                                # Import the correct function
                                from herd_ai.snippets import process_directory as process_snippets
                                
                                # Set up parameters
                                result = process_snippets(
                                    directory=session_root[0],
                                    recursive=action_args[0],
                                    batch_size=50,
                                    exclude_ext=None,
                                    log_callback=log_callback,
                                    provider=session_provider[0]
                                )
                                
                                # Display results
                                if result.get('success', False):
                                    console.print(f"[bold bright_green]✅ Code snippets extracted successfully![/bold bright_green]")
                                    console.print(f"[bright_green]Processed {result.get('files_processed', 0)} files.[/bright_green]")
                                    console.print(f"[bright_green]Found {result.get('snippets_found', 0)} snippets in {result.get('with_snippets', 0)} files.[/bright_green]")
                                    console.print(f"[bright_green]Output directory: {result.get('output_dir', 'Unknown')}[/bright_green]")
                                else:
                                    console.print(f"[bold yellow]⚠️ Snippet extraction completed with issues: {result.get('error', 'Unknown error')}[/bold yellow]")
                            elif action_name == " • Idealize Content":
                                try:
                                    console.print(f"[dim]Idealizing content in [bright_cyan]{filepath}[/bright_cyan][/dim]")
                                    result = action_fn(
                                        filepath, 
                                        recursive=action_args[0], 
                                        exclude_ext=action_args[1],
                                        provider=session_provider[0], 
                                        log_callback=log_callback if use_log else None
                                    )
                                    
                                    if isinstance(result, dict) and result.get('success', False):
                                        processed += 1
                                        if 'files_idealized' in result and result['files_idealized'] > 0:
                                            console.print(f"[bright_green]Idealized {result['files_idealized']} files from {filepath}[/bright_green]")
                                            console.print(f"[dim]Idealized files saved to: {result.get('output_dir', 'unknown')}[/dim]")
                                        else:
                                            console.print(f"[yellow]No files were idealized from {filepath}[/yellow]")
                                    else:
                                        console.print(f"[yellow]Failed to idealize content from {filepath}: {result.get('error', 'Unknown error')}[/yellow]")
                                except Exception as e:
                                    console.print(f"[bold bright_red]Error idealizing {filepath}: {e}[/bold bright_red]")
                            elif action_name == " • Process Images":
                                # Only process this section once - we'll use a function here
                                try:
                                    # Import the correct function
                                    from herd_ai.image_processor import process_directory as process_images
                                    
                                    # Use existing parameters and call the function directly
                                    result = action_fn(session_root[0], recursive=action_args[0], provider=session_provider[0], log_callback=log_callback)
                                    
                                    console.print(f"[bold bright_green]✅ Image processing completed successfully![/bold bright_green]")
                                    console.print(f"[bright_green]Processed {result.get('files_processed', 0)} images.[/bright_green]")
                                    console.print(f"[bright_green]Output directory: {result.get('output_dir', 'Unknown')}[/bright_green]")
                                except Exception as e:
                                    console.print(f"[bold bright_red]❌ Error processing images: {e}[/bold bright_red]")
                            else:
                                if use_log:
                                    action_fn(filepath, *action_args, log_callback=log_callback, provider=session_provider[0])
                                else:
                                    action_fn(filepath, *action_args, provider=session_provider[0])
                            processed += 1
                        except Exception as e:
                            console.print(f"[bold bright_red]Error processing {filepath}: {e}[/bold bright_red]")
                            
                        print_progress_bar(idx, total, f"{action_name}")
                        
                    if processed > 0:
                        summary = f"Successfully processed {processed}/{len(targets)} files"
                        console.print(f"[bold bright_green]{summary}[/bold bright_green]")
                    else:
                        summary = "No files were successfully processed"
                        console.print(f"[bold yellow]{summary}[/bold yellow]")
                    
                    print_progress_bar(total, total, f"{action_name} Complete")
                
                # UNKNOWN ACTION TYPE
                else:
                    console.print(f"[bold bright_red]Unknown action type: {action_type}[/bold bright_red]")
            except Exception as e:
                console.print(f"[bold bright_red]Error in {action_name}: {e}[/bold bright_red]")
                logger.exception(f"Error in {action_name}")
            
            # Update content area with completion message after action
            console.print(Panel(
                f"[bright_green]{action_name} completed.[/bright_green]\n\nPress ENTER to return to menu, [bold bright_red]'q'[/bold bright_red] to quit",
                title="[bold bright_yellow]Output[/bold bright_yellow]",
                border_style="bright_blue",
                box=box.ROUNDED,
                padding=(1, 2)
            ))
            
            console.clear()
            console.print(create_header_with_menu(selected_action, session_root[0], session_provider[0]))
            
            # Handle input after action completes
            response = Prompt.ask("[bright_green]>[/bright_green]", default="")
            
            if response.lower() == "q":
                break
            
            # Reset for next action
            selected_action = None
    except KeyboardInterrupt:
        console.print("[bold yellow]KeyboardInterrupt: Returning to menu...[/bold yellow]")
        # Return to the main menu by recursively calling the function
        return rich_interface(session_root[0], omni_paths, session_provider[0])

def handle_login(args):
    if not herd_config:
        print("[ERROR] Config utility not available.")
        return
    if not args.provider or not args.api_key:
        print("[ERROR] --provider and --api-key are required for login.")
        return
    # Validate API key if provider is xai or gemini
    if args.provider == "xai":
        print("[INFO] Validating X.AI API key...")
        if not validate_xai_api_key(args.api_key):
            print("[ERROR] Invalid X.AI API key. Please check and try again.")
            return
    elif args.provider == "gemini":
        print("[INFO] Validating Gemini API key...")
        if not validate_gemini_api_key(args.api_key):
            print("[ERROR] Invalid Gemini API key. Please check and try again.")
            return
    herd_config.set_api_key(args.provider, args.api_key)
    print(f"[SUCCESS] API key for provider '{args.provider}' saved.")

def handle_logout(args):
    if not herd_config:
        print("[ERROR] Config utility not available.")
        return
    if not args.provider:
        print("[ERROR] --provider is required for logout.")
        return
    herd_config.clear_api_key(args.provider)
    print(f"[SUCCESS] API key for provider '{args.provider}' cleared.")

def handle_provider(args):
    if not herd_config:
        print("[ERROR] Config utility not available.")
        return
    if args.set:
        herd_config.set_provider(args.set)
        print(f"[SUCCESS] Provider set to '{args.set}'.")
    else:
        provider = herd_config.get_provider()
        print(f"[INFO] Current provider: {provider if provider else 'Not set'}")

def handle_settings_menu(session_root, session_provider, console):
    """Handle the settings menu options."""
    while True:
        console.print(Panel(
            f"[bright_cyan]Settings Menu[/bright_cyan]\n\n"
            f"[bold]1.[/bold] Change working directory (current: [yellow]{session_root[0]}[/yellow])\n"
            f"[bold]2.[/bold] Select AI provider (current: [yellow]{session_provider[0]}[/yellow])\n"
            f"[bold]3.[/bold] Select Ollama model\n"
            f"[bold]q.[/bold] Return to main menu",
            title="[bold bright_yellow]Settings[/bold bright_yellow]",
            border_style="bright_blue",
            box=box.ROUNDED,
            padding=(1, 2)
        ))
        setting_choice = Prompt.ask("[bright_green]Select option[/bright_green]", choices=["1", "2", "3", "q"], default="q")
        if setting_choice == "q":
            break
        elif setting_choice == "1":
            new_dir = Prompt.ask("[bright_yellow]Enter new working directory[/bright_yellow]", default=str(session_root[0]))
            new_path = Path(new_dir).expanduser().resolve()
            if new_path.exists() and new_path.is_dir():
                session_root[0] = new_path
                console.print(f"[bright_green]Working directory changed to {new_path}[/bright_green]")
            else:
                console.print(f"[bold bright_red]Invalid directory: {new_path}[/bold bright_red]")
        elif setting_choice == "2":
            # Display available providers and get the current one
            provider_list = list(AI_PROVIDERS)
            provider_display = "\n".join([f"[bold]{i+1}.[/bold] {provider}" for i, provider in enumerate(provider_list)])
            
            console.print(Panel(
                f"[bright_cyan]Available AI Providers[/bright_cyan]\n\n"
                f"{provider_display}\n\n"
                f"Current provider: [yellow]{session_provider[0]}[/yellow]",
                title="[bold bright_yellow]AI Provider Selection[/bold bright_yellow]",
                border_style="bright_blue",
                box=box.ROUNDED,
                padding=(1, 2)
            ))
            
            provider_choice = Prompt.ask(
                "[bright_yellow]Select AI provider[/bright_yellow]",
                choices=[str(i+1) for i in range(len(provider_list))],
                default=str(provider_list.index(session_provider[0])+1)
            )
            
            try:
                provider_idx = int(provider_choice) - 1
                if 0 <= provider_idx < len(provider_list):
                    new_provider = provider_list[provider_idx]
                    
                    # If user selects xai, prompt for API key if not set
                    if new_provider == "xai" and not os.environ.get("XAI_API_KEY"):
                        api_key = Prompt.ask(
                            "[bright_yellow]Enter X.AI API key (leave blank to skip)[/bright_yellow]",
                            password=True,
                            default=""
                        )
                        if api_key:
                            os.environ["XAI_API_KEY"] = api_key
                            console.print("[bright_green]X.AI API key set for this session[/bright_green]")
                        else:
                            console.print("[yellow]No API key provided. X.AI features may not work correctly.[/yellow]")
                    
                    # If user selects gemini, prompt for API key if not set
                    elif new_provider == "gemini" and not os.environ.get("GEMINI_API_KEY"):
                        api_key = Prompt.ask(
                            "[bright_yellow]Enter Gemini API key (leave blank to skip)[/bright_yellow]",
                            password=True,
                            default=""
                        )
                        if api_key:
                            os.environ["GEMINI_API_KEY"] = api_key
                            console.print("[bright_green]Gemini API key set for this session[/bright_green]")
                        else:
                            console.print("[yellow]No API key provided. Gemini features may not work correctly.[/yellow]")
                    
                    session_provider[0] = new_provider
                    console.print(f"[bright_green]AI provider changed to {new_provider}[/bright_green]")
                    if herd_config:
                        herd_config.set_provider(new_provider)
                        console.print(f"[bright_green]Provider persisted as {new_provider}[/bright_green]")
                        
                        # Handle X.AI API key validation
                        if new_provider == "xai":
                            api_key = herd_config.get_api_key("xai")
                            if not api_key or not validate_xai_api_key(api_key):
                                while True:
                                    api_key = Prompt.ask(
                                        "[bright_yellow]Enter X.AI API key (required for X.AI features)[/bright_yellow]",
                                        password=True,
                                        default=""
                                    )
                                    if not api_key:
                                        console.print("[bold yellow]No API key provided. X.AI features will not work until a valid key is set.[/bold yellow]")
                                        break
                                    if validate_xai_api_key(api_key):
                                        herd_config.set_api_key("xai", api_key)
                                        console.print("[bright_green]X.AI API key saved and validated.[/bright_green]")
                                        break
                                    else:
                                        console.print("[bold red]Invalid X.AI API key. Please try again.[/bold red]")
                                        
                        # Handle Gemini API key validation
                        elif new_provider == "gemini":
                            api_key = herd_config.get_api_key("gemini")
                            if not api_key or not validate_gemini_api_key(api_key):
                                while True:
                                    api_key = Prompt.ask(
                                        "[bright_yellow]Enter Gemini API key (required for Gemini features)[/bright_yellow]",
                                        password=True,
                                        default=""
                                    )
                                    if not api_key:
                                        console.print("[bold yellow]No API key provided. Gemini features will not work until a valid key is set.[/bold yellow]")
                                        break
                                    if validate_gemini_api_key(api_key):
                                        herd_config.set_api_key("gemini", api_key)
                                        console.print("[bright_green]Gemini API key saved and validated.[/bright_green]")
                                        break
                                    else:
                                        console.print("[bold red]Invalid Gemini API key. Please try again.[/bold red]")
                else:
                    console.print(f"[bold bright_red]Invalid provider selection: {provider_choice}[/bold bright_red]")
            except ValueError:
                console.print(f"[bold bright_red]Invalid selection: {provider_choice}[/bold bright_red]")
        elif setting_choice == "3":
            # Ollama model selection
            try:
                from herd_ai.utils.ollama import (
                    check_ollama_running, 
                    get_available_models,
                    get_system_resources,
                    check_model_compatibility,
                    get_recommended_models
                )
                
                # Check if Ollama is running
                if not check_ollama_running():
                    console.print("[bold bright_red]Ollama is not running. Please start the Ollama service.[/bold bright_red]")
                    continue
                
                # Show a spinner while loading models and checking system resources
                with console.status("[bright_cyan]Loading Ollama models and checking system compatibility...[/bright_cyan]", spinner="dots") as status:
                    # Get system resources
                    system_resources = get_system_resources()
                    
                    # Get available models
                    available_models = get_available_models()
                    
                    # Get current model from config
                    if herd_config:
                        current_model = herd_config.get_ollama_model() or OLLAMA_TEXT_MODEL
                    else:
                        current_model = OLLAMA_TEXT_MODEL
                    
                    # Get recent models
                    recent_models = []
                    if herd_config:
                        recent_models = herd_config.get_recent_ollama_models()
                
                # Display system information
                system_info = (
                    f"CPU: [bright_yellow]{system_resources['cpu_count']} cores[/bright_yellow] "
                    f"([bright_yellow]{system_resources['cpu_threads']} threads[/bright_yellow])\n"
                    f"RAM: [bright_yellow]{system_resources['ram_total_gb']}GB[/bright_yellow] total, "
                    f"[bright_yellow]{system_resources['ram_available_gb']}GB[/bright_yellow] available\n"
                )
                
                # Add GPU info if available
                if system_resources["gpu_info"]:
                    gpu_info = []
                    for gpu in system_resources["gpu_info"]:
                        gpu_info.append(
                            f"- {gpu['name']}: [bright_yellow]{gpu['vram_total_gb']}GB[/bright_yellow] VRAM "
                            f"([bright_yellow]{gpu['vram_free_gb']}GB[/bright_yellow] free)"
                        )
                    system_info += "GPUs:\n" + "\n".join(gpu_info)
                else:
                    system_info += "[dim]No compatible GPUs detected[/dim]"
                
                # Create a panel with system information
                console.print(Panel(
                    system_info,
                    title="[bold bright_yellow]System Resources[/bold bright_yellow]",
                    border_style="bright_blue",
                    box=box.ROUNDED,
                    padding=(1, 2)
                ))
                
                # If no models found or error
                if not available_models:
                    console.print("[bold bright_red]No Ollama models found. Please install models using 'ollama pull <model>'.[/bold bright_red]")
                    continue
                
                # Create a table of available models with compatibility info
                models_table = Table(
                    box=box.ROUNDED,
                    title="[bold bright_yellow]Available Ollama Models[/bold bright_yellow]",
                    show_header=True,
                    header_style="bold bright_cyan",
                    border_style="bright_blue",
                    padding=(0, 1)
                )
                
                models_table.add_column("#", style="dim", justify="right")
                models_table.add_column("Model", style="bright_green")
                models_table.add_column("Size", style="bright_yellow")
                models_table.add_column("Family", style="bright_magenta")
                models_table.add_column("Compatibility", style="bright_cyan")
                
                # Check compatibility for each model
                model_choices = []
                index_to_model = {}
                model_to_index = {}
                
                for i, model in enumerate(available_models, 1):
                    model_name = model.get("name", "")
                    model_choices.append(str(i))
                    index_to_model[i] = model_name
                    model_to_index[model_name] = i
                    
                    # Check model compatibility
                    compatibility = check_model_compatibility(model_name, system_resources)
                    compat_message = compatibility.get("message", "")
                    
                    # Format the message with appropriate styling
                    if "✅" in compat_message:
                        compat_style = "[bright_green]"
                    elif "✓" in compat_message:
                        compat_style = "[green]"
                    elif "⚠️" in compat_message:
                        compat_style = "[yellow]"
                    else:
                        compat_style = "[bright_red]"
                    
                    # Get model details
                    size = model.get("size", "Unknown")
                    if isinstance(size, int):
                        # Convert bytes to human-readable
                        size_gb = size / (1024**3)
                        if size_gb < 1:
                            size_str = f"{size/(1024**2):.1f} MB"
                        else:
                            size_str = f"{size_gb:.1f} GB"
                    else:
                        size_str = str(size)
                    
                    # Get model family info if available
                    family = model.get("details", {}).get("family", "")
                    if not family:
                        family_str = "-"
                    elif isinstance(family, list):
                        family_str = ", ".join(family)
                    else:
                        family_str = str(family)
                    
                    # Mark current model
                    model_indicator = " "
                    if model_name == current_model:
                        model_indicator = "→"
                    
                    models_table.add_row(
                        f"{model_indicator}{i}",
                        model_name,
                        size_str,
                        family_str,
                        f"{compat_style}{compat_message}[/]"
                    )
                
                # Show recent models section if available
                if recent_models:
                    recent_list = []
                    for i, model_name in enumerate(recent_models, 1):
                        if model_name in model_to_index:
                            model_num = model_to_index[model_name]
                            recent_list.append(f"[bright_yellow]{i}[/bright_yellow]: [bright_green]{model_name}[/bright_green] (#{model_num})")
                    
                    if recent_list:
                        console.print(Panel(
                            "\n".join(recent_list),
                            title="[bold bright_yellow]Recently Used Models[/bold bright_yellow]",
                            border_style="bright_blue",
                            box=box.ROUNDED,
                            padding=(1, 1)
                        ))
                
                # Display the table
                console.print(models_table)
                
                # Prompt for model selection
                model_choice = Prompt.ask(
                    f"[bright_yellow]Select model by number (current: {current_model})[/bright_yellow]",
                    choices=model_choices + ["r1", "r2", "r3", "r4", "r5", "c", "q"],
                    default="q"
                )
                
                # Handle recent model shortcuts (r1-r5)
                if model_choice.startswith("r") and len(model_choice) == 2:
                    try:
                        recent_idx = int(model_choice[1]) - 1
                        if 0 <= recent_idx < len(recent_models):
                            model_choice = str(model_to_index.get(recent_models[recent_idx], "q"))
                        else:
                            model_choice = "q"
                    except ValueError:
                        model_choice = "q"
                
                # Check if they want to cancel
                if model_choice == "q":
                    console.print("[dim]Cancelled model selection[/dim]")
                    continue
                
                # Check if they want to clear the model selection
                if model_choice == "c":
                    if herd_config:
                        herd_config.clear_ollama_model()
                    console.print(f"[bright_green]Cleared model selection. Using default model: {OLLAMA_TEXT_MODEL}[/bright_green]")
                    continue
                
                try:
                    selected_index = int(model_choice)
                    if selected_index in index_to_model:
                        selected_model = index_to_model[selected_index]
                        
                        # Check compatibility
                        compatibility = check_model_compatibility(selected_model, system_resources)
                        if not compatibility.get("can_run", False):
                            # Get user confirmation for incompatible models
                            confirm = Prompt.ask(
                                f"[bold bright_red]Warning:[/bold bright_red] {compatibility.get('message', '')}. Use anyway?",
                                choices=["y", "n"],
                                default="n"
                            )
                            
                            if confirm.lower() != "y":
                                console.print("[dim]Cancelled selection of incompatible model[/dim]")
                                continue
                        
                        # Save the selection
                        if herd_config:
                            herd_config.set_ollama_model(selected_model)
                        
                        console.print(f"[bright_green]Ollama model set to: {selected_model}[/bright_green]")
                    else:
                        console.print(f"[bold bright_red]Invalid model selection: {model_choice}[/bold bright_red]")
                except ValueError:
                    console.print(f"[bold bright_red]Invalid selection: {model_choice}[/bold bright_red]")
            except ImportError as e:
                console.print(f"[bold bright_red]Error loading Ollama utilities: {e}[/bold bright_red]")
            except Exception as e:
                console.print(f"[bold bright_red]Error selecting Ollama model: {e}[/bold bright_red]")

def main(cli_args=None, omni_paths=None):
    """
    Main entry point for the HERD AI CLI.
    
    Args:
        cli_args: Directory to process (if None, will prompt)
        omni_paths: Dictionary of paths for various operations
    """
    if omni_paths is None:
        omni_paths = {}
    
    # Show welcome banner
    console.print(HERD_LOGO)
    
    parser = argparse.ArgumentParser(description="HERD AI - Document & Code Intelligence")
    parser.add_argument("--dir", "-d", required=False, help="Project directory (defaults to current directory)")
    parser.add_argument("--version", "-v", action="version", version="HERD AI v0.4")
    parser.add_argument("--quiet", "-q", action="store_true", help="Reduce output verbosity")
    parser.add_argument("--force", "-f", action="store_true", help="Force operations even when cached results exist")
    parser.add_argument("--provider", type=str, choices=AI_PROVIDERS, default=None,
                       help=f"AI provider to use (default: {DEFAULT_AI_PROVIDER})")
    parser.add_argument("--api-key", type=str, help="API key for selected provider (if needed)")
    
    # Add subparsers for specific tools
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Citations parser
    citations_parser = subparsers.add_parser("citations", help="Extract citations from documents")
    citations_parser.add_argument("--recursive", "-r", action="store_true", help="Process subdirectories recursively")
    citations_parser.add_argument("--styles", "-s", nargs="+", 
                                  choices=["apa", "mla", "chicago", "ieee", "vancouver"], 
                                  default=["apa"], 
                                  help="Citation styles to extract (default: apa)")
    citations_parser.add_argument("--outputs", "-o", nargs="+", 
                                  choices=["md", "json", "txt", "bib", "mla", "chicago", "ieee"], 
                                  default=["md"], 
                                  help="Output formats (default: md)")
    
    # Idealize parser
    idealize_parser = subparsers.add_parser("idealize", help="Create idealized versions of content")
    idealize_parser.add_argument("--recursive", "-r", action="store_true", help="Process subdirectories recursively")
    idealize_parser.add_argument("--exclude", "-e", nargs="+", 
                                default=[], 
                                help="File extensions to exclude (e.g., '.py .js')")
    
    # Docs parser
    docs_parser = subparsers.add_parser("docs", help="Generate project documentation")
    docs_parser.add_argument("--recursive", "-r", action="store_true", help="Process subdirectories recursively")
    
    # Parse actual command line arguments
    if cli_args:
        # If cli_args is a string, split it
        if isinstance(cli_args, str):
            import shlex
            cli_args = shlex.split(cli_args)
        args = parser.parse_args(cli_args)
    else:
        args = parser.parse_args()
    # Always use the provided directory argument if present, otherwise use current working directory.
    if hasattr(args, 'dir') and args.dir:
        root = Path(args.dir)
    else:
        root = Path.cwd()
        console.print(f"[dim]No directory specified, using current directory:[/dim] [bright_yellow]{root}[/bright_yellow]")

    # Handle provider choice and API key
    provider = args.provider
    # If provider not specified in args, try to get from config
    if provider is None and herd_config:
        provider = herd_config.get_provider()
        if provider:
            console.print(f"[dim]Using provider from config:[/dim] [bright_yellow]{provider}[/bright_yellow]")
    
    # If still None, use default
    if provider is None:
        provider = DEFAULT_AI_PROVIDER
    
    if args.api_key:
        if provider == "xai":
            os.environ["XAI_API_KEY"] = args.api_key
            console.print(f"[bright_green]X.AI API key set from command line[/bright_green]")
        elif provider == "gemini":
            os.environ["GEMINI_API_KEY"] = args.api_key
            console.print(f"[bright_green]Gemini API key set from command line[/bright_green]")
    elif provider == "xai" and herd_config:
        # Try to get API key from config
        api_key = herd_config.get_api_key("xai")
        if api_key:
            os.environ["XAI_API_KEY"] = api_key
            console.print(f"[bright_green]X.AI API key loaded from config[/bright_green]")
    elif provider == "gemini" and herd_config:
        # Try to get API key from config
        api_key = herd_config.get_api_key("gemini")
        if api_key:
            os.environ["GEMINI_API_KEY"] = api_key
            console.print(f"[bright_green]Gemini API key loaded from config[/bright_green]")

    # Validate directory
    while not root.exists() or not root.is_dir():
        console.print(f"[bold bright_red]Invalid directory:[/bold bright_red] {root}")
        root_input = Prompt.ask("[bright_yellow]Please enter a valid project directory[/bright_yellow]")
        root = Path(root_input.strip())

    # Set up paths
    _, omni_paths = setup_paths(root, omni_paths)
    
    # Process specific command if provided
    if hasattr(args, 'command') and args.command:
        try:
            def cli_log_callback(msg: str):
                # Strip existing rich tags for clean styling
                # This regex handles both [tag] and [/tag] formats
                plain_msg = re.sub(r"\[/?[a-zA-Z0-9_\s]+?\]", "", msg)
                # Remove any potentially unmatched closing tags
                plain_msg = plain_msg.replace("[/]", "")
                console.print(plain_msg)
            
            if args.command == "citations":
                from herd_ai.citations import process_directory as process_citations
                console.print(f"[bold cyan]Extracting Citations from {root}[/bold cyan]")
                console.print(f"[dim]Styles: {', '.join(args.styles)}[/dim]")
                console.print(f"[dim]Outputs: {', '.join(args.outputs)}[/dim]")
                
                result = process_citations(
                    root, 
                    recursive=args.recursive, 
                    styles=args.styles, 
                    outputs=args.outputs,
                    provider=provider,
                    log_callback=cli_log_callback
                )
                
                if result.get('success', False):
                    console.print(f"[bold green]✅ Citations extracted successfully![/bold green]")
                    console.print(f"[green]Found {result.get('unique_citations', 0)} unique citations across {result.get('files_processed', 0)} files.[/green]")
                    if 'outputs' in result and result['outputs']:
                        console.print("[blue]Output files:[/blue]")
                        for style, files in result.get('outputs', {}).items():
                            for fmt, path in files.items():
                                console.print(f"  [yellow]{style.upper()} ({fmt})[/yellow]: {path}")
                else:
                    console.print(f"[bold red]❌ Citation extraction failed: {result.get('error', 'Unknown error')}[/bold red]")
                
                return  # Exit after completing the command
                
            elif args.command == "idealize":
                from herd_ai.idealize import idealize_directory
                exclude_ext = set(args.exclude) if args.exclude else set()
                console.print(f"[bold cyan]Idealizing content in {root}[/bold cyan]")
                console.print(f"[dim]Recursive: {args.recursive}, Excluded extensions: {', '.join(exclude_ext) or 'None'}[/dim]")
                
                result = idealize_directory(
                    root,
                    recursive=args.recursive,
                    exclude_ext=exclude_ext,
                    provider=provider,
                    log_callback=cli_log_callback
                )
                
                if result.get('success', False):
                    console.print(f"[bold green]✅ Content idealization completed![/bold green]")
                    console.print(f"[green]Processed {result.get('files_processed', 0)} files and idealized {result.get('files_idealized', 0)} files.[/green]")
                    console.print(f"[green]Output directory: {result.get('output_dir', 'Unknown')}[/green]")
                    console.print(f"[green]Backup directory: {result.get('backup_dir', 'Unknown')}[/green]")
                else:
                    console.print(f"[bold red]❌ Content idealization failed: {result.get('error', 'Unknown error')}[/bold red]")
                
                return  # Exit after completing the command
                
            elif args.command == "docs":
                from herd_ai.docs import generate_docs
                console.print(f"[bold cyan]Generating documentation for {root}[/bold cyan]")
                console.print(f"[dim]Recursive: {args.recursive}[/dim]")
                
                result = generate_docs(
                    root,
                    recursive=args.recursive,
                    provider=provider
                )
                
                if result.get('success', False):
                    if result.get('readme_path'):
                        console.print(f"[bold green]✅ Documentation generated successfully![/bold green]")
                        console.print(f"[green]Generated README.md at: {result['readme_path']}[/green]")
                        console.print(f"[green]Processed {result.get('files_processed', 0)} files.[/green]")
                    else:
                        console.print(f"[yellow]⚠️ No README.md was generated: {result.get('message', 'No applicable files found')}[/yellow]")
                else:
                    console.print(f"[bold red]❌ Documentation generation failed: {result.get('message', 'Unknown error')}[/bold red]")
                    if 'error' in result:
                        console.print(f"[red]Error details: {result['error']}[/red]")
                
                return  # Exit after completing the command
        
        except Exception as e:
            console.print(f"[bold red]❌ Error executing {args.command}:[/bold red] {str(e)}")
            return

    # Launch the interactive interface if no specific command was provided
    rich_interface(root, omni_paths, provider)

if __name__ == "__main__":
    # Add code to handle direct execution
    import sys
    from pathlib import Path
    
    # Get the current directory and parent
    current_dir = Path(__file__).resolve().parent
    parent_dir = current_dir.parent
    
    # Add parent directory to path for imports
    sys.path.insert(0, str(parent_dir))
    
    # Call the main function with a nice startup animation
    with console.status("[bold bright_green]Starting HERD AI...", spinner="dots"):
        time.sleep(1)  # Brief pause for effect
        main()

# --- Accessibility & Theming Note ---
# This interface is designed for clarity and accessibility.
# - High contrast elements with consistent color coding
# - Clear visual hierarchy with icons and spacing
# - Logical navigation flow with numbered options
# - Consistent interaction patterns
# - Progress indicators and status feedback
# - Vivid color palette with bright and standard variants for maximum visibility
# For best results, use a terminal with at least 100x32 size.

try:
    from herd_ai.utils.xai import validate_xai_api_key
    from herd_ai.utils.gemini import validate_gemini_api_key
except ImportError:
    def validate_xai_api_key(api_key):
        return True  # fallback: always accept