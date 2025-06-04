###############################################################################
# Herd AI - Perplexity API Utilities
#
# This module provides utility functions for interacting with the Perplexity API
# via the MCP (Modular Command Platform) integration. It supports sending chat
# prompts and research queries to Perplexity models and retrieving responses.
#
# Credentials:
#   - Requires MCP integration with Perplexity API tools available in the environment.
#   - No direct API key is handled here; MCP must be configured separately.
#
# Functions:
#   - send_prompt_to_perplexity: Send a chat prompt and receive a model response.
#   - send_research_to_perplexity: Send a research prompt and receive structured results.
#
# Argument Formats:
#   - prompt (str): The user message or research question.
#   - model (str): The Perplexity model to use (default: "sonar").
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
#   Optional[str]: The model's response text, or None if an error occurred.
#
# Credentials:
#   - Requires MCP integration with Perplexity API tools available.
###############################################################################
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
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        logger.debug(f"Sending prompt to Perplexity API using {model} model")
        result = mcp_perplexity_ask_perplexity_ask({"messages": messages})

        if not result:
            logger.warning("Empty response from Perplexity API")
            return None

        if isinstance(result, dict):
            if "answer" in result:
                answer = result["answer"]
                logger.debug(f"Received answer from Perplexity API: {answer[:100]}...")
                return answer
            if "choices" in result and result["choices"]:
                content = result["choices"][0].get("message", {}).get("content")
                if content:
                    logger.debug(f"Received content from Perplexity API: {content[:100]}...")
                    return content
            logger.warning(f"Could not extract answer from Perplexity response: {result}")
        else:
            logger.warning(f"Unexpected response format from Perplexity API: {type(result)}")

        return None
    except Exception as e:
        logger.error(f"Perplexity API error: {e}")
        return None

###############################################################################
# send_research_to_perplexity
#
# Sends a research prompt to the Perplexity API via MCP and returns the full
# research response as a dictionary, including citations and structured data.
#
# Arguments:
#   prompt (str): The research question or topic.
#   system_prompt (Optional[str]): Optional system prompt to guide the research.
#
# Returns:
#   Optional[Dict[str, Any]]: Dictionary with research results and citations,
#   or None if an error occurred.
#
# Credentials:
#   - Requires MCP integration with Perplexity Research API tools available.
###############################################################################
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
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        logger.debug("Sending research prompt to Perplexity API")
        result = mcp_perplexity_ask_perplexity_research({"messages": messages})

        if result and isinstance(result, dict):
            logger.debug("Received research response from Perplexity API")
            return result

        logger.warning(f"Invalid research response from Perplexity API: {result}")
        return None
    except Exception as e:
        logger.error(f"Perplexity Research API error: {e}")
        return None
