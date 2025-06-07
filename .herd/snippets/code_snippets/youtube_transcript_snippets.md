# Code Snippets from toollama/API/api-tools/tools/Untitled/youtube_transcript.py

File: `toollama/API/api-tools/tools/Untitled/youtube_transcript.py`  
Language: Python  
Extracted: 2025-06-07 05:20:28  

## Snippet 1
Lines 1-17

```Python
"""
title: Youtube Transcript Provider
description: A tool that returns the full, detailed youtube transcript in English of a passed in youtube url.
author: ekatiyar
author_url: https://github.com/ekatiyar
github: https://github.com/ekatiyar/open-webui-tools
funding_url: https://github.com/open-webui
version: 0.0.6
license: MIT
"""

from langchain_community.document_loaders import YoutubeLoader
import re
from typing import Callable, Any

import unittest
```

## Snippet 2
Lines 32-42

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
Lines 49-51

```Python
async def get_youtube_transcript(self, url: str, __event_emitter__: Callable[[dict], Any] = None) -> str:
        """
        Provides the title and full transcript of a YouTube video in English.
```

## Snippet 4
Lines 52-58

```Python
Only use if the user supplied a valid YouTube URL.
        Examples of valid YouTube URLs: https://youtu.be/dQw4w9WgXcQ, https://www.youtube.com/watch?v=dQw4w9WgXcQ

        :param url: The URL of the youtube video that you want the transcript for.
        :return: The title and full transcript of the YouTube video in English, or an error message.
        """
        emitter = EventEmitter(__event_emitter__)
```

## Snippet 5
Lines 62-64

```Python
await emitter.progress_update(f"Getting transcript for {url}")

            error_message = f"Error: Invalid YouTube URL: {url}"
```

## Snippet 6
Lines 65-67

```Python
if not url or url == "":
                await emitter.error_update(error_message)
                return error_message
```

## Snippet 7
Lines 75-78

```Python
error_message = f"Error: Failed to find transcript for {url}"
                await emitter.error_update(error_message)
                return error_message
```

## Snippet 8
Lines 85-89

```Python
except Exception as e:
            error_message = f"Error: {str(e)}"
            await emitter.error_update(error_message)
            return error_message
```

## Snippet 9
Lines 94-97

```Python
async def assert_transcript_error(self, url: str):
        response = await Tools().get_youtube_transcript(url)
        self.assertTrue("Error" in response)
```

## Snippet 10
Lines 98-101

```Python
async def test_get_youtube_transcript(self):
        url = "https://www.youtube.com/watch?v=zhWDdy_5v2w"
        await self.assert_transcript_length(url, 1384)
```

## Snippet 11
Lines 102-110

```Python
async def test_get_youtube_transcript_with_invalid_url(self):
        invalid_url = "https://www.example.com/invalid"
        missing_url = "https://www.youtube.com/watch?v=zhWDdy_5v3w"
        rick_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

        await self.assert_transcript_error(invalid_url)
        await self.assert_transcript_error(missing_url)
        await self.assert_transcript_error(rick_url)
```

## Snippet 12
Lines 111-114

```Python
async def test_get_youtube_transcript_with_none_arg(self):
        await self.assert_transcript_error(None)
        await self.assert_transcript_error("")
```

