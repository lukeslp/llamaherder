# Code Snippets from toollama/soon/tools_pending/unprocessed/dev_etranscribe.py

File: `toollama/soon/tools_pending/unprocessed/dev_etranscribe.py`  
Language: Python  
Extracted: 2025-06-07 05:15:30  

## Snippet 1
Lines 1-16

```Python
"""
title: Audio Transcription using OpenAI Whisper API
author: Your Name
funding_url: https://github.com/your-repo
version: 0.1.0
license: MIT
"""

import os
import requests
import json
from pydantic import BaseModel, Field
from typing import Callable, Any
import asyncio
from main.app.state import config
```

## Snippet 2
Lines 22-33

```Python
if self.event_emitter:
            await self.event_emitter(
                {
                    "type": "status",
                    "data": {
                        "status": status,
                        "description": description,
                        "done": done,
                    },
                }
            )
```

## Snippet 3
Lines 35-52

```Python
class Valves(BaseModel):
        MODEL: str = Field(
            default="whisper-1",
            description="ID of the model to use",
        )
        LANGUAGE: str = Field(
            default="",
            description="Language of the input audio in ISO-639-1 format (optional)",
        )
        RESPONSE_FORMAT: str = Field(
            default="json",
            description="Format of the transcript output: json, text, srt, verbose_json, or vtt",
        )
        TEMPERATURE: float = Field(
            default=0.0,
            description="Sampling temperature between 0 and 1",
        )
```

## Snippet 4
Lines 53-59

```Python
def __init__(self):
        self.valves = self.Valves()
        self.headers = {
            "Authorization": f"Bearer {config.OPENAI_API_KEY}",
        }
        self.api_url = "https://api.openai.com/v1/audio/transcriptions"
```

## Snippet 5
Lines 60-73

```Python
async def transcribe_audio(
        self,
        file_path: str,
        __event_emitter__: Callable[[dict], Any] = None,
    ) -> str:
        """
        Transcribe an audio file using the OpenAI Whisper API.
        :param file_path: The path to the audio file to transcribe.
        :return: The transcription result in the specified format.
        """
        emitter = EventEmitter(__event_emitter__)

        await emitter.emit(f"Starting transcription for: {file_path}")
```

## Snippet 6
Lines 74-87

```Python
if not os.path.isfile(file_path):
            await emitter.emit(
                status="error",
                description=f"File not found: {file_path}",
                done=True,
            )
            return json.dumps({"error": "File not found."})

        files = {
            "file": (os.path.basename(file_path), open(file_path, "rb")),
            "model": (None, self.valves.MODEL),
            "response_format": (None, self.valves.RESPONSE_FORMAT),
        }
```

## Snippet 7
Lines 90-127

```Python
if self.valves.TEMPERATURE != 0.0:
            files["temperature"] = (None, str(self.valves.TEMPERATURE))

        try:
            await emitter.emit("Sending transcription request to OpenAI API")

            response = requests.post(
                self.api_url,
                headers=self.headers,
                files=files,
                timeout=120,
            )
            response.raise_for_status()
            result = response.json()

            await emitter.emit(
                status="complete",
                description="Transcription completed successfully",
                done=True,
            )

            return json.dumps(result, ensure_ascii=False)

        except requests.exceptions.RequestException as e:
            await emitter.emit(
                status="error",
                description=f"Error during transcription: {str(e)}",
                done=True,
            )
            return json.dumps({"error": str(e)})

        except json.JSONDecodeError:
            await emitter.emit(
                status="error",
                description="Failed to decode the transcription response",
                done=True,
            )
            return json.dumps({"error": "Failed to decode the response."})
```

