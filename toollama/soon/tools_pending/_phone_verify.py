import requests
from typing import Dict, Any, Optional, Callable, Awaitable
from pydantic import BaseModel


class NumberVerificationClient:
    class UserValves(BaseModel):
        """Requires NUMBER_VERIFICATION API Key"""
        NUMBER_VERIFICATION: str

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.numberverify.com/validate"

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

            if not details.get("valid", False):
                return f"Phone number '{phone_number}' is invalid."

            results = f"Phone Number Verification:\n\n"
            results += f"  Number: {details.get('international_format', phone_number)}\n"
            results += f"  Country: {details.get('country_name', 'Unknown')}\n"
            results += f"  Carrier: {details.get('carrier', 'Unknown')}\n"
            results += f"  Line Type: {details.get('line_type', 'Unknown')}\n"

            if __event_emitter__:
                await __event_emitter__(
                    {
                        "type": "status",
                        "data": {"description": "Verification completed", "done": True},
                    }
                )

            return results

        except requests.RequestException as e:
            error_msg = f"Error verifying phone number: {str(e)}"
            if __event_emitter__:
                await __event_emitter__(
                    {"type": "status", "data": {"description": error_msg, "done": True}}
                )
            return error_msg
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            if __event_emitter__:
                await __event_emitter__(
                    {"type": "status", "data": {"description": error_msg, "done": True}}
                )
            return error_msg


# Example usage:
if __name__ == "__main__":
    api_key = "PiHucpwCUfpA87dOUSWhqV0MJXQLBo89"  # Replace with your actual Number Verification key
    number_verification_client = NumberVerificationClient(api_key)
    phone_number = "+14155552671"  # Example phone number
    import asyncio
    print(asyncio.run(number_verification_client.verify_number(phone_number)))