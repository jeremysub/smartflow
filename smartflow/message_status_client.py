from azure.data.tables import TableClient, TableServiceClient
from azure.core.credentials import AzureNamedKeyCredential
import uuid
from datetime import datetime, timezone
import os
import logging
from uuid import UUID
from smartflow.models.messaging import WorkflowMessageStatus
from smartflow.const import Constants

class MessageStatusClient:
    """
    A helper class for interacting with Azure Table Storage.
    Provides functionality for managing message status records.
    """
    
    def __init__(self):
        """
        Initialize the Azure Table Storage client
        """
        self._connection_string = os.getenv(Constants.STORAGE_CONNECTION_STRING_ENV_VAR)
        
        if self._connection_string is None:
            raise ValueError(f"{Constants.STORAGE_CONNECTION_STRING_ENV_VAR} environment variable is not set")
        
        # Initialize Table Client
        self._table_client = TableClient.from_connection_string(self._connection_string, Constants.MESSAGE_STATUS_TABLE_NAME)

    def save_message_status(self, message_id: UUID, status: str, display: str = None, details: str = None, reference_id: str = None):
        """
        Save or update message status in Table Storage.
        
        Args:
            message_id: Unique identifier for the message
            status: Current status of the message
            details: Optional details of the message
            reference_id: Optional reference identifier for the message (e.g. metadata about the thing we're processing - email subject, for instance)
        """
        entity = {
            "PartitionKey": Constants.MESSAGE_STATUS_PARTITION_KEY,  # Simple fixed partition
            "RowKey": str(message_id),        # UUID as unique key
            "Status": status,
            "Display": display,
            "Details": details,
            "ReferenceId": reference_id,
            "LastUpdated": datetime.now(timezone.utc).isoformat()
        }

        # Upsert to insert or update the entity
        try:
            self._table_client.upsert_entity(entity)
            logging.info(f"Saved status for message {message_id}: {status}")
        except Exception as e:
            logging.error(f"Error saving status for message {message_id}: {str(e)}")
            raise

    def get_message_status(self, message_id: UUID) -> WorkflowMessageStatus:
        """
        Retrieve message status by UUID.
        
        Args:
            message_id: Unique identifier for the message
            
        Returns:
            WorkflowMessageStatus object containing message status details or None if not found
        """
        try:
            entity = self._table_client.get_entity(partition_key=Constants.MESSAGE_STATUS_PARTITION_KEY, row_key=str(message_id))
            # get status message from the entity (details may not be present)
            display = None
            if "Display" in entity:
                display = entity["Display"]

            details = None
            if "Details" in entity:
                details = entity["Details"]
            
            reference_id = None
            if "ReferenceId" in entity:
                reference_id = entity["ReferenceId"]

            status_msg = WorkflowMessageStatus(
                message_id=message_id,
                status=entity["Status"],
                display=display,
                details=details,
                reference_id=reference_id,
                last_updated=datetime.fromisoformat(entity["LastUpdated"])
            )
            logging.info(f"Retrieved status for message {message_id}: {status_msg.status}")
            return status_msg
        except Exception as e:
            logging.warning(f"Error retrieving message {message_id}: {str(e)}")
            return None


# Example usage
if __name__ == "__main__":
    
    from dotenv import load_dotenv
    
    load_dotenv()
    
    # Create a table storage client
    table_client = MessageStatusClient()
    
    # Generate a sample UUID
    sample_uuid = uuid.uuid4()
    
    # Save a successful message status
    table_client.save_message_status(sample_uuid, "Completed")
    
    # Save a failed message status with error details
    table_client.save_message_status(sample_uuid, "Failed", "Database connection timeout")
    
    # Retrieve and print status
    status = table_client.get_message_status(sample_uuid)
    if status:
        print(f"Retrieved status: {status}")