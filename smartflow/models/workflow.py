from pydantic import BaseModel, Field
from typing import Dict, List, Optional

class Action(BaseModel):
    """
    Represents an action in a workflow
    """
    action_type: str = Field(..., description="The type of action to perform")
    name: Optional[str] = Field(None, description="The optional name of the action. If not provided, the action_type will be used.")
    display: Optional[str] = Field(None, description="The optional display message for the action. If not provided, the action_type will be used.")
    condition: Optional[str] = Field(None, description="The optional condition for the action. If provided, it must evaluate to true for the action to be executed. If not provided, the action will always be executed.")
    parameters: Optional[Dict[str, str]] = Field(None, description="Parameters for this action")

class Workflow(BaseModel):
    """
    Represents a sequence of actions to be performed
    """
    name: str = Field(..., description="Name of the workflow")
    description: Optional[str] = Field(None, description="Description of the workflow")
    actions: List[Action] = Field(default_factory=list, description="List of actions to perform in sequence")
    error_actions: Optional[List[Action]] = Field(None, description="List of actions to perform if an error occurs")
    parameters: Optional[Dict[str, str]] = Field(None, description="Global parameters for the workflow")
    success_details: Optional[str] = Field(None, description="The details return upon success of the workflow, which may include context values. e.g 'record_id={some_action.record_id}'")
