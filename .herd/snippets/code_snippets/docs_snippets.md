# Code Snippets from src/herd_ai/docs.py

File: `src/herd_ai/docs.py`  
Language: Python  
Extracted: 2025-06-07 05:09:38  

## Snippet 1
Lines 6-18

```Python
# citation extraction. It leverages LLMs for summarization and technical writing,
# and integrates with the rest of the herd_ai ecosystem.
# =============================================================================

from pathlib import Path
import logging
from typing import List, Dict, Any, Optional

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel

# =============================================================================
```

## Snippet 2
Lines 19-36

```Python
# Import configuration and utility functions with fallbacks for various contexts
# =============================================================================
try:
    from herd_ai.utils.file import get_file_text
    from herd_ai.utils.ai_provider import process_with_ai
    from herd_ai.rename import generate_description
    from herd_ai.citations import extract_citations_from_text
    from herd_ai.utils.analysis import generate_document_summary
    from herd_ai.config import DEFAULT_AI_PROVIDER, CODE_EXTENSIONS, TEXT_EXTENSIONS
    from herd_ai.utils import config as herd_config
except Exception as e:
    print(f"Error importing modules in docs.py: {e}")
    print("Make sure you're running from the project directory or the package is installed.")

console = Console()

# =============================================================================
# generate_docs
```

## Snippet 3
Lines 41-44

```Python
def generate_docs(directory: Path, recursive: bool, provider: Optional[str] = None, log_callback: Optional[Any] = None):
    """
    Generate a full README.md by summarizing project files with rich feedback.
    Args:
```

## Snippet 4
Lines 49-59

```Python
Returns:
        Dictionary with results of the documentation generation process
    """
    result = {
        "success": False,
        "files_processed": 0,
        "readme_path": None,
        "error": None
    }
    try:
        # Ensure directory is a Path object
```

## Snippet 5
Lines 63-67

```Python
if log_callback:
                log_callback(msg)
            else:
                console.print(msg)
```

## Snippet 6
Lines 74-76

```Python
if saved_provider:
                provider = saved_provider
                log(f"[cyan]Loading provider from config: {saved_provider}[/cyan]")
```

## Snippet 7
Lines 77-84

```Python
provider = provider or DEFAULT_AI_PROVIDER

        log(Panel.fit("[bold blue]Generating Documentation[/bold blue]", title="Documentation Operation"))
        log(f"[bold cyan]Using AI provider: {provider}[/bold cyan]")

        # Get relevant file extensions from config
        try:
            code_exts = set(CODE_EXTENSIONS.keys())
```

## Snippet 8
Lines 88-92

```Python
except Exception as e:
            valid_exts = {'.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.c', '.cpp', '.h', '.cs', '.go', '.rs', '.php', '.rb', '.md'}
            log(f"[yellow]Could not load extension list from config, using defaults. Error: {e}[/yellow]")

        entries = []
```

## Snippet 9
Lines 104-113

```Python
if not files:
            msg = "No code or Markdown files found to document!"
            log(f"[yellow]{msg}[/yellow]")
            result["success"] = True
            result["message"] = msg
            return result

        processed_files = 0
        error_files = 0
```

## Snippet 10
Lines 119-123

```Python
log(f"[dim]Generating description for {p.name}[/dim]")
                    desc = generate_description(p, provider=provider)
                    rel = p.relative_to(directory)
                    entries.append(f"- **{rel}**: {desc[:200]}")
                    processed_files += 1
```

## Snippet 11
Lines 124-129

```Python
except Exception as e:
                    log(f"[red]Error analyzing {p.name}: {e}[/red]")
                    error_files += 1

                progress.update(task, advance=1)
```

## Snippet 12
Lines 134-153

```Python
log(f"[dim]Sending prompt to {provider} for README generation[/dim]")

        system_prompt = (
            "You are a technical documentation expert. Generate a professional README.md file "
            "based on the file descriptions provided. Include the following sections: "
            "Overview, Installation, Usage, Features, and Project Structure. "
            "Format with proper Markdown and use concise, clear language."
        )

        # Use a placeholder file path since we're not processing a specific file
        placeholder_file = directory / "README.md.tmp"
        log(f"[dim]Using placeholder file: {placeholder_file}[/dim]")

        resp = process_with_ai(placeholder_file, prompt, provider=provider, custom_system_prompt=system_prompt)
        readme_path = directory / "README.md"

        # Ensure output directory exists
        readme_path.parent.mkdir(parents=True, exist_ok=True)

        # Process AI response and save README
```

## Snippet 13
Lines 155-163

```Python
log(f"[dim]Got response of length {len(resp)} from {provider}[/dim]")
            readme_path.write_text(resp, encoding="utf-8")
            log(Panel.fit(f"[green]README.md successfully generated at {readme_path}![/]", title="Documentation Complete"))

            result["success"] = True
            result["files_processed"] = processed_files
            result["readme_path"] = str(readme_path)
            result["readme_size"] = len(resp)
            return result
```

## Snippet 14
Lines 164-172

```Python
else:
            msg = "Documentation generation failed. Empty response from AI provider."
            log(f"[red]{msg}[/red]")

            result["error"] = msg
            result["files_processed"] = processed_files
            result["readme_path"] = None
            return result
```

## Snippet 15
Lines 175-179

```Python
if log_callback:
            log_callback(f"[red]{error_msg}[/red]")
        result["error"] = error_msg
        return result
```

## Snippet 16
Lines 186-192

```Python
def export_document_summary(dir: Path, out: Path = None, provider: Optional[str] = None) -> Path:
    """
    Generate and export a document summary as Markdown.

    Args:
        dir: Directory containing documents to summarize.
        out: Output path (defaults to dir/document_summary.md).
```

## Snippet 17
Lines 195-198

```Python
Returns:
        Path to the generated summary file.
    """
    sm = generate_document_summary(dir, provider=provider)
```

## Snippet 18
Lines 209-214

```Python
for kw, c in sorted(sm['top_keywords'].items(), key=lambda x: -x[1])[:20]:
        md += f"- {kw}: {c}\n"

    out.write_text(md)
    return out
```

## Snippet 19
Lines 221-233

```Python
def extract_citations_from_document(file_path: Path, styles: Optional[List[str]] = None) -> List[Dict[str, Any]]:
    """
    Extract citations from a document using robust text extraction and citation parsing.

    Args:
        file_path: Path to the document.
        styles: List of citation styles to extract (default: ['apa']).

    Returns:
        List of citation dictionaries.
    """
    try:
        text = get_file_text(file_path)
```

## Snippet 20
Lines 234-237

```Python
if not text or not text.strip():
            logging.info(f"No text extracted from {file_path}")
            return []
```

## Snippet 21
Lines 238-241

```Python
if styles is None:
            styles = ['apa']

        citations = extract_citations_from_text(text, styles)
```

## Snippet 22
Lines 244-246

```Python
except Exception as e:
        logging.error(f"Error extracting citations from {file_path}: {e}")
        return []
```

