# Code Snippets from toollama/tool_archive_wayback.py

File: `toollama/tool_archive_wayback.py`  
Language: Python  
Extracted: 2025-06-07 05:08:12  

## Snippet 1
Lines 1-19

```Python
import requests
import logging
import sys
import time
from datetime import datetime
import json

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

WAYBACK_SAVE_URL = "https://web.archive.org/save/"
WAYBACK_AVAIL_URL = "https://archive.org/wayback/available?url="
```

## Snippet 2
Lines 20-25

```Python
def submit_url_to_archive(url):
    """Submits a URL to the Wayback Machine and retrieves the archived page link."""
    logging.info(f"Submitting URL to Wayback Machine: {url}")

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36",
```

## Snippet 3
Lines 35-51

```Python
if avail_data.get('archived_snapshots', {}).get('closest', {}).get('url'):
            logging.info("URL already archived")
            return avail_data['archived_snapshots']['closest']['url']

        # If not archived, try to archive it
        save_url = f"https://web.archive.org/save/{url}"
        logging.info(f"Attempting to save URL: {save_url}")

        response = requests.get(
            save_url,
            headers=headers,
            allow_redirects=True,
            timeout=30
        )

        logging.debug(f"Save response status: {response.status_code}")
```

## Snippet 4
Lines 59-64

```Python
if avail_data.get('archived_snapshots', {}).get('closest', {}).get('url'):
            return avail_data['archived_snapshots']['closest']['url']

        logging.error("Failed to find archived version after save attempt")
        return None
```

## Snippet 5
Lines 65-76

```Python
except requests.exceptions.RequestException as e:
        logging.error(f"Network error: {str(e)}")
        logging.exception(e)
    except json.JSONDecodeError as e:
        logging.error(f"JSON parsing error: {str(e)}")
        logging.exception(e)
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        logging.exception(e)

    return None
```

## Snippet 6
Lines 78-86

```Python
if len(sys.argv) != 2:
        logging.error("Usage: python3 tool_archive_wayback.py <URL_TO_ARCHIVE>")
        sys.exit(1)

    target_url = sys.argv[1]
    print(f"\nAttempting to archive: {target_url}")

    archived_url = submit_url_to_archive(target_url)
```

## Snippet 7
Lines 87-92

```Python
if archived_url:
        print(f"\n✅ Successfully archived!")
        print(f"Archive URL: {archived_url}")
    else:
        print("\n❌ Failed to archive URL")
        print("Try visiting https://web.archive.org/ and submitting the URL manually")
```

