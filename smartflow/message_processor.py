import logging
import json
from typing import Dict
from .models.workflow import Workflow, Action
from .models.messaging import WorkflowMessage
from .utils.utilities import Utilities
from .utils.blob_storage import BlobStorageClient
from .message_status_client import MessageStatusClient
from .action_registry import default_registry
from .const import Constants

class MessageProcessor:
    """
    Processes workflow messages by loading workflow configurations and executing
    the workflow and associated actions.
    """
    
    def __init__(self, workflow: Workflow = None):
        """
        Initialize the MessageProcessor with necessary clients.
        
        Args:
            workflow: The workflow to use for the message processor. In case we want to load locally for testing.
        """
        Utilities.verify_settings()
        self._status_client = MessageStatusClient()
        self._blob_client = BlobStorageClient(Constants.WORKFLOW_FOLDER)
        self._workflow = workflow
    
    def process_message(self, workflow_message: WorkflowMessage) -> Dict[str, str]:
        """
        Processes a workflow message by loading the workflow config and executing the workflow 
        and associated actions. Logs errors in the associated status table. 
        Attempts to execute the error workflow if the main workflow fails.
        
        Args:
            workflow_message: The workflow message to process (i.e. received from a queue)
            
        Returns:
            Dict[str, str]: The final context after workflow execution
        """
        
        logging.info(f"Processing workflow message in smartflow: {workflow_message.message_id}")
        # update status to processing
        self._status_client.save_message_status(workflow_message.message_id, "Processing")
        
        # build context to be used through the workflow
        context: Dict[str, str] = {}
        
        # Add message metadata
        context["workflow.message_id"] = str(workflow_message.message_id)
        context["workflow.config_name"] = workflow_message.config_name
        context["workflow.result"] = "Processing"
        
        # if the workflow is not provided, load it from blob storage
        if self._workflow is None:
            logging.info(f"Loading workflow config '{workflow_message.config_name}'")
            
            self._workflow = Utilities.load_workflow_config(workflow_message.config_name)
            
            if (self._workflow is None):

                err = f"Missing or malformed workflow config '{workflow_message.config_name}'."
                logging.error(err)
                self._status_client.save_message_status(workflow_message.message_id, "Error", err)
                context["workflow.result"] = "Error"
                return context
        else:
            logging.info(f"Using provided workflow '{self._workflow.name}'")
        
        # set workflow name
        context["workflow.name"] = self._workflow.name
        
        # Add workflow parameters, but with "workflow." prefix (if any)
        if workflow_message.parameters:
            context.update({f"workflow.{key}": value for key, value in workflow_message.parameters.items()})
        
        # try to execute the workflow, on failure, try to execute error workflow
        try:
            logging.info(f"Executing workflow: {self._workflow.name}")
            
            # execute the workflow
            context = self._execute_workflow(self._workflow, context)
            
            # if workflow.result is error, raise an error, triggering error workflow
            if context["workflow.result"].lower() == "error":
                raise
            
            # update status to success (optionally include success details)
            if self._workflow.success_details:
                self._status_client.save_message_status(workflow_message.message_id, "Success", display=None, details=Utilities.replace_placeholders(self._workflow.success_details, context))
            else:
                self._status_client.save_message_status(workflow_message.message_id, "Success", display=None, details=None)
            
            # return the context
            context["workflow.result"] = "Success"
            return context
        
        except Exception as e:
            err = f"Workflow execution failed for '{self._workflow.name}'. Last action was '{context['workflow.last_action']}'."
            logging.error(err)
            #set status to error
            self._status_client.save_message_status(workflow_message.message_id, "Error", err)
            
            # save error details to working folder
            message_folder = Utilities.get_message_storage_client(workflow_message.message_id)
            error_json = {
                "error": str(e),
                "workflow": self._workflow.name,
                "config_name": workflow_message.config_name,
                "context": context
            }
            error_json_bytes = json.dumps(error_json).encode("utf-8")
            message_folder.upload_file("error.json", error_json_bytes)
            
        # return the context
        return context

    def _execute_workflow(self, workflow: Workflow, context: Dict[str, str]) -> Dict[str, str]:
        """
        Executes actions and updates context each time; context is chained through each action. If 
        an action fails, the workflow.result is set to error and no further actions are executed.
        
        Args:
            workflow: The workflow to execute
            context: The initial context
            
        Returns:
            Dict: The final context after workflow execution
        """
        
        logging.info(f"Executing workflow: {workflow.name} with {len(workflow.actions)} actions.")
        
        is_error = False
        
        # execute each action and add results to the context
        for action in workflow.actions:
            action_name = action.name if action.name else action.action_type
            action_prefix = action_name.replace(" ", "_")
            action_display = action.display if action.display else f"Executing {action_name}..."
            logging.info(f"Executing action: {action_name} ({action.action_type})")
            
            # update status to executing
            # detail parameter may be used for user display purposes
            self._status_client.save_message_status(context["workflow.message_id"], f"Executing: {action_name}", action_display)

            # execute action
            action_context = {}
            try:
                # set workflow.last_action to the action name
                context["workflow.last_action"] = action_name
                
                action_context = self._execute_action(action, context)
                
                # error can be gracefully handled by the action handler, so we need to check for it
                is_error = action_context["result"] and action_context["result"].lower() == "error"
                
            except Exception as e:
                # error can also be raised by the action handler, so we need to check for it as well
                logging.error(f"Action execution failed: {e}")
                action_context = {"result": "Error", "error": str(e)}
                is_error = True            
            
            # prefix each key in the action context with the action name (using dot notation)
            action_context = {f"{action_prefix}.{key}": value for key, value in action_context.items()}
            context.update(action_context)
            
            # if the last action result in error, stop execution of actions
            if is_error:
                context["workflow.result"] = "Error"
                break
            
        # if an error occurred, execute the error actions
        if is_error and workflow.error_actions:
            logging.info(f"Executing {len(workflow.error_actions)} error actions...")
            for error_action in workflow.error_actions:
                logging.info(f"Executing error action: {error_action.name} ({error_action.action_type})")
                
                # execute error action
                try:
                    self._execute_action(error_action, context)
                except Exception as e:
                    logging.error(f"Error executing error action '{error_action.name}': {e}")
                    break
        
        return context

    def _execute_action(self, action: Action, context: Dict[str, str]):
        """
        Loads and executes an action handler with the given context
        
        Args:
            action: The action to execute
            context: The context to execute the action with
            
        Returns:
            Dict: The updated context with the action result
        """
        
        logging.info(f"Executing action: {action.name} ({action.action_type})")
        
        # load action handler class
        action_handler_class = default_registry.get_handler(action.action_type)
        if action_handler_class is None:
            # raise error
            raise ValueError(f"Action handler not found for action: {action.action_type}")

        # instantiate the handler class
        action_handler = action_handler_class()
        
        # replace placeholders in the action parameters
        action_parameters = {}
        if action.parameters is not None:
            # loop through action parameters and replace placeholders
            for key, value in action.parameters.items():
                action_parameters[key] = Utilities.replace_placeholders(value, context)
        
        # combine context and action parameters
        action_input_context = {**context, **action_parameters}

        # validate inputs
        action_handler.validate_inputs(action_input_context)

        # execute action handler
        action_output_context = action_handler.execute(action_input_context)
        
        # if no result key found assume success
        if "result" not in action_output_context:
            action_output_context["result"] = "Success"
        else:
            # if not successful, log error and return
            if action_output_context["result"].lower() != "success":
                logging.error(f"Action handler {action_handler.__class__.__name__} execution failed")
        
        # return updated context
        return action_output_context