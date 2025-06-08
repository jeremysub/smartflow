from typing import Dict, Type, Optional, Any, Callable, TypeVar
from .action_handler import ActionHandler
import logging

# Define a type variable for the ActionHandler class
T = TypeVar('T', bound=ActionHandler)

class ActionRegistry:
    """
    Registry for action handlers that can be referenced in workflows.
    """
    
    def __init__(self):
        """
        Initialize a new action registry.
        """
        self._action_registry: Dict[str, Type[T]] = {}
    
    def register(self, action_type: str, handler_class: Type[T]) -> Type[T]:
        """
        Register an action handler class in the registry
        
        Args:
            action_type: The type of action this handler handles
            handler_class: The action handler class to register
            
        Returns:
            The handler class (to allow use as a decorator)
        """
        self._action_registry[action_type] = handler_class
        logging.info(f"Registered action handler for '{action_type}'")
        
        # Return the class to support decorator pattern
        return handler_class
    
    def get_handler(self, action_type: str) -> Optional[Type[T]]:
        """
        Get the handler class for a specific action type
        
        Args:
            action_type: The type of action to get the handler for
        
        Returns:
            The handler class, or None if not found
        """
        return self._action_registry.get(action_type)

# Create a default registry instance
default_registry = ActionRegistry()

# Decorator for registering action handlers with the default registry
def register_action(action_type: str):
    """
    Decorator for registering action handlers with the default registry.
    
    Args:
        action_type: The type of action this handler handles.
    
    Example:
        @register_action("my_action")
        class MyActionHandler(ActionHandler):
            def execute(self, context):
                # Implement action logic
                return context
    """
    def decorator(cls: Type[T]) -> Type[T]:
        # Set the action_type on the class for reference
        cls.action_type = action_type
        # Register with the action_type
        return default_registry.register(action_type, cls)
    
    return decorator
