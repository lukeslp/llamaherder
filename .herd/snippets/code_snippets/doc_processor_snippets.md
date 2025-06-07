# Code Snippets from toollama/moe/tools/document/content/doc_processor.py

File: `toollama/moe/tools/document/content/doc_processor.py`  
Language: Python  
Extracted: 2025-06-07 05:13:03  

## Snippet 1
Lines 1-23

```Python
"""
Document management tools with enhanced accessibility and formatting
"""

import json
import os
import shutil
import logging
import hashlib
import datetime
import zipfile
import tarfile
from pathlib import Path
from typing import Dict, Any, Optional, Union, List, Callable
from pydantic import BaseModel, Field
import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import requests
from bs4 import BeautifulSoup
import markdown
import html2text
```

## Snippet 2
Lines 39-48

```Python
if self.event_emitter:
            await self.event_emitter({
                "type": "status",
                "data": {
                    "status": status,
                    "description": description,
                    "done": done,
                }
            })
```

## Snippet 3
Lines 52-71

```Python
class Valves(BaseModel):
        PAPERLESS_URL: str = Field(
            default="http://localhost:8000",
            description="Paperless-ngx server URL"
        )
        PAPERLESS_TOKEN: str = Field(
            default="",
            description="Paperless-ngx API token"
        )
        OCR_LANGUAGES: List[str] = Field(
            default=["eng"],
            description="Default OCR languages"
        )
        FILE_PATTERNS: Dict[str, List[str]] = Field(
            default={
                "documents": [".pdf", ".doc", ".docx", ".txt", ".rtf"],
                "images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff"],
                "archives": [".zip", ".tar", ".gz", ".7z", ".rar"],
                "code": [".py", ".js", ".html", ".css", ".json", ".xml"]
            },
```

## Snippet 4
Lines 75-78

```Python
def __init__(self):
        """Initialize document management tools"""
        self.valves = self.Valves()
```

## Snippet 5
Lines 88-92

```Python
async def process_ocr(self, file_path: str, options: dict = {}, __event_emitter__: Callable[[dict], Any] = None) -> Dict[str, Any]:
        """Extract text from images and PDFs using OCR"""
        emitter = EventEmitter(__event_emitter__)

        try:
```

## Snippet 6
Lines 96-107

```Python
if not os.path.exists(file_path):
                raise ValueError(f"File not found: {file_path}")

            # Process options
            language = options.get("language", self.valves.OCR_LANGUAGES[0])
            format_type = options.get("format", "text")
            include_metadata = options.get("include_metadata", False)

            extracted_text = ""
            metadata = {}

            # Handle PDFs
```

## Snippet 7
Lines 108-116

```Python
if file_path.lower().endswith(".pdf"):
                pdf_document = fitz.open(file_path)
                metadata = {
                    "pages": len(pdf_document),
                    "title": pdf_document.metadata.get("title", ""),
                    "author": pdf_document.metadata.get("author", ""),
                    "creation_date": str(pdf_document.metadata.get("creationDate", ""))
                }
```

## Snippet 8
Lines 117-128

```Python
for page_num in range(len(pdf_document)):
                    await emitter.progress_update(f"Processing page {page_num + 1}/{len(pdf_document)}")

                    page = pdf_document[page_num]
                    pix = page.get_pixmap()
                    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

                    text = pytesseract.image_to_string(img, lang=language)
                    extracted_text += f"\n\nPage {page_num + 1}:\n{text}"

                pdf_document.close()
```

## Snippet 9
Lines 129-140

```Python
# Handle images
            else:
                img = Image.open(file_path)
                metadata = {
                    "format": img.format,
                    "size": img.size,
                    "mode": img.mode
                }

                extracted_text = pytesseract.image_to_string(img, lang=language)

            # Format output
```

## Snippet 10
Lines 141-146

```Python
if format_type == "json":
                result = {
                    "text": extracted_text.strip(),
                    "language": language,
                    "file": file_path
                }
```

## Snippet 11
Lines 158-172

```Python
else:  # text
                result = extracted_text.strip()

            await emitter.success_update(f"Successfully processed {file_path}")

            return {
                "status": "success",
                "data": {
                    "result": result,
                    "format": format_type,
                    "language": language,
                    "pages": metadata.get("pages", 1)
                }
            }
```

## Snippet 12
Lines 173-180

```Python
except Exception as e:
            error_message = f"Error processing OCR: {str(e)}"
            await emitter.error_update(error_message)
            return {
                "status": "error",
                "message": error_message
            }
```

## Snippet 13
Lines 181-192

```Python
async def get_paperless_documents(self, documentTypeName: Optional[str] = None,
                                    documentTagName: Optional[str] = None,
                                    correspondent: Optional[str] = None,
                                    created_year: Optional[int] = None,
                                    created_month: Optional[int] = None,
                                    __event_emitter__: Callable[[dict], Any] = None) -> Dict[str, Any]:
        """Search and retrieve documents from Paperless"""
        emitter = EventEmitter(__event_emitter__)

        try:
            await emitter.progress_update("Searching Paperless documents")
```

## Snippet 14
Lines 193-203

```Python
if not self.valves.PAPERLESS_TOKEN:
                raise ValueError("Paperless API token not configured")

            # Prepare API request
            headers = {
                "Authorization": f"Token {self.valves.PAPERLESS_TOKEN}",
                "Content-Type": "application/json"
            }

            # Build query parameters
            params = {}
```

## Snippet 15
Lines 212-227

```Python
if created_month:
                params["created__month"] = created_month

            # Make API request
            response = requests.get(
                f"{self.valves.PAPERLESS_URL}/api/documents/",
                headers=headers,
                params=params,
                timeout=30
            )
            response.raise_for_status()

            # Process results
            results = response.json()
            documents = []
```

## Snippet 16
Lines 228-240

```Python
for doc in results.get("results", []):
                document = {
                    "id": doc.get("id"),
                    "title": doc.get("title"),
                    "created_date": doc.get("created"),
                    "modified_date": doc.get("modified"),
                    "correspondent": doc.get("correspondent_name"),
                    "document_type": doc.get("document_type_name"),
                    "tags": doc.get("tags", []),
                    "content": doc.get("content", "")
                }
                documents.append(document)
```

## Snippet 17
Lines 241-257

```Python
await emitter.success_update(f"Found {len(documents)} documents")

            return {
                "status": "success",
                "data": {
                    "documents": documents,
                    "count": len(documents),
                    "query": {
                        "type": documentTypeName,
                        "tag": documentTagName,
                        "correspondent": correspondent,
                        "year": created_year,
                        "month": created_month
                    }
                }
            }
```

## Snippet 18
Lines 258-265

```Python
except Exception as e:
            error_message = f"Error searching Paperless: {str(e)}"
            await emitter.error_update(error_message)
            return {
                "status": "error",
                "message": error_message
            }
```

## Snippet 19
Lines 266-273

```Python
async def manage_files(self, operation: str, params: dict, __event_emitter__: Callable[[dict], Any] = None) -> Dict[str, Any]:
        """Perform file management operations"""
        emitter = EventEmitter(__event_emitter__)

        try:
            await emitter.progress_update(f"Starting file operation: {operation}")

            source = params.get("source", "")
```

## Snippet 20
Lines 284-288

```Python
elif operation == "delete":
                return await self._delete_files(source, params, emitter)
            else:
                raise ValueError(f"Unknown operation: {operation}")
```

## Snippet 21
Lines 289-296

```Python
except Exception as e:
            error_message = f"Error in file operation: {str(e)}"
            await emitter.error_update(error_message)
            return {
                "status": "error",
                "message": error_message
            }
```

## Snippet 22
Lines 297-305

```Python
async def _organize_files(self, source: str, params: dict, emitter: EventEmitter) -> Dict[str, Any]:
        """Organize files by type"""
        recursive = params.get("recursive", False)
        create_dirs = params.get("create_dirs", True)

        organized = defaultdict(list)
        skipped = []

        # Walk through source directory
```

## Snippet 23
Lines 310-315

```Python
for filename in files:
                filepath = os.path.join(root, filename)
                file_ext = os.path.splitext(filename)[1].lower()

                # Determine file type
                file_type = None
```

## Snippet 24
Lines 317-320

```Python
if file_ext in extensions:
                        file_type = type_name
                        break
```

## Snippet 25
Lines 321-325

```Python
if not file_type:
                    file_type = "other"

                # Create type directory
                type_dir = os.path.join(source, file_type)
```

## Snippet 26
Lines 326-331

```Python
if create_dirs and not os.path.exists(type_dir):
                    os.makedirs(type_dir)

                # Move file
                try:
                    dest_path = os.path.join(type_dir, filename)
```

## Snippet 27
Lines 332-337

```Python
if os.path.exists(dest_path):
                        base, ext = os.path.splitext(filename)
                        dest_path = os.path.join(type_dir, f"{base}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}{ext}")

                    shutil.move(filepath, dest_path)
                    organized[file_type].append(filename)
```

## Snippet 28
Lines 341-347

```Python
await emitter.success_update("File organization complete")

        return {
            "status": "success",
            "data": {
                "organized": dict(organized),
                "skipped": skipped,
```

## Snippet 29
Lines 353-355

```Python
async def _transfer_files(self, operation: str, source: str, params: dict, emitter: EventEmitter) -> Dict[str, Any]:
        """Move or copy files"""
        destination = params.get("destination", "")
```

## Snippet 30
Lines 356-362

```Python
if not destination:
            raise ValueError("Destination path required")

        pattern = params.get("pattern", "*")
        recursive = params.get("recursive", False)
        create_dirs = params.get("create_dirs", True)
```

## Snippet 31
Lines 363-369

```Python
if create_dirs:
            os.makedirs(destination, exist_ok=True)

        transferred = []
        skipped = []

        # Process files
```

## Snippet 32
Lines 375-381

```Python
if not Path(filename).match(pattern):
                    continue

                src_path = os.path.join(root, filename)
                dst_path = os.path.join(destination, filename)

                try:
```

## Snippet 33
Lines 382-386

```Python
if operation == "move":
                        shutil.move(src_path, dst_path)
                    else:  # copy
                        shutil.copy2(src_path, dst_path)
                    transferred.append(filename)
```

## Snippet 34
Lines 390-402

```Python
await emitter.success_update(f"File {operation} complete")

        return {
            "status": "success",
            "data": {
                "operation": operation,
                "transferred": transferred,
                "skipped": skipped,
                "total_transferred": len(transferred),
                "total_skipped": len(skipped)
            }
        }
```

## Snippet 35
Lines 403-405

```Python
async def _archive_files(self, source: str, params: dict, emitter: EventEmitter) -> Dict[str, Any]:
        """Archive files"""
        archive_name = params.get("destination", f"archive_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}")
```

## Snippet 36
Lines 406-415

```Python
if not archive_name.endswith((".zip", ".tar.gz")):
            archive_name += ".zip"

        pattern = params.get("pattern", "*")
        recursive = params.get("recursive", False)

        archived = []
        skipped = []

        # Create archive
```

## Snippet 37
Lines 423-432

```Python
if not Path(filename).match(pattern):
                            continue

                        filepath = os.path.join(root, filename)
                        try:
                            archive.write(filepath, os.path.relpath(filepath, source))
                            archived.append(filename)
                        except Exception as e:
                            skipped.append({"file": filename, "error": str(e)})
```

## Snippet 38
Lines 440-449

```Python
if not Path(filename).match(pattern):
                            continue

                        filepath = os.path.join(root, filename)
                        try:
                            archive.add(filepath, arcname=os.path.relpath(filepath, source))
                            archived.append(filename)
                        except Exception as e:
                            skipped.append({"file": filename, "error": str(e)})
```

## Snippet 39
Lines 450-462

```Python
await emitter.success_update("Archive creation complete")

        return {
            "status": "success",
            "data": {
                "archive": archive_name,
                "archived": archived,
                "skipped": skipped,
                "total_archived": len(archived),
                "total_skipped": len(skipped)
            }
        }
```

## Snippet 40
Lines 463-471

```Python
async def _delete_files(self, source: str, params: dict, emitter: EventEmitter) -> Dict[str, Any]:
        """Delete files"""
        pattern = params.get("pattern", "*")
        recursive = params.get("recursive", False)

        deleted = []
        skipped = []

        # Process files
```

## Snippet 41
Lines 477-486

```Python
if not Path(filename).match(pattern):
                    continue

                filepath = os.path.join(root, filename)
                try:
                    os.remove(filepath)
                    deleted.append(filename)
                except Exception as e:
                    skipped.append({"file": filename, "error": str(e)})
```

## Snippet 42
Lines 487-497

```Python
await emitter.success_update("File deletion complete")

        return {
            "status": "success",
            "data": {
                "deleted": deleted,
                "skipped": skipped,
                "total_deleted": len(deleted),
                "total_skipped": len(skipped)
            }
        }
```

