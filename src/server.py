import json
# import os # No longer needed
from pathlib import Path
from kaggle.api.kaggle_api_extended import KaggleApi
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
import mcp.types as types
# import asyncio # No longer explicitly needed here unless used elsewhere
# import uvicorn # No longer using uvicorn directly

# Define run_server function to encapsulate the logic
def run_server():
    load_dotenv()

    # Initialize Kaggle API
    api = None # Initialize api as None first
    try:
        api = KaggleApi()
        api.authenticate()
        print("Kaggle API Authenticated Successfully.")
    except Exception as e:
        print(f"Error authenticating Kaggle API: {e}")
        # api remains None if authentication fails

    # Initialize the FastMCP server
    mcp = FastMCP("kaggle-mcp")

    # --- Define Tools ---
    # Tools need access to 'api'. Define them inside run_server so they capture 'api' from the outer scope.
    @mcp.tool()
    async def search_kaggle_datasets(query: str) -> str:
        """Searches for datasets on Kaggle matching the query using the Kaggle API."""
        if not api:
            # Return an informative error if API is not available
            return json.dumps({"error": "Kaggle API not authenticated or available."})

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
            download_path: Optional. The path to download the files to. Defaults to '<project_root>/datasets/<dataset_slug>'.
        """
        if not api:
            # Return an informative error if API is not available
            return json.dumps({"error": "Kaggle API not authenticated or available."})

        print(f"Attempting to download dataset: {dataset_ref}")

        # Determine absolute download path based on script location
        # Use Path.cwd() if run via script entry point, or __file__ if run directly
        try:
            project_root = Path(__file__).parent.parent.resolve() # NEW: this is the parent of src/, i.e., the project root
        except NameError: # __file__ might not be defined when run via entry point
            project_root = Path.cwd() # NEW: Assume cwd is project root if __file__ is not defined


        if not download_path:
            try:
                dataset_slug = dataset_ref.split('/')[1]
            except IndexError:
                return f"Error: Invalid dataset_ref format '{dataset_ref}'. Expected 'username/dataset-slug'."
            # Construct absolute path relative to project root
            download_path_obj = project_root / "datasets" / dataset_slug # NEW
        else:
            # If a path is provided, resolve it relative to project root
            download_path_obj = project_root / Path(download_path) # NEW
            # Ensure it's fully resolved
            download_path_obj = download_path_obj.resolve()


        # Ensure download directory exists (using the Path object)
        try:
            download_path_obj.mkdir(parents=True, exist_ok=True)
            print(f"Ensured download directory exists: {download_path_obj}") # Will print absolute path
        except OSError as e:
            return f"Error creating download directory '{download_path_obj}': {e}"

        try:
            print(f"Calling api.dataset_download_files for {dataset_ref} to path {str(download_path_obj)}")
            # Pass the path as a string to the Kaggle API
            api.dataset_download_files(dataset_ref, path=str(download_path_obj), unzip=True, quiet=False)
            return f"Successfully downloaded and unzipped dataset '{dataset_ref}' to '{str(download_path_obj)}'." # Show absolute path
        except Exception as e:
            # Log the error potentially
            print(f"Error downloading dataset '{dataset_ref}': {e}")
            # Check for 404 Not Found
            if "404" in str(e):
                return f"Error: Dataset '{dataset_ref}' not found or access denied."
            # Check for other specific Kaggle errors if needed
            return f"Error downloading dataset '{dataset_ref}': {str(e)}"


    # --- Define Prompts ---
    @mcp.prompt()
    async def generate_eda_notebook(dataset_ref: str) -> types.GetPromptResult:
        """Generates a basic EDA prompt for a given Kaggle dataset reference."""
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

    # --- Start the Server ---
    print("Starting Kaggle MCP Server via mcp.run()...")

    # Call the run() method on the FastMCP instance
    # This likely contains the server startup logic used by the CLI
    mcp.run()

    # The code below this point will only execute after mcp.run() stops
    print("Kaggle MCP Server stopped.")


# Standard boilerplate to run the server function when the script is executed directly
if __name__ == "__main__":
    # This block is less relevant now that we use `uv run kaggle-mcp`
    # which directly calls run_server(), but we keep it for potential direct execution
    print("Setting up and running Kaggle MCP Server (direct script run)...")
    run_server()
    # The mcp.run() call above will block, so messages below won't print until shutdown
    print("Server run finished (direct script run).")

# Remove the old print statement from the global scope
# print("Kaggle MCP Server defined. Run with 'mcp run server.py'")
