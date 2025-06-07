# Code Snippets from toollama/soon/tools_pending/unprocessed/dev_eocr.py

File: `toollama/soon/tools_pending/unprocessed/dev_eocr.py`  
Language: Python  
Extracted: 2025-06-07 05:16:02  

## Snippet 1
Lines 1-24

```Python
import os
import requests
from datetime import datetime
import fitz  # PyMuPDF
import pytesseract
from PIL import Image
from open_webui.apps.webui.models.tools import ToolForm, ToolModel, ToolResponse, Tools
from open_webui.apps.webui.models.users import Users
from pathlib import Path
from typing import Optional
from open_webui.apps.webui.models.tools import ToolForm, ToolModel, ToolResponse, Tools
from open_webui.apps.webui.utils import load_toolkit_module_by_id, replace_imports
from open_webui.config import CACHE_DIR, DATA_DIR
from typing import Optional

from open_webui.apps.webui.models.models import (
    ModelForm,
    ModelModel,
    ModelResponse,
    Models,
)
from open_webui.constants import ERROR_MESSAGES
from fastapi import APIRouter, Depends, HTTPException, Request, status
from open_webui.utils.utils import get_admin_user, get_verified_user
```

## Snippet 2
Lines 28-31

```Python
def __init__(self):
        # Specify the Tesseract-OCR executable path
        pytesseract.pytesseract.tesseract_cmd = r"C://Users//muhammad.tayyab//AppData//Local//Programs//Tesseract-OCR//tesseract.exe"
```

## Snippet 3
Lines 32-38

```Python
def get_user_name_and_email_and_id(self, __user__: dict = {}) -> str:
        """
        Get the user name, Email and ID from the user object.
        """
        print(__user__)
        result = ""
```

## Snippet 4
Lines 46-50

```Python
if result == "":
            result = "User: Unknown"

        return result
```

## Snippet 5
Lines 51-60

```Python
def get_current_time(self) -> str:
        """
        Get the current time in a more human-readable format.
        :return: The current time.
        """
        now = datetime.now()
        current_time = now.strftime("%I:%M:%S %p")
        current_date = now.strftime("%A, %B %d, %Y")
        return f"Current Date and Time = {current_date}, {current_time}"
```

## Snippet 6
Lines 61-67

```Python
def calculator(self, equation: str) -> str:
        """
        Calculate the result of an equation.
        :param equation: The equation to calculate.
        """
        try:
            result = eval(equation)
```

## Snippet 7
Lines 69-72

```Python
except Exception as e:
            print(e)
            return "Invalid equation"
```

## Snippet 8
Lines 75-79

```Python
Get the current weather for a given city.
        :param city: The name of the city to get the weather for.
        :return: The current weather information or an error message.
        """
        api_key = os.getenv("OPENWEATHER_API_KEY")
```

## Snippet 9
Lines 80-96

```Python
if not api_key:
            return (
                "API key is not set in the environment variable 'OPENWEATHER_API_KEY'."
            )

        base_url = "http://api.openweathermap.org/data/2.5/weather"
        params = {
            "q": city,
            "appid": api_key,
            "units": "metric",
        }

        try:
            response = requests.get(base_url, params=params)
            response.raise_for_status()
            data = response.json()
```

## Snippet 10
Lines 97-105

```Python
if data.get("cod") != 200:
                return f"Error fetching weather data: {data.get('message')}"

            weather_description = data["weather"][0]["description"]
            temperature = data["main"]["temp"]
            humidity = data["main"]["humidity"]
            wind_speed = data["wind"]["speed"]

            return f"Weather in {city}: {temperature}°C"
```

## Snippet 11
Lines 109-120

```Python
def extract_text_from_pdf(self, pdf_path: str) -> str:
        """
        Extract text from a scanned PDF file using OCR.
        :param pdf_path: Path to the PDF file.
        :return: Extracted text from the PDF.
        """
        extracted_text = ""

        try:
            # Open the PDF file
            pdf_document = fitz.open(pdf_path)
```

## Snippet 12
Lines 121-133

```Python
for page_num in range(len(pdf_document)):
                # Get the page
                page = pdf_document[page_num]
                # Render the page to an image
                pix = page.get_pixmap()
                # Convert the image to a PIL Image
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

                # Use pytesseract to do OCR on the image
                text = pytesseract.image_to_string(img)
                extracted_text += f"Page {page_num + 1}:\n{text}\n\n"

            pdf_document.close()
```

## Snippet 13
Lines 134-137

```Python
except Exception as e:
            return f"Error extracting text from PDF: {str(e)}"

        return extracted_text.strip()  # Return extracted text without trailing spaces
```

