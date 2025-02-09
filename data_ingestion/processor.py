from typing import List, Dict, Any
import vertexai
from vertexai.language_models import TextEmbeddingModel
from langchain.text_splitter import RecursiveCharacterTextSplitter
import numpy as np
import os

class DocumentProcessor:
    def __init__(
        self,
        project_id: str,
        location: str,
        embedding_model: str,
        chunk_size: int = 500,
        chunk_overlap: int = 50,
    ):
        vertexai.init(project=project_id, location=location)
        self.embedding_model = TextEmbeddingModel.from_pretrained(embedding_model)
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
        )

    def chunk_document(self, text: str) -> List[str]:
        """Split document into chunks."""
        return self.text_splitter.split_text(text)

    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for text chunks."""
        embeddings = []
        for chunk in texts:
            embedding = self.embedding_model.get_embeddings([chunk])[0].values
            embeddings.append(embedding)
        return embeddings

    def process_document(self, document_text: str, metadata: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Process document: chunk and generate embeddings."""
        chunks = self.chunk_document(document_text)
        embeddings = self.generate_embeddings(chunks)
        
        processed_chunks = []
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            chunk_data = {
                "chunk_id": i,
                "text": chunk,
                "embedding": embedding,
                "metadata": metadata or {}
            }
            processed_chunks.append(chunk_data)
        
        return processed_chunks 