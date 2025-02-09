from google.cloud import storage
from typing import List, Optional
import os
from pathlib import Path

class StorageClient:
    def __init__(self, bucket_name: str):
        self.client = storage.Client()
        self.bucket = self.client.bucket(bucket_name)

    def upload_file(self, source_file_path: str, destination_blob_name: Optional[str] = None) -> str:
        """Upload a file to Cloud Storage bucket."""
        if destination_blob_name is None:
            destination_blob_name = Path(source_file_path).name
        
        blob = self.bucket.blob(destination_blob_name)
        blob.upload_from_filename(source_file_path)
        return destination_blob_name

    def download_file(self, source_blob_name: str, destination_file_path: str) -> None:
        """Download a file from Cloud Storage bucket."""
        blob = self.bucket.blob(source_blob_name)
        os.makedirs(os.path.dirname(destination_file_path), exist_ok=True)
        blob.download_to_filename(destination_file_path)

    def list_files(self, prefix: Optional[str] = None) -> List[str]:
        """List all files in the bucket with optional prefix."""
        blobs = self.client.list_blobs(self.bucket, prefix=prefix)
        return [blob.name for blob in blobs]

    def read_file(self, blob_name: str) -> str:
        """Read file content from Cloud Storage."""
        blob = self.bucket.blob(blob_name)
        return blob.download_as_text()

    def file_exists(self, blob_name: str) -> bool:
        """Check if a file exists in the bucket."""
        blob = self.bucket.blob(blob_name)
        return blob.exists() 