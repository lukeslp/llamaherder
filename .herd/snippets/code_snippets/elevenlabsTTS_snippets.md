# Code Snippets from toollama/API/api-tools/tools/Untitled/elevenlabsTTS.py

File: `toollama/API/api-tools/tools/Untitled/elevenlabsTTS.py`  
Language: Python  
Extracted: 2025-06-07 05:20:30  

## Snippet 1
Lines 1-18

```Python
"""
title: ElevenLabs Text-to-Speech Tool
author: justinh-rahb
author_url: https://github.com/justinh-rahb
funding_url: https://github.com/open-webui
version: 0.2.3
license: MIT
"""

import requests
import uuid
import os
from pydantic import BaseModel, Field
from typing import Callable, Union, Any
from open_webui.config import UPLOAD_DIR
from open_webui.apps.webui.models.files import Files

DEBUG = False
```

## Snippet 2
Lines 22-30

```Python
class Valves(BaseModel):
        ELEVENLABS_API_KEY: str = Field(
            default=None, description="Your ElevenLabs API key."
        )
        ELEVENLABS_MODEL_ID: str = Field(
            default="eleven_multilingual_v2",
            description="ID of the ElevenLabs TTS model to use.",
        )
```

## Snippet 3
Lines 31-34

```Python
def __init__(self):
        self.valves = self.Valves()
        self.voice_id_cache = {}
```

## Snippet 4
Lines 35-40

```Python
def fetch_available_voices(self) -> str:
        """
        Fetches the list of available voices from the ElevenLabs API.

        :return: A formatted string containing the names and descriptions of available voices.
        """
```

## Snippet 5
Lines 41-56

```Python
if DEBUG:
            print("Debug: Fetching available voices")

        base_url = "https://api.elevenlabs.io/v1"
        headers = {
            "xi-api-key": self.valves.ELEVENLABS_API_KEY,
            "Content-Type": "application/json",
        }

        voices_url = f"{base_url}/voices"
        try:
            response = requests.get(voices_url, headers=headers)
            response.raise_for_status()
            voices_data = response.json()

            message = "Here are the available voices from ElevenLabs:\n\n"
```

## Snippet 6
Lines 66-69

```Python
if DEBUG:
                print(f"Debug: Error fetching voices: {str(e)}")
            return "Sorry, I couldn't fetch the list of available voices at the moment."
```

## Snippet 7
Lines 70-78

```Python
def get_voice_list(self) -> str:
        """
        Retrieves and returns a list of available voices as a formatted string.

        :return: A formatted string containing the list of voices.
        """
        voices_message = self.fetch_available_voices()
        return voices_message
```

## Snippet 8
Lines 79-89

```Python
async def elevenlabs_text_to_speech(
        self,
        text: str,
        voice_name: str = "rachel",
        __user__: dict = {},
        __event_emitter__: Callable[[dict], Any] = None,
    ) -> str:
        """
        Converts text to speech using the ElevenLabs API or lists available voices.

        :param text: The text to convert to speech or "list voices" to retrieve available voices.
```

## Snippet 9
Lines 92-95

```Python
:param __event_emitter__: An optional callback function to emit status events throughout the process.
        :return: A message indicating the result of the operation (success or error).
        """
```

## Snippet 10
Lines 101-104

```Python
def status_object(
            description="Unknown State", status="in_progress", done=False
        ):
            """
```

## Snippet 11
Lines 105-120

```Python
Helper function to create a status object.

            :param description: A short description of the current status.
            :param status: Status type (e.g., 'in_progress', 'error', 'complete').
            :param done: Boolean indicating whether the operation is done.
            :return: A dictionary representing the status object.
            """
            return {
                "type": "status",
                "data": {
                    "status": status,
                    "description": description,
                    "done": done,
                },
            }
```

## Snippet 12
Lines 121-125

```Python
if __event_emitter__:
            await __event_emitter__(
                status_object("Initializing ElevenLabs Text-to-Speech")
            )
```

## Snippet 13
Lines 127-132

```Python
if __event_emitter__:
                await __event_emitter__(
                    status_object("Error: API key not set", status="error", done=True)
                )
            return "ElevenLabs API key is not set. Please set it in your environment variables."
```

## Snippet 14
Lines 134-141

```Python
if __event_emitter__:
                await __event_emitter__(
                    status_object(
                        "Error: User not authenticated", status="error", done=True
                    )
                )
            return "Error: User ID is not available. Please ensure you're logged in."
```

## Snippet 15
Lines 142-148

```Python
if text.lower().strip() in [
            "list voices",
            "show voices",
            "available voices",
            "what voices are available",
        ]:
            voices = self.get_voice_list()
```

## Snippet 16
Lines 149-156

```Python
if __event_emitter__:
                await __event_emitter__(
                    status_object(
                        "Available voices fetched", status="complete", done=True
                    )
                )
            return voices
```

## Snippet 17
Lines 161-168

```Python
if __event_emitter__:
                    await __event_emitter__(
                        status_object(
                            "Error: Could not fetch voices", status="error", done=True
                        )
                    )
                return voices_message
```

## Snippet 18
Lines 171-180

```Python
if __event_emitter__:
                    await __event_emitter__(
                        status_object(
                            f"Error: Voice '{voice_name}' not found",
                            status="error",
                            done=True,
                        )
                    )
                return f"Error: Voice '{voice_name}' not found. Use 'list voices' to see available options."
```

## Snippet 19
Lines 181-200

```Python
if __event_emitter__:
            await __event_emitter__(status_object("Generating speech"))

        base_url = "https://api.elevenlabs.io/v1"
        headers = {
            "xi-api-key": self.valves.ELEVENLABS_API_KEY,
            "Content-Type": "application/json",
        }

        tts_url = f"{base_url}/text-to-speech/{voice_id}"
        payload = {
            "text": text,
            "model_id": self.valves.ELEVENLABS_MODEL_ID,
            "voice_settings": {"stability": 0.5, "similarity_boost": 0.5},
        }

        try:
            response = requests.post(tts_url, json=payload, headers=headers)
            response.raise_for_status()
```

## Snippet 20
Lines 201-207

```Python
if response.status_code == 200:
                audio_data = response.content
                file_name = f"tts_{uuid.uuid4()}.mp3"

                file_id = self._create_file(
                    file_name, "Generated Audio", audio_data, "audio/mpeg", __user__
                )
```

## Snippet 21
Lines 210-217

```Python
if __event_emitter__:
                        await __event_emitter__(
                            status_object(
                                "Generated successfully",
                                status="complete",
                                done=True,
                            )
                        )
```

## Snippet 22
Lines 219-227

```Python
if __event_emitter__:
                            await __event_emitter__(
                                {
                                    "type": "message",
                                    "data": {
                                        "content": f"\n[click to listen]({file_url})\n"
                                    },
                                }
                            )
```

## Snippet 23
Lines 230-236

```Python
if __event_emitter__:
                        await __event_emitter__(
                            status_object(
                                "Error saving audio file", status="error", done=True
                            )
                        )
                    return "Error saving audio file."
```

## Snippet 24
Lines 238-245

```Python
if __event_emitter__:
                    await __event_emitter__(
                        status_object(
                            f"Error: Unexpected API response", status="error", done=True
                        )
                    )
                return f"Error generating speech: {response.text}"
```

## Snippet 25
Lines 247-254

```Python
if __event_emitter__:
                await __event_emitter__(
                    status_object(
                        f"Error: API request failed", status="error", done=True
                    )
                )
            return f"Error generating speech: {str(e)}"
```

## Snippet 26
Lines 255-270

```Python
def _create_file(
        self,
        file_name: str,
        title: str,
        content: Union[str, bytes],
        content_type: str,
        __user__: dict = {},
    ) -> str:
        """
        Creates and saves a file in the local upload directory and registers it with the Files API.

        :param file_name: The name of the file to save.
        :param title: The title of the file.
        :param content: The content of the file, either as a string or bytes.
        :param content_type: The MIME type of the file (e.g., "audio/mpeg").
        :param __user__: A dictionary containing user information.
```

## Snippet 27
Lines 273-278

```Python
if DEBUG:
            print(f"Debug: Entering _create_file method")
            print(f"Debug: File name: {file_name}")
            print(f"Debug: Content type: {content_type}")
            print(f"Debug: User: {__user__}")
```

## Snippet 28
Lines 280-283

```Python
if DEBUG:
                print("Debug: User ID is not available")
            return None
```

## Snippet 29
Lines 288-302

```Python
mode = "w" if isinstance(content, str) else "wb"

        try:
            os.makedirs(base_path, exist_ok=True)
            with open(file_path, mode) as f:
                f.write(content)

            meta = {
                "source": file_path,
                "title": title,
                "content_type": content_type,
                "size": os.path.getsize(file_path),
                "path": file_path,
            }
```

## Snippet 30
Lines 303-310

```Python
class FileForm(BaseModel):
                id: str
                filename: str
                meta: dict = {}

            formData = FileForm(id=file_id, filename=file_name, meta=meta)
            file = Files.insert_new_file(__user__["id"], formData)
```

## Snippet 31
Lines 311-314

```Python
if DEBUG:
                print(f"Debug: File saved to local storage. File path: {file_path}")
                print(f"Debug: Meta information: {meta}")
            return file.id
```

## Snippet 32
Lines 316-319

```Python
if DEBUG:
                print(f"Debug: Error saving file: {e}")
            return None
```

## Snippet 33
Lines 320-327

```Python
def _get_file_url(self, file_id: str) -> str:
        """
        Constructs and returns the URL to access the file content by its ID.

        :param file_id: The ID of the file.
        :return: The URL to access the file content.
        """
        return f"/api/v1/files/{file_id}/content"
```

