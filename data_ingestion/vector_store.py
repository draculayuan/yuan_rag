from google.cloud import aiplatform
from google.cloud.aiplatform_v1.types import IndexDatapoint
from typing import List, Dict, Any
import time

class VectorSearchManager:
    def __init__(
        self,
        project_id: str,
        location: str,
        index_id: str = None,
        dimensions: int = 768,
        display_name: str = "rag-vector-index",
    ):
        self.project_id = project_id
        self.location = location
        self.index_id = index_id
        self.dimensions = dimensions
        self.display_name = display_name
        
        aiplatform.init(project=project_id, location=location)

    def create_index(self) -> str:
        """Create a new Vector Search index."""
        index = aiplatform.MatchingEngineIndex.create_tree_ah_index(
            display_name=self.display_name,
            dimensions=self.dimensions,
            approximate_neighbors_count=50,
            distance_measure_type="COSINE_DISTANCE",
            index_update_method="STREAM_UPDATE",
            description="RAG Vector Search Index",
        )
        self.index_id = index.resource_name
        return self.index_id

    def get_or_create_index(self) -> str:
        """Get existing index or create new one."""
        if self.index_id:
            try:
                index = aiplatform.MatchingEngineIndex(index_name=self.index_id)
                return self.index_id
            except Exception:
                pass
        return self.create_index()

    def update_index(self, vectors: List[Dict[str, Any]], batch_size: int = 100):
        """Update index with new vectors."""
        index = aiplatform.MatchingEngineIndex(index_name=self.index_id)
        
        datapoints = [
            IndexDatapoint(
                datapoint_id = str(v["chunk_id"]),
                feature_vector = v["embedding"],
                attributes = {
                    "original_text": v["text"]
                }
            )
            for v in vectors
        ]
        """
        for i in range(0, len(vectors), batch_size):
            batch = vectors[i:i + batch_size]
            
            # Prepare data in the required format
            embeddings = [v["embedding"] for v in batch]
            ids = [str(v["chunk_id"]) for v in batch]
            
            # Update index
            index.upsert_datapoints(
                embeddings=embeddings,
                ids=ids,
            )
            
            # Small delay to avoid rate limiting
            time.sleep(0.1)
        """
        index.upsert_datapoints(datapoints=datapoints)

    def search_similar(self, query_embedding: List[float], num_neighbors: int = 5) -> List[Dict[str, Any]]:
        """Search for similar vectors."""
        index = aiplatform.MatchingEngineIndex(index_name=self.index_id)
        response = index.find_neighbors(
            query_embeddings=[query_embedding],
            num_neighbors=num_neighbors,
        )
        
        results = []
        for match in response[0]:
            results.append({
                "id": match.id,
                "distance": match.distance,
            })
        
        return results 
