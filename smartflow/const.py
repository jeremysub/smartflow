class Constants:
    
    # connection string env var names
    STORAGE_CONNECTION_STRING_ENV_VAR = "SMARTFLOW_STORAGE_CONNECTION_STRING"
    SERVICE_BUS_CONNECTION_STRING_ENV_VAR = "SMARTFLOW_SERVICE_BUS_CONNECTION_STRING"

    # storage container names
    WORKING_FOLDER = "working"
    WORKFLOW_FOLDER = "workflows"
        
    # table names
    MESSAGE_STATUS_TABLE_NAME = "MessageStatus"
    MESSAGE_STATUS_PARTITION_KEY = "Messages"