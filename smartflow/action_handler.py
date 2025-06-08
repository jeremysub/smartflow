from typing import Dict, List
import logging
import os

class ActionHandler:
    """Base class for all action handlers"""
    
    # Define action type that this handler processes
    action_type: str = None
    
    # define required environment variables for this action
    required_env_vars: List[str] = []
    
    # Define required input fields for this action
    required_fields: List[str] = []
    
    @classmethod
    def register(cls):
        """Register this action handler in the registry"""
        # Import here to avoid circular imports
        from action_registry import register_action_handler
        register_action_handler(cls)
    
    def validate_inputs(self, context: Dict[str, str]) -> None:
        """
        Validate that all required fields are present in the context
        
        Raises:
            ValueError: If any required fields are missing
        Args:
            context: The context to validate
        Returns:
            An updated context with the parameters added if they are not None
        """
        logging.info(f"Base ActionHandler.validate_inputs called by {type(self).__name__}")
        
        # validate that all required environment variables are present
        missing_env_vars = [env_var for env_var in self.required_env_vars if env_var not in os.environ]
        if missing_env_vars:
            # raise error (show env vars that are missing)
            raise ValueError(f"Missing required environment variables: {missing_env_vars}")
        
        # validate thae required fields are in the context        
        if context is None:
            context = {}

        # validate that all required fields are present
        missing_fields = [field for field in self.required_fields if field not in context]
        if missing_fields:
            # raise error (show fields that are missing)
            raise ValueError(f"Missing required fields: {missing_fields}")
        
        return
    
    def execute(self, context: Dict[str, str]) -> Dict[str, str]:
        """
        Execute the action with the given context
        Must be implemented by subclasses
        Returns its own context after execution
        
        Args:
            context: The current context containing all data
            
        Returns:
            This specific action handler's context after execution ("result" key is returned by convention)
        """
        raise NotImplementedError("Action handlers must implement execute method") 