from smartflow.action_registry import register_action
from smartflow.action_handler import ActionHandler
from typing import Dict

@register_action("create_some_record")
class CreateSomeRecordAction(ActionHandler):
    """A simple action that simulates creating a record and returns the record id."""
    
    def execute(self, context: Dict[str, str] = None) -> Dict[str, str]:
        """Execute the hello world action."""
        
        action_context = {}
    
        # do some work here
        action_context["record_id"] = "1234567890"

        # add success indicator to the context
        action_context["result"] = "success"

        return action_context
