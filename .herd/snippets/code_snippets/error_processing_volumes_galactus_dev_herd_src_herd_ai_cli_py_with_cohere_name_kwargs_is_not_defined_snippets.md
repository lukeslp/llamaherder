# Code Snippets from storage/debug_files/error_processing_volumes_galactus_dev_herd_src_herd_ai_cli_py_with_cohere_name_kwargs_is_not_defined.py

File: `storage/debug_files/error_processing_volumes_galactus_dev_herd_src_herd_ai_cli_py_with_cohere_name_kwargs_is_not_defined.py`  
Language: Python  
Extracted: 2025-06-07 05:08:24  

## Snippet 1
Lines 6-91

```Python
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
```

## Snippet 2
Lines 92-105

```Python
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
```

## Snippet 3
Lines 106-112

```Python
__||__@(    )___||___(o  o)___||______#`(.'( . ( (',)_____||__
            --||----"--"----||----`--'----||-------'\\_.).(_.). )------||--
                ||            ||       `||~|||~~|""||  `W W    W W      ||
            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

                    Document & Code Intelligence v0.7
```

## Snippet 4
Lines 113-133

```Python
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
```

## Snippet 5
Lines 134-150

```Python
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
```

## Snippet 6
Lines 153-159

```Python
if omni_paths is None:
        omni_paths = {}

    # Create .herd in the target directory
    base_dir = root / ".herd"
    base_dir.mkdir(exist_ok=True)
```

## Snippet 7
Lines 164-175

```Python
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
```

## Snippet 8
Lines 177-180

```Python
if key not in omni_paths:
            omni_paths[key] = base_dir / subdir

        # Convert string paths to Path objects
```

## Snippet 9
Lines 181-187

```Python
if isinstance(omni_paths[key], str):
            omni_paths[key] = Path(omni_paths[key])

        # Create directory
        omni_paths[key].mkdir(exist_ok=True, parents=True)
        logger.debug(f"Created directory: {omni_paths[key]}")
```

## Snippet 10
Lines 188-196

```Python
# Set up file paths
    file_paths = {
        "log": "log.txt",
        "undo_log": "undo_log.json",
        "citations_md": "citations.md",
        "citations_bib": "citations.bib",
        "api_creds": "api_credentials.txt"
    }
```

## Snippet 11
Lines 199-202

```Python
if key not in omni_paths:
            omni_paths[key] = base_dir / filename

        # Convert string paths to Path objects
```

## Snippet 12
Lines 217-224

```Python
Clear the cache directory for the specified project path.

    Args:
        directory: The project root directory. Cache will be cleaned from .herd/cache

    Returns:
        Dictionary with operation results
    """
```

## Snippet 13
Lines 225-231

```Python
if directory is None:
        directory = Path.cwd()

    # Set up paths to ensure the cache directory exists
    _, paths = setup_paths(directory)
    cache_dir = paths["cache_dir"]  # Get cache_dir from omni_paths
```

## Snippet 14
Lines 232-237

```Python
# Count files before deletion for reporting
    files_removed = 0
    space_saved = 0

    try:
        # Get size information before deletion
```

## Snippet 15
Lines 239-245

```Python
if file.is_file():
                try:
                    space_saved += file.stat().st_size
                    files_removed += 1
                except:
                    pass
```

## Snippet 16
Lines 248-253

```Python
if file.is_file():
                try:
                    file.unlink()
                except Exception as e:
                    logger.error(f"Error removing {file}: {e}")
```

## Snippet 17
Lines 254-258

```Python
console.print(f"[green]Cleared {files_removed} cached files, freeing {space_saved / (1024*1024):.2f} MB[/green]")
        return {
            "success": True,
            "files_removed": files_removed,
            "space_saved": space_saved,
```

## Snippet 18
Lines 261-269

```Python
except Exception as e:
        error_msg = f"Error clearing cache: {e}"
        console.print(f"[red]{error_msg}[/red]")
        return {
            "success": False,
            "error": str(e),
            "message": error_msg
        }
```

## Snippet 19
Lines 270-293

```Python
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
```

## Snippet 20
Lines 295-325

```Python
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
```

## Snippet 21
Lines 330-334

```Python
"fn": None,  # Special handler for the report function
        "type": "analysis_report",
        "args": [],
        "log": False,
        "description": "Analyze documents, show stats, and export summary report"
```

## Snippet 22
Lines 336-344

```Python
]

UTILITY_ACTIONS = [
    {
        "name": " • Scramble Files",
        "fn": scramble_directory,
        "type": "scrambler",
        "args": [],
        "log": True,
```

## Snippet 23
Lines 346-352

```Python
},
    {
        "name": " • Sample Files",
        "fn": generate_sample_files,
        "type": "scrambler_sample",
        "args": [],
        "log": True,
```

## Snippet 24
Lines 354-364

```Python
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
```

## Snippet 25
Lines 365-369

```Python
"fn": None,  # Special handler for GUI launch
        "type": "gui",
        "args": [],
        "log": False,
        "description": "Launch the Herd AI GUI web application"
```

## Snippet 26
Lines 370-386

```Python
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
```

## Snippet 27
Lines 387-424

```Python
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
```

## Snippet 28
Lines 426-428

```Python
def create_header_with_menu(selected=None, project_path=None, provider=None):
    # Create info strings
    info_lines = []
```

## Snippet 29
Lines 431-442

```Python
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
```

## Snippet 30
Lines 443-457

```Python
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
```

## Snippet 31
Lines 467-470

```Python
else:
            left_action = ""

        # Utility task (right)
```

## Snippet 32
Lines 475-479

```Python
else:
            right_action = ""

        menu_table.add_row(left_action, right_action)
```

## Snippet 33
Lines 486-513

```Python
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
```

## Snippet 34
Lines 514-526

```Python
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
```

## Snippet 35
Lines 536-540

```Python
if provider is None:
            # Fall back to DEFAULT_AI_PROVIDER from config
            config = get_config_module()
            provider = config.DEFAULT_AI_PROVIDER
```

## Snippet 36
Lines 548-553

```Python
# Strip existing rich tags for clean styling
        plain_msg = re.sub(r"\[/?[a-zA-Z0-9_\s]+?\]", "", msg)
        # Remove any potentially unmatched closing tags
        plain_msg = plain_msg.replace("[/]", "")
        console.print(plain_msg)
```

## Snippet 37
Lines 558-566

```Python
while True:
            console.clear()
            console.print(create_header_with_menu(selected_action, session_root[0], session_provider[0]))

            # Get user input
            action_count = len(PRIMARY_ACTIONS) + len(UTILITY_ACTIONS)
            special_keys = list(SPECIAL_ACTIONS.keys())

            # If readchar is available, use arrow key navigation
```

## Snippet 38
Lines 574-576

```Python
if key == readchar.key.UP and selected_action > 1:
                    selected_action -= 1
                    continue
```

## Snippet 39
Lines 577-579

```Python
elif key == readchar.key.DOWN and selected_action < action_count:
                    selected_action += 1
                    continue
```

## Snippet 40
Lines 595-606

```Python
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
```

## Snippet 41
Lines 607-615

```Python
for i, action in enumerate(PRIMARY_ACTIONS, 1):
                            primary_table.add_row(str(i), action["name"].strip(), action["description"])
                        utility_table = Table(box=box.SIMPLE, show_header=True)
                        utility_table.add_column("#", style="bright_cyan", justify="right", width=3)
                        utility_table.add_column("Task", style="bright_green")
                        utility_table.add_column("Description", style="dim")
                        utility_title = Text("Utilities")
                        utility_title.stylize("bold bright_magenta")
                        utility_table.title = utility_title
```

## Snippet 42
Lines 616-624

```Python
for i, action in enumerate(UTILITY_ACTIONS, len(PRIMARY_ACTIONS) + 1):
                            utility_table.add_row(str(i), action["name"].strip(), action["description"])
                        special_table = Table(box=box.SIMPLE, show_header=True)
                        special_table.add_column("Key", style="bright_cyan", justify="center", width=3)
                        special_table.add_column("Command", style="bright_green")
                        special_table.add_column("Description", style="dim")
                        special_title = Text("Special Commands")
                        special_title.stylize("bold bright_yellow")
                        special_table.title = special_title
```

## Snippet 43
Lines 625-647

```Python
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
```

## Snippet 44
Lines 648-653

```Python
if action_type == "quit":
                        console.print("[bold bright_red]Exiting HERD AI. Goodbye![/bold bright_red]")
                        sys.exit(0)
                    # Add more special actions as needed
                    continue
```

## Snippet 45
Lines 655-660

```Python
elif key in special_keys:
                    choice = key

                else:
                    # Try interpreting as a number
                    try:
```

## Snippet 46
Lines 663-665

```Python
if 1 <= num <= action_count:
                                selected_action = num
                            continue
```

## Snippet 47
Lines 668-670

```Python
except Exception:
                        continue
                    try:
```

## Snippet 48
Lines 673-675

```Python
if 1 <= num <= action_count:
                                selected_action = num
                            continue
```

## Snippet 49
Lines 676-679

```Python
elif key == 'q':
                            break
                        else:
                            continue
```

## Snippet 50
Lines 685-692

```Python
prompt_text = f"[bright_green]Action[/bright_green] ([bright_cyan]1-{action_count}[/bright_cyan], [bright_cyan]n[/bright_cyan]=next, [bright_cyan]p[/bright_cyan]=prev, {', '.join(f'[bright_cyan]{k}[/bright_cyan]' for k in special_keys)})"
                choice = Prompt.ask(
                    prompt_text,
                    choices=choices,
                    default=str(selected_action)
                )

                # Handle navigation commands
```

## Snippet 51
Lines 694-696

```Python
if selected_action < action_count:
                        selected_action += 1
                    continue
```

## Snippet 52
Lines 698-701

```Python
if selected_action > 1:
                        selected_action -= 1
                    continue
```

## Snippet 53
Lines 715-731

```Python
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
```

## Snippet 54
Lines 732-746

```Python
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
```

## Snippet 55
Lines 747-761

```Python
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
```

## Snippet 56
Lines 762-792

```Python
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
```

## Snippet 57
Lines 796-803

```Python
# Handle number selection
                try:
                    selected_action = int(choice)
                    # Continue to process
                except ValueError:
                    console.print(f"[bold bright_red]Invalid option: {choice}[/bold bright_red]")
                    continue
```

## Snippet 58
Lines 811-831

```Python
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
```

## Snippet 59
Lines 832-848

```Python
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
```

## Snippet 60
Lines 859-861

```Python
if not gui_path:
                        console.print("[bold red]Error: Could not find herd_gui.py[/bold red]")
                        console.print("[yellow]Searched in the following locations:[/yellow]")
```

## Snippet 61
Lines 862-866

```Python
for path in possible_paths:
                            console.print(f"  - {path.resolve()}")
                        Prompt.ask("[bright_yellow]Press Enter to return to menu[/bright_yellow]")
                        continue
```

## Snippet 62
Lines 867-874

```Python
# Launch the GUI using subprocess
                    console.print(f"[cyan]Found GUI at: {gui_path}[/cyan]")
                    console.print(f"[cyan]Starting web server at http://localhost:4343[/cyan]")
                    console.print("[yellow]GUI will launch in a separate window. Close this terminal when done.[/yellow]")

                    subprocess.run([sys.executable, str(gui_path)])
                    continue
```

## Snippet 63
Lines 875-880

```Python
except Exception as e:
                    console.print(f"[bold red]Error launching GUI: {e}[/bold red]")
                    traceback.print_exc()
                    Prompt.ask("[bright_yellow]Press Enter to return to menu[/bright_yellow]")
                    continue
```

## Snippet 64
Lines 881-886

```Python
console.clear()
            console.print(header)

            # Process action
            try:
                # FUNCTION-BASED OPERATIONS
```

## Snippet 65
Lines 896-902

```Python
console.print(f"[bright_cyan]Scanning for duplicates in {directory}...[/bright_cyan]")
                            with console.status("[bright_cyan]Scanning files...[/bright_cyan]", spinner="dots"):
                                # Initialize and scan
                                detector = DuplicateDetector(directory, recursive)
                                results = detector.scan_directory()

                            # Get duplicate counts
```

## Snippet 66
Lines 909-911

```Python
if total_dupes > 0 or similar_text_count > 0:
                                space_saved = format_size(results['potential_space_saving'])
                                console.print(Panel(
```

## Snippet 67
Lines 913-918

```Python
f"[bright_green]Found {similar_text_count} similar text files[/bright_green]\n"
                                    f"[bright_yellow]Potential space savings: {space_saved}[/bright_yellow]",
                                    title="[bold bright_yellow]Deduplication Results[/bold bright_yellow]",
                                    border_style="bright_blue",
                                    box=box.ROUNDED,
                                    padding=(1, 2)
```

## Snippet 68
Lines 950-954

```Python
if delete_action:
                                        with console.status("[bright_cyan]Deleting duplicates...[/bright_cyan]", spinner="dots"):
                                            deletion_result = detector.delete_duplicates(keep_first=True)

                                        space_saved = format_size(deletion_result['total_space_saved'])
```

## Snippet 69
Lines 1014-1018

```Python
# Prompt for output formats
                            format_input = Prompt.ask(
                                "[bright_yellow]Which output format(s) do you want?[/bright_yellow] (md, json, txt, bib, mla, chicago, ieee) [comma-separated, default: md]",
                                default="md"
                            )
```

## Snippet 70
Lines 1023-1027

```Python
# Prompt for citation styles
                            style_input = Prompt.ask(
                                "[bright_yellow]Which citation style(s) do you want?[/bright_yellow] (apa, mla, chicago, ieee, vancouver) [comma-separated, default: apa]",
                                default="apa"
                            )
```

## Snippet 71
Lines 1032-1035

```Python
console.print(f"[dim]Extracting citations in {', '.join(styles)} style(s) with {', '.join(outputs)} output format(s)[/dim]")

                            try:
                                result = action_fn(session_root[0], recursive=action_args[0], styles=styles, outputs=outputs, provider=session_provider[0], log_callback=log_callback)
```

## Snippet 72
Lines 1049-1053

```Python
# Only process this section once - we'll use a function here
                            try:
                                # Import the correct function
                                from herd_ai.image_processor import process_directory as process_images
```

## Snippet 73
Lines 1054-1057

```Python
# Use existing parameters and call the function directly
                                result = action_fn(session_root[0], recursive=action_args[0], provider=session_provider[0], log_callback=log_callback)

                                console.print(f"[bold bright_green]✅ Image processing completed successfully![/bold bright_green]")
```

## Snippet 74
Lines 1076-1124

```Python
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
```

## Snippet 75
Lines 1126-1139

```Python
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
```

## Snippet 76
Lines 1148-1151

```Python
else:
                            console.print(Panel(
                                f"[bold bright_yellow]⚠️ Analysis Report Partially Completed[/bold bright_yellow]\n\n"
                                f"Report location: [bright_yellow]{output_path}[/bright_yellow]\n"
```

## Snippet 77
Lines 1156-1163

```Python
except Exception as e:
                        console.print(Panel(
                            f"[bold bright_red]❌ Error Generating Analysis Report[/bold bright_red]\n\n"
                            f"Error: {e}",
                            border_style="bright_red",
                            box=box.ROUNDED
                        ))
```

## Snippet 78
Lines 1169-1175

```Python
if not target_dir.exists() or not target_dir.is_dir():
                        console.print(f"[bold bright_red]Invalid directory: {target_dir}[/bold bright_red]")
                        time.sleep(2)
                        selected_action = None
                        continue
                    console.print(f"[dim]Scrambling filenames in [bright_cyan]{target_dir}[/bright_cyan]...[/dim]")
                    count = scramble_directory(target_dir, log_callback=log_callback)
```

## Snippet 79
Lines 1180-1191

```Python
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
```

## Snippet 80
Lines 1235-1242

```Python
if use_log:
                            try:
                                rel_path = filepath.relative_to(session_root[0])
                            except ValueError:
                                rel_path = filepath
                            console.print(f"[dim]Processing → [bright_cyan]{rel_path}[/bright_cyan][/dim]")

                        try:
```

## Snippet 81
Lines 1246-1262

```Python
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
```

## Snippet 82
Lines 1270-1277

```Python
elif action_name == " • Idealize Content":
                                try:
                                    console.print(f"[dim]Idealizing content in [bright_cyan]{filepath}[/bright_cyan][/dim]")
                                    result = action_fn(
                                        filepath,
                                        recursive=action_args[0],
                                        exclude_ext=action_args[1],
                                        provider=session_provider[0],
```

## Snippet 83
Lines 1293-1297

```Python
# Only process this section once - we'll use a function here
                                try:
                                    # Import the correct function
                                    from herd_ai.image_processor import process_directory as process_images
```

## Snippet 84
Lines 1298-1301

```Python
# Use existing parameters and call the function directly
                                    result = action_fn(session_root[0], recursive=action_args[0], provider=session_provider[0], log_callback=log_callback)

                                    console.print(f"[bold bright_green]✅ Image processing completed successfully![/bold bright_green]")
```

## Snippet 85
Lines 1307-1310

```Python
if use_log:
                                    action_fn(filepath, *action_args, log_callback=log_callback, provider=session_provider[0])
                                else:
                                    action_fn(filepath, *action_args, provider=session_provider[0])
```

## Snippet 86
Lines 1312-1316

```Python
except Exception as e:
                            console.print(f"[bold bright_red]Error processing {filepath}: {e}[/bold bright_red]")

                        print_progress_bar(idx, total, f"{action_name}")
```

## Snippet 87
Lines 1320-1323

```Python
else:
                        summary = "No files were successfully processed"
                        console.print(f"[bold yellow]{summary}[/bold yellow]")
```

## Snippet 88
Lines 1326-1328

```Python
# UNKNOWN ACTION TYPE
                else:
                    console.print(f"[bold bright_red]Unknown action type: {action_type}[/bold bright_red]")
```

## Snippet 89
Lines 1329-1334

```Python
except Exception as e:
                console.print(f"[bold bright_red]Error in {action_name}: {e}[/bold bright_red]")
                logger.exception(f"Error in {action_name}")

            # Update content area with completion message after action
            console.print(Panel(
```

## Snippet 90
Lines 1335-1339

```Python
f"[bright_green]{action_name} completed.[/bright_green]\n\nPress ENTER to return to menu, [bold bright_red]'q'[/bold bright_red] to quit",
                title="[bold bright_yellow]Output[/bold bright_yellow]",
                border_style="bright_blue",
                box=box.ROUNDED,
                padding=(1, 2)
```

## Snippet 91
Lines 1340-1347

```Python
))

            console.clear()
            console.print(create_header_with_menu(selected_action, session_root[0], session_provider[0]))

            # Handle input after action completes
            response = Prompt.ask("[bright_green]>[/bright_green]", default="")
```

## Snippet 92
Lines 1353-1357

```Python
except KeyboardInterrupt:
        console.print("[bold yellow]KeyboardInterrupt: Returning to menu...[/bold yellow]")
        # Return to the main menu by recursively calling the function
        return rich_interface(session_root[0], omni_paths, session_provider[0])
```

## Snippet 93
Lines 1359-1361

```Python
if not herd_config:
        print("[ERROR] Config utility not available.")
        return
```

## Snippet 94
Lines 1368-1370

```Python
if not validate_xai_api_key(args.api_key):
            print("[ERROR] Invalid X.AI API key. Please check and try again.")
            return
```

## Snippet 95
Lines 1373-1375

```Python
if not validate_gemini_api_key(args.api_key):
            print("[ERROR] Invalid Gemini API key. Please check and try again.")
            return
```

## Snippet 96
Lines 1380-1382

```Python
if not herd_config:
        print("[ERROR] Config utility not available.")
        return
```

## Snippet 97
Lines 1390-1392

```Python
if not herd_config:
        print("[ERROR] Config utility not available.")
        return
```

## Snippet 98
Lines 1393-1397

```Python
if args.set:
        herd_config.set_provider(args.set)
        print(f"[SUCCESS] Provider set to '{args.set}'.")
    else:
        provider = herd_config.get_provider()
```

## Snippet 99
Lines 1402-1414

```Python
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
```

## Snippet 100
Lines 1420-1424

```Python
if new_path.exists() and new_path.is_dir():
                session_root[0] = new_path
                console.print(f"[bright_green]Working directory changed to {new_path}[/bright_green]")
            else:
                console.print(f"[bold bright_red]Invalid directory: {new_path}[/bold bright_red]")
```

## Snippet 101
Lines 1428-1441

```Python
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
```

## Snippet 102
Lines 1444-1447

```Python
)

            try:
                provider_idx = int(provider_choice) - 1
```

## Snippet 103
Lines 1452-1457

```Python
if new_provider == "xai" and not os.environ.get("XAI_API_KEY"):
                        api_key = Prompt.ask(
                            "[bright_yellow]Enter X.AI API key (leave blank to skip)[/bright_yellow]",
                            password=True,
                            default=""
                        )
```

## Snippet 104
Lines 1465-1470

```Python
elif new_provider == "gemini" and not os.environ.get("GEMINI_API_KEY"):
                        api_key = Prompt.ask(
                            "[bright_yellow]Enter Gemini API key (leave blank to skip)[/bright_yellow]",
                            password=True,
                            default=""
                        )
```

## Snippet 105
Lines 1479-1483

```Python
if herd_config:
                        herd_config.set_provider(new_provider)
                        console.print(f"[bright_green]Provider persisted as {new_provider}[/bright_green]")

                        # Handle X.AI API key validation
```

## Snippet 106
Lines 1493-1495

```Python
if not api_key:
                                        console.print("[bold yellow]No API key provided. X.AI features will not work until a valid key is set.[/bold yellow]")
                                        break
```

## Snippet 107
Lines 1496-1502

```Python
if validate_xai_api_key(api_key):
                                        herd_config.set_api_key("xai", api_key)
                                        console.print("[bright_green]X.AI API key saved and validated.[/bright_green]")
                                        break
                                    else:
                                        console.print("[bold red]Invalid X.AI API key. Please try again.[/bold red]")
```

## Snippet 108
Lines 1513-1515

```Python
if not api_key:
                                        console.print("[bold yellow]No API key provided. Gemini features will not work until a valid key is set.[/bold yellow]")
                                        break
```

## Snippet 109
Lines 1516-1521

```Python
if validate_gemini_api_key(api_key):
                                        herd_config.set_api_key("gemini", api_key)
                                        console.print("[bright_green]Gemini API key saved and validated.[/bright_green]")
                                        break
                                    else:
                                        console.print("[bold red]Invalid Gemini API key. Please try again.[/bold red]")
```

## Snippet 110
Lines 1526-1536

```Python
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
```

## Snippet 111
Lines 1542-1550

```Python
# Show a spinner while loading models and checking system resources
                with console.status("[bright_cyan]Loading Ollama models and checking system compatibility...[/bright_cyan]", spinner="dots") as status:
                    # Get system resources
                    system_resources = get_system_resources()

                    # Get available models
                    available_models = get_available_models()

                    # Get current model from config
```

## Snippet 112
Lines 1551-1557

```Python
if herd_config:
                        current_model = herd_config.get_ollama_model() or OLLAMA_TEXT_MODEL
                    else:
                        current_model = OLLAMA_TEXT_MODEL

                    # Get recent models
                    recent_models = []
```

## Snippet 113
Lines 1572-1577

```Python
for gpu in system_resources["gpu_info"]:
                        gpu_info.append(
                            f"- {gpu['name']}: [bright_yellow]{gpu['vram_total_gb']}GB[/bright_yellow] VRAM "
                            f"([bright_yellow]{gpu['vram_free_gb']}GB[/bright_yellow] free)"
                        )
                    system_info += "GPUs:\n" + "\n".join(gpu_info)
```

## Snippet 114
Lines 1578-1590

```Python
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
```

## Snippet 115
Lines 1591-1610

```Python
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
```

## Snippet 116
Lines 1616-1626

```Python
for i, model in enumerate(available_models, 1):
                    model_name = model.get("name", "")
                    model_choices.append(str(i))
                    index_to_model[i] = model_name
                    model_to_index[model_name] = i

                    # Check model compatibility
                    compatibility = check_model_compatibility(model_name, system_resources)
                    compat_message = compatibility.get("message", "")

                    # Format the message with appropriate styling
```

## Snippet 117
Lines 1631-1637

```Python
elif "⚠️" in compat_message:
                        compat_style = "[yellow]"
                    else:
                        compat_style = "[bright_red]"

                    # Get model details
                    size = model.get("size", "Unknown")
```

## Snippet 118
Lines 1652-1658

```Python
elif isinstance(family, list):
                        family_str = ", ".join(family)
                    else:
                        family_str = str(family)

                    # Mark current model
                    model_indicator = " "
```

## Snippet 119
Lines 1659-1669

```Python
if model_name == current_model:
                        model_indicator = "→"

                    models_table.add_row(
                        f"{model_indicator}{i}",
                        model_name,
                        size_str,
                        family_str,
                        f"{compat_style}{compat_message}[/]"
                    )
```

## Snippet 120
Lines 1674-1677

```Python
if model_name in model_to_index:
                            model_num = model_to_index[model_name]
                            recent_list.append(f"[bright_yellow]{i}[/bright_yellow]: [bright_green]{model_name}[/bright_green] (#{model_num})")
```

## Snippet 121
Lines 1678-1686

```Python
if recent_list:
                        console.print(Panel(
                            "\n".join(recent_list),
                            title="[bold bright_yellow]Recently Used Models[/bold bright_yellow]",
                            border_style="bright_blue",
                            box=box.ROUNDED,
                            padding=(1, 1)
                        ))
```

## Snippet 122
Lines 1690-1697

```Python
# Prompt for model selection
                model_choice = Prompt.ask(
                    f"[bright_yellow]Select model by number (current: {current_model})[/bright_yellow]",
                    choices=model_choices + ["r1", "r2", "r3", "r4", "r5", "c", "q"],
                    default="q"
                )

                # Handle recent model shortcuts (r1-r5)
```

## Snippet 123
Lines 1698-1700

```Python
if model_choice.startswith("r") and len(model_choice) == 2:
                    try:
                        recent_idx = int(model_choice[1]) - 1
```

## Snippet 124
Lines 1701-1704

```Python
if 0 <= recent_idx < len(recent_models):
                            model_choice = str(model_to_index.get(recent_models[recent_idx], "q"))
                        else:
                            model_choice = "q"
```

## Snippet 125
Lines 1715-1719

```Python
if herd_config:
                        herd_config.clear_ollama_model()
                    console.print(f"[bright_green]Cleared model selection. Using default model: {OLLAMA_TEXT_MODEL}[/bright_green]")
                    continue
```

## Snippet 126
Lines 1722-1726

```Python
if selected_index in index_to_model:
                        selected_model = index_to_model[selected_index]

                        # Check compatibility
                        compatibility = check_model_compatibility(selected_model, system_resources)
```

## Snippet 127
Lines 1728-1734

```Python
# Get user confirmation for incompatible models
                            confirm = Prompt.ask(
                                f"[bold bright_red]Warning:[/bold bright_red] {compatibility.get('message', '')}. Use anyway?",
                                choices=["y", "n"],
                                default="n"
                            )
```

## Snippet 128
Lines 1740-1743

```Python
if herd_config:
                            herd_config.set_ollama_model(selected_model)

                        console.print(f"[bright_green]Ollama model set to: {selected_model}[/bright_green]")
```

## Snippet 129
Lines 1748-1752

```Python
except ImportError as e:
                console.print(f"[bold bright_red]Error loading Ollama utilities: {e}[/bold bright_red]")
            except Exception as e:
                console.print(f"[bold bright_red]Error selecting Ollama model: {e}[/bold bright_red]")
```

## Snippet 130
Lines 1761-1773

```Python
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
```

## Snippet 131
Lines 1776-1802

```Python
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
```

## Snippet 132
Lines 1805-1808

```Python
if isinstance(cli_args, str):
            import shlex
            cli_args = shlex.split(cli_args)
        args = parser.parse_args(cli_args)
```

## Snippet 133
Lines 1812-1820

```Python
if hasattr(args, 'dir') and args.dir:
        root = Path(args.dir)
    else:
        root = Path.cwd()
        console.print(f"[dim]No directory specified, using current directory:[/dim] [bright_yellow]{root}[/bright_yellow]")

    # Handle provider choice and API key
    provider = args.provider
    # If provider not specified in args, try to get from config
```

## Snippet 134
Lines 1831-1833

```Python
if provider == "xai":
            os.environ["XAI_API_KEY"] = args.api_key
            console.print(f"[bright_green]X.AI API key set from command line[/bright_green]")
```

## Snippet 135
Lines 1834-1836

```Python
elif provider == "gemini":
            os.environ["GEMINI_API_KEY"] = args.api_key
            console.print(f"[bright_green]Gemini API key set from command line[/bright_green]")
```

## Snippet 136
Lines 1837-1839

```Python
elif provider == "xai" and herd_config:
        # Try to get API key from config
        api_key = herd_config.get_api_key("xai")
```

## Snippet 137
Lines 1840-1842

```Python
if api_key:
            os.environ["XAI_API_KEY"] = api_key
            console.print(f"[bright_green]X.AI API key loaded from config[/bright_green]")
```

## Snippet 138
Lines 1843-1845

```Python
elif provider == "gemini" and herd_config:
        # Try to get API key from config
        api_key = herd_config.get_api_key("gemini")
```

## Snippet 139
Lines 1846-1849

```Python
if api_key:
            os.environ["GEMINI_API_KEY"] = api_key
            console.print(f"[bright_green]Gemini API key loaded from config[/bright_green]")
```

## Snippet 140
Lines 1851-1858

```Python
while not root.exists() or not root.is_dir():
        console.print(f"[bold bright_red]Invalid directory:[/bold bright_red] {root}")
        root_input = Prompt.ask("[bright_yellow]Please enter a valid project directory[/bright_yellow]")
        root = Path(root_input.strip())

    # Set up paths
    _, omni_paths = setup_paths(root, omni_paths)
```

## Snippet 141
Lines 1863-1869

```Python
# Strip existing rich tags for clean styling
                # This regex handles both [tag] and [/tag] formats
                plain_msg = re.sub(r"\[/?[a-zA-Z0-9_\s]+?\]", "", msg)
                # Remove any potentially unmatched closing tags
                plain_msg = plain_msg.replace("[/]", "")
                console.print(plain_msg)
```

## Snippet 142
Lines 1870-1884

```Python
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
```

## Snippet 143
Lines 1893-1897

```Python
else:
                    console.print(f"[bold red]❌ Citation extraction failed: {result.get('error', 'Unknown error')}[/bold red]")

                return  # Exit after completing the command
```

## Snippet 144
Lines 1900-1911

```Python
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
```

## Snippet 145
Lines 1917-1921

```Python
else:
                    console.print(f"[bold red]❌ Content idealization failed: {result.get('error', 'Unknown error')}[/bold red]")

                return  # Exit after completing the command
```

## Snippet 146
Lines 1924-1932

```Python
console.print(f"[bold cyan]Generating documentation for {root}[/bold cyan]")
                console.print(f"[dim]Recursive: {args.recursive}[/dim]")

                result = generate_docs(
                    root,
                    recursive=args.recursive,
                    provider=provider
                )
```

## Snippet 147
Lines 1947-1950

```Python
except Exception as e:
            console.print(f"[bold red]❌ Error executing {args.command}:[/bold red] {str(e)}")
            return
```

## Snippet 148
Lines 1954-1962

```Python
if __name__ == "__main__":
    # Add code to handle direct execution
    import sys
    from pathlib import Path

    # Get the current directory and parent
    current_dir = Path(__file__).resolve().parent
    parent_dir = current_dir.parent
```

## Snippet 149
Lines 1978-1984

```Python
# - Vivid color palette with bright and standard variants for maximum visibility
# For best results, use a terminal with at least 100x32 size.

try:
    from herd_ai.utils.xai import validate_xai_api_key
    from herd_ai.utils.gemini import validate_gemini_api_key
except ImportError:
```

