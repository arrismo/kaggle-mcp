from fastapi import FastAPI, HTTPException, Depends, Body
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import os
import json
import pandas as pd
from kaggle.api.kaggle_api_extended import KaggleApi
import tempfile
from dotenv import load_dotenv


# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(title="Kaggle MCP Server")

# Initialize Kaggle API
api = KaggleApi()
api.authenticate()

# Models for MCP interaction
class MessageContent(BaseModel):
    role: str
    content: str
    context: Optional[Dict[str, Any]] = None

class MCPRequest(BaseModel):
    messages: List[MessageContent]
    max_tokens: Optional[int] = 1000

class MCPResponse(BaseModel):
    message: MessageContent
    usage: Optional[Dict[str, Any]] = None


def process_search_request(query, context):
    """Process a search request for Kaggle datasets"""
    try:
        # Search datasets
        search_results = api.dataset_list(search=query)
        print(search_results)
        
        return {
            "results": [
                {
                    "ref": ds.ref,
                    "title": ds.title,
                    "subtitle": ds.subtitle,
                    "download_count": ds.download_count,
                    "last_updated": ds.last_updated,
                    "usability_rating": ds.usability_rating
                }
                for ds in search_results[:10]  # Limit to 10 results
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing search: {str(e)}")

# Routes
@app.post("/v1/chat/completions", response_model=MCPResponse)
async def chat_completions(request: MCPRequest = Body(...)):
    # Get the latest user message
    latest_message = None
    for message in reversed(request.messages):
        if message.role == "user":
            latest_message = message
            break
    
    if not latest_message:
        raise HTTPException(status_code=400, detail="No user message found in the request")
    
    user_content = latest_message.content.lower()
    context = latest_message.context or {}
    
    # Process based on intent
    response_content = {}
    
    
    if "search" in user_content and context.get("query"):
        # Handle search requests
        query = context["query"]
        response_content = process_search_request(query, context)
        message = f"Here are the search results for '{query}'."
    
    else:
        # General response when no specific intent is matched
        message = (
            "I can help you interact with Kaggle. Please provide context in your request:\n"
            "- For dataset info: Include 'dataset_name' in the context\n"
            "- For competition info: Include 'competition_name' in the context\n"
            "- For search: Include 'query' in the context"
        )
    
    # Create response
    return MCPResponse(
        message=MessageContent(
            role="assistant",
            content=message,
            context=response_content
        ),
        usage={
            "prompt_tokens": sum(len(m.content.split()) for m in request.messages),
            "completion_tokens": len(message.split()) + 100,  # Estimate
            "total_tokens": sum(len(m.content.split()) for m in request.messages) + len(message.split()) + 100
        }
    )

@app.get("/")
async def root():
    return {"message": "Kaggle MCP Server is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)