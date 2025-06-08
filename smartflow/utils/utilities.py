import os
import re
import logging
import uuid
from typing import Optional, Dict
from ..models.workflow import Workflow
from .blob_storage import BlobStorageClient
from ..const import Constants

class Utilities:
    @staticmethod
    def get_message_storage_client(message_id: uuid.UUID) -> BlobStorageClient:
        """
        Returns a blob storage client for the working folder and message id as the folder path.
        """
        blob_client = BlobStorageClient(Constants.WORKING_FOLDER, message_id)
        return blob_client
    
    @staticmethod
    def replace_placeholders(text: str, context: Dict[str, str]) -> str:
        """
        Replaces placeholders in the text with the values from the context
        
        Placholders are expressed as {key} in the text and can appear multiple times, for multiple keys.
        
        Args:
            text: The text to replace placeholders in
            context: The context to use to replace placeholders
            
        Returns:
            The text with placeholders replaced
        """
        
        if text is None:
            return None
            
        # get all placholders found in the text
        placeholders = re.findall(r"\{([^{}]+)\}", text)

        # replace placeholders in the text with the values from the context
        for placeholder in placeholders:
            if placeholder in context:
                text = text.replace(f"{{{placeholder}}}", str(context[placeholder]))
            else:
                logging.warning(f"Placeholder '{placeholder}' not found in context")

        return text
    
    @staticmethod
    def verify_settings():
        """
        Verifies that the required environment variables are set.
        """
        if not os.getenv(Constants.STORAGE_CONNECTION_STRING_ENV_VAR):
            raise ValueError(f"{Constants.STORAGE_CONNECTION_STRING_ENV_VAR} is not set")
        if not os.getenv(Constants.SERVICE_BUS_CONNECTION_STRING_ENV_VAR):
            raise ValueError(f"{Constants.SERVICE_BUS_CONNECTION_STRING_ENV_VAR} is not set")

    @staticmethod
    def load_workflow_config(workflow_config_name: str) -> Optional[Workflow]:
        """
        Loads a workflow configuration for a given route name from blob storage. Each route has its own configuration file.
        
        Args:
            workflow_config_name (str): The name of the workflow to load the configuration for
            
        Returns:
            Configuration: The configuration for the given route name
        """

        # get the config from blob storage
        blob_client = BlobStorageClient(Constants.WORKFLOW_FOLDER)
        
        # add .json to the end of the config name if it's not there
        if not workflow_config_name.endswith(".json"):
            workflow_config_name = f"{workflow_config_name}.json"
        
        # if config doesn't exist, return None, if mal-formed, raise error
        config_json = blob_client.download_file(workflow_config_name)
        # deserialize the config
        config = Workflow.model_validate_json(config_json)
        return config
