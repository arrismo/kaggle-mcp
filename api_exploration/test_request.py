import requests
import json

# The API endpoint
url = "http://localhost:8000/v1/chat/completions"

# Sample request data
data = {
    "messages": [
        {
            "role": "user",
            "content": "Search for datasets about machine learning",
            "context": {
                "query": "machine learning datasets"
            }
        }
    ],
    "max_tokens": 1000
}

# Make the POST request
response = requests.post(url, json=data)

# Print the response
print("Status Code:", response.status_code)
print("Response:")
print(json.dumps(response.json(), indent=2)) 