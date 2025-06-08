import uuid
from typing import Dict
from .models.messaging import WorkflowMessage, WorkflowMessageStatus
from .utils.queue_client import QueueClient
from .utils.utilities import Utilities
from .message_status_client import MessageStatusClient

class WorkInitiator():
    """
    This class is used for building up and enqueuing a workflow message.
    """
    def __init__(self, queue_name: str, config_name: str, message_id: uuid.UUID = None, reference_id: str = None):
        """
        Initializes the WorkInitiator with a queue name and workflow name.
        
        Args:
            queue_name: The name of the queue to enqueue the message to.
            config_name: The name of the workflow config to use for the message.
            message_id: The ID of the message to use for the message. Can be explicitly set for processing across separate workflows.
            reference_id: Optional reference identifier for the message (e.g. metadata about the thing we're processing - email subject, for instance)
        """
        
        # verify the environment variables are set
        Utilities.verify_settings()
        
        # generate a new message id if not provided
        message_id = message_id or uuid.uuid4()
        
        # create the workflow message that will be enqueued
        self._message = WorkflowMessage(
            message_id=message_id,
            config_name=config_name,
            parameters={})
        
        self._reference_id = reference_id

        self._queue_client = QueueClient(queue_name=queue_name)
        
        self._status_client = MessageStatusClient()
        
        # set the status to Started
        self._status_client.save_message_status(self._message.message_id, "Started", reference_id=self._reference_id)

    def add_context(self, key: str, value: str) -> None:
        """
        Adds context variables to the message.
        
        Args:
            context: A dictionary of context variables to add to the message context collection.
        """
            
        # update the context with the new variables
        self._message.parameters[key] = value
            
    def get_message(self) -> WorkflowMessage:
        """
        Returns the message that will be enqueued.
        
        Returns:
            The message that will be enqueued.
        """
        return self._message
        
    def add_file(self, file_name: str, file_content: str) -> None:
        """
        Adds a file to the working folder associated with the message.
        
        Args:
            file_name: The name of the file to add.
            file_content: The base64 encoded content of the file to add.
            
        Returns:
            The file path relative to the working folder.
        """
        # create message working folder
        message_folder = Utilities.get_message_storage_client(self._message.message_id)
        
        # add the file to the working folder
        message_folder.upload_file(file_name, file_content)
        
    def enqueue_work(self) -> uuid.UUID:
        """
        Enqueues the message for processing.
        """
        # serialize the message
        message_body = self._message.model_dump_json()
        
        # send the message to the queue
        self._queue_client.send_message(message_body)
        
        # update the message status to enqueued
        self._status_client.save_message_status(self._message.message_id, "Queued", reference_id=self._reference_id)

        return self._message.message_id
    
    def set_status(self, status: str, details: str = None) -> None:
        """
        Sets the status of the message.
        """
        self._status_client.save_message_status(self._message.message_id, status, details=details)
        
    def get_status(self) -> WorkflowMessageStatus:
        """
        Returns the status of the message.
        """
        status = self._status_client.get_message_status(self._message.message_id)
        
        return status