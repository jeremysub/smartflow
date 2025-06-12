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
        Keys are matched case-insensitively.
        
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

        # Create a case-insensitive context dictionary
        context_lower = {k.lower(): v for k, v in context.items()}

        # replace placeholders in the text with the values from the context
        for placeholder in placeholders:
            placeholder_lower = placeholder.lower()
            if placeholder_lower in context_lower:
                text = text.replace(f"{{{placeholder}}}", str(context_lower[placeholder_lower]))
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
        
        try:
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
        except Exception as e:
            logging.error(f"Error loading workflow config '{workflow_config_name}': {e}")
            return None

    @staticmethod
    def evaluate_condition(condition: str, context: Dict[str, str]) -> bool:
        """
        Evaluates a condition string against a context dictionary.
        Examples of conditions:
        - "workflow.some_param == 'value'" - true if the value is equal to 'value'
        - "workflow.some_param != 'value'" - true if the value is not equal to 'value'
        - "workflow.some_param > 10" - true if the numeric value is greater than 10
        - "workflow.some_param < 10" - true if the numeric value is less than 10
        - "workflow.some_param >= 10" - true if the numeric value is greater than or equal to 10
        - "workflow.some_param <= 10" - true if the numeric value is less than or equal to 10
        - "workflow.some_param is not None" - true if the value is not None
        - "My_Action.result == 'success'" - true if the action result is equal to 'success'
        - "My_Action.result != 'success'" - true if the action result is not equal to 'success'
        - "My_Action.result is not None" - true if the action result is not None
        - "My_Action.result is None" - true if the action result is None
        
        Comparisons to strings are case-insensitive.
        And conditions are supported.
        Or conditions are supported.
        Parentheses are not supported.
        Key matching in context is case-insensitive.
        
        Invalid conditions will return False.
        
        Args:
            condition: The condition to evaluate
            context: The context to use to evaluate the condition
            
        Returns:
            True if the condition is met, False otherwise
        """
        if not condition:
            return True

        try:
            # Create a case-insensitive context dictionary
            context_lower = {k.lower(): v for k, v in context.items()}

            # Split the condition into parts if it contains 'or'
            if ' or ' in condition:
                parts = condition.split(' or ')
                if not all(part.strip() for part in parts):  # Check for empty parts
                    return False
                return any(Utilities.evaluate_condition(part.strip(), context) for part in parts)

            # Split the condition into parts if it contains 'and'
            if ' and ' in condition:
                parts = condition.split(' and ')
                if not all(part.strip() for part in parts):  # Check for empty parts
                    return False
                return all(Utilities.evaluate_condition(part.strip(), context) for part in parts)

            # Handle 'is None' and 'is not None' checks
            if ' is None' in condition:
                key = condition.split(' is None')[0].strip()
                if not key:  # Empty key
                    return False
                return key.lower() not in context_lower or context_lower[key.lower()] is None
            if ' is not None' in condition:
                key = condition.split(' is not None')[0].strip()
                if not key:  # Empty key
                    return False
                return key.lower() in context_lower and context_lower[key.lower()] is not None

            # Handle comparison operators
            operators = ['==', '!=', '>=', '<=', '>', '<']
            for op in operators:
                if f' {op} ' in condition:
                    parts = condition.split(f' {op} ')
                    if len(parts) != 2:  # Must have exactly two parts
                        return False
                    left, right = parts
                    left = left.strip()
                    right = right.strip()
                    
                    if not left or not right:  # Empty left or right side
                        return False

                    # Get the value from context using case-insensitive key
                    if left.lower() not in context_lower:
                        return False
                    left_value = context_lower[left.lower()]

                    # Handle string values (remove quotes)
                    if right.startswith("'") and right.endswith("'"):
                        right = right[1:-1]
                    elif right.startswith('"') and right.endswith('"'):
                        right = right[1:-1]
                    elif not right.isdigit():  # Only require quotes for non-numeric values
                        return False  # String values must be quoted

                    # Try to convert to number if possible
                    try:
                        if isinstance(left_value, str) and left_value.isdigit():
                            left_value = int(left_value)
                        if isinstance(right, str) and right.isdigit():
                            right = int(right)
                    except ValueError:
                        pass

                    # For string comparisons, convert both sides to lowercase
                    if isinstance(left_value, str) and isinstance(right, str):
                        left_value = left_value.lower()
                        right = right.lower()

                    # Evaluate the comparison
                    if op == '==':
                        return left_value == right
                    elif op == '!=':
                        return left_value != right
                    elif op == '>=':
                        return left_value >= right
                    elif op == '<=':
                        return left_value <= right
                    elif op == '>':
                        return left_value > right
                    elif op == '<':
                        return left_value < right

            return False  # No valid operator found
        except Exception:
            return False  # Any other error returns False
