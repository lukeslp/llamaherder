# Code Snippets from toollama/soon/tools_pending/unprocessed/dev_eperplexity.py

File: `toollama/soon/tools_pending/unprocessed/dev_eperplexity.py`  
Language: Python  
Extracted: 2025-06-07 05:15:52  

## Snippet 1
Lines 1-18

```Python
"""
title: Perplexity Manifold Pipe
author: nikolaskn, justinh-rahb, moblangeois
author_url: https://github.com/open-webui
funding_url: https://github.com/open-webui
version: 0.2.1
license: MIT
"""

from pydantic import BaseModel, Field
from typing import Optional, Union, Generator, Iterator
from open_webui.utils.misc import get_last_user_message
from open_webui.utils.misc import pop_system_message

import os
import json
import time
import requests
```

## Snippet 2
Lines 22-28

```Python
class Valves(BaseModel):
        NAME_PREFIX: str = Field(
            default="Perplexity/",
            description="The prefix applied before the model names.",
        )
        PERPLEXITY_API_BASE_URL: str = Field(
            default="https://api.perplexity.ai",
```

## Snippet 3
Lines 30-35

```Python
)
        PERPLEXITY_API_KEY: str = Field(
            default="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",
            description="Required API key to access Perplexity services.",
        )
```

## Snippet 4
Lines 36-39

```Python
def __init__(self):
        self.type = "manifold"
        self.valves = self.Valves()
```

## Snippet 5
Lines 40-71

```Python
def pipes(self):
        return [
            {
                "id": "llama-3.1-sonar-small-128k-online",
                "name": f"{self.valves.NAME_PREFIX}Llama 3.1 Sonar Small 128k Online",
            },
            {
                "id": "llama-3.1-sonar-large-128k-online",
                "name": f"{self.valves.NAME_PREFIX}Llama 3.1 Sonar Large 128k Online",
            },
            {
                "id": "llama-3.1-sonar-huge-128k-online",
                "name": f"{self.valves.NAME_PREFIX}Llama 3.1 Sonar Huge 128k Online",
            },
            {
                "id": "llama-3.1-sonar-small-128k-chat",
                "name": f"{self.valves.NAME_PREFIX}Llama 3.1 Sonar Small 128k Chat",
            },
            {
                "id": "llama-3.1-sonar-large-128k-chat",
                "name": f"{self.valves.NAME_PREFIX}Llama 3.1 Sonar Large 128k Chat",
            },
            {
                "id": "llama-3.1-8b-instruct",
                "name": f"{self.valves.NAME_PREFIX}Llama 3.1 8B Instruct",
            },
            {
                "id": "llama-3.1-70b-instruct",
                "name": f"{self.valves.NAME_PREFIX}Llama 3.1 70B Instruct",
            },
        ]
```

## Snippet 6
Lines 75-85

```Python
if not self.valves.PERPLEXITY_API_KEY:
            raise Exception("PERPLEXITY_API_KEY not provided in the valves.")

        headers = {
            "Authorization": f"Bearer {self.valves.PERPLEXITY_API_KEY}",
            "Content-Type": "application/json",
            "accept": "application/json",
        }

        system_message, messages = pop_system_message(body.get("messages", []))
        system_prompt = "You are a helpful assistant."
```

## Snippet 7
Lines 86-89

```Python
if system_message is not None:
            system_prompt = system_message["content"]

        model_id = body["model"]
```

## Snippet 8
Lines 92-105

```Python
if model_id.startswith("perplexity."):
            model_id = model_id[len("perplexity.") :]

        payload = {
            "model": model_id,
            "messages": [{"role": "system", "content": system_prompt}, *messages],
            "stream": body.get("stream", True),
            "return_citations": True,
            "return_images": True,
        }

        url = f"{self.valves.PERPLEXITY_API_BASE_URL}/chat/completions"

        try:
```

## Snippet 9
Lines 106-109

```Python
if body.get("stream", False):
                return self.stream_response(url, headers, payload)
            else:
                return self.non_stream_response(url, headers, payload)
```

## Snippet 10
Lines 110-116

```Python
except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            return f"Error: Request failed: {e}"
        except Exception as e:
            print(f"Error in pipe method: {e}")
            return f"Error: {e}"
```

## Snippet 11
Lines 117-121

```Python
def stream_response(self, url, headers, payload):
        try:
            with requests.post(
                url, headers=headers, json=payload, stream=True, timeout=(3.05, 60)
            ) as response:
```

## Snippet 12
Lines 122-128

```Python
if response.status_code != 200:
                    raise Exception(
                        f"HTTP Error {response.status_code}: {response.text}"
                    )

                data = None
```

## Snippet 13
Lines 132-145

```Python
if line.startswith("data: "):
                            try:
                                data = json.loads(line[6:])
                                yield data["choices"][0]["delta"]["content"]

                                time.sleep(
                                    0.01
                                )  # Delay to avoid overwhelming the client

                            except json.JSONDecodeError:
                                print(f"Failed to parse JSON: {line}")
                            except KeyError as e:
                                print(f"Unexpected data structure: {e}")
                                print(f"Full data: {data}")
```

## Snippet 14
Lines 151-157

```Python
except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            yield f"Error: Request failed: {e}"
        except Exception as e:
            print(f"General error in stream_response method: {e}")
            yield f"Error: {e}"
```

## Snippet 15
Lines 158-162

```Python
def non_stream_response(self, url, headers, payload):
        try:
            response = requests.post(
                url, headers=headers, json=payload, timeout=(3.05, 60)
            )
```

## Snippet 16
Lines 163-168

```Python
if response.status_code != 200:
                raise Exception(f"HTTP Error {response.status_code}: {response.text}")

            res = response.json()
            citations = res.get("citations", [])
            citations_string = "\n".join(
```

## Snippet 17
Lines 172-174

```Python
except requests.exceptions.RequestException as e:
            print(f"Failed non-stream request: {e}")
            return f"Error: {e}"
```

