from smartflow import ActionHandler, register_action
from typing import Dict
import logging

@register_action("dummy_ret_global")
class DummyRetGlobalAction(ActionHandler):
    """
    Dummy action that does nothing
    
    Output Context:
        action_result: "success" or "error"
    """
    
    def execute(self, context: Dict[str, str]) -> Dict[str, str]:
        
        action_context = {}

        logging.info("Dummy action executed - returning global value")

        # return a global value to workflow -- will replace the workflow parameter value of same name
        action_context["workflow.wf_param_set_in_action"] = "A new value from action"
        action_context["workflow.wf_param_set_in_definition"] = "A new value from definition - replaces action value"

        action_context["result"] = "success"
        
        return action_context