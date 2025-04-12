from kaggle.api.kaggle_api_extended import KaggleApi
import json
from datetime import datetime

def json_serializer(obj):
    """Custom JSON serializer for datetime objects"""
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")

def print_object_structure(obj, name):
    """Print the structure of a Kaggle API object"""
    print(f"\n{name} Structure:")
    print("-" * 50)
    print(f"Type: {type(obj)}")
    print("Available attributes:")
    for attr in dir(obj):
        if not attr.startswith('_'):  # Skip private attributes
            try:
                value = getattr(obj, attr)
                print(f"{attr}: {type(value)}")
            except:
                print(f"{attr}: <error accessing>")
    print("-" * 50)

def main():
    # Initialize Kaggle API
    api = KaggleApi()
    api.authenticate()
    
    # Example 1: Search for datasets
    print("\n=== Example 1: Dataset Search ===")
    search_results = api.dataset_list(search="weather")
    if search_results:
        print_object_structure(search_results[0], "Dataset Search Result")
        print("\nFirst result details:")
        print(json.dumps({
            "ref": search_results[0].ref,
            "title": search_results[0].title,
            "subtitle": search_results[0].subtitle,
            "download_count": search_results[0].download_count,
            "last_updated": search_results[0].last_updated,
            "usability_rating": search_results[0].usability_rating
        }, indent=2, default=json_serializer))
    

if __name__ == "__main__":
    main() 