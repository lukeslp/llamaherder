# =============================================================================
# herd_ai.snippets.py
#
# Code Snippet Extraction and Organization Utilities
#
# This module provides functionality for extracting, categorizing, and organizing
# code snippets from source files. It supports batch processing, code block
# detection, metadata tagging, and output with syntax highlighting.
#
# Major features:
#   - Extracts code blocks from files with known code extensions or shebangs
#   - Categorizes and tags snippets based on content and file type
#   - Writes organized snippet files and summary indices
#   - Supports batch and recursive directory processing
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

# Setup path for local imports
current_dir = Path(__file__).parent.resolve()
parent_dir = current_dir.parent.resolve()
root_dir = parent_dir.parent.resolve()
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))
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
    
    def is_code_extension(file_path):
        ext = file_path.suffix.lower() if hasattr(file_path, 'suffix') else ''
        if not ext and hasattr(file_path, 'name'):
            parts = file_path.name.split('.')
            if len(parts) > 1:
                ext = f".{parts[-1].lower()}"
        return ext in CODE_EXTENSIONS
    
    def get_file_text(path):
        try:
            return Path(path).read_text(encoding='utf-8', errors='ignore')
        except:
            return ""
            
    def send_prompt_to_ollama(prompt, model=None, max_tokens=2048, temperature=0.7, system_prompt=None, n=1, stream=False):
        print("Mock Ollama API call (module not available)")
        return {"text": "API module not available"}

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

class CodeBlock(NamedTuple):
    """
    Represents a block of code with its location in the source file.
    """
    content: str
    start_line: int
    end_line: int

def current_timestamp() -> str:
    """
    Returns a formatted timestamp string for the current time.
    """
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def log_message(msg: str, log_path: Path):
    """
    Appends a timestamped message to the specified log file.
    """
    with open(log_path, "a", encoding="utf-8") as lf:
        lf.write(f"[{current_timestamp()}] {msg}\n")

def scan_for_api_credentials(content: str) -> Dict[str, List[str]]:
    """
    Scans text content for API credentials, endpoints, schemas, and connection strings.

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
        r'@app\.(?:get|post|put|delete|patch)\(["\']([^"\']+)["\']',
        r'function\s+\w+\([^)]*\)\s*{[\s\S]*?fetch\(["\']([^"\']+)["\']',
        r'(?:routes|endpoints)\s*=\s*\[[\s\S]*?\]',
        r'openapi:\s*3\.[0-9]+[\s\S]*?paths:[\s\S]*?}'
    ]
    conn_patterns = [
        r'(?:connection[_-]?string|conn[_-]?str)["\']?\s*(?::|=|:=|\+=)\s*["\']([^\'\"]+)["\']',
        r'(?:mongodb|postgresql|mysql|redis)://[^\s\'\"<>]+',
        r'(?:Data Source|Server|Database|User ID|Password)=[^;]+'
    ]
    for pattern in key_patterns:
        matches = re.finditer(pattern, content, re.IGNORECASE)
        for match in matches:
            key = match.group(1) if len(match.groups()) > 0 else match.group(0)
            if not any(x in key.lower() for x in ['yourkey', 'example', 'placeholder', 'xxxxxx', '<key>']):
                creds["api_keys"].append(key)
    for pattern in endpoint_patterns:
        matches = re.finditer(pattern, content, re.IGNORECASE)
        for match in matches:
            endpoint = match.group(1) if len(match.groups()) > 0 else match.group(0)
            if not any(x in endpoint.lower() for x in ['example', 'placeholder', '<url>']):
                creds["endpoints"].append(endpoint)
    for pattern in schema_patterns:
        matches = re.finditer(pattern, content, re.MULTILINE | re.DOTALL)
        for match in matches:
            schema = match.group(1) if len(match.groups()) > 0 else match.group(0)
            if schema and len(schema.strip()) > 10:
                creds["schemas"].append(schema.strip())
    for pattern in conn_patterns:
        matches = re.finditer(pattern, content, re.IGNORECASE)
        for match in matches:
            conn_str = match.group(1) if len(match.groups()) > 0 else match.group(0)
            if not any(x in conn_str.lower() for x in ['example', 'placeholder', '<connection>']):
                creds["connection_strings"].append(conn_str)
    for key in creds:
        creds[key] = list(dict.fromkeys(creds[key]))
    return creds

def split_into_chunks(text: str, size: int = 6000) -> List[str]:
    """
    Splits text into chunks of approximately the specified size (in characters).
    """
    lines, out, buf, count = text.splitlines(), [], [], 0
    for ln in lines:
        if count + len(ln) > size and buf:
            out.append("\n".join(buf))
            buf = []
            count = 0
        buf.append(ln)
        count += len(ln)
    if buf:
        out.append("\n".join(buf))
    return out

def group_chunks(chunks: List[str], threshold: float = 0.8) -> List[str]:
    """
    Groups similar text chunks together based on a similarity threshold.
    """
    from difflib import SequenceMatcher
    grouped, current = [], [chunks[0]]
    for c in chunks[1:]:
        if SequenceMatcher(None, current[-1], c).ratio() > threshold:
            current.append(c)
        else:
            grouped.append("\n".join(current))
            current = [c]
    grouped.append("\n".join(current))
    return grouped

def group_batches(items: List[str], batch_size: int = 25) -> List[List[str]]:
    """
    Splits a list into batches of the specified size.
    """
    return [items[i:i+batch_size] for i in range(0, len(items), batch_size)]

@dataclass
class CodeSnippet:
    """
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

    def to_dict(self) -> Dict[str, Any]:
        """
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

    @classmethod
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
            r"@api\s+|@endpoint\s+"
        ),
        "authentication": (
            r"auth|login|logout|session|token|jwt|oauth|permission",
            r"@auth\s+|@login\s+|@secure\s+",
            r"authenticate|authorize|verify"
        ),
        "database": (
            r"(?:select|insert|update|delete)\s+(?:from|into|where)",
            r"mongoose|sequelize|prisma|typeorm",
            r"db\.|database\.|connection\.",
            r"@entity\s+|@repository\s+"
        ),
        "streaming": (
            r"stream\.|createStream|pipe\(",
            r"websocket|socket\.|ws\.",
            r"@stream\s+|@realtime\s+",
            r"EventSource|SSE|Server-Sent"
        ),
        "configuration": (
            r"config\.|settings\.|env\.",
            r"process\.env",
            r"@config\s+|@setting\s+",
            r"\.env|config\.json|settings\.yaml"
        ),
        "utility": (
            r"util\.|helper\.|common\.",
            r"@util\s+|@helper\s+",
            r"function\s+\w+\s*\([^)]*\)"
        )
    }
    category = "other"
    tags = set()
    ext = Path(file_path).suffix.lower()
    if ext in SNIPPET_EXTENSIONS:
        tags.add(f"lang:{SNIPPET_EXTENSIONS[ext]}")
    for cat, patterns in categories.items():
        if any(re.search(pattern, content, re.IGNORECASE | re.MULTILINE) for pattern in patterns):
            category = cat
            tags.add(cat)
            break
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
    for tag, pattern in tag_patterns.items():
        if re.search(pattern, content, re.IGNORECASE | re.MULTILINE):
            tags.add(tag)
    return category, tags

def compute_snippet_hash(content: str) -> str:
    """
    Computes a hash of the snippet content for deduplication.
    """
    normalized = re.sub(r'\s+', ' ', content)
    normalized = re.sub(r'//.*$|\s*/\*.*?\*/\s*', '', normalized, flags=re.MULTILINE)
    return hashlib.sha256(normalized.encode()).hexdigest()[:16]

def find_related_snippets(snippet: CodeSnippet, all_snippets: List[CodeSnippet]) -> List[str]:
    """
    Finds related snippets to the given snippet based on tags, imports, and function patterns.
    Returns a list of related snippet hashes.
    """
    related = []
    for other in all_snippets:
        if other.hash == snippet.hash:
            continue
        common_tags = len(snippet.tags & other.tags)
        if common_tags >= 2:
            related.append(other.hash)
        if any(mod in snippet.content for mod in extract_imports(other.content)):
            related.append(other.hash)
        if similar_patterns(snippet.content, other.content):
            related.append(other.hash)
    return related[:5]

def extract_imports(content: str) -> Set[str]:
    """
    Extracts imported module names from code content.
    """
    imports = set()
    for match in re.finditer(r'(?:from|import)\s+([\w.]+)', content):
        imports.add(match.group(1).split('.')[0])
    for match in re.finditer(r'(?:import|require)\s*\([\'"]([^\'\"]+)[\'"]\)', content):
        imports.add(match.group(1).split('/')[0])
    return imports

def similar_patterns(content1: str, content2: str) -> bool:
    """
    Checks if two code snippets have similar function names or API call patterns.
    """
    funcs1 = set(re.findall(r'function\s+(\w+)', content1))
    funcs2 = set(re.findall(r'function\s+(\w+)', content2))
    if funcs1 & funcs2:
        return True
    patterns1 = set(re.findall(r'\.(?:get|post|put|delete|patch)\s*\([\'"]([^\'"]+)[\'"]', content1))
    patterns2 = set(re.findall(r'\.(?:get|post|put|delete|patch)\s*\([\'"]([^\'"]+)[\'"]', content2))
    return bool(patterns1 & patterns2)

def extract_snippets(content: str) -> List[Tuple[str, int, int]]:
    """
    Extracts code snippets from content using block analysis.
    Returns a list of (snippet, start_line, end_line) tuples.
    """
    blocks = split_into_blocks(content)
    return [(block.content, block.start_line, block.end_line) for block in blocks]

def split_into_blocks(content: str) -> List[CodeBlock]:
    """
    Splits text content into meaningful code blocks using indentation and pattern heuristics.
    Returns a list of CodeBlock objects.
    """
    lines = content.splitlines()
    if not lines:
        return []
    blocks = []
    current_block = []
    start_line = 1
    block_indent_level = None
    for i, line in enumerate(lines, 1):
        line_content = line.rstrip()
        line_indent = len(line_content) - len(line_content.lstrip())
        if not current_block and not line_content.strip():
            start_line = i + 1
            continue
        if not current_block and line_content.strip():
            block_indent_level = line_indent
            current_block.append(line_content)
            continue
        if line_content.strip() and any(pattern in line_content for pattern in [
            "def ", "class ", "function ", "async def", "@", "if ", "for ", "while ",
            "{ ", "} ", "/*", "*/", "/**", "*/", "# SECTION", "# --", "// --"
        ]):
            if current_block:
                block_content = '\n'.join(current_block)
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
        if block_indent_level is not None:
            if line_content.strip() and line_indent < block_indent_level:
                if current_block:
                    block_content = '\n'.join(current_block)
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
        current_block.append(line_content)
        if i > 2 and not line_content.strip() and not lines[i-2].strip():
            if current_block:
                block_content = '\n'.join(current_block[:-2])
                if is_meaningful_block(block_content):
                    blocks.append(CodeBlock(
                        content=block_content,
                        start_line=start_line,
                        end_line=i-2
                    ))
            current_block = []
            start_line = i + 1
            block_indent_level = None
    if current_block:
        block_content = '\n'.join(current_block)
        if is_meaningful_block(block_content):
            blocks.append(CodeBlock(
                content=block_content,
                start_line=start_line,
                end_line=len(lines)
            ))
    return blocks

def is_meaningful_block(content: str) -> bool:
    """
    Determines if a block of code is meaningful enough to extract as a snippet.
    Returns True if the block is considered meaningful.
    """
    if not content.strip():
        return False
    lines = content.splitlines()
    if len(lines) < 3:
        return False
    if all(line.strip().startswith(("#", "//", "/*", "*", "'''", '"""', "<!--", "-->")) 
           for line in lines if line.strip()):
        return False
    non_empty_lines = len([line for line in lines if line.strip()])
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
        r"@\w+",
        r"<\w+[^>]*>",
        r"\w+\s*\(\s*\)\s*\{",
        r"\w+\s*=\s*function",
        r"\w+:\s*\w+",
        r"#include\s+[<\"]",
        r"#define\s+\w+",
    ]
    for pattern in code_patterns:
        if re.search(pattern, content, re.MULTILINE):
            return True
    return False

def process_snippet_file(
    file_path: Path, 
    output_path: Path, 
    api_creds_path: Optional[Path], 
    log_path: Optional[Path], 
    log_callback: Optional[Callable[[str], None]] = None,
    provider: str = None
) -> Dict[str, Any]:
    """
    Processes a single file for snippet extraction.
    Extracts code blocks, writes them to output, and returns extraction results.
    
    Args:
        file_path: Path to the file to process
        output_path: Path to write the extracted snippets
        api_creds_path: Path to write API credentials found in the file
        log_path: Path to write logs
        log_callback: Optional callback for logging
        provider: AI provider to use for advanced features
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
        if log_callback:
            log_callback(f"[dim]Reading {len(content)} bytes from {file_path}[/dim]")
        time.sleep(0.5)
        if log_callback:
            log_callback(f"[dim]Analyzing content to extract code blocks from {file_path}...[/dim]")
        blocks = split_into_blocks(content)
        if log_callback:
            log_callback(f"[dim]Found {len(blocks)} potential code blocks in {file_path}[/dim]")
        if blocks:
            results["snippets_found"] = True
            language = CODE_EXTENSIONS.get(file_path.suffix.lower(), "txt")
            snippet_file = output_path / f"{file_path.stem}_snippets.md"
            snippet_file.parent.mkdir(parents=True, exist_ok=True)
            if log_callback:
                log_callback(f"[info]Writing {len(blocks)} snippets to {snippet_file}[/info]")
            with snippet_file.open('w', encoding='utf-8') as f:
                f.write(f"# Code Snippets from {file_path}\n\n")
                f.write(f"File: `{file_path}`  \n")
                f.write(f"Language: {language}  \n")
                f.write(f"Extracted: {current_timestamp()}  \n\n")
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
            time.sleep(0.5)
            if log_callback:
                log_callback(f"[success]Extracted {len(blocks)} snippets from {file_path} to {snippet_file}[/success]")
        else:
            if log_callback:
                log_callback(f"[warning]No snippets found in {file_path} after analysis[/warning]")
    except Exception as e:
        results["error"] = str(e)
        if log_callback:
            log_callback(f"[error]Error processing {file_path}: {str(e)}[/error]")
    return results

def write_organized_snippets(snippets: List[CodeSnippet], output_path: Path) -> None:
    """
    Writes snippets to organized files by category and generates an index.
    """
    output_path.mkdir(parents=True, exist_ok=True)
    with open(output_path / "index.md", "w", encoding="utf-8") as f:
        f.write("# Code Snippets\n\n")
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
                if snippet.related_snippets:
                    sf.write("## Related Snippets\n\n")
                    for related in snippet.related_snippets:
                        sf.write(f"- [{related}](./{related}.md)\n")
            f.write(f"## [{snippet.hash}](./{snippet.hash}.md)\n\n")
            f.write(f"Source: `{snippet.file_path}`\n\n")
            f.write(f"Tags: {', '.join(sorted(snippet.tags))}\n\n")
            f.write("```" + snippet.language.lower() + "\n")
            f.write(snippet.content[:200] + "...\n")
            f.write("```\n\n")

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
    Processes files in batches for snippet extraction.
    Returns a dictionary with processing statistics.
    
    Args:
        files: List of files to process
        output_path: Path to write the extracted snippets
        api_creds_path: Path to write API credentials found in the files
        log_path: Path to write logs
        batch_size: Number of files to process in each batch
        log_callback: Optional callback for logging
        provider: AI provider to use for advanced features
    """
    def log(msg: str) -> None:
        if log_callback:
            log_callback(msg)
        if log_path:
            log_message(msg, log_path)
    if not files:
        log("[yellow]No files to process for snippets.[/]")
        return {"total": 0, "with_snippets": 0, "with_creds": 0, "errors": 0}
    stats = {
        "total": len(files),
        "with_snippets": 0,
        "with_creds": 0,
        "errors": 0
    }
    batches = [files[i:i+batch_size] for i in range(0, len(files), batch_size)]
    log(f"[cyan]Processing {len(files)} files in {len(batches)} batches[/]")
    for batch_idx, batch in enumerate(batches, 1):
        log(f"[cyan]Processing batch {batch_idx}/{len(batches)} ({len(batch)} files)[/]")
        for file_idx, file_path in enumerate(batch, 1):
            log(f"[cyan]Processing file {file_idx}/{len(batch)} in batch {batch_idx}: {file_path.name}[/]")
            result = process_snippet_file(file_path, output_path, api_creds_path, log_path, log_callback, provider)
            if result["snippets_found"]:
                stats["with_snippets"] += 1
            if result["api_creds_found"]:
                stats["with_creds"] += 1
            if result["error"]:
                stats["errors"] += 1
    return stats

def is_code_file(file_path: Path) -> bool:
    """
    Determines if a file is a code file that should be processed for snippets.
    Returns True if the file is a code file, False otherwise.
    """
    if is_code_extension(file_path):
        return True
    try:
        with file_path.open('r', encoding='utf-8', errors='ignore') as f:
            first_line = f.readline().strip()
            if first_line.startswith('#!') and ('/bin/' in first_line or '/usr/bin/' in first_line):
                return True
    except Exception:
        pass
    return False

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
    Main entry point for extracting code snippets from a file or directory.
    Handles batch processing, directory traversal, and progress reporting.
    
    Args:
        file_or_dir: File or directory to process
        recursive: If True, process subdirectories recursively
        batch_size: Number of files to process in each batch
        exclude_ext: Set of extensions to exclude
        omni_paths: Dictionary of paths to use for output
        log_callback: Optional callback for logging
        provider: AI provider to use (ollama, xai, gemini)
    """
    if omni_paths is None:
        omni_paths = {}
    if exclude_ext is None:
        exclude_ext = {".git", ".env", ".venv", "__pycache__", ".pyc", ".pyo"}
    base_dir = omni_paths.get("base_dir", Path(".herd"))
    snippets_dir = omni_paths.get("snippets_dir", base_dir / "snippets")
    log_file = omni_paths.get("log", base_dir / "log.txt")
    snippets_dir.mkdir(parents=True, exist_ok=True)
    if log_callback:
        log_callback(f"[info]Starting snippet extraction (code files only)...[/info]")
        log_callback(f"[dim]Looking in {file_or_dir} {'recursively' if recursive else 'non-recursively'}[/dim]")
        if provider:
            log_callback(f"[cyan]Using provider: {provider}[/cyan]")
    files_to_process = []
    if file_or_dir.is_file():
        if is_code_file(file_or_dir):
            files_to_process.append(file_or_dir)
        elif log_callback:
            log_callback(f"[info]Skipping non-code file: {file_or_dir}[/info]")
    else:
        if recursive:
            for root, dirs, files in os.walk(file_or_dir):
                dirs[:] = [d for d in dirs if not d.startswith('.') and not d.startswith('__')]
                root_path = Path(root)
                for file in files:
                    if file.startswith('.'):
                        continue
                    file_path = root_path / file
                    if is_code_file(file_path):
                        files_to_process.append(file_path)
        else:
            for f in file_or_dir.iterdir():
                if f.is_file() and not f.name.startswith('.') and is_code_file(f):
                    files_to_process.append(f)
    if not files_to_process:
        if log_callback:
            log_callback(f"[warning]No code files found for snippet extraction. Make sure files have extensions defined in CODE_EXTENSIONS.[/warning]")
        console.print(Panel(
            f"[yellow]No code files found for snippet extraction[/yellow]\n\n"
            f"Supported code extensions: {', '.join(sorted(CODE_EXTENSIONS.keys()))}",
            title="[bold]Warning[/bold]",
            border_style="yellow",
            box=box.ROUNDED
        ))
        return
    extension_counts = {}
    for file in files_to_process:
        ext = file.suffix.lower() if file.suffix else "(no extension)"
        extension_counts[ext] = extension_counts.get(ext, 0) + 1
    if log_callback:
        log_callback(f"[info]Found {len(files_to_process)} code files to process:[/info]")
        for ext, count in extension_counts.items():
            log_callback(f"[dim]  - {ext}: {count} files[/dim]")
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
        for i in range(0, len(files_to_process), batch_size):
            batch = files_to_process[i:i + batch_size]
            for file_path in batch:
                try:
                    progress.update(total_task, description=f"[cyan]Processing[/cyan] → {file_path.name}")
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
                    if result.get("error"):
                        if log_callback:
                            log_callback(f"[error]Error processing {file_path}: {result['error']}[/error]")
                        stats["failed"] += 1
                    elif result.get("snippets_found"):
                        snippet_count = len(result.get('extracted_snippets', []))
                        stats["total_snippets"] += snippet_count
                        if log_callback:
                            log_callback(f"[success]Extracted {snippet_count} snippets from {file_path}[/success]")
                        stats["with_snippets"] += 1
                    else:
                        if log_callback:
                            log_callback(f"[info]No snippets found in {file_path}[/info]")
                except Exception as e:
                    if log_callback:
                        log_callback(f"[error]Failed to process {file_path}: {str(e)}[/error]")
                    stats["failed"] += 1
                progress.update(total_task, advance=1)
            time.sleep(0.05)
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
    
    Wrapper around process_snippets for backward compatibility.
    
    Args:
        directory: Directory to process
        recursive: Whether to process subdirectories
        batch_size: Number of files to process in one batch
        exclude_ext: Set of file extensions to exclude
        log_callback: Optional callback for logging
        provider: AI provider to use
        omni_paths: Optional dictionary of paths for the operation
        
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
        if isinstance(directory, str):
            directory = Path(directory)
        
        # Report start of processing
        if log_callback:
            log_callback(f"[bold cyan]Processing directory for snippets: {directory}[/bold cyan]")
            
        # Set default exclude extensions
        if exclude_ext is None:
            exclude_ext = {".git", ".env", ".venv", "__pycache__", ".pyc", ".pyo"}
            
        # Check if directory exists
        if not directory.exists():
            error_msg = f"Directory not found: {directory}"
            if log_callback:
                log_callback(f"[red]{error_msg}[/red]")
            result["error"] = error_msg
            return result
            
        # Set up paths
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
        
        if directory.is_file():
            if is_code_file(directory):
                files_to_process.append(directory)
                if log_callback:
                    log_callback(f"[cyan]Found 1 code file to process: {directory}[/cyan]")
            else:
                if log_callback:
                    log_callback(f"[yellow]File {directory} is not a recognized code file[/yellow]")
                result["success"] = True
                result["message"] = "No code files to process"
                result["output_dir"] = str(snippets_dir)
                return result
        else:
            if recursive:
                for root, dirs, files in os.walk(directory):
                    # Skip ignored directories
                    dirs[:] = [d for d in dirs if not d.startswith('.') and not d.startswith('__')]
                    root_path = Path(root)
                    
                    for file in files:
                        if file.startswith('.'):
                            continue
                        file_path = root_path / file
                        if is_code_file(file_path):
                            files_to_process.append(file_path)
            else:
                for f in directory.iterdir():
                    if f.is_file() and not f.name.startswith('.') and is_code_file(f):
                        files_to_process.append(f)
        
        # Log number of files found
        if log_callback:
            log_callback(f"[cyan]Found {len(files_to_process)} code files to process[/cyan]")
            
        # Process files in batches
        if not files_to_process:
            if log_callback:
                log_callback("[yellow]No code files found to process[/yellow]")
            result["success"] = True
            result["message"] = "No code files found for processing"
            result["output_dir"] = str(snippets_dir)
            return result
            
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
        
    except Exception as e:
        error_msg = f"Error processing directory for snippets: {str(e)}"
        if log_callback:
            log_callback(f"[red]{error_msg}[/red]")
        result["error"] = error_msg
        return result

# Functions for importing and exporting snippets
def search_snippets(
    query: str,
    snippets_dir: Path,
    limit: int = 10
) -> List[Dict[str, Any]]:
    """
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
    for snippet_file in snippet_files[:100]:  # Limit to prevent too much processing
        try:
            with open(snippet_file, "r", encoding="utf-8") as f:
                snippet_data = json.load(f)
                
                if (pattern.search(snippet_data.get("content", "")) or 
                    pattern.search(snippet_data.get("category", "")) or
                    any(pattern.search(tag) for tag in snippet_data.get("tags", []))):
                    results.append(snippet_data)
                    
                    if len(results) >= limit:
                        break
        except Exception as e:
            print(f"Error reading snippet file {snippet_file}: {e}")
    
    return results

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
    
    for snippet_file in snippet_files:
        try:
            with open(snippet_file, "r", encoding="utf-8") as f:
                snippet_data = json.load(f)
                snippets.append(snippet_data)
        except Exception as e:
            print(f"Error reading snippet file {snippet_file}: {e}")
    
    # Generate output based on format
    output = ""
    if output_format == "markdown":
        output = "# Code Snippets\n\n"
        for snippet in snippets:
            output += f"## {snippet.get('category', 'Uncategorized')}\n\n"
            output += f"**File:** {snippet.get('file_path')}\n\n"
            output += f"**Tags:** {', '.join(snippet.get('tags', []))}\n\n"
            output += "```" + snippet.get('language', '') + "\n"
            output += snippet.get('content', '') + "\n"
            output += "```\n\n"
    elif output_format == "json":
        output = json.dumps(snippets, indent=2)
    elif output_format == "html":
        output = "<!DOCTYPE html><html><head><title>Code Snippets</title></head><body>\n"
        for snippet in snippets:
            output += f"<h2>{snippet.get('category', 'Uncategorized')}</h2>\n"
            output += f"<p><strong>File:</strong> {snippet.get('file_path')}</p>\n"
            output += f"<p><strong>Tags:</strong> {', '.join(snippet.get('tags', []))}</p>\n"
            output += f"<pre><code class='{snippet.get('language', '')}'>\n"
            output += snippet.get('content', '') + "\n"
            output += "</code></pre>\n\n"
        output += "</body></html>"
    
    # Write to file if specified
    if output_file:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(output)
    
    return output

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
    
    # Create output directory if it doesn't exist
    output_path = snippets_dir / "code_snippets"
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Save snippet to file
    snippet_file = output_path / f"{snippet.hash}.snippet.json"
    with open(snippet_file, "w", encoding="utf-8") as f:
        json.dump(snippet.to_dict(), f, indent=2)
    
    return snippet.to_dict()

def list_snippet_formats() -> List[str]:
    """
    List available snippet export formats.
    
    Returns:
        List of available format names
    """
    return ["markdown", "json", "html"] 