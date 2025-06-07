# Code Snippets from toollama/moe/tools/document/content/wayback_archiver.py

File: `toollama/moe/tools/document/content/wayback_archiver.py`  
Language: Python  
Extracted: 2025-06-07 05:13:01  

## Snippet 1
Lines 1-7

```Python
from typing import Optional, Dict, Any
import requests
import logging
import time
import json
from ...base import BaseTool
```

## Snippet 2
Lines 14-17

```Python
def __init__(self):
        super().__init__()
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36",
```

## Snippet 3
Lines 22-29

```Python
def submit_url_to_archive(self, url: str) -> Optional[str]:
        """
        Submit a URL to the Wayback Machine and retrieve the archived page link.

        Args:
            url (str): The URL to archive

        Returns:
```

## Snippet 4
Lines 39-55

```Python
if avail_data.get('archived_snapshots', {}).get('closest', {}).get('url'):
                self.logger.info("URL already archived")
                return avail_data['archived_snapshots']['closest']['url']

            # If not archived, try to archive it
            save_url = f"{self.WAYBACK_SAVE_URL}{url}"
            self.logger.info(f"Attempting to save URL: {save_url}")

            response = requests.get(
                save_url,
                headers=self.headers,
                allow_redirects=True,
                timeout=30
            )

            self.logger.debug(f"Save response status: {response.status_code}")
```

## Snippet 5
Lines 63-68

```Python
if avail_data.get('archived_snapshots', {}).get('closest', {}).get('url'):
                return avail_data['archived_snapshots']['closest']['url']

            self.logger.error("Failed to find archived version after save attempt")
            return None
```

## Snippet 6
Lines 69-80

```Python
except requests.exceptions.RequestException as e:
            self.logger.error(f"Network error: {str(e)}")
            self.logger.exception(e)
        except json.JSONDecodeError as e:
            self.logger.error(f"JSON parsing error: {str(e)}")
            self.logger.exception(e)
        except Exception as e:
            self.logger.error(f"Unexpected error: {str(e)}")
            self.logger.exception(e)

        return None
```

## Snippet 7
Lines 81-90

```Python
def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Execute the wayback archiver tool.

        Args:
            url (str): The URL to archive

        Returns:
            Dict[str, Any]: A dictionary containing:
                - success (bool): Whether the operation was successful
```

## Snippet 8
Lines 95-102

```Python
if not url:
            return {
                'success': False,
                'error': 'No URL provided'
            }

        archived_url = self.submit_url_to_archive(url)
```

## Snippet 9
Lines 103-113

```Python
if archived_url:
            return {
                'success': True,
                'archived_url': archived_url
            }
        else:
            return {
                'success': False,
                'error': 'Failed to archive URL'
            }
```

## Snippet 10
Lines 123-130

```Python
def parameters(self) -> Dict[str, Dict[str, Any]]:
        return {
            "url": {
                "type": "string",
                "description": "The URL to archive",
                "required": True
            }
        }
```

