# Code Snippets from toollama/soon/tools_pending/flux.py

File: `toollama/soon/tools_pending/flux.py`  
Language: Python  
Extracted: 2025-06-07 05:13:34  

## Snippet 1
Lines 1-11

```Python
"""
title: Black Forest Labs API - Flux Pro Image Generator
author: Henning Kosmalla
author: https://github.com/hkosm
version: 0.0.2
license: MIT
description: BFL API Docs: https://api.bfl.ml/docs | images are not stored inside openwebui
"""

import time
import requests
```

## Snippet 2
Lines 22-31

```Python
async def create_flux_image(
            self,
            prompt: str,
            image_format: str,
            __event_emitter__=None,
    ) -> str:
        """
        This Tool creates visually stunning images with text prompts using the black forest labs API with the Flux.1-pro model.

        :param prompt: the prompt to generate the image
```

## Snippet 3
Lines 32-72

```Python
:param image_format: either 'default' for a square image, 'landscape' for a landscape format or 'portrait' for a portrait of mobile format
        """

        await __event_emitter__(
            {
                "type": "status",
                "data": {"description": "Creating FLUX Image...", "done": False},
            }
        )

        try:
            await __event_emitter__(
                {
                    "type": "status",
                    "data": {"description": "Creating FLUX Image...", "done": False},
                }
            )

            request_id = send_image_generation_request(
                prompt=prompt, image_format=image_format, steps=25
            )
            print(f"flux image request: {request_id}")
            image_url = poll_result(request_id)
            print(f"flux image url: {image_url}")

            await __event_emitter__(
                {
                    "type": "status",
                    "data": {"description": "FLUX Image Generated", "done": True},
                }
            )

            await __event_emitter__(
                {
                    "type": "message",
                    "data": {"content": f"![Image]({image_url}) \n"},
                }
            )
            await __event_emitter__(
                {
                    "type": "message",
```

## Snippet 4
Lines 75-78

```Python
)

            return f"Only tell the user that the image was successfully generated with the format '{image_format}'. Do not show any links."
```

## Snippet 5
Lines 79-87

```Python
except Exception as e:
            await __event_emitter__(
                {
                    "type": "status",
                    "data": {"description": f"An error occured: {e}", "done": True},
                }
            )

            return f"Tell the user that an error occurred and the image generation was not successful. Reason: {e}"
```

## Snippet 6
Lines 90-97

```Python
FORMATS = {
    "default": (1024, 1024),
    "square": (1024, 1024),
    "landscape": (1024, 768),
    "landscape_large": (1440, 1024),
    "portrait": (768, 1024),
    "portrait_large": (1024, 1440),
}
```

## Snippet 7
Lines 100-123

```Python
def send_image_generation_request(
        prompt: str, image_format: str = "default", steps: int = 30
) -> str:
    """
    Send a request to the BFL API to generate an image based on the given prompt.
    :param prompt: The prompt to generate the image from.
    :param image_format: The format of the image to generate.
    Must be one of "default", "square", "landscape", "landscape_large", "portrait", "portrait_large".
    :param steps: The number of steps to generate the image.
    :return:
    """

    width, heigth = FORMATS[image_format]
    request = requests.post(
        "https://api.bfl.ml/v1/image",
        headers={
            "accept": "application/json",
            "x-key": BFL_API_KEY,
            "Content-Type": "application/json",
        },
        json={"prompt": prompt, "width": width, "height": heigth, "steps": steps},
    ).json()
    print(request)
    return request["id"]
```

## Snippet 8
Lines 128-132

```Python
Poll the BFL API for the result of the image generation request. Returns the resulting url.
    :param request_id: The ID of the image generation request
    :return: The URL of the generated image
    :raises RuntimeError: If the status is not "Ready"
    """
```

## Snippet 9
Lines 133-144

```Python
while get_result(request_id)["status"] not in [
        "Ready",
        "Error",
        "Content Moderated",
        "Request Moderated",
        "Task not found",
    ]:
        time.sleep(1)

    result = get_result(request_id)
    status = result["status"]
```

## Snippet 10
Lines 147-153

```Python
elif status in [
        "Error",
        "Content Moderated",
        "Request Moderated",
        "Task not found",
    ]:
        raise RuntimeError(f"Image generation failed. Status: {status}")
```

## Snippet 11
Lines 156-167

```Python
def get_result(request_id: str):
    result = requests.get(
        "https://api.bfl.ml/v1/get_result",
        headers={
            "accept": "application/json",
            "x-key": BFL_API_KEY,
        },
        params={
            "id": request_id,
        },
    ).json()
    return result
```

