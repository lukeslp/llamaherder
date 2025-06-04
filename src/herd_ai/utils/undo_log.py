#!/usr/bin/env python3
"""
Undo Log Utility for Herd AI

This module provides functionality for logging operations performed by Herd AI
and undoing them when requested. It maintains a JSON file with operation history
and parameters needed to revert changes.

Functions:
- log_action: Records an action in the undo log
- undo_last_action: Attempts to undo the most recent action in the log
- list_undo_actions: Returns a list of all logged actions 
- get_undo_log_path: Helper to get the undo log path for a directory
"""

import os
import json
import time
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from rich.console import Console
from rich.table import Table

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

def get_undo_log_path(directory: Union[str, Path]) -> Path:
    """Get the path to the undo log file for a directory"""
    directory = Path(directory) if isinstance(directory, str) else directory
    return directory / ".herd" / "undo_log.json"

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
        bool: True if the action was logged successfully
    """
    try:
        directory = Path(directory) if isinstance(directory, str) else directory
        log_path = get_undo_log_path(directory)
        
        # Create .herd directory if it doesn't exist
        log_path.parent.mkdir(exist_ok=True, parents=True)
        
        # Load existing log if it exists
        actions = []
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
    except Exception as e:
        console.print(f"[red]Error logging action: {e}[/red]")
        return False

def list_undo_actions(directory: Union[str, Path]) -> List[Dict[str, Any]]:
    """
    List all actions in the undo log for a directory
    
    Args:
        directory: Directory to get the undo log for
    
    Returns:
        list: List of action dictionaries, most recent first
    """
    try:
        directory = Path(directory) if isinstance(directory, str) else directory
        log_path = get_undo_log_path(directory)
        
        if not log_path.exists():
            return []
        
        with open(log_path, "r", encoding="utf-8") as f:
            actions = json.load(f)
        
        # Sort actions by timestamp, most recent first
        return sorted(actions, key=lambda x: x.get("timestamp", 0), reverse=True)
    except Exception as e:
        console.print(f"[red]Error listing undo actions: {e}[/red]")
        return []

def display_undo_log(directory: Union[str, Path]) -> None:
    """
    Display the undo log as a formatted table
    
    Args:
        directory: Directory to display the undo log for
    """
    actions = list_undo_actions(directory)
    
    if not actions:
        console.print("[yellow]No actions found in undo log[/yellow]")
        return
    
    table = Table(title="Undo Log")
    table.add_column("ID", justify="right", style="cyan")
    table.add_column("Time", style="green")
    table.add_column("Action", style="magenta")
    table.add_column("Parameters", style="bright_blue")
    
    for i, action in enumerate(actions):
        params = ", ".join(f"{k}={v}" for k, v in action.get("parameters", {}).items())
        table.add_row(
            str(i),
            action.get("formatted_time", "Unknown"),
            action.get("action_type", "Unknown"),
            params[:50] + ("..." if len(params) > 50 else "")
        )
    
    console.print(table)

def undo_last_action(directory: Union[str, Path]) -> bool:
    """
    Undo the most recent action in the log
    
    Args:
        directory: Directory to undo the action for
    
    Returns:
        bool: True if the action was successfully undone
    """
    try:
        directory = Path(directory) if isinstance(directory, str) else directory
        actions = list_undo_actions(directory)
        
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
        
        if action_type == "rename":
            success = _undo_rename(directory, action)
        elif action_type == "dedupe":
            success = _undo_dedupe(directory, action)
        elif action_type == "images":
            success = _undo_images(directory, action)
        else:
            console.print(f"[yellow]Undo not implemented for '{action_type}' actions[/yellow]")
            return False
        
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
    except Exception as e:
        console.print(f"[red]Error undoing action: {e}[/red]")
        return False

def _undo_rename(directory: Path, action: Dict[str, Any]) -> bool:
    """Helper to undo a rename action by loading and applying the rename log"""
    try:
        # For rename operations, we check the backup directory for a rename log
        params = action.get("parameters", {})
        backup_dir = directory / ".herd" / "backup"
        rename_log = backup_dir / "rename_log.json"
        
        if not rename_log.exists():
            console.print("[yellow]No rename log found to restore filenames[/yellow]")
            return False
        
        with open(rename_log, "r", encoding="utf-8") as f:
            renames = json.load(f)
        
        # Renames are stored as {"old": "/path/to/original.txt", "new": "/path/to/renamed.txt"}
        # To undo, we reverse the operation
        success_count = 0
        total_count = len(renames)
        
        for rename in renames:
            old_path = Path(rename.get("old"))
            new_path = Path(rename.get("new"))
            
            if new_path.exists() and not old_path.exists():
                try:
                    new_path.rename(old_path)
                    success_count += 1
                    console.print(f"[green]Restored: {new_path.name} → {old_path.name}[/green]")
                except Exception as e:
                    console.print(f"[red]Error restoring {new_path} to {old_path}: {e}[/red]")
        
        console.print(f"[green]Restored {success_count} of {total_count} renamed files[/green]")
        return success_count > 0
    except Exception as e:
        console.print(f"[red]Error undoing rename: {e}[/red]")
        return False

def _undo_dedupe(directory: Path, action: Dict[str, Any]) -> bool:
    """Helper to undo a dedupe action by restoring from backup"""
    try:
        # For dedupe operations, we check if there's a backup directory
        params = action.get("parameters", {})
        backup_dir = directory / ".herd" / "backup" / "dedupe"
        
        if not backup_dir.exists():
            console.print("[yellow]No dedupe backup found to restore files[/yellow]")
            return False
        
        # Ask for confirmation
        if console.input("[yellow]Restoring from dedupe backup will copy files back. Continue? (y/n)[/yellow] ").lower() != "y":
            return False
        
        # Use a simple file copy approach to restore files
        import shutil
        success_count = 0
        total_count = 0
        
        for root, _, files in os.walk(backup_dir):
            for file in files:
                total_count += 1
                source = Path(root) / file
                # Determine the relative path from backup_dir to the file
                rel_path = source.relative_to(backup_dir)
                # Construct the target path in the original directory
                target = directory / rel_path
                
                try:
                    # Create parent directories if they don't exist
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(source, target)
                    success_count += 1
                except Exception as e:
                    console.print(f"[red]Error restoring {source} to {target}: {e}[/red]")
        
        console.print(f"[green]Restored {success_count} of {total_count} files from dedupe backup[/green]")
        return success_count > 0
    except Exception as e:
        console.print(f"[red]Error undoing dedupe: {e}[/red]")
        return False

def _undo_images(directory: Path, action: Dict[str, Any]) -> bool:
    """Helper to undo image processing actions"""
    try:
        # For image processing, check if there's a rename log or backups
        params = action.get("parameters", {})
        backup_dir = directory / ".herd" / "backup" / "images"
        
        if not backup_dir.exists():
            console.print("[yellow]No image processing backup found[/yellow]")
            return False
        
        # For renamed images, there should be a rename log
        rename_log = backup_dir / "image_rename_log.json"
        if rename_log.exists():
            with open(rename_log, "r", encoding="utf-8") as f:
                renames = json.load(f)
            
            success_count = 0
            for rename in renames:
                old_path = Path(rename.get("old"))
                new_path = Path(rename.get("new"))
                
                if new_path.exists() and not old_path.exists():
                    try:
                        new_path.rename(old_path)
                        success_count += 1
                        console.print(f"[green]Restored image name: {new_path.name} → {old_path.name}[/green]")
                    except Exception as e:
                        console.print(f"[red]Error restoring image name {new_path} to {old_path}: {e}[/red]")
            
            if success_count > 0:
                console.print(f"[green]Restored {success_count} image names[/green]")
                return True
        
        # For other image processing, like alt text embedding, offer to restore from backup
        if console.input("[yellow]Restore original images from backup? (y/n)[/yellow] ").lower() == "y":
            import shutil
            success_count = 0
            total_count = 0
            
            for root, _, files in os.walk(backup_dir):
                for file in files:
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
                            console.print(f"[red]Error restoring {source} to {target}: {e}[/red]")
            
            console.print(f"[green]Restored {success_count} of {total_count} images from backup[/green]")
            return success_count > 0
        
        return False
    except Exception as e:
        console.print(f"[red]Error undoing image processing: {e}[/red]")
        return False

if __name__ == "__main__":
    # Simple CLI for testing
    import argparse
    
    parser = argparse.ArgumentParser(description="Undo Log Utility")
    parser.add_argument('--dir', '-d', type=str, default=os.getcwd(), help='Project directory')
    parser.add_argument('--list', '-l', action='store_true', help='List undo actions')
    parser.add_argument('--undo', '-u', action='store_true', help='Undo the last action')
    
    args = parser.parse_args()
    directory = Path(args.dir)
    
    if args.list:
        display_undo_log(directory)
    elif args.undo:
        undo_last_action(directory)
    else:
        console.print("[yellow]No action specified. Use --list or --undo[/yellow]") 