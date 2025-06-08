from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from datetime import datetime
from uuid import UUID

class WorkflowMessage(BaseModel):
    """
    Represents a message that needs to be processed through a workflow
    """
    message_id: UUID = Field(..., description="Unique identifier for this message")
    config_name: str = Field(..., description="The name/ID of the workflow config file to process this message with; found in workflow storage")
    parameters: Dict[str, str] = Field(default_factory=dict, description="The parameters for the workflow, if any")

class WorkflowMessageStatus(BaseModel):
    """
    Represents the status of a message that needs to be processed through a workflow
    """
    message_id: UUID = Field(..., description="Unique identifier for the message on which this status is based")
    status: str = Field(..., description="The status of the message appropriate for the current step in the workflow. Starts as 'Queued'. Could also be 'Error', 'Processing', 'Completed', etc.")
    display: Optional[str] = Field(None, description="The display message for the status. Used when needed in some user interface.")
    details: Optional[str] = Field(None, description="The details of the message. This would contain the error message if the status is 'Error'.")
    reference_id: Optional[str] = Field(None, description="Some referenceidentifier of the message (e.g. metadata about the thing we're processing - email subject, for instance)")
    last_updated: datetime = Field(..., description="The last updated date and time of the message")