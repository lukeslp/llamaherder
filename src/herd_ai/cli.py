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
from rich.prompt import Prompt, Confirm
from rich.live import Live
from rich import box
from rich.align import Align
from rich.text import Text
from rich.padding import Padding
from rich.style import Style
from rich.columns import Columns
from rich.console import Group
import re
import importlib.util
import asyncio

# Configure logging
logger = logging.getLogger(__name__)
console = Console()

# Ensure 'src' is in the Python path for imports
try:
    # Get the current directory
    current_dir = Path(__file__).resolve().parent
    # Get the parent directory (src)
    src_dir = current_dir.parent
    # Get the project root
    project_root = src_dir.parent
    
    # Add src to Python path if not already there
    if str(src_dir) not in sys.path:
        sys.path.insert(0, str(src_dir))
    
    # Also add project root for direct imports
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
        
    console.print(f"[dim]Python path updated: Added {src_dir} and {project_root}[/dim]")
except Exception as e:
    console.print(f"[yellow]Warning: Could not update Python path: {e}[/yellow]")

# Module import confirmation function
def confirm_module_import(module_name):
    """Print confirmation when a module is successfully imported"""
    console.print(f"[green]✓ Successfully loaded module:[/green] [bold cyan]{module_name}[/bold cyan]")

# Try import as if from a package first, fall back to direct import
console.print("[bold]Loading modules...[/bold]")
try:
    # Package imports (when installed or run as a module)
    try:
        # Try importing each module, with confirmation for each successful import
        modules_loaded = 0
        
        try:
            from herd_ai.rename import process_renames
            confirm_module_import("herd_ai.rename")
            modules_loaded += 1
        except ImportError as e:
            console.print(f"[yellow]Could not import herd_ai.rename: {e}[/yellow]")
        
        try:
            from herd_ai.snippets import process_snippets
            confirm_module_import("herd_ai.snippets")
            modules_loaded += 1
        except ImportError as e:
            console.print(f"[yellow]Could not import herd_ai.snippets: {e}[/yellow]")
        
        try:
            from herd_ai.idealize import process_ideal, idealize_directory
            confirm_module_import("herd_ai.idealize")
            modules_loaded += 1
        except ImportError as e:
            console.print(f"[yellow]Could not import herd_ai.idealize: {e}[/yellow]")
        
        try:
            from herd_ai.docs import generate_docs, export_document_summary
            confirm_module_import("herd_ai.docs")
            modules_loaded += 1
        except ImportError as e:
            console.print(f"[yellow]Could not import herd_ai.docs: {e}[/yellow]")
        
        try:
            from herd_ai.citations import process_file_or_directory
            confirm_module_import("herd_ai.citations")
            modules_loaded += 1
        except ImportError as e:
            console.print(f"[yellow]Could not import herd_ai.citations: {e}[/yellow]")
        
        try:
            from herd_ai.utils.analysis import analyze_documents, generate_document_summary
            confirm_module_import("herd_ai.utils.analysis")
            modules_loaded += 1
        except ImportError as e:
            console.print(f"[yellow]Could not import herd_ai.utils.analysis: {e}[/yellow]")
        
        try:
            from herd_ai.utils.cache import clear_cache
            confirm_module_import("herd_ai.utils.cache")
            modules_loaded += 1
        except ImportError as e:
            console.print(f"[yellow]Could not import herd_ai.utils.cache: {e}[/yellow]")
        
        try:
            from herd_ai.image_processor import process_images_cli, process_directory as process_images
            confirm_module_import("herd_ai.image_processor")
            modules_loaded += 1
        except ImportError as e:
            console.print(f"[yellow]Could not import herd_ai.image_processor: {e}[/yellow]")
        
        try:
            from herd_ai.utils.scrambler import scramble_directory, generate_sample_files
            confirm_module_import("herd_ai.utils.scrambler")
            modules_loaded += 1
        except ImportError as e:
            console.print(f"[yellow]Could not import herd_ai.utils.scrambler: {e}[/yellow]")
        
        try:
            from herd_ai.config import AI_PROVIDERS, DEFAULT_AI_PROVIDER
            confirm_module_import("herd_ai.config")
            modules_loaded += 1
        except ImportError as e:
            console.print(f"[yellow]Could not import herd_ai.config: {e}[/yellow]")
        
        try:
            from herd_ai.utils import config as herd_config
            confirm_module_import("herd_ai.utils.config")
            modules_loaded += 1
        except ImportError as e:
            console.print(f"[yellow]Could not import herd_ai.utils.config: {e}[/yellow]")
        
        if modules_loaded > 0:
            console.print(f"[bold green]✓ Successfully loaded {modules_loaded} herd_ai modules![/bold green]")
            # If we got here, we don't need to try the other import paths
            # But we continue with the rest of the code to ensure fallbacks work if needed
        
    except ImportError:
        # Legacy package imports
        try:
            console.print("[yellow]Falling back to llamacleaner imports...[/yellow]")
            
            from llamacleaner.rename import process_renames
            confirm_module_import("llamacleaner.rename")
            
            from llamacleaner.snippets import process_snippets
            confirm_module_import("llamacleaner.snippets")
            
            from llamacleaner.idealize import process_ideal, idealize_directory
            confirm_module_import("llamacleaner.idealize")
            
            from llamacleaner.docs import generate_docs, export_document_summary
            confirm_module_import("llamacleaner.docs")
            
            from llamacleaner.citations import process_file_or_directory
            confirm_module_import("llamacleaner.citations")
            
            from llamacleaner.utils.analysis import analyze_documents, generate_document_summary
            confirm_module_import("llamacleaner.utils.analysis")
            
            from llamacleaner.utils.cache import clear_cache
            confirm_module_import("llamacleaner.utils.cache")
            
            from llamacleaner.image_processor import process_images_cli, process_directory as process_images
            confirm_module_import("llamacleaner.image_processor")
            
            from llamacleaner.utils.scrambler import scramble_directory, generate_sample_files
            confirm_module_import("llamacleaner.utils.scrambler")
            
            from llamacleaner.config import AI_PROVIDERS, DEFAULT_AI_PROVIDER
            confirm_module_import("llamacleaner.config")
            
            from llamacleaner.utils import config as herd_config
            confirm_module_import("llamacleaner.utils.config")
            
            console.print("[bold green]✓ Successfully loaded all llamacleaner modules![/bold green]")
        except ImportError:
            # Direct imports (when run directly, not as a module)
            console.print("[yellow]Falling back to direct imports...[/yellow]")
            
            from rename import process_renames
            confirm_module_import("rename")
            
            from snippets import process_snippets
            confirm_module_import("snippets")
            
            from idealize import process_ideal, idealize_directory
            confirm_module_import("idealize")
            
            from docs import generate_docs, export_document_summary
            confirm_module_import("docs")
            
            from citations import process_file_or_directory
            confirm_module_import("citations")
            
            from utils.analysis import analyze_documents, generate_document_summary
            confirm_module_import("utils.analysis")
            
            from utils.cache import clear_cache
            confirm_module_import("utils.cache")
            
            from image_processor import process_images_cli, process_directory as process_images
            confirm_module_import("image_processor")
            
            from utils.scrambler import scramble_directory, generate_sample_files
            confirm_module_import("utils.scrambler")
            
            from config import AI_PROVIDERS, DEFAULT_AI_PROVIDER
            confirm_module_import("config")
            
            import utils.config as herd_config
            confirm_module_import("utils.config")
            
            console.print("[bold green]✓ Successfully loaded all direct modules![/bold green]")
except Exception as e:
    print(f"Error importing modules: {e}")
    print("Make sure you're running from the project directory or the package is installed.")
    sys.exit(1)

# Default to XAI when available
DEFAULT_PROVIDER = "xai"

# ASCII Art Banner
BANNER = """
                            ██╗  ██╗███████╗██████╗ ██████╗  
                            ██║  ██║██╔════╝██╔══██╗██╔══██╗ 
                            ███████║█████╗  ██████╔╝██║  ██║ 
                            ██╔══██║██╔══╝  ██╔══██╗██║  ██║  
                            ██║  ██║███████╗██║  ██║██████╔╝  
                            ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═════╝     
            ,   #                                                     _
            (\\\\_(^>                            _.                    >(')__,
            (_(__)           ||          _.||~~ {^--^}.-._._.---.__.-;(_~_/
                ||   (^..^)   ||  (\\\\(__)/)  ||   {6 6 }.')' (. )' ).-`  ||
            __||____(oo)____||___`(QQ)'___||___( v  )._('.) ( .' )____||__
            --||----"- "----||----)  (----||----`-.''(.' .( ' ) .)----||--
            __||__@(    )___||___(o  o)___||______#`(.'( . ( (',)_____||__
            --||----"--"----||----`--'----||-------'\\\\_.).(_.). )------||--
                ||            ||       `||~|||~~|""||  `W W    W W      ||
            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  
                    Document & Code Intelligence v0.7

"""

# Styling constants
STYLES = {
    "header": Style(color="cyan", bold=True),
    "subheader": Style(color="magenta", italic=True),
    "success": Style(color="green", bold=True),
    "error": Style(color="red", bold=True),
    "warning": Style(color="yellow"),
    "info": Style(color="blue"),
    "highlight": Style(color="cyan", bold=True, underline=True),
    "dim": Style(color="grey70", italic=True),
    "action": Style(color="magenta", bold=True),
    "progress": Style(color="green"),
    "menu_selected": Style(color="cyan", bold=True, reverse=True),
    "menu_unselected": Style(color="cyan"),
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

def get_provider_settings():
    """Get the current provider settings or set default to XAI"""
    provider = "xai"  # Set default provider to XAI
    
    # Try to get from config if available
    if herd_config:
        try:
            config_provider = herd_config.get_provider()
            if config_provider:
                provider = config_provider
        except:
            pass
    
    # Get available providers for display
    providers = AI_PROVIDERS if 'AI_PROVIDERS' in globals() else ["xai", "ollama", "openai", "anthropic", "groq"]
    
    return provider, providers

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
        "images_dir": "images"
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

def create_header_with_menu(actions, selected=None, project_path=None, provider=None):
    """Create a styled header with integrated vertical menu including descriptions"""
    # Format project path with icon
    project_info = f"[dim]📁 Project:[/dim] [yellow]{project_path}[/yellow]" if project_path else ""
    
    # Get API key status for the current provider
    api_key_status = ""
    if provider:
        env_var_map = {
            "xai": "XAI_API_KEY",
            "openai": "OPENAI_API_KEY",
            "anthropic": "ANTHROPIC_API_KEY",
            "groq": "GROQ_API_KEY",
            "cohere": "COHERE_API_KEY",
            "gemini": "GEMINI_API_KEY"
        }
        if provider in env_var_map and os.environ.get(env_var_map[provider]):
            api_key_status = "[green]✓ API Key[/green]"
        elif provider in env_var_map:
            api_key_status = "[red]✗ No API Key[/red]"
        
    provider_info = f"[dim]🤖 Provider:[/dim] [bright_yellow]{provider}[/bright_yellow] {api_key_status}" if provider else ""
    
    # Display loaded providers info
    loaded_providers = []
    # Use AI_PROVIDERS from config when available, fallback to default list
    providers_list = AI_PROVIDERS if 'AI_PROVIDERS' in globals() else ["xai", "ollama", "openai", "anthropic", "groq", "cohere", "gemini"]
    
    for p in providers_list:
        # For API-based providers, check for API key
        if p != "ollama":
            env_var = f"{p.upper()}_API_KEY"
            if os.environ.get(env_var):
                loaded_providers.append(f"[green]{p}[/green]")
            else:
                loaded_providers.append(f"[dim]{p}[/dim]")
        else:
            # For Ollama, check if Ollama URL is set or default
            ollama_url = os.environ.get("OLLAMA_API_URL", "http://localhost:11434")
            if ollama_url:
                loaded_providers.append(f"[green]{p}[/green]")
            else:
                loaded_providers.append(f"[dim]{p}[/dim]")
    
    providers_info = f"[dim]📦 Available Providers:[/dim] {' | '.join(loaded_providers)}"
    
    # Create vertical menu with descriptions
    menu_items = []
    icons = {
        "Rename Files": "📝",
        "Extract Snippets": "✂️",
        "Generate Docs": "📚",
        "Extract Citations": "📎",
        "Idealize Content": "✨",
        "Process Images": "🖼️",
        "Analysis Report": "📊",
        "Scramble Files": "🔀",
        "Sample Files": "📋",
        "Clear Cache": "🗑️",
        "Code Executor": "💻",
    }
    
    # Find the longest menu name for padding
    max_name_length = max(len(action["name"]) for action in actions)
    name_pad = max_name_length + 2  # Add some extra padding
    
    for idx, action in enumerate(actions, 1):
        name = action["name"]
        desc = action.get("description", "")
        icon = icons.get(name, "•")
        
        # Use the calculated padding
        if selected == idx:
            menu_items.append(f"[reverse][bold cyan]{idx:2}[/bold cyan] {icon} {name.ljust(name_pad)}[/reverse] [dim]{desc}[/dim]")
        else:
            menu_items.append(f"[cyan]{idx:2}[/cyan] {icon} {name.ljust(name_pad)} [dim]{desc}[/dim]")
    
    # Add a separator before menu items
    menu_separator = "─" * 70
    
    # Build menu items string outside the f-string to avoid backslash in f-string expression
    menu_items_str = "\n".join(menu_items)
    
    # Combine into header with banner and all menu items
    header_content = (
        f"{BANNER}\n"
        f"{project_info}   {provider_info}\n"
        f"{providers_info}\n\n"
        f"[blue]{menu_separator}[/blue]\n"
        f"{menu_items_str}\n"
        f"[blue]{menu_separator}[/blue]\n\n"
        f"[dim]Select action (1-{len(actions)}) or 'q' to quit, 's' for settings, 'd' to change directory, '?' for help[/dim]"
    )
    
    return Panel(
        header_content,
        border_style="blue",
        box=box.HEAVY,
        padding=(1, 2),
        title="[bold blue]Herd AI Control Panel[/bold blue]",
        subtitle="[dim]Press ? for help[/dim]"
    )

def print_progress_bar(current, total, description=""):
    """Create a rich progress bar with spinner"""
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(complete_style="green", finished_style="bright_green"),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeRemainingColumn(),
        console=console
    ) as progress:
        task = progress.add_task(description, total=total)
        progress.update(task, completed=current)

def show_settings_menu(provider, providers, root=None):
    """Show and manage application settings"""
    console.clear()
    
    # Create settings panel
    settings_panel = Panel(
        f"[bold cyan]Herd AI Settings[/bold cyan]\n\n"
        f"[dim]Current Provider:[/dim] [bright_yellow]{provider}[/bright_yellow]\n"
        f"[dim]Available Providers:[/dim] {', '.join(providers)}\n"
        f"[dim]Project Directory:[/dim] {root}\n\n"
        f"1. Change AI Provider\n"
        f"2. Configure API Keys\n"
        f"3. Back to Main Menu",
        title="Settings",
        border_style="green",
        box=box.ROUNDED,
        padding=(1, 2)
    )
    
    console.print(settings_panel)
    
    choice = Prompt.ask(
        "Option",
        choices=["1", "2", "3", "q"],
        default="3"
    )
    
    if choice == "1":
        new_provider = Prompt.ask(
            "Select provider",
            choices=providers,
            default=provider
        )
        
        # Save the new provider to config
        if herd_config:
            try:
                herd_config.set_provider(new_provider)
                console.print(f"[green]Provider changed to: {new_provider}[/green]")
            except Exception as e:
                console.print(f"[yellow]Could not save provider setting: {e}[/yellow]")
        else:
            console.print(f"[green]Provider changed to: {new_provider}[/green] (for this session only)")
        
        time.sleep(1)
        return new_provider
    
    elif choice == "2":
        # API key configuration
        # Providers requiring API keys
        key_providers = ["xai", "openai", "anthropic", "groq", "cohere", "gemini"]
        
        if provider in key_providers:
            # Try/except to prevent potential crashes
            try:
                api_key = Prompt.ask(f"Enter {provider.upper()} API Key", password=True, default="")
                
                if api_key:
                    # Save the API key to environment and config
                    if provider == "xai":
                        os.environ["XAI_API_KEY"] = api_key
                    elif provider == "openai":
                        os.environ["OPENAI_API_KEY"] = api_key
                    elif provider == "anthropic":
                        os.environ["ANTHROPIC_API_KEY"] = api_key
                    elif provider == "groq":
                        os.environ["GROQ_API_KEY"] = api_key
                    elif provider == "cohere":
                        os.environ["COHERE_API_KEY"] = api_key
                    elif provider == "gemini":
                        os.environ["GEMINI_API_KEY"] = api_key
                    
                    # Save to config if available
                    if herd_config:
                        try:
                            herd_config.set_api_key(provider, api_key)
                            console.print(f"[green]{provider.upper()} API key configured successfully[/green]")
                        except Exception as e:
                            console.print(f"[yellow]API key saved for this session but could not be saved to config: {e}[/yellow]")
                    else:
                        console.print(f"[green]{provider.upper()} API key configured for this session[/green]")
                else:
                    console.print(f"[yellow]No API key provided for {provider.upper()}[/yellow]")
            except Exception as e:
                console.print(f"[red]Error configuring API key: {e}[/red]")
                # Continue despite error - don't crash the application
                time.sleep(2)
        else:
            console.print(f"[yellow]No API key configuration needed for {provider}[/yellow]")
        
        time.sleep(1.5)
    
    return provider

def show_help_screen(root=None, provider=None, providers=None):
    """Display a comprehensive help screen with keyboard shortcuts and feature explanations"""
    console.clear()
    
    # Calculate content width for consistent formatting
    width = console.width - 8  # Account for padding and borders
    half_width = (width // 2) - 4
    
    # Build help content sections
    overview = Panel(
        "[bold]Herd AI[/bold] is a document & code intelligence tool that uses AI to analyze, transform, and enhance your files.\n\n"
        "This tool can rename files based on content, extract code snippets, generate documentation, process citations, "
        "idealize content, analyze images, and generate comprehensive project reports.",
        title="Overview",
        border_style="cyan",
        box=box.ROUNDED,
        width=width,
        padding=(1, 2)
    )
    
    # Create keyboard shortcuts panel
    shortcuts = Table(title="Keyboard Shortcuts", box=box.SIMPLE, show_header=True, min_width=half_width, pad_edge=False)
    shortcuts.add_column("Key", style="cyan", no_wrap=True)
    shortcuts.add_column("Action", style="green")
    
    shortcuts.add_row("1-0", "Select menu option")
    shortcuts.add_row("q", "Quit current screen/application")
    shortcuts.add_row("s", "Open settings menu")
    shortcuts.add_row("d", "Change working directory")
    shortcuts.add_row("?", "Show this help screen")
    shortcuts.add_row("Ctrl+C", "Return to main menu (or exit if already there)")
    shortcuts.add_row("Enter", "Confirm selection/Continue")
    
    # Create AI providers panel
    ai_providers = Table(title="Supported AI Providers", box=box.SIMPLE, show_header=True, min_width=half_width, pad_edge=False)
    ai_providers.add_column("Provider", style="cyan", no_wrap=True)
    ai_providers.add_column("Description", style="green")
    
    ai_providers.add_row("xai", "X.AI/Grok API (requires API key)")
    ai_providers.add_row("ollama", "Local models via Ollama")
    ai_providers.add_row("openai", "OpenAI API (requires API key)")
    ai_providers.add_row("anthropic", "Anthropic Claude API (requires API key)")
    ai_providers.add_row("groq", "Groq API (requires API key)")
    ai_providers.add_row("cohere", "Cohere API (requires API key)")
    ai_providers.add_row("gemini", "Google Gemini API (requires API key)")
    
    # Create a table with the two columns side by side
    tables = Columns([shortcuts, ai_providers], width=half_width, equal=True, align="center")
    
    # Create features panel with descriptions of each function
    features = Table(title="Available Features", box=box.SIMPLE, show_header=True, width=width, pad_edge=False)
    features.add_column("Feature", style="cyan", no_wrap=True)
    features.add_column("Description", style="green")
    
    features.add_row("Rename Files", "Analyze file content and suggest better filenames based on the content")
    features.add_row("Extract Snippets", "Extract useful code snippets and examples from documents")
    features.add_row("Generate Docs", "Generate documentation for your project files")
    features.add_row("Extract Citations", "Extract academic citations from documents in various styles (APA, MLA, etc.)")
    features.add_row("Idealize Content", "Create idealized versions of file content using AI")
    features.add_row("Process Images", "Generate alt text, descriptions, and rename images based on content")
    features.add_row("Analysis Report", "Generate comprehensive analysis of project documents")
    features.add_row("Scramble Files", "Randomize filenames while preserving extensions (for privacy/testing)")
    features.add_row("Sample Files", "Generate sample files of different types for testing")
    features.add_row("Clear Cache", "Clear the document analysis cache to force fresh analysis")
    
    # Create CLI usage examples panel
    examples = Panel(
        "[bold cyan]Basic Usage:[/bold cyan]\n"
        "  [green]herd --dir /path/to/project[/green]     Run interactive CLI on a directory\n"
        "  [green]herd --gui[/green]                     Launch the web-based GUI\n"
        "\n"
        "[bold cyan]Direct Commands:[/bold cyan]\n"
        "  [green]herd --dir /path/to/project --rename[/green]              Rename files\n"
        "  [green]herd --dir /path/to/project --snippets[/green]            Extract code snippets\n"
        "  [green]herd --dir /path/to/project --citations[/green]           Extract citations\n"
        "  [green]herd --dir /path/to/project --process-images[/green]      Process images\n"
        "\n"
        "[bold cyan]Provider Selection:[/bold cyan]\n"
        "  [green]herd --provider xai --api-key YOUR_KEY[/green]            Use X.AI provider\n"
        "  [green]herd --provider ollama[/green]                          Use local Ollama models\n"
        "\n"
        "[bold cyan]Advanced Options:[/bold cyan]\n"
        "  [green]herd --process-all[/green]                              Run all processing tasks\n"
        "  [green]herd --recursive[/green]                                Process subdirectories\n"
        "  [green]herd --undo[/green]                                     Undo last operation",
        title="Command Line Examples",
        border_style="green",
        box=box.ROUNDED,
        width=width,
        padding=(1, 2)
    )
    
    # Add development mode information
    dev_info = Panel(
        "[bold cyan]Running in Development Mode:[/bold cyan]\n"
        "You can run Herd AI in development mode using the [green]run_herd.py[/green] script:\n"
        "  [green]python run_herd.py[/green]                              Run in development mode\n"
        "\n"
        "[bold cyan]Environment Variables:[/bold cyan]\n"
        "  [green]XAI_API_KEY=[/green]                                    X.AI API key\n"
        "  [green]OPENAI_API_KEY=[/green]                                 OpenAI API key\n"
        "  [green]ANTHROPIC_API_KEY=[/green]                              Anthropic API key\n"
        "  [green]OLLAMA_API_URL=[/green]                                 Custom Ollama API URL\n"
        "  [green]OLLAMA_TEXT_MODEL=[/green]                              Custom Ollama text model\n"
        "\n"
        "[bold cyan]Configuration Files:[/bold cyan]\n"
        "  [green].env[/green]                                           Environment variables\n"
        "  [green].herd/[/green]                                          Output and cache directory",
        title="Development Information",
        border_style="magenta",
        box=box.ROUNDED,
        width=width,
        padding=(1, 2)
    )
    
    # Create the current settings display
    current_settings = Table(title="Current Settings", box=box.SIMPLE, width=width, pad_edge=False)
    current_settings.add_column("Setting", style="cyan", no_wrap=True)
    current_settings.add_column("Value", style="green")
    
    current_settings.add_row("Working Directory", str(root) if root else "Not set")
    current_settings.add_row("Current Provider", provider if provider else "Default")
    current_settings.add_row("Available Providers", ", ".join(providers) if providers else "Default")
    
    # Create the help layout
    help_layout = Layout()
    help_layout.split(
        Layout(name="header", size=3),
        Layout(name="body")
    )
    help_layout["header"].update(
        Panel(
            "[bold cyan]Herd AI Help[/bold cyan]",
            border_style="blue",
            box=box.HEAVY,
            padding=(1, 2)
        )
    )
    
    # Main content with scrolling
    help_content = Group(
        overview,
        tables,
        features,
        examples,
        dev_info,
        current_settings,
        Panel(
            "[cyan]Press any key to return to the main menu[/cyan]",
            border_style="blue",
            box=box.ROUNDED,
            padding=(1, 2)
        )
    )
    
    help_layout["body"].update(help_content)
    console.print(help_layout)
    
    # Wait for any key press
    try:
        input("Press Enter to continue...")
    except (KeyboardInterrupt, EOFError):
        pass  # Gracefully handle Ctrl+C or other interrupts

def rich_interface(root: Path, omni_paths=None):
    """Interactive rich UI for LlamaCleaner operations with a minimal layout"""
    # Set up paths
    paths, omni_paths = setup_paths(root, omni_paths)
    
    # Get provider settings
    session_provider, providers = get_provider_settings()

    # Define actions with metadata for argument requirements
    actions = [
        {
            "name": "Rename Files",
            "fn": process_renames,
            "type": "file",
            "args": [True, set()],
            "log": True,
            "description": "Rename files based on content analysis"
        },
        {
            "name": "Extract Snippets",
            "fn": process_snippets,
            "type": "file",
            "args": [True, 100, set()],
            "log": True,
            "description": "Extract code snippets from documents"
        },
        {
            "name": "Generate Docs",
            "fn": generate_docs,
            "type": "dir",
            "args": [True],
            "log": False,
            "description": "Generate documentation from project files"
        },
        {
            "name": "Extract Citations",
            "fn": process_file_or_directory,
            "type": "dir",
            "args": [True],
            "log": False,
            "description": "Extract citations from academic documents"
        },
        {
            "name": "Idealize Content",
            "fn": idealize_directory,
            "type": "dir",
            "args": [True, set()],
            "log": True,
            "description": "Generate idealized versions of content"
        },
        {
            "name": "Process Images",
            "fn": process_images_cli,
            "type": "dir",
            "args": [True],
            "log": True,
            "description": "Process and optimize images (alt text, markdown, renaming, accessibility)"
        },
        {
            "name": "Analysis Report",
            "fn": None,
            "type": "analysis_report",
            "args": [],
            "log": False,
            "description": "Analyze documents, show stats, and export summary report"
        },
        {
            "name": "Scramble Files",
            "fn": scramble_directory,
            "type": "scrambler_function",
            "args": [],
            "log": True,
            "description": "Randomize filenames (preserves extensions)"
        },
        {
            "name": "Sample Files",
            "fn": generate_sample_files,
            "type": "sample_function",
            "args": [],
            "log": True,
            "description": "Generate sample files"
        },
        {
            "name": "Clear Cache",
            "fn": clear_cache,
            "type": "func",
            "args": [None],
            "log": False,
            "description": "Clear document analysis cache"
        },
        {
            "name": "Code Executor",
            "fn": None,
            "type": "code_executor",
            "args": [],
            "log": False,
            "description": "Run Python or Bash code in a secure sandbox"
        },
    ]

    # Define log callback with rich styling
    def log_callback(msg: str):
        # Strip existing rich tags for clean styling
        plain_msg = re.sub(r"\[/?[a-zA-Z0-9_]+\]", "", msg)
        plain_msg = plain_msg.replace("[/]", "")
        
        # Add appropriate styling based on message content
        if "error" in plain_msg.lower():
            styled_msg = f"[bold red]❌ {plain_msg}[/bold red]"
        elif "warning" in plain_msg.lower():
            styled_msg = f"[yellow]⚠️ {plain_msg}[/yellow]"
        elif "success" in plain_msg.lower() or "complete" in plain_msg.lower():
            styled_msg = f"[bold green]✅ {plain_msg}[/bold green]"
        elif "processing" in plain_msg.lower():
            styled_msg = f"[cyan]⚙️ {plain_msg}[/cyan]"
        else:
            styled_msg = f"[dim]ℹ️ {plain_msg}[/dim]"
        
        console.print(styled_msg)

    # Main application loop
    selected_action = None
    menu_level = "main"  # Track menu level: "main", "action", "settings"
    exit_requested = False

    while True:
        try:
            # Clear screen and show header with menu
            console.clear()
            console.print(create_header_with_menu(actions, selected_action, root, session_provider))
            
            if selected_action is None:
                menu_level = "main"  # We're at the main menu
                # Get user input
                choice = Prompt.ask(
                    "Action",
                    choices=[str(i) for i in range(1, len(actions)+1)] + ["q", "s", "d", "?"],
                    default="1"
                )
                
                if choice == "q":
                    break
                
                if choice == "s":
                    menu_level = "settings"
                    # Show settings menu
                    session_provider = show_settings_menu(session_provider, providers, root)
                    continue
                
                if choice == "d":
                    # Change directory option
                    console.print("[cyan]Change target directory[/cyan]")
                    current_dir = str(root)
                    new_dir = Prompt.ask("Enter new directory path", default=current_dir)
                    new_path = Path(new_dir)
                    
                    if not new_path.exists() or not new_path.is_dir():
                        console.print(f"[red]Error: {new_dir} is not a valid directory[/red]")
                        time.sleep(2)
                        continue
                    
                    # Update root and paths
                    root = new_path
                    console.print(f"[green]Directory changed to: {root}[/green]")
                    # Reset paths for the new directory
                    paths, omni_paths = setup_paths(root, omni_paths)
                    time.sleep(1)
                    continue
                
                if choice == "?":
                    # Show help screen
                    show_help_screen(root, session_provider, providers)
                    continue
                    
                try:
                    selected_action = int(choice)
                except ValueError:
                    console.print(f"[red]Invalid option: {choice}[/red]")
                    continue
                
                console.clear()
                console.print(create_header_with_menu(actions, selected_action, root, session_provider))
                continue

            menu_level = "action"  # We're in an action submenu
            action_idx = selected_action - 1
            if action_idx < 0 or action_idx >= len(actions):
                console.print(f"[red]Invalid action index: {action_idx}[/red]")
                selected_action = None
                continue
            action = actions[action_idx]
            action_name = action["name"]
            action_fn = action["fn"]
            action_type = action["type"]
            action_args = action["args"]
            use_log = action["log"]
            
            # Debug: print selected action
            console.print(f"[bold yellow]Selected action index: {action_idx}, name: {action_name}[/bold yellow]")
            
            # Update header to show current action
            header = create_header_with_menu(actions, selected_action, root, session_provider)
            console.print(header)
            
            # Update content area to show we're starting the action
            console.print(Panel(
                f"[cyan]Running {action_name}...[/cyan]",
                title="Output",
                border_style="cyan",
                box=box.ROUNDED,
                padding=(1, 2)
            ))
            
            console.clear()
            console.print(header)
            
            # Process action
            try:
                if action_type == "file":
                    console.print(f"[dim]Scanning for files in {root}...[/dim]")
                    all_files = list(root.rglob("*") if action_args[0] else root.glob("*"))
                    targets = [
                        f for f in all_files 
                        if f.is_file() 
                        and not f.name.startswith('.')
                        and not f.name.startswith('|_')
                        and not any(part.startswith('.') or part.startswith('|_') for part in f.parts)
                    ]
                    config = get_config_module()
                    if action_name == "Rename Files":
                        targets = [f for f in targets if f.suffix.lower() in config.SUPPORTED_EXTENSIONS]
                    elif action_name == "Extract Snippets":
                        targets = [f for f in targets if f.suffix.lower() in config.CODE_EXTENSIONS]
                        if not targets:
                            console.print("[yellow]No code files found to extract snippets from.[/yellow]")
                            time.sleep(2)
                            selected_action = None
                            continue
                        
                        console.print(f"[blue]Found {len(targets)} code files to process[/blue]")
                        time.sleep(1)  # Give user time to see the count
                    
                    console.print(f"[blue]Found {len(targets)} files to process[/blue]")
                    
                    if not targets:
                        console.print(f"[yellow]No applicable files found for {action_name}[/yellow]")
                        time.sleep(2)
                        selected_action = None
                        continue
                        
                    processed = 0
                    total = len(targets)
                    
                    for idx, filepath in enumerate(targets, 1):
                        if use_log:
                            try:
                                rel_path = filepath.relative_to(root)
                            except ValueError:
                                rel_path = filepath
                            console.print(f"[dim]Processing → {rel_path}[/dim]")
                            
                        try:
                            if action_name == "Rename Files":
                                action_fn(filepath, recursive=action_args[0], exclude_ext=action_args[1], 
                                          omni_paths=omni_paths, log_callback=log_callback if use_log else None,
                                          provider=session_provider)
                            elif action_name == "Extract Snippets":
                                action_fn(
                                    filepath,
                                    recursive=action_args[0],
                                    batch_size=action_args[1],
                                    exclude_ext=action_args[2],
                                    omni_paths={
                                        'base_dir': omni_paths.get('base_dir'),
                                        'snippets_dir': omni_paths.get('snippets_dir'),
                                        'log': omni_paths.get('log'),
                                        'api_creds': omni_paths.get('api_creds')
                                    },
                                    log_callback=log_callback if use_log else None,
                                    provider=session_provider
                                )
                                time.sleep(0.5)  # Add delay between files
                            else:
                                if use_log:
                                    action_fn(filepath, *action_args, log_callback)
                                else:
                                    action_fn(filepath, *action_args)
                            processed += 1
                        except Exception as e:
                            console.print(f"[red]Error processing {filepath}: {e}[/red]")
                            
                        print_progress_bar(idx, total, f"{action_name}")
                        
                    if processed > 0:
                        summary = f"Successfully processed {processed}/{len(targets)} files"
                        console.print(f"[green]{summary}[/green]")
                    else:
                        summary = "No files were successfully processed"
                        console.print(f"[yellow]{summary}[/yellow]")
                    
                    print_progress_bar(total, total, f"{action_name} Complete")
                
                # DIRECTORY-BASED OPERATIONS
                elif action_type == "dir":
                    console.print(f"[dim]Processing directory {root}...[/dim]")
                    
                    try:
                        # Call appropriate function based on action
                        if action_name == "Generate Docs":
                            # Filter for code files only
                            config = get_config_module()
                            code_files = [
                                f for f in root.rglob("*") 
                                if f.is_file() 
                                and not f.name.startswith('.')
                                and not any(part.startswith('.') for part in f.parts)
                                and f.suffix.lower() in config.CODE_EXTENSIONS
                            ]
                            
                            if not code_files:
                                console.print("[yellow]No code files found to generate documentation from.[/yellow]")
                                time.sleep(2)
                                selected_action = None
                                continue
                            
                            console.print(f"[blue]Found {len(code_files)} code files to document[/blue]")
                            time.sleep(1)  # Give user time to see the count
                            
                            # Call the function with proper parameters and handle the result
                            result = action_fn(root, recursive=action_args[0], log_callback=log_callback, provider=session_provider)
                            
                            # Check the result and display appropriate message
                            if isinstance(result, dict):
                                if result.get('success', False):
                                    console.print(f"[green]Generated documentation for {result.get('files_processed', 0)} code files[/green]")
                                    console.print(f"[green]README.md written to {result.get('readme_path', 'Unknown')}[/green]")
                                else:
                                    console.print(f"[yellow]Documentation generation completed with issues: {result.get('error', 'Unknown error')}[/yellow]")
                            else:
                                console.print(f"[green]Generated documentation for {len(code_files)} code files[/green]")
                                console.print(f"[green]Output written to {omni_paths.get('base_dir')}/docs/[/green]")
                            
                        elif action_name == "Extract Citations":
                            # Prompt for citation styles and output formats
                            style_input = Prompt.ask(
                                "Which citation style(s) do you want? (apa, mla, chicago, ieee, vancouver) [comma-separated, default: apa]",
                                default="apa"
                            )
                            format_input = Prompt.ask(
                                "Which output format(s) do you want? (md, bib, txt, csv) [comma-separated, default: md]",
                                default="md"
                            )
                            
                            styles = [s.strip() for s in style_input.split(",") if s.strip() in ("apa", "mla", "chicago", "ieee", "vancouver")]
                            outputs = [f.strip() for f in format_input.split(",") if f.strip() in ("md", "bib", "txt", "csv")]
                            
                            if not styles:
                                styles = ["apa"]
                            if not outputs:
                                outputs = ["md"]
                                
                            console.print(f"[cyan]Using styles: {', '.join(styles)}[/cyan]")
                            console.print(f"[cyan]Using output formats: {', '.join(outputs)}[/cyan]")
                            
                            # Call the function with proper parameters and capture the result
                            result = process_file_or_directory(
                                root, 
                                recursive=action_args[0], 
                                styles=styles, 
                                outputs=outputs, 
                                log_callback=log_callback, 
                                provider=session_provider
                            )
                            
                            # Check the result and display appropriate message
                            if isinstance(result, dict):
                                if result.get('success', False):
                                    console.print(f"[bold green]Citations extracted successfully![/bold green]")
                                    console.print(f"[green]Processed {result.get('files_processed', 0)} files and found {result.get('unique_citations', 0)} unique citations.[/green]")
                                    
                                    # Show output files for each style
                                    if 'outputs' in result:
                                        console.print("[green]Output files:[/green]")
                                        for style, files in result['outputs'].items():
                                            console.print(f"[green]Style {style.upper()}:[/green]")
                                            for fmt, path in files.items():
                                                console.print(f"[green]  {fmt.upper()}: {path}[/green]")
                                else:
                                    console.print(f"[yellow]Citation extraction completed with issues: {result.get('error', 'Unknown error')}[/yellow]")
                            else:
                                console.print(f"[bold green]Citations extracted. See {omni_paths.get('citations_dir')} for results.[/bold green]")
                            
                        elif action_name == "Process Images":
                            # Prompt for options interactively
                            force = Prompt.ask("Force reprocessing even if .md or cache exists? (y/n)", default="n").lower() == "y"
                            rename = Prompt.ask("Rename files based on content analysis? (y/n)", default="n").lower() == "y"
                            override_md = Prompt.ask("Override existing markdown file check and reprocess images? (y/n)", default="n").lower() == "y"
                            test = Prompt.ask("Check metadata before and after embedding alt text? (y/n)", default="n").lower() == "y"
                            console.print(f"[blue]Options: force={force}, rename={rename}, override_md={override_md}, test={test}[/blue]")
                            
                            # Use the correct function with proper parameters
                            try:
                                result = process_images(
                                    directory=root,
                                    recursive=True,
                                    force=force,
                                    rename=rename,
                                    override_md=override_md,
                                    test=test,
                                    log_callback=log_callback,
                                    provider=session_provider
                                )
                                
                                if isinstance(result, dict) and result.get('success', False):
                                    console.print(f"[bold bright_green]✅ Image processing completed successfully![/bold bright_green]")
                                    console.print(f"[bright_green]Processed {result.get('files_processed', 0)} images.[/bright_green]")
                                    console.print(f"[bright_green]Output directory: {result.get('output_dir', 'Unknown')}[/bright_green]")
                                else:
                                    console.print(f"[bold yellow]⚠️ Image processing completed with issues: {result.get('error', 'Unknown error')}[/bold yellow]")
                            except Exception as e:
                                console.print(f"[bold bright_red]❌ Error processing images: {e}[/bold bright_red]")
                                
                        elif action_name == "Idealize Content":
                            # We're using idealize_directory which is the wrapper function
                            exclude_ext = set()
                            if Prompt.ask("Exclude any file extensions? (y/n)", default="n").lower() == "y":
                                ext_input = Prompt.ask("Enter extensions to exclude (comma-separated, e.g. .py,.js)", default="")
                                if ext_input:
                                    exclude_ext = {ext.strip().lower() for ext in ext_input.split(",") if ext.strip()}
                            
                            console.print(f"[cyan]Starting content idealization in {root} (recursive={action_args[0]})[/cyan]")
                            console.print(f"[cyan]Excluding extensions: {', '.join(exclude_ext) if exclude_ext else 'None'}[/cyan]")
                            
                            # Call idealize_directory with proper parameters
                            result = idealize_directory(
                                root,
                                recursive=action_args[0],
                                exclude_ext=exclude_ext,
                                log_callback=log_callback,
                                provider=session_provider
                            )
                            
                            # Process the result and show appropriate feedback
                            if isinstance(result, dict):
                                if result.get('success', False):
                                    console.print(f"[bold green]✅ Content idealization completed successfully![/bold green]")
                                    console.print(f"[green]Processed {result.get('files_processed', 0)} files.[/green]")
                                    console.print(f"[green]Created {result.get('files_idealized', 0)} idealized versions.[/green]")
                                    console.print(f"[green]Output directory: {result.get('output_dir')}[/green]")
                                    console.print(f"[green]Backup directory: {result.get('backup_dir')}[/green]")
                                else:
                                    console.print(f"[bold yellow]⚠️ Content idealization completed with issues: {result.get('error', 'Unknown error')}[/bold yellow]")
                            else:
                                console.print(f"[yellow]Content idealization completed but didn't return a proper status.[/yellow]")
                            
                        elif action_name == "Analysis Report":
                            # Run analyze_documents, generate_document_summary, and export_document_summary in sequence
                            console.print(f"[cyan]Analyzing documents in {root}...[/cyan]")
                            try:
                                console.print(f"[cyan]Step 1: Analyzing document content...[/cyan]")
                                analyze_result = analyze_documents(root, recursive=True, force=False)
                                if analyze_result:
                                    file_count = len(analyze_result)
                                    console.print(f"[green]Analyzed {file_count} documents successfully.[/green]")
                                
                                console.print(f"[cyan]Step 2: Generating document summary...[/cyan]")
                                stats = generate_document_summary(root, recursive=True, force=False)
                                
                                console.print(f"[cyan]Step 3: Exporting document summary...[/cyan]")
                                output_path = omni_paths.get('base_dir') / "document_summary.md"
                                export_document_summary(root, output_path)
                                
                                console.print(f"[bold green]✅ Analysis completed successfully![/bold green]")
                                if stats:
                                    console.print(f"[green]Found {stats.get('count', 0)} documents, {stats.get('total_words', 0)} words total[/green]")
                                    
                                    # Display document types distribution
                                    if 'document_types' in stats and stats['document_types']:
                                        console.print("[green]Document types distribution:[/green]")
                                        for ext, count in stats['document_types'].items():
                                            console.print(f"[green]  {ext}: {count}[/green]")
                                    
                                    # Display top keywords
                                    if 'top_keywords' in stats and stats['top_keywords']:
                                        console.print("[green]Top keywords:[/green]")
                                        top_10 = sorted(stats['top_keywords'].items(), key=lambda x: -x[1])[:10]
                                        for kw, count in top_10:
                                            console.print(f"[green]  {kw}: {count}[/green]")
                                
                                console.print(f"[green]Exported summary to {output_path}[/green]")
                            except Exception as e:
                                console.print(f"[red]Error in Analysis Report: {e}[/red]")
                            print_progress_bar(1, 1, "Analysis Report Complete")
                            
                        else:
                            # Generic fallback
                            result = action_fn(root, *action_args)
                            console.print("[green]Operation completed successfully.[/green]")
                    except Exception as e:
                        console.print(f"[red]Error in {action_name}: {e}[/red]")
                
                # FUNCTION-BASED OPERATIONS
                elif action_type == "func":
                    console.print(f"[dim]Executing {action_name}...[/dim]")
                    
                    try:
                        if action_name == "Clear Cache":
                            result = action_fn(*action_args)
                            console.print(f"[green]Cache cleared successfully[/green]")
                        else:
                            result = action_fn(*action_args)
                            console.print(f"[green]{action_name} completed successfully[/green]")
                    except Exception as e:
                        console.print(f"[red]Error in {action_name}: {e}[/red]")
                
                # SCRAMBLER ACTIONS - Updated to use the function directly
                elif action_type == "scrambler_function":
                    # No need to prompt for directory, use the root directory
                    console.print(f"[dim]Scrambling filenames in {root}...[/dim]")
                    try:
                        # Call the scramble_directory function directly
                        count = scramble_directory(root, log_callback=log_callback)
                        console.print(f"[green]Scrambled {count} files in {root}[/green]")
                    except Exception as e:
                        console.print(f"[red]Error scrambling files: {e}[/red]")
                        
                elif action_type == "sample_function":
                    # No need to prompt for directory, use the root directory
                    console.print(f"[dim]Generating sample files in {root}...[/dim]")
                    
                    # Prompt for number of files per extension
                    files_per_ext = Prompt.ask("How many sample files per file type?", default="3")
                    try:
                        files_per_ext = int(files_per_ext)
                    except Exception:
                        files_per_ext = 3
                        
                    try:
                        # Call the function directly
                        count = generate_sample_files(root, files_per_ext=files_per_ext, log_callback=log_callback)
                        console.print(f"[green]Generated {count} sample files in {root}[/green]")
                    except Exception as e:
                        console.print(f"[red]Error generating sample files: {e}[/red]")
                
                # CODE EXECUTOR ACTION
                elif action_type == "code_executor":
                    # Launch the code executor CLI
                    try:
                        console.print("[cyan]Launching code executor CLI...[/cyan]")
                        
                        # Import the code executor module
                        try:
                            from herd_ai.utils.code_executor import interactive_cli
                            console.print("[green]Successfully imported code executor module[/green]")
                        except ImportError as e:
                            console.print(f"[yellow]Import error: {e}[/yellow]")
                            console.print("[yellow]Attempting alternative import paths...[/yellow]")
                            try:
                                # Try loading directly from file path
                                code_exec_path = os.path.join(os.path.dirname(__file__), 'utils', 'code_executor.py')
                                console.print(f"[dim]Looking for module at: {code_exec_path}[/dim]")
                                
                                if os.path.exists(code_exec_path):
                                    spec = importlib.util.spec_from_file_location('code_executor', code_exec_path)
                                    if spec and spec.loader:
                                        code_executor = importlib.util.module_from_spec(spec)
                                        sys.modules['code_executor'] = code_executor
                                        spec.loader.exec_module(code_executor)
                                        interactive_cli = code_executor.interactive_cli
                                        console.print("[green]Successfully loaded code executor from file[/green]")
                                    else:
                                        raise ImportError("Invalid module specification")
                                else:
                                    raise FileNotFoundError(f"Code executor module not found at {code_exec_path}")
                            except Exception as inner_e:
                                console.print(f"[red]Failed to import code executor: {inner_e}[/red]")
                                # Continue with main menu instead of crashing
                                selected_action = None
                                time.sleep(2)
                                continue
                        
                        # Since interactive_cli is async, we need to run it properly
                        if 'interactive_cli' in locals():
                            console.print("[cyan]Starting code executor...[/cyan]")
                            # Clear the screen for the code executor
                            console.clear()
                            # Run the async function using asyncio
                            asyncio.run(interactive_cli())
                            console.print("[green]Code executor session completed[/green]")
                        else:
                            console.print("[red]Code executor function not available[/red]")
                            
                        # After returning from code executor, reset selection
                        selected_action = None
                        # Brief pause to let user see any messages
                        time.sleep(1)
                    except Exception as e:
                        console.print(f"[red]Error in code executor: {e}[/red]")
                        import traceback
                        traceback.print_exc()
                        # Pause to let user see the error
                        time.sleep(3)
                    finally:
                        # Always reset the selection
                        selected_action = None
                
                # UNKNOWN ACTION TYPE
                else:
                    console.print(f"[red]Unknown action type: {action_type}[/red]")
            except Exception as e:
                console.print(f"[red]Error in {action_name}: {e}[/red]")
                logger.exception(f"Error in {action_name}")
            
            # Update content area with completion message after action
            console.print(Panel(
                f"[green]{action_name} completed.[/green]\n\nPress ENTER to return to menu, 'q' to quit",
                title="Output",
                border_style="cyan",
                box=box.ROUNDED,
                padding=(1, 2)
            ))
            
            # Wait for user input after action completes
            # This is important to give the user time to see the results
            console.print("[dim]Press ENTER to continue or 'q' to quit[/dim]")
            response = input("> ")
            
            if response.lower() == "q":
                break
            
            # Reset for next action
            selected_action = None
            
        except KeyboardInterrupt:
            # Handle Ctrl-C based on the current menu level
            if menu_level == "main":
                console.print("[yellow]KeyboardInterrupt: Exiting.[/yellow]")
                exit_requested = True
                break
            else:  # action or settings menu level
                console.print("[yellow]KeyboardInterrupt: Returning to main menu.[/yellow]")
                selected_action = None
                menu_level = "main"
                time.sleep(1)
    
    # Exit if requested
    if exit_requested:
        return

def main(cli_args=None, omni_paths=None):
    """
    Main entry point for the Herd AI CLI.
    
    Args:
        cli_args: Directory to process (if None, will prompt)
        omni_paths: Dictionary of paths for various operations
    """
    if omni_paths is None:
        omni_paths = {}
    
    # Show welcome banner
    console.print(BANNER)
    console.print("[dim]Welcome to Herd AI![/dim]")
    
    # Check for environment variables and show provider info
    provider, _ = get_provider_settings()
    console.print(f"[dim]Using AI provider:[/dim] [bright_yellow]{provider}[/bright_yellow]")
    
    # Check required API keys
    api_key = None
    if provider == "xai":
        api_key = os.environ.get("XAI_API_KEY")
        if not api_key:
            console.print("[yellow]⚠️ No XAI API key found. You can set this in Settings.[/yellow]")
    elif provider == "openai":
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            console.print("[yellow]⚠️ No OpenAI API key found. You can set this in Settings.[/yellow]")
    elif provider == "anthropic":
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            console.print("[yellow]⚠️ No Anthropic API key found. You can set this in Settings.[/yellow]")
    elif provider == "groq":
        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            console.print("[yellow]⚠️ No Groq API key found. You can set this in Settings.[/yellow]")
    
    parser = argparse.ArgumentParser(description="Herd AI")
    parser.add_argument("--dir", "-d", required=False, help="Project directory")
    args = parser.parse_args([])  # Create empty namespace for merging
    
    # Override with cli_args if provided
    if cli_args:
        args.dir = cli_args
    
    # Get directory from args or prompt
    if hasattr(args, 'dir') and args.dir:
        root = Path(args.dir)
    else:
        root_input = Prompt.ask("Enter the project directory")
        root = Path(root_input.strip())

    # Validate directory
    while not root.exists() or not root.is_dir():
        console.print(f"[red]Invalid directory:[/red] {root}")
        root_input = Prompt.ask("Please enter a valid project directory")
        root = Path(root_input.strip())

    # Set up paths and launch interface
    rich_interface(root, omni_paths)

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
    with console.status("[bold green]Starting Herd AI...", spinner="dots"):
        time.sleep(1)  # Brief pause for effect
        main()

# --- Accessibility & Theming Note ---
# This interface is designed for clarity and accessibility.
# - High contrast elements with consistent color coding
# - Clear visual hierarchy with icons and spacing
# - Logical navigation flow with numbered options
# - Consistent interaction patterns
# - Progress indicators and status feedback
# For best results, use a terminal with at least 100x32 size.