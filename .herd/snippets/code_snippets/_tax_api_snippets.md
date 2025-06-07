# Code Snippets from toollama/soon/tools_pending/_tax_api.py

File: `toollama/soon/tools_pending/_tax_api.py`  
Language: Python  
Extracted: 2025-06-07 05:13:39  

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
        """Requires TAX_DATA API Key"""
        TAX_DATA: str
```

## Snippet 3
Lines 11-14

```Python
def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.taxdata.com/rates"
```

## Snippet 4
Lines 15-23

```Python
async def fetch_tax_rates(
        self,
        country: str = "US",
        state: Optional[str] = None,
        city: Optional[str] = None,
        __user__: dict = {},
        __event_emitter__: Optional[Callable[[Any], Awaitable[None]]] = None,
    ) -> str:
        """
```

## Snippet 5
Lines 24-27

```Python
Fetch tax rates for a specific country, state, or city.

        Args:
            country (str): Country code (default: "US").
```

## Snippet 6
Lines 31-33

```Python
Returns:
            str: Formatted tax rate information.
        """
```

## Snippet 7
Lines 34-38

```Python
if __event_emitter__:
            await __event_emitter__(
                {
                    "type": "status",
                    "data": {
```

## Snippet 8
Lines 48-55

```Python
if city:
            params["city"] = city

        try:
            response = requests.get(self.base_url, params=params, timeout=15)
            response.raise_for_status()
            tax_data = response.json()
```

## Snippet 9
Lines 63-72

```Python
if __event_emitter__:
                await __event_emitter__(
                    {
                        "type": "status",
                        "data": {"description": "Fetch completed", "done": True},
                    }
                )

            return results
```

## Snippet 10
Lines 75-79

```Python
if __event_emitter__:
                await __event_emitter__(
                    {"type": "status", "data": {"description": error_msg, "done": True}}
                )
            return error_msg
```

## Snippet 11
Lines 82-86

```Python
if __event_emitter__:
                await __event_emitter__(
                    {"type": "status", "data": {"description": error_msg, "done": True}}
                )
            return error_msg
```

## Snippet 12
Lines 90-95

```Python
if __name__ == "__main__":
    api_key = "PiHucpwCUfpA87dOUSWhqV0MJXQLBo89"  # Replace with your actual Tax Data key
    tax_data_client = TaxDataClient(api_key)
    country, state, city = "US", "CA", "San Francisco"
    import asyncio
    print(asyncio.run(tax_data_client.fetch_tax_rates(country, state, city)))
```

