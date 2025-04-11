import requests
import json
from typing import List, Dict, Any, Optional

class KaggleMCPClient:
    def __init__(self, server_url="http://localhost:8000"):
        self.server_url = server_url
        self.conversation_history = []
    
    def get_dataset_info(self, dataset_name, include_sample=False):
        """Get information about a Kaggle dataset"""
        message = {
            "role": "user",
            "content": f"Please provide information about the dataset {dataset_name}",
            "context": {
                "dataset_name": dataset_name,
                "include_sample": include_sample
            }
        }
        
        return self._send_request(message)
    
    def search_datasets(self, query):
        """Search for Kaggle datasets"""
        message = {
            "role": "user",
            "content": f"Search for datasets related to {query}",
            "context": {
                "query": query
            }
        }
        
        return self._send_request(message)
    
    def get_competition_info(self, competition_name):
        """Get information about a Kaggle competition"""
        message = {
            "role": "user",
            "content": f"Please provide information about the competition {competition_name}",
            "context": {
                "competition_name": competition_name
            }
        }
        
        return self._send_request(message)
    
    def _send_request(self, message):
        """Send request to MCP server"""
        self.conversation_history.append(message)
        
        payload = {
            "messages": self.conversation_history,
            "max_tokens": 1000
        }
        
        response = requests.post(
            f"{self.server_url}/v1/chat/completions",
            json=payload
        )
        
        if response.status_code == 200:
            response_data = response.json()
            if "message" in response_data:
                self.conversation_history.append(response_data["message"])
            return response_data
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return None

# Example usage
if __name__ == "__main__":
    client = KaggleMCPClient()
    
    # Search for datasets
    search_results = client.search_datasets("covid")
    print(json.dumps(search_results, indent=2))
    
    # Get dataset info
    dataset_info = client.get_dataset_info("rohanrao/formula-1-world-championship-1950-2020", include_sample=True)
    print(json.dumps(dataset_info, indent=2))