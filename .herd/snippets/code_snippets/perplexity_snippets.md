# Code Snippets from build/lib/herd_ai/utils/perplexity.py

File: `build/lib/herd_ai/utils/perplexity.py`  
Language: Python  
Extracted: 2025-06-07 05:09:12  

## Snippet 1
Lines 19-42

```Python
#   - system_prompt (Optional[str]): Optional system prompt for model guidance.
#
# Returns:
#   - For chat: Optional[str] (model's response or None on error)
#   - For research: Optional[Dict[str, Any]] (structured research result or None)
###############################################################################

import logging
from typing import Optional, Dict, Any, List

logger = logging.getLogger(__name__)

###############################################################################
# send_prompt_to_perplexity
#
# Sends a chat prompt to the Perplexity API via MCP and returns the assistant's
# reply as a string. Handles different response formats and logs errors.
#
# Arguments:
#   prompt (str): The user message to send.
#   model (str): The Perplexity model to use (default: "sonar").
#   system_prompt (Optional[str]): Optional system prompt to guide the model.
#
# Returns:
```

## Snippet 2
Lines 48-60

```Python
def send_prompt_to_perplexity(
    prompt: str,
    model: str = "sonar",
    system_prompt: Optional[str] = None
) -> Optional[str]:
    try:
        try:
            from functions import mcp_perplexity_ask_perplexity_ask
        except ImportError:
            logger.warning("Perplexity API tools not available - MCP integration required")
            return None

        messages = []
```

## Snippet 3
Lines 61-64

```Python
if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
```

## Snippet 4
Lines 68-71

```Python
if not result:
            logger.warning("Empty response from Perplexity API")
            return None
```

## Snippet 5
Lines 73-76

```Python
if "answer" in result:
                answer = result["answer"]
                logger.debug(f"Received answer from Perplexity API: {answer[:100]}...")
                return answer
```

## Snippet 6
Lines 79-81

```Python
if content:
                    logger.debug(f"Received content from Perplexity API: {content[:100]}...")
                    return content
```

## Snippet 7
Lines 83-86

```Python
else:
            logger.warning(f"Unexpected response format from Perplexity API: {type(result)}")

        return None
```

## Snippet 8
Lines 87-90

```Python
except Exception as e:
        logger.error(f"Perplexity API error: {e}")
        return None
```

## Snippet 9
Lines 108-119

```Python
def send_research_to_perplexity(
    prompt: str,
    system_prompt: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    try:
        try:
            from functions import mcp_perplexity_ask_perplexity_research
        except ImportError:
            logger.warning("Perplexity Research API tools not available - MCP integration required")
            return None

        messages = []
```

## Snippet 10
Lines 120-126

```Python
if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        logger.debug("Sending research prompt to Perplexity API")
        result = mcp_perplexity_ask_perplexity_research({"messages": messages})
```

## Snippet 11
Lines 127-132

```Python
if result and isinstance(result, dict):
            logger.debug("Received research response from Perplexity API")
            return result

        logger.warning(f"Invalid research response from Perplexity API: {result}")
        return None
```

## Snippet 12
Lines 133-135

```Python
except Exception as e:
        logger.error(f"Perplexity Research API error: {e}")
        return None
```

