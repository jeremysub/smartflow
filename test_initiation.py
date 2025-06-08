import logging
import base64
from smartflow.work_initiator import WorkInitiator
import uuid

def main():
    """Test initiating work through smartflow."""
    logging.info("Testing work initiation")
    
    # Create a WorkInitiator instance
    message_id = uuid.uuid4()
    initiator = WorkInitiator(queue_name="work-queue", config_name="test-workflow", message_id=message_id, reference_id="test-reference-id")
    
    # add context to the message
    initiator.add_context("key1", "value1")
    initiator.add_context("key2", "value2")
    
    print(initiator.get_message())
    
    # add a file to the message (get local file and base64 encode it)
    with open("test.txt", "rb") as file:
        file_content = file.read()
        base64_content = base64.b64encode(file_content).decode("utf-8")
        initiator.add_file("test.txt", base64_content)

    print(initiator.get_message())
    
    print(initiator.get_status())
    
    # Initiate the work
    message_id = initiator.enqueue_work()
    
    # check status of the message
    print(initiator.get_status())
    
    logging.info(f"work initiated for message ID: {message_id}")
    
if __name__ == "__main__":
    
    from dotenv import load_dotenv
    
    load_dotenv()
    
    main()
