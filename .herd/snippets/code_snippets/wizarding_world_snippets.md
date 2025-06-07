# Code Snippets from toollama/API/api-tools/tools/tools/tools2/wizarding_world.py

File: `toollama/API/api-tools/tools/tools/tools2/wizarding_world.py`  
Language: Python  
Extracted: 2025-06-07 05:25:35  

## Snippet 1
Lines 1-8

```Python
import requests
from runtime import Args
from typings.getPottered.getPottered import Input, Output
from typing import Optional, Dict, Any, Union
import uuid

BASE_URL = "https://wizard-world-api.herokuapp.com"
```

## Snippet 2
Lines 9-11

```Python
def get_elixirs(args: Args[Input]) -> Output:
    endpoint = f"{BASE_URL}/Elixirs"
    params = {
```

## Snippet 3
Lines 18-21

```Python
def get_houses() -> Output:
    endpoint = f"{BASE_URL}/Houses"
    return make_request(endpoint)
```

## Snippet 4
Lines 22-24

```Python
def get_spells(args: Args[Input]) -> Output:
    endpoint = f"{BASE_URL}/Spells"
    params = {
```

## Snippet 5
Lines 31-33

```Python
def get_wizards(args: Args[Input]) -> Output:
    endpoint = f"{BASE_URL}/Wizards"
    params = {
```

## Snippet 6
Lines 40-44

```Python
if not is_valid_uuid(wizard_id):
        return Output(data=None, error="Invalid wizard ID format")
    endpoint = f"{BASE_URL}/Wizards/{wizard_id}"
    return make_request(endpoint)
```

## Snippet 7
Lines 45-51

```Python
def is_valid_uuid(uuid_string: str) -> bool:
    try:
        uuid.UUID(uuid_string)
        return True
    except ValueError:
        return False
```

## Snippet 8
Lines 56-58

```Python
if response.status_code == 200:
            data = response.json()
            return Output(data=data, error=None)
```

## Snippet 9
Lines 61-64

```Python
elif response.status_code == 429:
            return Output(data=None, error="Rate limit exceeded")
        else:
            return Output(data=None, error=f"Failed to retrieve data. Status code: {response.status_code}")
```

## Snippet 10
Lines 81-83

```Python
if wizard_id:
            return get_wizard_by_id(wizard_id)
        else:
```

