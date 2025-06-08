"""
SmartFlow: A workflow management system for processing actions via message queues.

A library for creating and executing workflow-based processing via message queues.
Clients can register custom actions, define workflows, and process messages.

Main components:
- ActionRegistry: Register and manage custom action handlers
- MessageProcessor: Process workflow messages through registered actions
- Workflow/Action models: Define workflow configurations
- WorkInitiator: Initiate work from a client
"""

# Core components for creating and registering actions
from .action_registry import ActionRegistry, register_action, default_registry
from .action_handler import ActionHandler

# Utilities
from .utils.utilities import Utilities

# Work initiation
from .work_initiator import WorkInitiator

# Message processing
from .message_processor import MessageProcessor

# For defining workflows and messages
from .models.workflow import Workflow, Action
from .models.messaging import WorkflowMessage, WorkflowMessageStatus

# Version information
from ._version import __version__

__all__ = [
    # Action creation and registration
    "ActionRegistry",
    "register_action",
    "default_registry",
    "get_action_handler",
    "ActionHandler",
    
    # Utilities
    "Utilities",
    
    # Message processing
    "MessageProcessor",
    
    # Models
    "Workflow",
    "Action",
    "WorkflowMessage",
    "WorkflowMessageStatus",
    
    # Work initiator
    "WorkInitiator",
]