import os
from typing import List, Dict, Any
import logging
from azure.storage.blob import BlobServiceClient
from azure.core.exceptions import ResourceExistsError, ResourceNotFoundError
from smartflow.const import Constants

class BlobStorageClient:
    """
    A helper class for interacting with Azure Blob Storage.
    Provides functionality for creating folders, listing files, uploading, downloading,
    and deleting operations.
    """

    def __init__(self, container_name: str, folder_path: str = None):
        """
        Initialize the Azure Blob Storage client
        """
        self._container_name = container_name
        
        self._folder_path = ""
        if folder_path:
            if not str(folder_path).endswith('/'):
                self._folder_path = f"{folder_path}/"
            else:
                self._folder_path = folder_path
        
        # Initialize clients directly
        _blob_service_client = BlobServiceClient.from_connection_string(os.getenv(Constants.STORAGE_CONNECTION_STRING_ENV_VAR))
        self._container_client = _blob_service_client.get_container_client(self._container_name)

    def create_folder(self) -> bool:
        """
        Create a virtual "folder" in Azure Blob Storage.
        
        In Azure Storage, folders are virtual and represented by prefixes in blob names.
        This method creates an empty blob with the folder name as a prefix to establish a folder structure.
        
        Args:
            folder_path: The folder path to create (e.g., "emails/12345")
            
        Returns:
            True if the folder was created, False otherwise
        """
        try:
            # Create an empty blob with the folder name to establish the folder
            blob_client = self._container_client.get_blob_client(self._folder_path)
            blob_client.upload_blob(data="", overwrite=True)
            logging.info(f"Created folder: {self._folder_path} in container {self._container_name}")
            return True
        except ResourceExistsError:
            # Folder already exists
            logging.info(f"Folder {self._folder_path} already exists in container {self._container_name}")
            return True
        except Exception as e:
            logging.error(f"Error creating folder {self._folder_path}: {str(e)}")
            return False
    
    def list_files(self) -> List[Dict[str, Any]]:
        """
        List all files in a folder.
        
        Args:
            folder_path: The folder path to list files from
            
        Returns:
            A list of dictionaries containing file information
        """
        try:                
            # List blobs with the folder prefix
            blobs = self._container_client.list_blobs(name_starts_with=self._folder_path)
            
            result = []
            for blob in blobs:
                # Skip the folder marker itself (empty blob with just the folder name)
                if blob.name == self._folder_path:
                    continue
                    
                result.append({
                    "name": blob.name,
                    "filename": os.path.basename(blob.name),
                    "size": blob.size,
                    "created_at": blob.creation_time,
                    "modified_at": blob.last_modified,
                    "content_type": blob.content_settings.content_type,
                })
            
            return result
        except Exception as e:
            logging.error(f"Error listing files in folder {self._folder_path}: {str(e)}")
            return []
    
    def upload_file(self, file_name: str, content: bytes):
        """
        Upload a file to blob storage
        
        Args:
            file_name: Name of the file to upload
            content: The base64 encoded content to upload
        """
                
        try:
            blob_client = self._container_client.get_blob_client(f"{self._folder_path}{file_name}")
            blob_client.upload_blob(content, overwrite=True)
            logging.info(f"Successfully uploaded blob to {self._folder_path}{file_name}")
        except Exception as e:
            logging.error(f"Error uploading blob to {self._folder_path}{file_name}: {str(e)}")
            raise
    
    def download_file(self, file_name: str) -> bytes:
        """
        Download a file from blob storage
        
        Args:
            blob_path: Path to the blob within the container
            
        Returns:
            The file content as a bytes object
        """

        try:
            blob_client = self._container_client.get_blob_client(f"{self._folder_path}{file_name}")
            blob_data = blob_client.download_blob()
            return blob_data.readall()
        except ResourceNotFoundError:
            logging.warning(f"Blob not found: {self._folder_path}{file_name}")
            return None
        except Exception as e:
            logging.error(f"Error downloading blob {self._folder_path}{file_name}: {str(e)}")
            raise
    
    def delete_file(self, file_name: str) -> bool:
        """
        Delete a file from Azure Blob Storage.
        
        Args:
            file_name: The name of the file to delete
            
        Returns:
            True if the file was deleted successfully, False otherwise
        """
        try:
            blob_client = self._container_client.get_blob_client(f"{self._folder_path}{file_name}")
            
            blob_client.delete_blob()
            logging.info(f"Deleted file {self._folder_path}{file_name} from container {self._container_name}")
            return True
        except ResourceNotFoundError:
            logging.warning(f"File {self._folder_path}{file_name} not found for deletion")
            return False
        except Exception as e:
            logging.error(f"Error deleting file {self._folder_path}{file_name}: {str(e)}")
            return False
    
    def delete_folder(self) -> bool:
        """
        Delete a folder and all its contents from Azure Blob Storage.
        
        Args:
            folder_path: The folder path to delete
            
        Returns:
            True if the folder was deleted successfully, False otherwise
        """
        try:
            # List all blobs in the folder
            blobs = self._container_client.list_blobs(name_starts_with=self._folder_path)
            
            # Delete each blob
            deleted_count = 0
            for blob in blobs:
                self._container_client.delete_blob(blob.name)
                deleted_count += 1
                
            logging.info(f"Deleted folder {self._folder_path} with {deleted_count} files from container {self._container_name}")
            return True
        except Exception as e:
            logging.error(f"Error deleting folder {self._folder_path}: {str(e)}")
            return False
