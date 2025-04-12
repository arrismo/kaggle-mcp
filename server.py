import json
import os
from pathlib import Path
from kaggle.api.kaggle_api_extended import KaggleApi
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
import mcp.types as types

# Load environment variables if .env file exists
load_dotenv()

# Initialize Kaggle API
try:
    api = KaggleApi()
    api.authenticate()
    print("Kaggle API Authenticated Successfully.")
except Exception as e:
    print(f"Error authenticating Kaggle API: {e}")
    # Decide how to handle this - maybe exit or run with limited functionality
    api = None


# Initialize the FastMCP server
mcp = FastMCP("kaggle-mcp")

# --- Define Resources ---
@mcp.resource("kaggle://competitions/{competition_id}")
async def get_competition_details(competition_id: str) -> str:
    """Provides details about a specific Kaggle competition using the Kaggle API."""
    if not api:
        raise ConnectionError("Kaggle API not authenticated.")

    print(f"Fetching details for competition: {competition_id}")
    try:
        competitions = api.competition_list(search=competition_id)
        found_comp = None
        for comp in competitions:
            if str(getattr(comp, 'id', '')) == competition_id or getattr(comp, 'ref', '') == competition_id:
                found_comp = comp
                break

        if found_comp:
            # Format the available basic info
            details = {
                "id": getattr(found_comp, 'id', 'N/A'),
                "ref": getattr(found_comp, 'ref', 'N/A'),
                "title": getattr(found_comp, 'title', 'N/A'),
                "category": getattr(found_comp, 'category', 'N/A'),
                "organizationName": getattr(found_comp, 'organizationName', 'N/A'),
                "evaluationMetric": getattr(found_comp, 'evaluationMetric', 'N/A'),
                "reward": getattr(found_comp, 'reward', 'N/A'),
                "userHasEntered": getattr(found_comp, 'userHasEntered', 'N/A'),
                "deadline": str(getattr(found_comp, 'deadline', 'N/A')),
            }
            return json.dumps(details, indent=2)
        else:
            raise ValueError(f"Competition '{competition_id}' not found via search.")
    except Exception as e:
        # Log the error potentially
        print(f"Error fetching competition details for {competition_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching competition details: {str(e)}")


# --- Define Tools ---
@mcp.tool()
async def search_kaggle_datasets(query: str) -> str:
    """Searches for datasets on Kaggle matching the query using the Kaggle API."""
    if not api:
        raise ConnectionError("Kaggle API not authenticated.")

    print(f"Searching datasets for: {query}")
    try:
        search_results = api.dataset_list(search=query)
        if not search_results:
            return "No datasets found matching the query."

        # Format results as JSON string for the tool output
        results_list = [
            {
                "ref": getattr(ds, 'ref', 'N/A'),
                "title": getattr(ds, 'title', 'N/A'),
                "subtitle": getattr(ds, 'subtitle', 'N/A'),
                "download_count": getattr(ds, 'downloadCount', 0), # Adjusted attribute name
                "last_updated": str(getattr(ds, 'lastUpdated', 'N/A')), # Adjusted attribute name
                "usability_rating": getattr(ds, 'usabilityRating', 'N/A') # Adjusted attribute name
            }
            for ds in search_results[:10]  # Limit to 10 results
        ]
        return json.dumps(results_list, indent=2)
    except Exception as e:
        # Log the error potentially
        print(f"Error searching datasets for '{query}': {e}")
        # Return error information as part of the tool output
        return json.dumps({"error": f"Error processing search: {str(e)}"})


@mcp.tool()
async def download_kaggle_dataset(dataset_ref: str, download_path: str | None = None) -> str:
    """Downloads files for a specific Kaggle dataset.
    Args:
        dataset_ref: The reference of the dataset (e.g., 'username/dataset-slug').
        download_path: Optional. The path to download the files to. Defaults to '<script_directory>/datasets/<dataset_slug>'.
    """
    if not api:
        raise ConnectionError("Kaggle API not authenticated.")

    print(f"Attempting to download dataset: {dataset_ref}")

    # Determine absolute download path based on script location
    script_dir = Path(__file__).parent.resolve() # Get the directory where server.py lives

    if not download_path:
        try:
            dataset_slug = dataset_ref.split('/')[1]
        except IndexError:
            return f"Error: Invalid dataset_ref format '{dataset_ref}'. Expected 'username/dataset-slug'."
        # Construct absolute path
        download_path = script_dir / "datasets" / dataset_slug
    else:
        # If a path is provided, resolve it to an absolute path to be safe
        download_path = Path(download_path).resolve()

    # Ensure download directory exists (using the Path object)
    try:
        download_path.mkdir(parents=True, exist_ok=True)
        print(f"Ensured download directory exists: {download_path}") # Will print absolute path
    except OSError as e:
        return f"Error creating download directory '{download_path}': {e}"

    try:
        print(f"Calling api.dataset_download_files for {dataset_ref} to path {str(download_path)}")
        # Pass the path as a string to the Kaggle API
        api.dataset_download_files(dataset_ref, path=str(download_path), unzip=True, quiet=False)
        return f"Successfully downloaded and unzipped dataset '{dataset_ref}' to '{str(download_path)}'." # Show absolute path
    except Exception as e:
        # Log the error potentially
        print(f"Error downloading dataset '{dataset_ref}': {e}")
        # Check for common errors like 404 Not Found
        if "404" in str(e):
            return f"Error: Dataset '{dataset_ref}' not found or access denied."
        return f"Error downloading dataset '{dataset_ref}': {str(e)}"


# --- Define Prompts ---
@mcp.prompt()
async def generate_eda_notebook(dataset_ref: str) -> types.GetPromptResult:
    """Generates a basic EDA prompt for a given Kaggle dataset reference."""
    # Example: dataset_ref could be 'kaggle/input/titanic'
    print(f"Generating EDA prompt for dataset: {dataset_ref}")
    prompt_text = f"Generate Python code for basic Exploratory Data Analysis (EDA) for the Kaggle dataset '{dataset_ref}'. Include loading the data, checking for missing values, visualizing key features, and basic statistics."
    return types.GetPromptResult(
        description=f"Basic EDA for {dataset_ref}",
        messages=[
            types.PromptMessage(
                role="user",
                content=types.TextContent(type="text", text=prompt_text),
            )
        ],
    )

print("Kaggle MCP Server defined. Run with 'mcp run server.py'")
