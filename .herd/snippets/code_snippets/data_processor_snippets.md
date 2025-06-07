# Code Snippets from toollama/API/api-tools/tools/data/processing/data_processor.py

File: `toollama/API/api-tools/tools/data/processing/data_processor.py`  
Language: Python  
Extracted: 2025-06-07 05:24:54  

## Snippet 1
Lines 1-20

```Python
"""
Data Processing tools combining JSON conversion, OCR, and audio transcription
Enhanced with accessibility features and improved formatting
"""

import json
import yaml
import toml
import xml.dom.minidom
import csv
import io
import pytesseract
from PIL import Image
import fitz  # PyMuPDF
import whisper
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, Union, List
import os
import tempfile
```

## Snippet 2
Lines 21-24

```Python
def _convert_to_json(data: Any, indent: Optional[int] = None) -> str:
    """Convert data to JSON format"""
    return json.dumps(data, indent=indent)
```

## Snippet 3
Lines 25-28

```Python
def _convert_to_yaml(data: Any) -> str:
    """Convert data to YAML format"""
    return yaml.dump(data, sort_keys=False, allow_unicode=True)
```

## Snippet 4
Lines 29-32

```Python
def _convert_to_toml(data: Any) -> str:
    """Convert data to TOML format"""
    return toml.dumps(data)
```

## Snippet 5
Lines 35-39

```Python
def dict_to_xml(data: Dict, root_name: str = "root") -> str:
        doc = xml.dom.minidom.Document()
        root = doc.createElement(root_name)
        doc.appendChild(root)
```

## Snippet 6
Lines 52-54

```Python
else:
                        child.appendChild(doc.createTextNode(str(item)))
                    parent.appendChild(child)
```

## Snippet 7
Lines 55-59

```Python
else:
                child = doc.createElement(key)
                child.appendChild(doc.createTextNode(str(value)))
                parent.appendChild(child)
```

## Snippet 8
Lines 60-64

```Python
for key, value in data.items():
            add_element(root, key, value)

        return doc.toprettyxml(indent="  ")
```

## Snippet 9
Lines 67-71

```Python
def _convert_to_csv(data: Any) -> str:
    """Convert data to CSV format"""
    output = io.StringIO()
    writer = None
```

## Snippet 10
Lines 73-79

```Python
if data and isinstance(data[0], dict):
            writer = csv.DictWriter(output, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
        else:
            writer = csv.writer(output)
            writer.writerows(data)
```

## Snippet 11
Lines 86-93

```Python
def _extract_text_from_image(image_path: str, language: str = "eng") -> str:
    """Extract text from image using OCR"""
    try:
        image = Image.open(image_path)
        return pytesseract.image_to_string(image, lang=language)
    except Exception as e:
        raise Exception(f"Error processing image: {str(e)}")
```

## Snippet 12
Lines 95-99

```Python
"""Extract text from PDF using OCR if needed"""
    try:
        doc = fitz.open(pdf_path)
        pages = []
```

## Snippet 13
Lines 105-111

```Python
if not text.strip():
                pix = page.get_pixmap()
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                text = pytesseract.image_to_string(img, lang=language)

            pages.append(text.strip())
```

## Snippet 14
Lines 116-130

```Python
def _transcribe_audio(
    audio_path: str,
    model_name: str = "base",
    language: Optional[str] = None,
    task: str = "transcribe",
    temperature: float = 0.0,
    format: str = "text"
) -> Union[str, Dict[str, Any]]:
    """Transcribe audio using Whisper"""
    try:
        # Load model
        model = whisper.load_model(model_name)

        # Set up options
        options = {}
```

## Snippet 15
Lines 131-142

```Python
if language:
            options["language"] = language

        # Transcribe
        result = model.transcribe(
            audio_path,
            task=task,
            temperature=temperature,
            **options
        )

        # Format output
```

## Snippet 16
Lines 145-150

```Python
elif format == "json":
            return {
                "text": result["text"],
                "segments": result["segments"],
                "language": result["language"]
            }
```

## Snippet 17
Lines 151-156

```Python
elif format in ["srt", "vtt"]:
            writer = whisper.utils.get_writer(format, ".")
            return writer(result, audio_path)
        else:
            raise ValueError(f"Unsupported format: {format}")
```

## Snippet 18
Lines 163-177

```Python
class Valves(BaseModel):
        TESSERACT_PATH: str = Field(
            default="",
            description="Path to Tesseract executable"
        )
        OCR_LANGUAGES: List[str] = Field(
            default=["eng"],
            description="List of installed OCR languages"
        )
        WHISPER_MODEL: str = Field(
            default="base",
            description="Default Whisper model to use"
        )
        JSON_INDENT: int = Field(
            default=2,
```

## Snippet 19
Lines 186-200

```Python
def convert_json(
        self,
        data: Union[str, Dict, List],
        target_format: str = "json",
        style: str = "pretty"
    ) -> Dict[str, Any]:
        """
        Convert data between JSON and other formats.

        :param data: Input data (string or Python object)
        :param target_format: Target format (json, yaml, toml, xml, csv)
        :param style: Output style (pretty, compact, single_line)
        :return: Dictionary with conversion results
        """
        try:
```

## Snippet 20
Lines 215-220

```Python
elif target_format == "csv":
                result = _convert_to_csv(data)
            else:
                raise ValueError(f"Unsupported format: {target_format}")

            # Apply style
```

## Snippet 21
Lines 221-231

```Python
if style == "single_line":
                result = result.replace("\n", " ").strip()

            return {
                "status": "success",
                "data": {
                    "converted": result,
                    "format": target_format,
                    "style": style
                }
            }
```

## Snippet 22
Lines 232-237

```Python
except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }
```

## Snippet 23
Lines 238-255

```Python
def process_ocr(
        self,
        file_path: str,
        language: str = "eng",
        format: str = "text"
    ) -> Dict[str, Any]:
        """
        Process image or PDF file with OCR.

        :param file_path: Path to image or PDF file
        :param language: OCR language
        :param format: Output format (text, json, markdown)
        :return: Dictionary with OCR results
        """
        try:
            # Check file type
            ext = os.path.splitext(file_path)[1].lower()
```

## Snippet 24
Lines 277-285

```Python
else:
                raise ValueError(f"Unsupported file type: {ext}")

            return {
                "status": "success",
                "data": {
                    "result": result,
                    "format": format,
                    "language": language,
```

## Snippet 25
Lines 289-294

```Python
except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }
```

## Snippet 26
Lines 295-339

```Python
def transcribe_audio(
        self,
        file_path: str,
        model: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None,
        format: str = "text"
    ) -> Dict[str, Any]:
        """
        Transcribe audio file using Whisper.

        :param file_path: Path to audio file
        :param model: Whisper model name (optional)
        :param options: Additional options (language, task, temperature)
        :param format: Output format (text, json, srt, vtt)
        :return: Dictionary with transcription results
        """
        try:
            # Set up options
            opts = options or {}
            model_name = model or self.valves.WHISPER_MODEL

            # Transcribe
            result = _transcribe_audio(
                file_path,
                model_name=model_name,
                language=opts.get("language"),
                task=opts.get("task", "transcribe"),
                temperature=opts.get("temperature", 0.0),
                format=format
            )

            return {
                "status": "success",
                "data": {
                    "result": result,
                    "format": format,
                    "model": model_name,
                    "options": opts
                }
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }
```

