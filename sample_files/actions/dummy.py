from smartflow import ActionHandler, register_action
from typing import Dict
import logging

@register_action("dummy")
class DummyAction(ActionHandler):
    """
    Dummy action that does nothing
    
    Output Context:
        action_result: "success" or "error"
    """
    
    def execute(self, context: Dict[str, str]) -> Dict[str, str]:
        
        action_context = {}

        logging.info("Dummy action executed")

        action_context["result"] = "Success"
        
        return action_context