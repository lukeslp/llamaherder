# Code Snippets from src/herd_ai/snippets.py

File: `src/herd_ai/snippets.py`  
Language: Python  
Extracted: 2025-06-07 05:09:22  

## Snippet 1
Lines 15-34

```Python
#   - Integrates with rich for styled CLI output and progress
# =============================================================================

from __future__ import annotations
import re
import time
import os
import sys
from pathlib import Path
from typing import Dict, List, Set, Optional, Callable, Any, Union, Tuple, NamedTuple
import hashlib
import json
from dataclasses import dataclass
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeRemainingColumn
from rich.syntax import Syntax
from rich.table import Table
from rich import box
```

## Snippet 2
Lines 43-73

```Python
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

try:
    try:
        # First try the standard package import
        from herd_ai.config import TEXT_EXTENSIONS, SNIPPET_EXTENSIONS, CODE_EXTENSIONS, is_code_extension
        from herd_ai.utils.file import get_file_text
        from herd_ai.utils.ollama import send_prompt_to_ollama
    except ImportError:
        try:
            # Then try legacy package import
            from llamacleaner.config import TEXT_EXTENSIONS, SNIPPET_EXTENSIONS, CODE_EXTENSIONS, is_code_extension
            from llamacleaner.utils.file import get_file_text
            from llamacleaner.utils.ollama import send_prompt_to_ollama
        except ImportError:
            try:
                # Then try relative imports from current directory
                from config import TEXT_EXTENSIONS, SNIPPET_EXTENSIONS, CODE_EXTENSIONS, is_code_extension
                from utils.file import get_file_text
                from utils.ollama import send_prompt_to_ollama
            except ImportError:
                # Finally try direct imports using the file path
                sys.path.insert(0, str(Path(__file__).resolve().parent))
                from herd_ai.config import TEXT_EXTENSIONS, SNIPPET_EXTENSIONS, CODE_EXTENSIONS, is_code_extension
                from herd_ai.utils.file import get_file_text
                from herd_ai.utils.ollama import send_prompt_to_ollama
except Exception as e:
    print(f"Error importing modules in snippets.py: {e}")
    print("Make sure you're running from the project directory or the package is installed.")
```

## Snippet 3
Lines 74-87

```Python
# Add fallback definitions for critical constants if imports fail
    TEXT_EXTENSIONS = {'.txt', '.md', '.rst', '.tex', '.json', '.yaml', '.yml', '.toml', '.xml', '.env', '.properties', '.conf', '.ini', '.sql', '.graphql', '.sh', '.bash', '.zsh', '.ps1', '.bat', '.cmd'}

    SNIPPET_EXTENSIONS = {
        '.py': 'Python', '.js': 'JavaScript', '.ts': 'TypeScript', '.jsx': 'React JSX',
        '.tsx': 'React TSX', '.html': 'HTML', '.css': 'CSS', '.scss': 'SCSS',
        '.less': 'Less', '.php': 'PHP', '.rb': 'Ruby', '.go': 'Go', '.rs': 'Rust',
        '.java': 'Java', '.kt': 'Kotlin', '.scala': 'Scala', '.c': 'C', '.cpp': 'C++',
        '.h': 'C Header', '.hpp': 'C++ Header', '.cs': 'C#', '.swift': 'Swift',
        '.vue': 'Vue', '.svelte': 'Svelte', '.dart': 'Dart'
    }

    CODE_EXTENSIONS = SNIPPET_EXTENSIONS
```

## Snippet 4
Lines 96-101

```Python
def get_file_text(path):
        try:
            return Path(path).read_text(encoding='utf-8', errors='ignore')
        except:
            return ""
```

## Snippet 5
Lines 102-105

```Python
def send_prompt_to_ollama(prompt, model=None, max_tokens=2048, temperature=0.7, system_prompt=None, n=1, stream=False):
        print("Mock Ollama API call (module not available)")
        return {"text": "API module not available"}
```

## Snippet 6
Lines 106-118

```Python
console = Console()

STYLES = {
    "header": "bold cyan",
    "subheader": "italic magenta",
    "success": "bold green",
    "error": "bold red",
    "warning": "yellow",
    "info": "blue",
    "highlight": "bold cyan underline",
    "dim": "grey70 italic",
}
```

## Snippet 7
Lines 119-126

```Python
class CodeBlock(NamedTuple):
    """
    Represents a block of code with its location in the source file.
    """
    content: str
    start_line: int
    end_line: int
```

## Snippet 8
Lines 129-133

```Python
Returns a formatted timestamp string for the current time.
    """
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
```

## Snippet 9
Lines 134-140

```Python
def log_message(msg: str, log_path: Path):
    """
    Appends a timestamped message to the specified log file.
    """
    with open(log_path, "a", encoding="utf-8") as lf:
        lf.write(f"[{current_timestamp()}] {msg}\n")
```

## Snippet 10
Lines 145-165

```Python
Returns a dictionary with lists of found items for each category.
    """
    creds = {
        "api_keys": [],
        "endpoints": [],
        "schemas": [],
        "connection_strings": []
    }
    key_patterns = [
        r'(?:api[_-]?key|apikey|access[_-]?token|auth[_-]?token|client[_-]?secret)["\']?\s*(?::|=|:=|\+=)\s*["\']([a-zA-Z0-9_\-\.]{20,})["\']',
        r'bearer\s+([a-zA-Z0-9_\-\.]{20,})',
        r'token["\']?\s*(?::|=|:=|\+=)\s*["\']([a-zA-Z0-9_\-\.]{20,})["\']',
        r'(?:password|secret|auth)["\']?\s*(?::|=|:=|\+=)\s*["\']([^\'\"]+)["\']'
    ]
    endpoint_patterns = [
        r'https?://([a-zA-Z0-9][-a-zA-Z0-9]*\.)*api\.[-a-zA-Z0-9.]+\.[a-zA-Z]{2,}/[-a-zA-Z0-9/%_.~?&=]*',
        r'https?://([a-zA-Z0-9][-a-zA-Z0-9]*\.)*[-a-zA-Z0-9.]+\.[a-zA-Z]{2,}/api/[-a-zA-Z0-9/%_.~?&=]*',
        r'(?:endpoint|url|uri|base[_-]?url)["\']?\s*(?::|=|:=|\+=)\s*["\']([^"\']+api[^"\']+)["\']'
    ]
    schema_patterns = [
        r'(?:schema|model)\s*=\s*{[\s\S]*?}',
```

## Snippet 11
Lines 166-169

```Python
r'@app\.(?:get|post|put|delete|patch)\(["\']([^"\']+)["\']',
        r'function\s+\w+\([^)]*\)\s*{[\s\S]*?fetch\(["\']([^"\']+)["\']',
        r'(?:routes|endpoints)\s*=\s*\[[\s\S]*?\]',
        r'openapi:\s*3\.[0-9]+[\s\S]*?paths:[\s\S]*?}'
```

## Snippet 12
Lines 170-175

```Python
]
    conn_patterns = [
        r'(?:connection[_-]?string|conn[_-]?str)["\']?\s*(?::|=|:=|\+=)\s*["\']([^\'\"]+)["\']',
        r'(?:mongodb|postgresql|mysql|redis)://[^\s\'\"<>]+',
        r'(?:Data Source|Server|Database|User ID|Password)=[^;]+'
    ]
```

## Snippet 13
Lines 200-203

```Python
for key in creds:
        creds[key] = list(dict.fromkeys(creds[key]))
    return creds
```

## Snippet 14
Lines 204-208

```Python
def split_into_chunks(text: str, size: int = 6000) -> List[str]:
    """
    Splits text into chunks of approximately the specified size (in characters).
    """
    lines, out, buf, count = text.splitlines(), [], [], 0
```

## Snippet 15
Lines 210-215

```Python
if count + len(ln) > size and buf:
            out.append("\n".join(buf))
            buf = []
            count = 0
        buf.append(ln)
        count += len(ln)
```

## Snippet 16
Lines 216-219

```Python
if buf:
        out.append("\n".join(buf))
    return out
```

## Snippet 17
Lines 220-225

```Python
def group_chunks(chunks: List[str], threshold: float = 0.8) -> List[str]:
    """
    Groups similar text chunks together based on a similarity threshold.
    """
    from difflib import SequenceMatcher
    grouped, current = [], [chunks[0]]
```

## Snippet 18
Lines 227-231

```Python
if SequenceMatcher(None, current[-1], c).ratio() > threshold:
            current.append(c)
        else:
            grouped.append("\n".join(current))
            current = [c]
```

## Snippet 19
Lines 235-238

```Python
def group_batches(items: List[str], batch_size: int = 25) -> List[List[str]]:
    """
    Splits a list into batches of the specified size.
    """
```

## Snippet 20
Lines 244-255

```Python
Represents a code snippet with associated metadata for organization and search.
    """
    content: str
    file_path: str
    start_line: int
    end_line: int
    language: str
    category: str
    tags: Set[str]
    hash: str
    related_snippets: List[str] = None
```

## Snippet 21
Lines 258-271

```Python
Converts the CodeSnippet to a dictionary for serialization.
        """
        return {
            "content": self.content,
            "file_path": self.file_path,
            "start_line": self.start_line,
            "end_line": self.end_line,
            "language": self.language,
            "category": self.category,
            "tags": list(self.tags),
            "hash": self.hash,
            "related_snippets": self.related_snippets or []
        }
```

## Snippet 22
Lines 273-288

```Python
def from_dict(cls, data: Dict[str, Any]) -> 'CodeSnippet':
        """
        Creates a CodeSnippet from a dictionary.
        """
        return cls(
            content=data["content"],
            file_path=data["file_path"],
            start_line=data["start_line"],
            end_line=data["end_line"],
            language=data["language"],
            category=data["category"],
            tags=set(data["tags"]),
            hash=data["hash"],
            related_snippets=data.get("related_snippets", [])
        )
```

## Snippet 23
Lines 289-298

```Python
def categorize_snippet(content: str, file_path: str) -> Tuple[str, Set[str]]:
    """
    Categorizes a code snippet and assigns relevant tags based on content and file type.
    Returns a tuple of (category, tags).
    """
    categories = {
        "api_client": (
            r"(?:fetch|axios|request|http|api|client)\s*\.",
            r"\.(?:get|post|put|delete|patch)\s*\(",
            r"new\s+(?:HttpClient|ApiClient|RestClient)",
```

## Snippet 24
Lines 305-309

```Python
),
        "database": (
            r"(?:select|insert|update|delete)\s+(?:from|into|where)",
            r"mongoose|sequelize|prisma|typeorm",
            r"db\.|database\.|connection\.",
```

## Snippet 25
Lines 340-351

```Python
tag_patterns = {
        "async": r"async|await|promise|then\(",
        "error-handling": r"try|catch|throw|error|exception",
        "testing": r"test|describe|it\(|assert|expect",
        "security": r"encrypt|decrypt|hash|salt|secure",
        "validation": r"validate|schema|check|verify",
        "caching": r"cache|redis|memcache",
        "logging": r"log\.|logger\.|console\.",
        "middleware": r"middleware|interceptor|filter",
        "frontend": r"component|render|view|template",
        "backend": r"controller|service|repository|model"
    }
```

## Snippet 26
Lines 367-370

```Python
Finds related snippets to the given snippet based on tags, imports, and function patterns.
    Returns a list of related snippet hashes.
    """
    related = []
```

## Snippet 27
Lines 372-374

```Python
if other.hash == snippet.hash:
            continue
        common_tags = len(snippet.tags & other.tags)
```

## Snippet 28
Lines 383-387

```Python
def extract_imports(content: str) -> Set[str]:
    """
    Extracts imported module names from code content.
    """
    imports = set()
```

## Snippet 29
Lines 390-393

```Python
for match in re.finditer(r'(?:import|require)\s*\([\'"]([^\'\"]+)[\'"]\)', content):
        imports.add(match.group(1).split('/')[0])
    return imports
```

## Snippet 30
Lines 396-399

```Python
Checks if two code snippets have similar function names or API call patterns.
    """
    funcs1 = set(re.findall(r'function\s+(\w+)', content1))
    funcs2 = set(re.findall(r'function\s+(\w+)', content2))
```

## Snippet 31
Lines 400-405

```Python
if funcs1 & funcs2:
        return True
    patterns1 = set(re.findall(r'\.(?:get|post|put|delete|patch)\s*\([\'"]([^\'"]+)[\'"]', content1))
    patterns2 = set(re.findall(r'\.(?:get|post|put|delete|patch)\s*\([\'"]([^\'"]+)[\'"]', content2))
    return bool(patterns1 & patterns2)
```

## Snippet 32
Lines 406-411

```Python
def extract_snippets(content: str) -> List[Tuple[str, int, int]]:
    """
    Extracts code snippets from content using block analysis.
    Returns a list of (snippet, start_line, end_line) tuples.
    """
    blocks = split_into_blocks(content)
```

## Snippet 33
Lines 414-419

```Python
def split_into_blocks(content: str) -> List[CodeBlock]:
    """
    Splits text content into meaningful code blocks using indentation and pattern heuristics.
    Returns a list of CodeBlock objects.
    """
    lines = content.splitlines()
```

## Snippet 34
Lines 420-425

```Python
if not lines:
        return []
    blocks = []
    current_block = []
    start_line = 1
    block_indent_level = None
```

## Snippet 35
Lines 442-451

```Python
if is_meaningful_block(block_content):
                    blocks.append(CodeBlock(
                        content=block_content,
                        start_line=start_line,
                        end_line=i-1
                    ))
                current_block = [line_content]
                start_line = i
                block_indent_level = line_indent
                continue
```

## Snippet 36
Lines 456-461

```Python
if is_meaningful_block(block_content):
                        blocks.append(CodeBlock(
                            content=block_content,
                            start_line=start_line,
                            end_line=i-1
                        ))
```

## Snippet 37
Lines 470-475

```Python
if is_meaningful_block(block_content):
                    blocks.append(CodeBlock(
                        content=block_content,
                        start_line=start_line,
                        end_line=i-2
                    ))
```

## Snippet 38
Lines 481-486

```Python
if is_meaningful_block(block_content):
            blocks.append(CodeBlock(
                content=block_content,
                start_line=start_line,
                end_line=len(lines)
            ))
```

## Snippet 39
Lines 494-496

```Python
if not content.strip():
        return False
    lines = content.splitlines()
```

## Snippet 40
Lines 503-522

```Python
if non_empty_lines >= 5:
        return True
    code_patterns = [
        r"\bdef\s+\w+",
        r"\bclass\s+\w+",
        r"\bimport\s+\w+",
        r"\bfrom\s+\w+",
        r"\breturn\b",
        r"\bfunction\s+\w+",
        r"\bconst\s+\w+\s*=",
        r"\blet\s+\w+\s*=",
        r"\bvar\s+\w+\s*=",
        r"\bpublic\s+\w+",
        r"\bprivate\s+\w+",
        r"\bif\s*\(",
        r"\bfor\s*\(",
        r"\bwhile\s*\(",
        r"\bswitch\s*\(",
        r"\btry\s*\{",
        r"\bcatch\s*\(",
```

## Snippet 41
Lines 523-529

```Python
r"@\w+",
        r"<\w+[^>]*>",
        r"\w+\s*\(\s*\)\s*\{",
        r"\w+\s*=\s*function",
        r"\w+:\s*\w+",
        r"#include\s+[<\"]",
        r"#define\s+\w+",
```

## Snippet 42
Lines 536-544

```Python
def process_snippet_file(
    file_path: Path,
    output_path: Path,
    api_creds_path: Optional[Path],
    log_path: Optional[Path],
    log_callback: Optional[Callable[[str], None]] = None,
    provider: str = None
) -> Dict[str, Any]:
    """
```

## Snippet 43
Lines 545-552

```Python
Processes a single file for snippet extraction.
    Extracts code blocks, writes them to output, and returns extraction results.

    Args:
        file_path: Path to the file to process
        output_path: Path to write the extracted snippets
        api_creds_path: Path to write API credentials found in the file
        log_path: Path to write logs
```

## Snippet 44
Lines 555-564

```Python
"""
    results = {
        "file": str(file_path),
        "snippets_found": False,
        "api_creds_found": False,
        "error": None,
        "extracted_snippets": []
    }
    try:
        content = file_path.read_text(encoding='utf-8', errors='ignore')
```

## Snippet 45
Lines 568-570

```Python
if log_callback:
            log_callback(f"[dim]Analyzing content to extract code blocks from {file_path}...[/dim]")
        blocks = split_into_blocks(content)
```

## Snippet 46
Lines 573-577

```Python
if blocks:
            results["snippets_found"] = True
            language = CODE_EXTENSIONS.get(file_path.suffix.lower(), "txt")
            snippet_file = output_path / f"{file_path.stem}_snippets.md"
            snippet_file.parent.mkdir(parents=True, exist_ok=True)
```

## Snippet 47
Lines 580-582

```Python
with snippet_file.open('w', encoding='utf-8') as f:
                f.write(f"# Code Snippets from {file_path}\n\n")
                f.write(f"File: `{file_path}`  \n")
```

## Snippet 48
Lines 585-597

```Python
for i, block in enumerate(blocks, 1):
                    syntax_language = CODE_EXTENSIONS.get(file_path.suffix.lower(), "text")
                    f.write(f"## Snippet {i}\n")
                    f.write(f"Lines {block.start_line}-{block.end_line}\n\n")
                    f.write("```" + syntax_language + "\n")
                    f.write(block.content.strip() + "\n")
                    f.write("```\n\n")
                    results["extracted_snippets"].append({
                        "content": block.content,
                        "start_line": block.start_line,
                        "end_line": block.end_line,
                        "language": syntax_language
                    })
```

## Snippet 49
Lines 610-616

```Python
def write_organized_snippets(snippets: List[CodeSnippet], output_path: Path) -> None:
    """
    Writes snippets to organized files by category and generates an index.
    """
    output_path.mkdir(parents=True, exist_ok=True)
    with open(output_path / "index.md", "w", encoding="utf-8") as f:
        f.write("# Code Snippets\n\n")
```

## Snippet 50
Lines 617-626

```Python
for snippet in snippets:
            snippet_file = output_path / f"{snippet.hash}.md"
            with open(snippet_file, "w", encoding="utf-8") as sf:
                sf.write(f"# Code Snippet {snippet.hash}\n\n")
                sf.write(f"Source: `{snippet.file_path}` (lines {snippet.start_line}-{snippet.end_line})\n\n")
                sf.write(f"Language: {snippet.language}\n\n")
                sf.write(f"Tags: {', '.join(sorted(snippet.tags))}\n\n")
                sf.write("```" + snippet.language.lower() + "\n")
                sf.write(snippet.content + "\n")
                sf.write("```\n\n")
```

## Snippet 51
Lines 631-637

```Python
f.write(f"## [{snippet.hash}](./{snippet.hash}.md)\n\n")
            f.write(f"Source: `{snippet.file_path}`\n\n")
            f.write(f"Tags: {', '.join(sorted(snippet.tags))}\n\n")
            f.write("```" + snippet.language.lower() + "\n")
            f.write(snippet.content[:200] + "...\n")
            f.write("```\n\n")
```

## Snippet 52
Lines 638-647

```Python
def batch_process_snippets(
    files: List[Path],
    output_path: Path,
    api_creds_path: Optional[Path],
    log_path: Optional[Path],
    batch_size: int = 50,
    log_callback: Optional[Callable[[str], None]] = None,
    provider: str = None
) -> Dict[str, Any]:
    """
```

## Snippet 53
Lines 648-656

```Python
Processes files in batches for snippet extraction.
    Returns a dictionary with processing statistics.

    Args:
        files: List of files to process
        output_path: Path to write the extracted snippets
        api_creds_path: Path to write API credentials found in the files
        log_path: Path to write logs
        batch_size: Number of files to process in each batch
```

## Snippet 54
Lines 668-673

```Python
stats = {
        "total": len(files),
        "with_snippets": 0,
        "with_creds": 0,
        "errors": 0
    }
```

## Snippet 55
Lines 694-698

```Python
if is_code_extension(file_path):
        return True
    try:
        with file_path.open('r', encoding='utf-8', errors='ignore') as f:
            first_line = f.readline().strip()
```

## Snippet 56
Lines 701-704

```Python
except Exception:
        pass
    return False
```

## Snippet 57
Lines 705-714

```Python
def process_snippets(
    file_or_dir: Path,
    recursive: bool = False,
    batch_size: int = 50,
    exclude_ext: Set[str] = None,
    omni_paths: Dict[str, Any] = None,
    log_callback: Optional[Callable[[str], None]] = None,
    provider: str = None
) -> None:
    """
```

## Snippet 58
Lines 715-722

```Python
Main entry point for extracting code snippets from a file or directory.
    Handles batch processing, directory traversal, and progress reporting.

    Args:
        file_or_dir: File or directory to process
        recursive: If True, process subdirectories recursively
        batch_size: Number of files to process in each batch
        exclude_ext: Set of extensions to exclude
```

## Snippet 59
Lines 729-734

```Python
if exclude_ext is None:
        exclude_ext = {".git", ".env", ".venv", "__pycache__", ".pyc", ".pyo"}
    base_dir = omni_paths.get("base_dir", Path(".herd"))
    snippets_dir = omni_paths.get("snippets_dir", base_dir / "snippets")
    log_file = omni_paths.get("log", base_dir / "log.txt")
    snippets_dir.mkdir(parents=True, exist_ok=True)
```

## Snippet 60
Lines 765-769

```Python
f"[yellow]No code files found for snippet extraction[/yellow]\n\n"
            f"Supported code extensions: {', '.join(sorted(CODE_EXTENSIONS.keys()))}",
            title="[bold]Warning[/bold]",
            border_style="yellow",
            box=box.ROUNDED
```

## Snippet 61
Lines 780-797

```Python
with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(complete_style="green", finished_style="bright_green"),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeRemainingColumn(),
        console=console
    ) as progress:
        total_task = progress.add_task(
            "[cyan]Processing files...",
            total=len(files_to_process)
        )
        stats = {
            "total": len(files_to_process),
            "with_snippets": 0,
            "failed": 0,
            "total_snippets": 0
        }
```

## Snippet 62
Lines 800-802

```Python
for file_path in batch:
                try:
                    progress.update(total_task, description=f"[cyan]Processing[/cyan] → {file_path.name}")
```

## Snippet 63
Lines 803-814

```Python
rel_path = file_path.relative_to(file_or_dir) if file_or_dir.is_dir() else file_path.name
                    output_dir = snippets_dir / "code_snippets" / Path(rel_path).parent
                    output_dir.mkdir(parents=True, exist_ok=True)
                    result = process_snippet_file(
                        file_path,
                        output_dir,
                        None,
                        log_file,
                        log_callback,
                        provider
                    )
                    time.sleep(0.1)
```

## Snippet 64
Lines 816-818

```Python
if log_callback:
                            log_callback(f"[error]Error processing {file_path}: {result['error']}[/error]")
                        stats["failed"] += 1
```

## Snippet 65
Lines 829-831

```Python
if log_callback:
                        log_callback(f"[error]Failed to process {file_path}: {str(e)}[/error]")
                    stats["failed"] += 1
```

## Snippet 66
Lines 834-847

```Python
console.print()
    console.print(Panel(
        f"[bold green]✓[/bold green] Snippet extraction complete!\n"
        f"[cyan]Code files processed:[/cyan] {stats['total']}\n"
        f"[cyan]Files with snippets:[/cyan] {stats['with_snippets']}\n"
        f"[cyan]Total snippets found:[/cyan] {stats['total_snippets']}\n"
        f"[cyan]Files with errors:[/cyan] {stats['failed']}\n"
        f"[cyan]Output directory:[/cyan] {snippets_dir / 'code_snippets'}\n\n"
        f"[dim]Note: Only code files (based on extension or shebang) were processed.[/dim]",
        title="[bold]Snippet Extraction Summary[/bold]",
        border_style="green",
        box=box.ROUNDED
    ))
```

## Snippet 67
Lines 848-859

```Python
def process_directory(
    directory: Path,
    recursive: bool = False,
    batch_size: int = 50,
    exclude_ext: Set[str] = None,
    log_callback: Optional[Callable[[str], None]] = None,
    provider: str = None,
    omni_paths: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Process a directory to extract code snippets.
```

## Snippet 68
Lines 860-866

```Python
Wrapper around process_snippets for backward compatibility.

    Args:
        directory: Directory to process
        recursive: Whether to process subdirectories
        batch_size: Number of files to process in one batch
        exclude_ext: Set of file extensions to exclude
```

## Snippet 69
Lines 871-883

```Python
Returns:
        Dictionary with processing statistics
    """
    result = {
        "success": False,
        "files_processed": 0,
        "snippets_found": 0,
        "output_dir": None,
        "error": None
    }

    try:
        # Ensure directory is a Path object
```

## Snippet 70
Lines 898-902

```Python
if log_callback:
                log_callback(f"[red]{error_msg}[/red]")
            result["error"] = error_msg
            return result
```

## Snippet 71
Lines 904-918

```Python
if omni_paths is None:
            base_dir = directory / ".herd"
            snippets_dir = base_dir / "snippets"
            log_file = base_dir / "log.txt"
        else:
            base_dir = omni_paths.get("base_dir", directory / ".herd")
            snippets_dir = omni_paths.get("snippets_dir", base_dir / "snippets")
            log_file = omni_paths.get("log", base_dir / "log.txt")

        # Ensure directories exist
        snippets_dir.mkdir(parents=True, exist_ok=True)

        # Find code files to process
        files_to_process = []
```

## Snippet 72
Lines 927-930

```Python
result["success"] = True
                result["message"] = "No code files to process"
                result["output_dir"] = str(snippets_dir)
                return result
```

## Snippet 73
Lines 955-957

```Python
if log_callback:
                log_callback("[yellow]No code files found to process[/yellow]")
            result["success"] = True
```

## Snippet 74
Lines 958-961

```Python
result["message"] = "No code files found for processing"
            result["output_dir"] = str(snippets_dir)
            return result
```

## Snippet 75
Lines 962-982

```Python
# Process the files
        stats = batch_process_snippets(
            files_to_process,
            snippets_dir,
            None,  # api_creds_path
            log_file,
            batch_size,
            log_callback,
            provider
        )

        # Return comprehensive results
        result["success"] = True
        result["files_processed"] = len(files_to_process)
        result["with_snippets"] = stats.get("with_snippets", 0)
        result["snippets_found"] = stats.get("total_snippets", 0)
        result["files_with_errors"] = stats.get("failed", 0)
        result["output_dir"] = str(snippets_dir / "code_snippets")

        return result
```

## Snippet 76
Lines 985-989

```Python
if log_callback:
            log_callback(f"[red]{error_msg}[/red]")
        result["error"] = error_msg
        return result
```

## Snippet 77
Lines 991-996

```Python
def search_snippets(
    query: str,
    snippets_dir: Path,
    limit: int = 10
) -> List[Dict[str, Any]]:
    """
```

## Snippet 78
Lines 997-1010

```Python
Search for snippets matching a query string.

    Args:
        query: Search query
        snippets_dir: Directory containing snippet files
        limit: Maximum number of results to return

    Returns:
        List of matching snippets as dictionaries
    """
    results = []
    pattern = re.compile(re.escape(query), re.IGNORECASE)

    snippet_files = list(snippets_dir.rglob("*.snippet.json"))
```

## Snippet 79
Lines 1011-1015

```Python
for snippet_file in snippet_files[:100]:  # Limit to prevent too much processing
        try:
            with open(snippet_file, "r", encoding="utf-8") as f:
                snippet_data = json.load(f)
```

## Snippet 80
Lines 1028-1046

```Python
def export_snippets(
    snippets_dir: Path,
    output_format: str = "markdown",
    output_file: Optional[Path] = None
) -> str:
    """
    Export snippets to a specific format.

    Args:
        snippets_dir: Directory containing snippet files
        output_format: Format to export (markdown, json, html)
        output_file: Optional file to write the output to

    Returns:
        Exported content as a string
    """
    snippet_files = list(snippets_dir.rglob("*.snippet.json"))
    snippets = []
```

## Snippet 81
Lines 1047-1056

```Python
for snippet_file in snippet_files:
        try:
            with open(snippet_file, "r", encoding="utf-8") as f:
                snippet_data = json.load(f)
                snippets.append(snippet_data)
        except Exception as e:
            print(f"Error reading snippet file {snippet_file}: {e}")

    # Generate output based on format
    output = ""
```

## Snippet 82
Lines 1059-1065

```Python
for snippet in snippets:
            output += f"## {snippet.get('category', 'Uncategorized')}\n\n"
            output += f"**File:** {snippet.get('file_path')}\n\n"
            output += f"**Tags:** {', '.join(snippet.get('tags', []))}\n\n"
            output += "```" + snippet.get('language', '') + "\n"
            output += snippet.get('content', '') + "\n"
            output += "```\n\n"
```

## Snippet 83
Lines 1070-1078

```Python
for snippet in snippets:
            output += f"<h2>{snippet.get('category', 'Uncategorized')}</h2>\n"
            output += f"<p><strong>File:</strong> {snippet.get('file_path')}</p>\n"
            output += f"<p><strong>Tags:</strong> {', '.join(snippet.get('tags', []))}</p>\n"
            output += f"<pre><code class='{snippet.get('language', '')}'>\n"
            output += snippet.get('content', '') + "\n"
            output += "</code></pre>\n\n"
        output += "</body></html>"
```

## Snippet 84
Lines 1080-1085

```Python
if output_file:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(output)

    return output
```

## Snippet 85
Lines 1086-1118

```Python
def import_snippet(
    content: str,
    file_path: str,
    language: str,
    category: str,
    tags: List[str],
    snippets_dir: Path
) -> Dict[str, Any]:
    """
    Import a new snippet into the snippet collection.

    Args:
        content: Snippet content
        file_path: Original file path
        language: Programming language
        category: Snippet category
        tags: List of tags
        snippets_dir: Directory to store snippets

    Returns:
        Imported snippet data
    """
    snippet = CodeSnippet(
        content=content,
        file_path=file_path,
        start_line=1,
        end_line=content.count("\n") + 1,
        language=language,
        category=category,
        tags=set(tags),
        hash=compute_snippet_hash(content)
    )
```

## Snippet 86
Lines 1119-1129

```Python
# Create output directory if it doesn't exist
    output_path = snippets_dir / "code_snippets"
    output_path.mkdir(parents=True, exist_ok=True)

    # Save snippet to file
    snippet_file = output_path / f"{snippet.hash}.snippet.json"
    with open(snippet_file, "w", encoding="utf-8") as f:
        json.dump(snippet.to_dict(), f, indent=2)

    return snippet.to_dict()
```

## Snippet 87
Lines 1130-1137

```Python
def list_snippet_formats() -> List[str]:
    """
    List available snippet export formats.

    Returns:
        List of available format names
    """
    return ["markdown", "json", "html"]
```

