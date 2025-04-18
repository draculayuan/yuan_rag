from google.cloud import aiplatform, firestore
from google.cloud.aiplatform_v1.types import IndexDatapoint
from typing import List, Dict, Any
import time

class VectorSearchManager:
    def __init__(
        self,
        project_id: str,
        location: str,
        index_id: str = None,
        index_endpoint_id: str = None,
        deployed_index_id: str = None,
        dimensions: int = 768,
        display_name: str = "rag-vector-index",
    ):
        self.project_id = project_id
        self.location = location
        self.index_id = index_id
        self.index_endpoint_id = index_endpoint_id
        self.deployed_index_id = deployed_index_id
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

    def update_index(self, vectors: List[Dict[str, Any]], database: str = "yuan-evernote-firestore"):
        index = aiplatform.MatchingEngineIndex(index_name=self.index_id)
        db = firestore.Client(database = database)
        
        datapoints = [
            IndexDatapoint(
                datapoint_id=str(v["chunk_id"]),
                feature_vector=v["embedding"],
            )
            for v in vectors
        ]

        # save to firestore for retrieval later
        for v in vectors:
            doc_id = str(v["chunk_id"])
            doc_ref = db.collection("rag_chunks").document(doc_id)
            doc_ref.set({"text": v["text"]})
        
        index.upsert_datapoints(datapoints=datapoints)

    def search_similar(self, query_embedding: List[float], num_neighbors: int = 5, database: str = "yuan-evernote-firestore") -> List[Dict[str, Any]]:
        """Search for similar vectors."""
        db = firestore.Client(database = database)
        #index = aiplatform.MatchingEngineIndex(index_name=self.index_id)
        index_endpoint = aiplatform.MatchingEngineIndexEndpoint(
            index_endpoint_name=self.index_endpoint_id
        )
        response = index_endpoint.find_neighbors(
            deployed_index_id=self.deployed_index_id,
            queries=query_embedding,
            num_neighbors=num_neighbors,
        )
        
        results = []
        for match in response[0]:
            doc_ref = db.collection("rag_chunks").document(str(match.id))
            doc = doc_ref.get()
            if doc.exists:
                text = doc.to_dict()["text"]
            else:
                text = "[Missing chunk]"
            results.append({
                "id": match.id,
                "distance": match.distance,
                "text": text
            })
        
        return results 
