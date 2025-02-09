from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional
import os
from dotenv import load_dotenv
from llm import LLMHandler
from data_ingestion.processor import DocumentProcessor
from data_ingestion.vector_store import VectorSearchManager

# Load environment variables
load_dotenv()

app = FastAPI(title="RAG API", description="Retrieval-Augmented Generation API")

# Mount static files
app.mount("/static", StaticFiles(directory="serving/static"), name="static")

# Initialize components
project_id = os.getenv("PROJECT_ID")
region = os.getenv("REGION")

processor = DocumentProcessor(
    project_id=project_id,
    location=region,
    embedding_model=os.getenv("VERTEX_EMBEDDING_MODEL"),
)

vector_store = VectorSearchManager(
    project_id=project_id,
    location=region,
    index_id=os.getenv("VECTOR_SEARCH_INDEX_ID"),
)

llm = LLMHandler(
    project_id=project_id,
    location=region,
    model_name=os.getenv("VERTEX_LLM_MODEL"),
)

class QueryRequest(BaseModel):
    query: str
    num_results: Optional[int] = 5

class QueryResponse(BaseModel):
    answer: str
    context: List[str]

@app.get("/")
async def root():
    """Serve the main page."""
    return FileResponse("serving/static/index.html")

@app.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    try:
        # Generate query embedding
        query_embedding = processor.generate_embeddings([request.query])[0]
        
        # Search for similar chunks
        similar_chunks = vector_store.search_similar(
            query_embedding,
            num_neighbors=request.num_results
        )
        
        # Get context from chunks
        context = []
        for chunk in similar_chunks:
            # Here you would typically retrieve the actual text from a database
            # For now, we're just using the IDs
            context.append(f"Chunk {chunk['id']}")
        
        # Generate response using LLM
        answer = llm.generate_response(
            query=request.query,
            context=context,
            safety_settings=llm.get_default_safety_settings()
        )
        
        return QueryResponse(answer=answer, context=context)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy"} 