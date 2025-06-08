from typing import Dict
import logging
from smartflow.action_handler import ActionHandler
from smartflow.action_registry import register_action
from smartflow.utils.utilities import Utilities

@register_action("create_some_file")
class CreateSomeFileAction(ActionHandler):
    """Action handler for creating a dummy file in the working folder"""
    
    def execute(self, context: Dict[str, str]) -> Dict[str, str]:

        action_context = {}

        # get working folder for this message
        message_folder = Utilities.get_message_storage_client(context["workflow.message_id"])

        try:
            message_folder.upload_file("test.txt", "Hello, world!")
        except Exception as e:
            logging.error(f"Error creating file in working folder: {e}")
            action_context["error"] = str(e)
            action_context["result"] = "error"
            return action_context

        action_context["result"] = "success"
        
        return action_context