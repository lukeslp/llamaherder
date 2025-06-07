"""
ToolLama MoE - Mixture of Experts System
"""

from moe.core import (
    ModelRegistry,
    SmartRouter,
    ToolDiscovery,
    ModelCommunicator,
    TaskManager,
    tool_capabilities
)

__version__ = "0.1.0"
__author__ = "Luke Steuber"
__email__ = "luke@actuallyuseful.ai"

__all__ = [
    "ModelRegistry",
    "SmartRouter",
    "ToolDiscovery",
    "ModelCommunicator",
    "TaskManager",
    "tool_capabilities"
] 