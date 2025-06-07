"""
title: status_emitter
author: stefanpietrusky
author_url: https://downchurch.studio/
version: 0.1
"""

import asyncio


class Tools:
    def __init__(self):
        pass

    async def run(self, prompt: str, __user__: dict, __event_emitter__=None) -> str:
        """
        The user is informed about the progress through an event emitter.
        """
        # Show start status
        if __event_emitter__:
            await __event_emitter__(
                {
                    "type": "status",
                    "data": {"description": "Processing started...", "done": False},
                }
            )

        # Simulate multiple processing steps
        for i in range(1, 6):  # Simulate 5 steps
            await asyncio.sleep(1)  # Simulates a time-consuming step
            if __event_emitter__:
                await __event_emitter__(
                    {
                        "type": "status",
                        "data": {
                            "description": f"Step {i} of 5 completed...",
                            "done": False,
                        },
                    }
                )

        # View completion status
        if __event_emitter__:
            await __event_emitter__(
                {
                    "type": "status",
                    "data": {
                        "description": "Processing completed!",
                        "done": True,
                    },
                }
            )

        return "Processing was completed successfully."
