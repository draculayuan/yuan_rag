import os
from dotenv import load_dotenv
from storage import StorageClient
from pubsub import PubSubClient
from processor import DocumentProcessor
from vector_store import VectorSearchManager
import json
import logging
from typing import Dict, Any

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataIngestionPipeline:
    def __init__(self):
        # Load configuration
        self.project_id = os.getenv("PROJECT_ID")
        self.region = os.getenv("REGION")
        self.bucket_name = os.getenv("BUCKET_NAME")
        self.topic_name = os.getenv("PUBSUB_TOPIC")
        self.subscription_name = os.getenv("PUBSUB_SUBSCRIPTION")
        
        # Initialize components
        self.storage = StorageClient(self.bucket_name)
        self.pubsub = PubSubClient(self.project_id, self.topic_name)
        self.processor = DocumentProcessor(
            project_id=self.project_id,
            location=self.region,
            embedding_model=os.getenv("VERTEX_EMBEDDING_MODEL"),
            chunk_size=int(os.getenv("CHUNK_SIZE", "500")),
            chunk_overlap=int(os.getenv("CHUNK_OVERLAP", "50")),
        )
        self.vector_store = VectorSearchManager(
            project_id=self.project_id,
            location=self.region,
            index_id=os.getenv("VECTOR_SEARCH_INDEX_ID"),
        )
        
        # Ensure vector index exists
        self.vector_store.get_or_create_index()

    def process_document(self, message_data: Dict[str, Any]):
        """Process a document when notified via Pub/Sub."""
        try:
            blob_name = message_data["name"]
            logger.info(f"Processing document: {blob_name}")
            
            # Read document content
            document_text = self.storage.read_file(blob_name)
            
            # Process document
            metadata = {
                "source": blob_name,
                "timestamp": message_data.get("timestamp"),
            }
            processed_chunks = self.processor.process_document(document_text, metadata)
            
            # Update vector index
            self.vector_store.update_index(processed_chunks)
            
            logger.info(f"Successfully processed document: {blob_name}")
            
        except Exception as e:
            logger.error(f"Error processing document: {str(e)}")
            raise

    def start(self):
        """Start the data ingestion pipeline."""
        logger.info("Starting data ingestion pipeline...")
        
        def callback(message_data: Dict[str, Any]):
            self.process_document(message_data)
        
        # Subscribe to Pub/Sub notifications
        future = self.pubsub.subscribe(self.subscription_name, callback)
        
        try:
            future.result()
        except KeyboardInterrupt:
            future.cancel()
            logger.info("Shutting down...")

if __name__ == "__main__":
    pipeline = DataIngestionPipeline()
    pipeline.start() 