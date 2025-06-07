# Code Snippets from toollama/soon/tools_pending/unprocessed/dev_ewaybackMachine.py

File: `toollama/soon/tools_pending/unprocessed/dev_ewaybackMachine.py`  
Language: Python  
Extracted: 2025-06-07 05:15:42  

## Snippet 1
Lines 2-6

```Python
"""
title: Wayback Machine API Integration
author: AI Assistant
version: 1.0
license: MIT
```

## Snippet 2
Lines 7-15

```Python
description: A tool that integrates the Wayback Machine API for retrieving archived web pages.
requirements: requests
"""

import os
import requests
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
```

## Snippet 3
Lines 17-19

```Python
class Valves(BaseModel):
        API_BASE_URL: str = Field(
            default="https://archive.org/wayback/available",
```

## Snippet 4
Lines 21-23

```Python
)
        USER_AGENT: str = Field(
            default="WaybackMachineAPI/1.0",
```

## Snippet 5
Lines 27-31

```Python
def __init__(self):
        self.valves = self.Valves()
        self.api_base_url = self.valves.API_BASE_URL
        self.user_agent = self.valves.USER_AGENT
```

## Snippet 6
Lines 32-34

```Python
def get_archived_snapshot(self, url: str, timestamp: Optional[str] = None) -> Dict[str, Any]:
        """
        Retrieve the closest archived snapshot of a given URL from the Wayback Machine.
```

## Snippet 7
Lines 35-40

```Python
:param url: The URL to check for archived snapshots.
        :param timestamp: Optional timestamp to find the closest snapshot (format: YYYYMMDDhhmmss).
        :return: A dictionary containing the response data.
        """
        try:
            params = {"url": url}
```

## Snippet 8
Lines 41-52

```Python
if timestamp:
                params["timestamp"] = timestamp

            headers = {
                "User-Agent": self.user_agent
            }

            response = requests.get(self.api_base_url, params=params, headers=headers, timeout=30)
            response.raise_for_status()

            data = response.json()
```

## Snippet 9
Lines 53-67

```Python
if "archived_snapshots" in data and "closest" in data["archived_snapshots"]:
                snapshot = data["archived_snapshots"]["closest"]
                return {
                    "status": "success",
                    "data": {
                        "available": snapshot["available"],
                        "url": snapshot["url"],
                        "timestamp": snapshot["timestamp"],
                        "status": snapshot["status"]
                    },
                    "original_url": url
                }
            else:
                return {
                    "status": "not_found",
```

## Snippet 10
Lines 72-78

```Python
except requests.exceptions.RequestException as e:
            return {
                "status": "error",
                "message": str(e),
                "original_url": url
            }
```

## Snippet 11
Lines 81-102

```Python
Retrieve the capture history for a given URL from the Wayback CDX Server API.
        :param url: The URL to retrieve capture history for.
        :return: A dictionary containing the response data.
        """
        try:
            cdx_api_url = "https://web.archive.org/cdx/search/cdx"
            params = {
                "url": url,
                "output": "json",
                "fl": "timestamp,original,mimetype,statuscode",
                "collapse": "timestamp:8"  # Group by YYYYMMDD
            }

            headers = {
                "User-Agent": self.user_agent
            }

            response = requests.get(cdx_api_url, params=params, headers=headers, timeout=30)
            response.raise_for_status()

            data = response.json()
```

## Snippet 12
Lines 103-105

```Python
if len(data) > 1:  # First row is the header
                return {
                    "status": "success",
```

## Snippet 13
Lines 109-111

```Python
else:
                return {
                    "status": "not_found",
```

## Snippet 14
Lines 116-121

```Python
except requests.exceptions.RequestException as e:
            return {
                "status": "error",
                "message": str(e),
                "original_url": url
            }
```

