import logging
import uuid
from smartflow.message_processor import MessageProcessor
from smartflow.models.messaging import WorkflowMessage
from smartflow.models.workflow import Workflow, Action

# Make sure our hello world action is registered
from sample_files.actions.hello_world_action import HelloWorldAction
from sample_files.actions.create_some_record import CreateSomeRecordAction
from sample_files.actions.dummy import DummyAction
from sample_files.actions.dummy_with_exception import DummyWithExceptionAction
from sample_files.actions.clean_up_working_folder import CleanUpWorkingFolderAction
from sample_files.actions.create_some_file import CreateSomeFileAction
from sample_files.actions.save_context import SaveContextAction

def main():
    
    """Test processing messages directly through the MessageProcessor."""
    logging.info("Testing message processing")
    
    # build testing workflow rather than retrieving from blob storage
    workflow = Workflow(
        name="Test Workflow",
        description="A test workflow",
        success_details="record_id={Create_Some_Record.record_id}",
        actions=[
            Action(
                action_type="create_some_file",
                name="Create Some File",
                display="Creating a file..."
            ),
            Action(
                action_type="create_some_record",
                name="Create Some Record",
                display="Creating a record..."
            ),
            Action(
                action_type="hello_world",
                name="Hello World 1",
                parameters={"user_name": "Bob {Create_Some_Record.record_id}"},
                display="Running hello world with parameter..."
            ),
            Action(
                action_type="hello_world",
                name="Hello World 2",
                parameters={"user_name": "Alice"},
                display="Running hello world..."
            ),
            Action(
                action_type="hello_world",
                name="Hello World 3",
                parameters={"user_name": "Charlie"},
                display="Running hello world..."
            ),
            Action(
                action_type="save_context",
                name="Save Context",
                display="Saving context..."
            ),
            Action(
                action_type="dummy",
                name="Dummy",
                display="Running dummy..."
            ),
            Action(
                action_type="clean_up_working_folder",
                name="Clean Up Working Folder",
                display="Cleaning up working folder..."
            )
        ],
        error_actions=[
            Action(
                action_type="dummy",
                name="Dummy",
                display="Running dummy action..."
            )
        ]
    )

    # Create a MessageProcessor instance with the provided workflow (for testing)
    processor = MessageProcessor(workflow)
    # processor = MessageProcessor()
    
    # Create a test message
    message = WorkflowMessage(
        message_id=str(uuid.uuid4()),
        config_name="dummy_workflow",
        parameters={"my_wf_param": "Some workflow parameter value"}
    )

    # Process the message
    resulting_context = processor.process_message(message)
    
    # print the result
    print(resulting_context)

if __name__ == "__main__":
    
    from dotenv import load_dotenv
    
    load_dotenv()
    
    main()
