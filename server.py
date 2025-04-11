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

# Helper functions
def process_dataset_request(dataset_name, context):
    """Process a request for Kaggle dataset information"""
    try:
        # Extract dataset owner and name
        if "/" not in dataset_name:
            raise ValueError("Dataset name should be in format 'owner/dataset-name'")
        
        # Get dataset information
        dataset_info = api.dataset_view(dataset_name)
        
        # Check if sample data is requested
        sample_data = None
        if context.get("include_sample", False):
            with tempfile.TemporaryDirectory() as tmp_dir:
                api.dataset_download_files(dataset_name, path=tmp_dir, unzip=True)
                # Find CSV files
                csv_files = [f for f in os.listdir(tmp_dir) if f.endswith('.csv')]
                if csv_files:
                    # Read the first CSV file
                    df = pd.read_csv(os.path.join(tmp_dir, csv_files[0]))
                    sample_data = df.head(5).to_dict(orient="records")
        
        return {
            "title": dataset_info.title,
            "size": dataset_info.size,
            "lastUpdated": str(dataset_info.lastUpdated),
            "totalBytes": dataset_info.totalBytes,
            "downloadCount": dataset_info.downloadCount,
            "files": [{"name": f.name, "size": f.size} for f in dataset_info.files],
            "sample_data": sample_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing dataset: {str(e)}")

def process_competition_request(competition_name, context):
    """Process a request for Kaggle competition information"""
    try:
        # Get competition information
        competition_info = api.competition_view(competition_name)
        
        return {
            "title": competition_info.title,
            "description": competition_info.description,
            "deadline": str(competition_info.deadline),
            "category": competition_info.category,
            "reward": competition_info.reward,
            "teamCount": competition_info.teamCount
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing competition: {str(e)}")

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
                    "size": ds.totalBytes if hasattr(ds, 'totalBytes') else "N/A"
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
    
    if "dataset" in user_content and context.get("dataset_name"):
        # Handle dataset requests
        dataset_name = context["dataset_name"]
        response_content = process_dataset_request(dataset_name, context)
        message = f"Here's information about the dataset '{dataset_name}'."
    
    elif "competition" in user_content and context.get("competition_name"):
        # Handle competition requests
        competition_name = context["competition_name"]
        response_content = process_competition_request(competition_name, context)
        message = f"Here's information about the competition '{competition_name}'."
    
    elif "search" in user_content and context.get("query"):
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