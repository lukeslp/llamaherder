# Code Snippets from src/herd_ai/citations.py

File: `src/herd_ai/citations.py`  
Language: Python  
Extracted: 2025-06-07 05:09:24  

## Snippet 1
Lines 1-33

```Python
#!/usr/bin/env python3
"""
Citations Extractor Module

This module extracts citations from text files and documents, supporting multiple
citation styles (APA, MLA, Chicago, IEEE, Vancouver) and output formats (Markdown,
BibTeX, plain text, CSV). It can process individual files or entire directories
recursively, with deduplication and DOI enrichment capabilities.

Key Features:
- Multi-style citation extraction (APA, MLA, Chicago, IEEE, Vancouver)
- Multiple output formats (Markdown, BibTeX, plain text, CSV)
- DOI enrichment via CrossRef API
- Deduplication by raw string or DOI
- Recursive directory processing
- Comprehensive error handling and logging
- Accessibility-focused output formatting

Author: Luke Steuber
License: MIT
"""

import os
import json
import logging
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
import re
from datetime import datetime
import csv
import argparse
```

## Snippet 2
Lines 34-41

```Python
# Try to import bibtexparser, but provide fallback if not available
try:
    import bibtexparser
    from bibtexparser.bwriter import BibTexWriter
    from bibtexparser.bibdatabase import BibDatabase
    BIBTEX_AVAILABLE = True
except ImportError:
    BIBTEX_AVAILABLE = False
```

## Snippet 3
Lines 51-53

```Python
def write(self, db):
            # Simple BibTeX writer fallback
            output = []
```

## Snippet 4
Lines 54-56

```Python
for entry in db.entries:
                entry_type = entry.get('ENTRYTYPE', 'article')
                entry_id = entry.get('ID', 'unknown')
```

## Snippet 5
Lines 65-69

```Python
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
```

## Snippet 6
Lines 78-81

```Python
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

# =============================================================================
```

## Snippet 7
Lines 82-109

```Python
# Import configuration and utility functions, with fallbacks for various contexts
# =============================================================================
try:
    try:
        # First try standard package imports
        from herd_ai.utils.file import get_file_text, is_ignored_file
        from herd_ai.config import TEXT_EXTENSIONS, DOCUMENT_EXTENSIONS
    except ImportError:
        try:
            # Then try legacy package imports
            from llamacleaner.utils.file import get_file_text, is_ignored_file
            from llamacleaner.config import TEXT_EXTENSIONS, DOCUMENT_EXTENSIONS
        except ImportError:
            try:
                # Then try relative imports
                from utils.file import get_file_text, is_ignored_file
                from config import TEXT_EXTENSIONS, DOCUMENT_EXTENSIONS
            except ImportError:
                # Last resort - direct imports using file path
                sys.path.insert(0, str(Path(__file__).resolve().parent))
                from herd_ai.utils.file import get_file_text, is_ignored_file
                from herd_ai.config import TEXT_EXTENSIONS, DOCUMENT_EXTENSIONS
except Exception as e:
    print(f"Warning: Some dependencies not available in citations.py: {e}")
    print("Citations module will work with limited functionality.")
    # Fallback definitions
    TEXT_EXTENSIONS = {'.txt', '.md', '.rst', '.tex', '.json', '.yaml', '.yml', '.toml', '.xml', '.env', '.properties', '.conf', '.ini', '.sql', '.graphql', '.sh', '.bash', '.zsh', '.ps1', '.bat', '.cmd'}
    DOCUMENT_EXTENSIONS = {'.pdf', '.docx', '.doc', '.pptx', '.ppt', '.xlsx', '.xls', '.odt', '.ods', '.odp'}
```

## Snippet 8
Lines 110-114

```Python
def get_file_text(path):
        try:
            return Path(path).read_text(encoding='utf-8', errors='ignore')
        except:
            return ""
```

## Snippet 9
Lines 118-135

```Python
console = Console()
logger = logging.getLogger(__name__)

CITATION_FORMATS = {
    'txt': 'Plain Text',
    'md': 'Markdown',
    'bib': 'BibTeX',
    'csv': 'CSV',
    'apa': 'APA',
    'mla': 'MLA',
    'chicago': 'Chicago',
    'ieee': 'IEEE',
    'vancouver': 'Vancouver'
}
SUPPORTED_EXTENSIONS = TEXT_EXTENSIONS.union(DOCUMENT_EXTENSIONS)
SUPPORTED_STYLES = ['apa', 'mla', 'chicago', 'ieee', 'vancouver']

# =============================================================================
```

## Snippet 10
Lines 140-146

```Python
Extract citations from text content for the requested styles.
    Args:
        text: The text content to analyze
        styles: List of citation styles to extract (default: ['apa'])
    Returns:
        List of dictionaries containing citation information
    """
```

## Snippet 11
Lines 147-151

```Python
if styles is None:
        styles = ['apa']

    citations = []
    # APA
```

## Snippet 12
Lines 156-158

```Python
if len(parts) >= 2:
                authors = parts[0].strip()
                year_match = re.search(r'(\d{4})', parts[1])
```

## Snippet 13
Lines 159-166

```Python
year = year_match.group(1) if year_match else ""
                citations.append({
                    "type": "in-text",
                    "style": "apa",
                    "authors": authors,
                    "year": year,
                    "raw": citation
                })
```

## Snippet 14
Lines 170-175

```Python
for citation in mla_in_text:
            citations.append({
                "type": "in-text",
                "style": "mla",
                "raw": citation
            })
```

## Snippet 15
Lines 179-184

```Python
for citation in chicago_in_text:
            citations.append({
                "type": "in-text",
                "style": "chicago",
                "raw": citation
            })
```

## Snippet 16
Lines 188-193

```Python
for citation in ieee_in_text:
            citations.append({
                "type": "in-text",
                "style": "ieee",
                "raw": citation
            })
```

## Snippet 17
Lines 198-208

```Python
if len(entry) >= 4:
                authors, year, title, source = entry[0], entry[1], entry[2], entry[3]
                citations.append({
                    "type": "reference",
                    "style": "apa",
                    "authors": authors,
                    "year": year,
                    "title": title,
                    "source": source,
                    "raw": " ".join(entry)
                })
```

## Snippet 18
Lines 212-220

```Python
for doi in dois:
        citations.append({
            "type": "doi",
            "style": "doi",
            "doi": doi,
            "raw": doi
        })
    return citations
```

## Snippet 19
Lines 224-228

```Python
def extract_citations_from_doi(doi: str, log_callback: Optional[Any] = None, provider: str = None) -> Optional[Dict[str, str]]:
    """
    Extract citation information from a DOI using CrossRef.
    Args:
        doi: Digital Object Identifier
```

## Snippet 20
Lines 233-236

```Python
"""
    try:
        import requests
        url = f"https://api.crossref.org/works/{doi}"
```

## Snippet 21
Lines 242-245

```Python
if response.status_code == 200:
            data = response.json()
            message = data.get("message", {})
            title = message.get("title", [])
```

## Snippet 22
Lines 256-261

```Python
container = container[0] if container and isinstance(container, list) else ""
            volume = message.get("volume", "")
            issue = message.get("issue", "")
            page = message.get("page", "")
            url_val = message.get("URL", "")
            author_string = ", ".join(authors)
```

## Snippet 23
Lines 262-274

```Python
if author_string:
                author_string += "."
            citation = {
                "type": "doi",
                "authors": author_string,
                "year": year,
                "title": title,
                "source": container,
                "volume": volume,
                "issue": issue,
                "pages": page,
                "doi": doi,
                "url": url_val,
```

## Snippet 24
Lines 283-285

```Python
except Exception as e:
        msg = f"[red]Error extracting citation from DOI {doi}: {e}[/red]"
        logger.error(msg)
```

## Snippet 25
Lines 293-298

```Python
def dedupe_citations(citations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Deduplicate citations by their 'raw' field or DOI.
    """
    seen = set()
    deduped = []
```

## Snippet 26
Lines 301-303

```Python
if key and key not in seen:
            deduped.append(c)
            seen.add(key)
```

## Snippet 27
Lines 309-317

```Python
def save_citations_json(citations: List[Dict[str, Any]], directory: Path) -> Path:
    meta_dir = directory / ".herd/citations"
    meta_dir.mkdir(exist_ok=True, parents=True)
    citations_file = meta_dir / "citations.json"
    with open(citations_file, 'w', encoding='utf-8') as f:
        json.dump(citations, f, indent=2, ensure_ascii=False)
    return citations_file

# =============================================================================
```

## Snippet 28
Lines 320-326

```Python
def generate_output(citations: List[Dict[str, Any]], directory: Path, formats: List[str], style: str) -> Dict[str, Path]:
    """
    Generate output files in requested formats and citation style.
    """
    outputs = {}
    meta_dir = directory / ".herd/citations"
    meta_dir.mkdir(exist_ok=True, parents=True)
```

## Snippet 29
Lines 330-335

```Python
if 'md' in formats:
        md_path = meta_dir / f"CITATIONS.{style}.md"
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(generate_markdown_citation_list(filtered, directory, style))
        outputs['md'] = md_path
    # BibTeX
```

## Snippet 30
Lines 336-341

```Python
if 'bib' in formats:
        bib_path = meta_dir / f"CITATIONS.{style}.bib"
        with open(bib_path, 'w', encoding='utf-8') as f:
            f.write(generate_bibtex_citations(filtered))
        outputs['bib'] = bib_path
    # Plain text
```

## Snippet 31
Lines 342-347

```Python
if 'txt' in formats:
        txt_path = meta_dir / f"CITATIONS.{style}.txt"
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(generate_plain_text_citations(filtered))
        outputs['txt'] = txt_path
    # CSV
```

## Snippet 32
Lines 348-353

```Python
if 'csv' in formats:
        csv_path = meta_dir / f"CITATIONS.{style}.csv"
        with open(csv_path, 'w', encoding='utf-8') as f:
            f.write(generate_csv_citations(filtered))
        outputs['csv'] = csv_path
    # MLA, Chicago, IEEE, Vancouver (as .txt)
```

## Snippet 33
Lines 354-358

```Python
if 'mla' in formats and style == 'mla':
        mla_path = meta_dir / f"CITATIONS.mla.txt"
        with open(mla_path, 'w', encoding='utf-8') as f:
            f.write(generate_mla_citations(filtered))
        outputs['mla'] = mla_path
```

## Snippet 34
Lines 359-363

```Python
if 'chicago' in formats and style == 'chicago':
        chicago_path = meta_dir / f"CITATIONS.chicago.txt"
        with open(chicago_path, 'w', encoding='utf-8') as f:
            f.write(generate_chicago_citations(filtered))
        outputs['chicago'] = chicago_path
```

## Snippet 35
Lines 364-368

```Python
if 'ieee' in formats and style == 'ieee':
        ieee_path = meta_dir / f"CITATIONS.ieee.txt"
        with open(ieee_path, 'w', encoding='utf-8') as f:
            f.write(generate_ieee_citations(filtered))
        outputs['ieee'] = ieee_path
```

## Snippet 36
Lines 381-384

```Python
if not citations:
        markdown += "No citations found.\n"
        return markdown
    markdown += "## References\n\n"
```

## Snippet 37
Lines 385-394

```Python
for ref in citations:
        authors = ref.get("authors", "")
        year = ref.get("year", "")
        title = ref.get("title", "")
        source = ref.get("source", "")
        volume = ref.get("volume", "")
        issue = ref.get("issue", "")
        pages = ref.get("pages", "")
        doi = ref.get("doi", "")
        url = ref.get("url", "")
```

## Snippet 38
Lines 402-404

```Python
if pages:
                citation += f", {pages}"
            citation += "."
```

## Snippet 39
Lines 405-407

```Python
if doi:
            doi_url = f"https://doi.org/{doi}"
            citation += f" [{doi}]({doi_url})"
```

## Snippet 40
Lines 408-410

```Python
elif url:
            citation += f" [Link]({url})"
        markdown += f"- {citation}\n\n"
```

## Snippet 41
Lines 453-466

```Python
author_key = ref.get('authors', '').split(',')[0].strip() if ref.get('authors') else "Unknown"
        year_key = ref.get('year', '')
        entry = {
            'ENTRYTYPE': 'article',
            'ID': f"{author_key}_{year_key}",
            'title': ref.get("title", ""),
            'author': ref.get("authors", ""),
            'year': ref.get("year", ""),
            'journal': ref.get("source", ""),
            'volume': ref.get("volume", ""),
            'number': ref.get("issue", ""),
            'pages': ref.get("pages", ""),
            'doi': ref.get("doi", "")
        }
```

## Snippet 42
Lines 469-472

```Python
writer = BibTexWriter()
    writer.indent = '    '
    return writer.write(db)
```

## Snippet 43
Lines 475-483

```Python
for ref in citations:
        authors = ref.get("authors", "")
        year = ref.get("year", "")
        title = ref.get("title", "")
        source = ref.get("source", "")
        volume = ref.get("volume", "")
        issue = ref.get("issue", "")
        pages = ref.get("pages", "")
        doi = ref.get("doi", "")
```

## Snippet 44
Lines 491-494

```Python
if doi:
            citation += f". https://doi.org/{doi}"
        citation += "."
        formatted_citations.append(citation)
```

## Snippet 45
Lines 497-503

```Python
def generate_csv_citations(citations: List[Dict[str, Any]]) -> str:
    import io
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=[
        'authors', 'year', 'title', 'source', 'volume', 'issue', 'pages', 'doi', 'url'
    ])
    writer.writeheader()
```

## Snippet 46
Lines 504-517

```Python
for ref in citations:
        writer.writerow({
            'authors': ref.get("authors", ""),
            'year': ref.get("year", ""),
            'title': ref.get("title", ""),
            'source': ref.get("source", ""),
            'volume': ref.get("volume", ""),
            'issue': ref.get("issue", ""),
            'pages': ref.get("pages", ""),
            'doi': ref.get("doi", ""),
            'url': ref.get("url", "")
        })
    return output.getvalue()
```

## Snippet 47
Lines 520-527

```Python
for ref in citations:
        authors = ref.get("authors", "")
        title = ref.get("title", "")
        source = ref.get("source", "")
        volume = ref.get("volume", "")
        issue = ref.get("issue", "")
        pages = ref.get("pages", "")
        year = ref.get("year", "")
```

## Snippet 48
Lines 533-536

```Python
if pages:
            citation += f", pp. {pages}"
        citation += f", {year}."
        formatted_citations.append(citation)
```

## Snippet 49
Lines 541-549

```Python
for ref in citations:
        authors = ref.get("authors", "")
        title = ref.get("title", "")
        source = ref.get("source", "")
        volume = ref.get("volume", "")
        issue = ref.get("issue", "")
        pages = ref.get("pages", "")
        year = ref.get("year", "")
        doi = ref.get("doi", "")
```

## Snippet 50
Lines 555-558

```Python
if pages:
            citation += f" ({year}): {pages}."
        else:
            citation += f" ({year})."
```

## Snippet 51
Lines 559-561

```Python
if doi:
            citation += f" https://doi.org/{doi}"
        formatted_citations.append(citation)
```

## Snippet 52
Lines 566-575

```Python
for i, ref in enumerate(citations, 1):
        authors = ref.get("authors", "")
        title = ref.get("title", "")
        source = ref.get("source", "")
        volume = ref.get("volume", "")
        issue = ref.get("issue", "")
        pages = ref.get("pages", "")
        year = ref.get("year", "")
        doi = ref.get("doi", "")
        citation = f"[{i}] {authors}, \"{title},\" {source}"
```

## Snippet 53
Lines 580-582

```Python
if pages:
            citation += f", pp. {pages}"
        citation += f", {year}."
```

## Snippet 54
Lines 583-585

```Python
if doi:
            citation += f" doi: {doi}"
        formatted_citations.append(citation)
```

## Snippet 55
Lines 593-599

```Python
Process a directory for citations, dedupe, enrich DOIs, and output in requested formats/styles.

    Args:
        directory: Directory to process
        recursive: Whether to process subdirectories recursively
        styles: Citation styles to extract (default: ['apa'])
        outputs: Output file formats (default: ['md'])
```

## Snippet 56
Lines 603-607

```Python
Returns:
        Dictionary with paths to generated output files
    """
    try:
        # Ensure directory is a Path object
```

## Snippet 57
Lines 623-627

```Python
if not directory.exists():
            log_callback(f"[red]Directory not found: {directory}[/red]")
            return {"error": f"Directory not found: {directory}", "success": False}

        # Find relevant files
```

## Snippet 58
Lines 634-637

```Python
if not files:
            log_callback(f"[yellow]No supported files found in {directory}[/yellow]")
            return {"files_processed": 0, "citations_found": 0, "success": True}
```

## Snippet 59
Lines 642-644

```Python
for file in files:
            try:
                text = get_file_text(file)
```

## Snippet 60
Lines 677-679

```Python
for style in styles:
            style_outputs = generate_output(deduped, directory, outputs, style)
            output_files[style] = style_outputs
```

## Snippet 61
Lines 683-693

```Python
# Create summary of results
        result = {
            "files_processed": processed_files,
            "citations_found": len(all_citations),
            "unique_citations": len(deduped),
            "outputs": output_files,
            "json_path": str(json_path),
            "success": True
        }

        # Final success message
```

## Snippet 62
Lines 695-698

```Python
log_callback(f"[green]Outputs: {', '.join([f'{s}:{list(o.keys())}' for s, o in output_files.items()])}\n[/green]")

        return result
```

## Snippet 63
Lines 699-701

```Python
except Exception as e:
        # Catch any exceptions and return error info
        error_msg = f"Error processing citations: {str(e)}"
```

## Snippet 64
Lines 702-705

```Python
if log_callback:
            log_callback(f"[red]{error_msg}[/red]")
        return {"error": error_msg, "success": False}
```

## Snippet 65
Lines 711-717

```Python
Process a file or directory for citations.

    Args:
        path: File or directory path to process
        recursive: Whether to process subdirectories recursively
        styles: Citation styles to extract (default: ['apa'])
        outputs: Output file formats (default: ['md'])
```

## Snippet 66
Lines 721-725

```Python
Returns:
        Dictionary with paths to generated output files
    """
    path = Path(path)
```

## Snippet 67
Lines 727-730

```Python
if log_callback:
            log_callback(f"[red]Path not found: {path}[/red]")
        return {}
```

## Snippet 68
Lines 731-739

```Python
if path.is_file():
        # For a single file, create a temporary directory with just this file
        import tempfile
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir) / path.name
            try:
                with open(path, 'rb') as src, open(temp_path, 'wb') as dst:
                    dst.write(src.read())
                result = process_directory(Path(temp_dir), False, styles, outputs, log_callback, provider)
```

## Snippet 69
Lines 740-742

```Python
if log_callback:
                    log_callback(f"[green]Processed file: {path.name}[/green]")
                return result
```

## Snippet 70
Lines 744-746

```Python
if log_callback:
                    log_callback(f"[red]Error processing file {path}: {e}[/red]")
                return {}
```

## Snippet 71
Lines 747-750

```Python
else:
        # For a directory, process it normally
        return process_directory(path, recursive, styles, outputs, log_callback, provider)
```

## Snippet 72
Lines 754-762

```Python
def main():
    parser = argparse.ArgumentParser(description="Citation extraction and management tool.")
    parser.add_argument("directory", type=str, help="Directory to process")
    parser.add_argument("--recursive", action="store_true", help="Process subdirectories recursively")
    parser.add_argument("--styles", nargs="*", default=["apa"], choices=SUPPORTED_STYLES, help="Citation styles to extract (default: apa)")
    parser.add_argument("--outputs", nargs="*", default=["md"], choices=list(CITATION_FORMATS.keys()), help="Output file formats (default: md)")
    args = parser.parse_args()
    process_directory(Path(args.directory), args.recursive, args.styles, args.outputs)
```

## Snippet 73
Lines 763-770

```Python
if __name__ == "__main__":
    main()

# =============================================================================
# Accessibility and Documentation Notes
# =============================================================================
# - All output files are UTF-8 encoded and screen-reader friendly.
# - Markdown and plain text outputs use semantic formatting.
```

