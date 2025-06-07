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


# Replace <my_bfl_api_key> with your own API key
BFL_API_KEY = "<my_bfl_api_key>"


class Tools:
    def __init__(self):
        pass

    async def create_flux_image(
            self,
            prompt: str,
            image_format: str,
            __event_emitter__=None,
    ) -> str:
        """
        This Tool creates visually stunning images with text prompts using the black forest labs API with the Flux.1-pro model.

        :param prompt: the prompt to generate the image
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
                    "data": {"content": f"Prompt: {prompt} \n"},
                }
            )

            return f"Only tell the user that the image was successfully generated with the format '{image_format}'. Do not show any links."

        except Exception as e:
            await __event_emitter__(
                {
                    "type": "status",
                    "data": {"description": f"An error occured: {e}", "done": True},
                }
            )

            return f"Tell the user that an error occurred and the image generation was not successful. Reason: {e}"


FORMATS = {
    "default": (1024, 1024),
    "square": (1024, 1024),
    "landscape": (1024, 768),
    "landscape_large": (1440, 1024),
    "portrait": (768, 1024),
    "portrait_large": (1024, 1440),
}


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


def poll_result(request_id: str) -> str:
    """
    Poll the BFL API for the result of the image generation request. Returns the resulting url.
    :param request_id: The ID of the image generation request
    :return: The URL of the generated image
    :raises RuntimeError: If the status is not "Ready"
    """
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

    if status == "Ready":
        return result["result"]["sample"]
    elif status in [
        "Error",
        "Content Moderated",
        "Request Moderated",
        "Task not found",
    ]:
        raise RuntimeError(f"Image generation failed. Status: {status}")


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
