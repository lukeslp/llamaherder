# Code Snippets from toollama/soon/tools_pending/_phone_verify.py

File: `toollama/soon/tools_pending/_phone_verify.py`  
Language: Python  
Extracted: 2025-06-07 05:14:29  

## Snippet 1
Lines 1-3

```Python
import requests
from typing import Dict, Any, Optional, Callable, Awaitable
from pydantic import BaseModel
```

## Snippet 2
Lines 7-10

```Python
class UserValves(BaseModel):
        """Requires NUMBER_VERIFICATION API Key"""
        NUMBER_VERIFICATION: str
```

## Snippet 3
Lines 11-14

```Python
def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.numberverify.com/validate"
```

## Snippet 4
Lines 15-29

```Python
async def verify_number(
        self,
        phone_number: str,
        __user__: dict = {},
        __event_emitter__: Optional[Callable[[Any], Awaitable[None]]] = None,
    ) -> str:
        """
        Verify a phone number's validity and retrieve details.

        Args:
            phone_number (str): The phone number to verify.

        Returns:
            str: Formatted phone number verification details.
        """
```

## Snippet 5
Lines 30-47

```Python
if __event_emitter__:
            await __event_emitter__(
                {
                    "type": "status",
                    "data": {
                        "description": f"Verifying phone number '{phone_number}'...",
                        "done": False,
                    },
                }
            )

        params = {"apiKey": self.api_key, "number": phone_number}

        try:
            response = requests.get(self.base_url, params=params, timeout=15)
            response.raise_for_status()
            details = response.json()
```

## Snippet 6
Lines 48-56

```Python
if not details.get("valid", False):
                return f"Phone number '{phone_number}' is invalid."

            results = f"Phone Number Verification:\n\n"
            results += f"  Number: {details.get('international_format', phone_number)}\n"
            results += f"  Country: {details.get('country_name', 'Unknown')}\n"
            results += f"  Carrier: {details.get('carrier', 'Unknown')}\n"
            results += f"  Line Type: {details.get('line_type', 'Unknown')}\n"
```

## Snippet 7
Lines 57-66

```Python
if __event_emitter__:
                await __event_emitter__(
                    {
                        "type": "status",
                        "data": {"description": "Verification completed", "done": True},
                    }
                )

            return results
```

## Snippet 8
Lines 69-73

```Python
if __event_emitter__:
                await __event_emitter__(
                    {"type": "status", "data": {"description": error_msg, "done": True}}
                )
            return error_msg
```

## Snippet 9
Lines 76-80

```Python
if __event_emitter__:
                await __event_emitter__(
                    {"type": "status", "data": {"description": error_msg, "done": True}}
                )
            return error_msg
```

## Snippet 10
Lines 84-89

```Python
if __name__ == "__main__":
    api_key = "PiHucpwCUfpA87dOUSWhqV0MJXQLBo89"  # Replace with your actual Number Verification key
    number_verification_client = NumberVerificationClient(api_key)
    phone_number = "+14155552671"  # Example phone number
    import asyncio
    print(asyncio.run(number_verification_client.verify_number(phone_number)))
```

