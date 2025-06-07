# Code Snippets from src/herd_ai/utils/undo_log.py

File: `src/herd_ai/utils/undo_log.py`  
Language: Python  
Extracted: 2025-06-07 05:09:43  

## Snippet 1
Lines 5-12

```Python
This module provides functionality for logging operations performed by Herd AI
and undoing them when requested. It maintains a JSON file with operation history
and parameters needed to revert changes.

Functions:
- log_action: Records an action in the undo log
- undo_last_action: Attempts to undo the most recent action in the log
- list_undo_actions: Returns a list of all logged actions
```

## Snippet 2
Lines 13-23

```Python
- get_undo_log_path: Helper to get the undo log path for a directory
"""

import os
import json
import time
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from rich.console import Console
from rich.table import Table
```

## Snippet 3
Lines 24-45

```Python
# --- Herd AI Utility Imports (robust, fallback style) ---
try:
    from herd_ai.utils import dedupe, analysis, config as herd_config, file, scrambler
except ImportError:
    try:
        from llamacleaner.utils import dedupe, analysis, config as herd_config, file, scrambler
    except ImportError:
        try:
            import utils.dedupe as dedupe
            import utils.analysis as analysis
            import utils.config as herd_config
            import utils.file as file
            import utils.scrambler as scrambler
        except ImportError:
            dedupe = None
            analysis = None
            herd_config = None
            file = None
            scrambler = None

console = Console()
```

## Snippet 4
Lines 51-64

```Python
def log_action(
    directory: Union[str, Path],
    action_type: str,
    parameters: Dict[str, Any]
) -> bool:
    """
    Log an action to the undo log

    Args:
        directory: Directory where the action was performed
        action_type: Type of action (rename, dedupe, etc.)
        parameters: Parameters needed to understand/undo the action

    Returns:
```

## Snippet 5
Lines 76-96

```Python
if log_path.exists():
            try:
                with open(log_path, "r", encoding="utf-8") as f:
                    actions = json.load(f)
            except json.JSONDecodeError:
                console.print(f"[yellow]Warning: Could not parse undo log at {log_path}, creating new log[/yellow]")

        # Append new action
        actions.append({
            "timestamp": time.time(),
            "formatted_time": time.strftime("%Y-%m-%d %H:%M:%S"),
            "action_type": action_type,
            "directory": str(directory),
            "parameters": parameters
        })

        # Write updated log
        with open(log_path, "w", encoding="utf-8") as f:
            json.dump(actions, f, indent=2)

        return True
```

## Snippet 6
Lines 97-100

```Python
except Exception as e:
        console.print(f"[red]Error logging action: {e}[/red]")
        return False
```

## Snippet 7
Lines 103-111

```Python
List all actions in the undo log for a directory

    Args:
        directory: Directory to get the undo log for

    Returns:
        list: List of action dictionaries, most recent first
    """
    try:
```

## Snippet 8
Lines 115-122

```Python
if not log_path.exists():
            return []

        with open(log_path, "r", encoding="utf-8") as f:
            actions = json.load(f)

        # Sort actions by timestamp, most recent first
        return sorted(actions, key=lambda x: x.get("timestamp", 0), reverse=True)
```

## Snippet 9
Lines 123-126

```Python
except Exception as e:
        console.print(f"[red]Error listing undo actions: {e}[/red]")
        return []
```

## Snippet 10
Lines 127-135

```Python
def display_undo_log(directory: Union[str, Path]) -> None:
    """
    Display the undo log as a formatted table

    Args:
        directory: Directory to display the undo log for
    """
    actions = list_undo_actions(directory)
```

## Snippet 11
Lines 136-145

```Python
if not actions:
        console.print("[yellow]No actions found in undo log[/yellow]")
        return

    table = Table(title="Undo Log")
    table.add_column("ID", justify="right", style="cyan")
    table.add_column("Time", style="green")
    table.add_column("Action", style="magenta")
    table.add_column("Parameters", style="bright_blue")
```

## Snippet 12
Lines 147-151

```Python
params = ", ".join(f"{k}={v}" for k, v in action.get("parameters", {}).items())
        table.add_row(
            str(i),
            action.get("formatted_time", "Unknown"),
            action.get("action_type", "Unknown"),
```

## Snippet 13
Lines 157-164

```Python
def undo_last_action(directory: Union[str, Path]) -> bool:
    """
    Undo the most recent action in the log

    Args:
        directory: Directory to undo the action for

    Returns:
```

## Snippet 14
Lines 171-184

```Python
if not actions:
            console.print("[yellow]No actions found to undo[/yellow]")
            return False

        # Get the most recent action
        action = actions[0]
        action_type = action.get("action_type")

        # Display action being undone
        console.print(f"[cyan]Undoing '{action_type}' action from {action.get('formatted_time')}[/cyan]")

        # Handle undo based on action type
        success = False
```

## Snippet 15
Lines 195-206

```Python
if success:
            # Remove the action from the log
            actions.pop(0)
            log_path = get_undo_log_path(directory)
            with open(log_path, "w", encoding="utf-8") as f:
                json.dump(actions, f, indent=2)

            console.print(f"[green]Successfully undid '{action_type}' action[/green]")
            return True
        else:
            console.print(f"[red]Failed to undo '{action_type}' action[/red]")
            return False
```

## Snippet 16
Lines 207-210

```Python
except Exception as e:
        console.print(f"[red]Error undoing action: {e}[/red]")
        return False
```

## Snippet 17
Lines 211-213

```Python
def _undo_rename(directory: Path, action: Dict[str, Any]) -> bool:
    """Helper to undo a rename action by loading and applying the rename log"""
    try:
```

## Snippet 18
Lines 219-230

```Python
if not rename_log.exists():
            console.print("[yellow]No rename log found to restore filenames[/yellow]")
            return False

        with open(rename_log, "r", encoding="utf-8") as f:
            renames = json.load(f)

        # Renames are stored as {"old": "/path/to/original.txt", "new": "/path/to/renamed.txt"}
        # To undo, we reverse the operation
        success_count = 0
        total_count = len(renames)
```

## Snippet 19
Lines 231-234

```Python
for rename in renames:
            old_path = Path(rename.get("old"))
            new_path = Path(rename.get("new"))
```

## Snippet 20
Lines 235-238

```Python
if new_path.exists() and not old_path.exists():
                try:
                    new_path.rename(old_path)
                    success_count += 1
```

## Snippet 21
Lines 245-248

```Python
except Exception as e:
        console.print(f"[red]Error undoing rename: {e}[/red]")
        return False
```

## Snippet 22
Lines 249-251

```Python
def _undo_dedupe(directory: Path, action: Dict[str, Any]) -> bool:
    """Helper to undo a dedupe action by restoring from backup"""
    try:
```

## Snippet 23
Lines 256-259

```Python
if not backup_dir.exists():
            console.print("[yellow]No dedupe backup found to restore files[/yellow]")
            return False
```

## Snippet 24
Lines 261-268

```Python
if console.input("[yellow]Restoring from dedupe backup will copy files back. Continue? (y/n)[/yellow] ").lower() != "y":
            return False

        # Use a simple file copy approach to restore files
        import shutil
        success_count = 0
        total_count = 0
```

## Snippet 25
Lines 270-278

```Python
for file in files:
                total_count += 1
                source = Path(root) / file
                # Determine the relative path from backup_dir to the file
                rel_path = source.relative_to(backup_dir)
                # Construct the target path in the original directory
                target = directory / rel_path

                try:
```

## Snippet 26
Lines 288-291

```Python
except Exception as e:
        console.print(f"[red]Error undoing dedupe: {e}[/red]")
        return False
```

## Snippet 27
Lines 292-294

```Python
def _undo_images(directory: Path, action: Dict[str, Any]) -> bool:
    """Helper to undo image processing actions"""
    try:
```

## Snippet 28
Lines 299-304

```Python
if not backup_dir.exists():
            console.print("[yellow]No image processing backup found[/yellow]")
            return False

        # For renamed images, there should be a rename log
        rename_log = backup_dir / "image_rename_log.json"
```

## Snippet 29
Lines 305-309

```Python
if rename_log.exists():
            with open(rename_log, "r", encoding="utf-8") as f:
                renames = json.load(f)

            success_count = 0
```

## Snippet 30
Lines 310-313

```Python
for rename in renames:
                old_path = Path(rename.get("old"))
                new_path = Path(rename.get("new"))
```

## Snippet 31
Lines 314-317

```Python
if new_path.exists() and not old_path.exists():
                    try:
                        new_path.rename(old_path)
                        success_count += 1
```

## Snippet 32
Lines 327-331

```Python
if console.input("[yellow]Restore original images from backup? (y/n)[/yellow] ").lower() == "y":
            import shutil
            success_count = 0
            total_count = 0
```

## Snippet 33
Lines 334-345

```Python
if file.endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp')):
                        total_count += 1
                        source = Path(root) / file
                        # Determine the relative path from backup_dir to the file
                        rel_path = source.relative_to(backup_dir)
                        # Construct the target path in the original directory
                        target = directory / rel_path

                        try:
                            shutil.copy2(source, target)
                            success_count += 1
                        except Exception as e:
```

## Snippet 34
Lines 352-355

```Python
except Exception as e:
        console.print(f"[red]Error undoing image processing: {e}[/red]")
        return False
```

## Snippet 35
Lines 357-367

```Python
# Simple CLI for testing
    import argparse

    parser = argparse.ArgumentParser(description="Undo Log Utility")
    parser.add_argument('--dir', '-d', type=str, default=os.getcwd(), help='Project directory')
    parser.add_argument('--list', '-l', action='store_true', help='List undo actions')
    parser.add_argument('--undo', '-u', action='store_true', help='Undo the last action')

    args = parser.parse_args()
    directory = Path(args.dir)
```

## Snippet 36
Lines 370-373

```Python
elif args.undo:
        undo_last_action(directory)
    else:
        console.print("[yellow]No action specified. Use --list or --undo[/yellow]")
```

