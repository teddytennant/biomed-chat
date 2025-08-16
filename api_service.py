import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from api_client import process_query
import os

# Initialize FastAPI app
app = FastAPI(
    title="Biomedical RAG API",
    description="An API for the RAG-enhanced biomedical chatbot.",
    version="1.0.0",
)

# Define the request body model
class ChatRequest(BaseModel):
    query: str

# Define the response body model
class ChatResponse(BaseModel):
    response: str

@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Receives a query, processes it through the RAG and LLM,
    and returns the response.
    """
    # This function from api_client.py does all the heavy lifting
    response_text = process_query(request.query)
    return ChatResponse(response=response_text)

@app.get("/api/health")
async def health_check():
    """
    A simple health check endpoint.
    """
    return {"status": "ok"}

if __name__ == "__main__":
    # Get port from environment variable or use 8000 as default
    port = int(os.getenv("PYTHON_API_PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
