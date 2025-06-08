import os
from azure.servicebus import ServiceBusClient, ServiceBusMessage
from smartflow.const import Constants

class QueueClient:
    """
    A client for sending and receiving messages from a Service Bus queue.
    """
    def __init__(self, queue_name: str):
        self.queue_name = queue_name
        connection_string = os.getenv(Constants.SERVICE_BUS_CONNECTION_STRING_ENV_VAR)
        if not connection_string:
            raise ValueError(f"Missing connection string in environment variable: {Constants.SERVICE_BUS_CONNECTION_STRING_ENV_VAR}")
        
        self.client = ServiceBusClient.from_connection_string(connection_string)
        self._receiver = None
        
    def __del__(self):
        """Cleanup resources when object is destroyed"""
        self.close()
        
    def close(self):
        """Close the client and receiver connections"""
        if self._receiver:
            self._receiver.close()
            self._receiver = None
        
    def send_message(self, message_body: str):
        """Send a message to the queue"""
        with self.client:
            sender = self.client.get_queue_sender(queue_name=self.queue_name)
            with sender:
                message = ServiceBusMessage(message_body)
                sender.send_messages(message)
    
    def _get_receiver(self):
        """Get or create a receiver"""
        if not self._receiver:
            self._receiver = self.client.get_queue_receiver(queue_name=self.queue_name)
        return self._receiver
    
    def receive_message(self, process_message_callback, timeout=5):
        """
        Receives a single message from the queue and processes it using the provided callback.
        After processing, it completes (removes) the message from the queue.
        
        Args:
            process_message_callback: A function that takes a message body (str) as an argument
            timeout: Time to wait for a message in seconds (default: 5 seconds)
        
        Returns:
            True if a message was received and processed, False otherwise
        """
        try:
            receiver = self._get_receiver()
            
            # Receive just one message with timeout
            received_msgs = receiver.receive_messages(max_message_count=1, max_wait_time=timeout)
            
            # Check if we received any messages
            if not received_msgs:
                return False
            
            for msg in received_msgs:
                try:
                    # Get the message content
                    message_body = next(msg.body) if hasattr(msg.body, '__iter__') else msg.body
                    
                    # If bytes, decode to string
                    if isinstance(message_body, bytes):
                        message_body = message_body.decode('utf-8')
                    
                    # Process the message with the callback
                    process_message_callback(message_body)
                    
                    # Complete the message (remove it from the queue)
                    receiver.complete_message(msg)
                    
                    # Return success
                    return True
                except Exception as e:
                    print(f"Error processing message: {str(e)}")
                    # Still mark the message as complete to avoid poison messages
                    receiver.complete_message(msg)
                    return False
            
            # If we get here but had messages, it means they weren't processed
            return False
                
        except Exception as e:
            print(f"Error receiving message: {str(e)}")
            # Close and reset the receiver on errors
            self.close()
            return False
    
    