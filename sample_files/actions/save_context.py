from typing import Dict
import logging
import json

from smartflow.action_handler import ActionHandler
from smartflow.action_registry import register_action
from smartflow.utils.utilities import Utilities

@register_action("save_context")
class SaveContextAction(ActionHandler):
    """
    Saves the context to a file in the working folder

    Output Context:
        result: "success" or "error"
        error: (optional) The error message if the action fails.
    """
    
    def execute(self, context: Dict[str, str]) -> Dict[str, str]:
        
        action_context = {}

        # get working folder for this message
        working_folder = Utilities.get_message_storage_client(context["workflow.message_id"])

        # get the context as a JSON string
        context_data = json.dumps(context)
        
        # save the context to a file in the working folder
        try:
            working_folder.upload_file("context.json", context_data)
            action_context["result"] = "Success"
            
        except Exception as e:
            logging.error(f"Error saving context to blob storage: {e}")
            action_context["result"] = "Error"
            action_context["error"] = str(e)

        # return the context
        return action_context
