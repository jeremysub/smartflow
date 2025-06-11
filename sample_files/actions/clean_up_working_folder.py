from typing import Dict
import logging
from smartflow.action_handler import ActionHandler
from smartflow.action_registry import register_action
from smartflow.utils.utilities import Utilities

@register_action("clean_up_working_folder")
class CleanUpWorkingFolderAction(ActionHandler):
    """Action handler for cleaning up artifacts after email processing"""
    
    def execute(self, context: Dict[str, str]) -> Dict[str, str]:

        action_context = {}

        # get working folder for this message
        working_folder = Utilities.get_message_storage_client(context["workflow.message_id"])

        try:
            working_folder.delete_folder()
        except Exception as e:
            logging.error(f"Error deleting working folder: {e}")
            action_context["error"] = str(e)
            action_context["result"] = "Error"
            return action_context

        action_context["result"] = "Success"
        
        return action_context