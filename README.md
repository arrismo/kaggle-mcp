[![smithery badge](https://smithery.ai/badge/@arrismo/kaggle-mcp)](https://smithery.ai/server/@arrismo/kaggle-mcp)
<a href="https://glama.ai/mcp/servers/arwswog1el"><img width="380" height="200" src="https://glama.ai/mcp/servers/arwswog1el/badge" alt="Kaggle MCP Server" /></a>

# Kaggle MCP (Model Context Protocol) Server
This repository contains an MCP (Model Context Protocol) server (`server.py`) built using the `fastmcp` library. It interacts with the Kaggle API to provide tools for searching and downloading datasets, and a prompt for generating EDA notebooks.

## Project Structure

-   `server.py`: The FastMCP server application. It defines resources, tools, and prompts for interacting with Kaggle.
-   `.env.example`: An example file for environment variables (Kaggle API credentials). Rename to `.env` and fill in your details.
-   `requirements.txt`: Lists the necessary Python packages.
-   `pyproject.toml` & `uv.lock`: Project metadata and locked dependencies for `uv` package manager.
-   `datasets/`: Default directory where downloaded Kaggle datasets will be stored.

## Setup

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd <repository-directory>
    ```

2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    # Or use uv: uv venv
    ```

3.  **Install dependencies:**
    Using pip:
    ```bash
    pip install -r requirements.txt
    ```
    Or using uv:
    ```bash
    uv sync
    ```

4.  **Set up Kaggle API credentials:**
    -   **Method 1 (Recommended): Environment Variables**
        -   Create `.env` file
        -   Open the `.env` file and add your Kaggle username and API key:
            ```dotenv
            KAGGLE_USERNAME=your_kaggle_username
            KAGGLE_KEY=your_kaggle_api_key
            ```
        -   You can obtain your API key from your Kaggle account page (`Account` > `API` > `Create New API Token`). This will download a `kaggle.json` file containing your username and key.
    -   **Method 2: `kaggle.json` file**
        -   Download your `kaggle.json` file from your Kaggle account.
        -   Place the `kaggle.json` file in the expected location (usually `~/.kaggle/kaggle.json` on Linux/macOS or `C:\Users\<Your User Name>\.kaggle\kaggle.json` on Windows). The `kaggle` library will automatically detect this file if the environment variables are not set.

## Running the Server

1.  **Ensure your virtual environment is active.**
2.  **Run the MCP server:**
    ```bash
    uv run kaggle-mcp
    ```
    The server will start and register its resources, tools, and prompts. You can interact with it using an MCP client or compatible tools.

## Running the Docker Container

### 1. Set up Kaggle API credentials

This project requires Kaggle API credentials to access Kaggle datasets.

- Go to https://www.kaggle.com/settings and click "Create New API Token" to download your `kaggle.json` file.
- Open the `kaggle.json` file and copy your username and key into a new `.env` file in the project root:

```
KAGGLE_USERNAME=your_username
KAGGLE_KEY=your_key
```

### 2. Build the Docker image

```sh
docker build -t kaggle-mcp-test .
```

### 3. Run the Docker container using your .env file

```sh
docker run --rm -it --env-file .env kaggle-mcp-test
```

This will automatically load your Kaggle credentials as environment variables inside the container.

---


## Server Features

The server exposes the following capabilities through the Model Context Protocol:
### Tools

*   **`search_kaggle_datasets(query: str)`**:
    *   Searches for datasets on Kaggle matching the provided query string.
    *   Returns a JSON list of the top 10 matching datasets with details like reference, title, download count, and last updated date.
*   **`download_kaggle_dataset(dataset_ref: str, download_path: str | None = None)`**:
    *   Downloads and unzips files for a specific Kaggle dataset.
    *   `dataset_ref`: The dataset identifier in the format `username/dataset-slug` (e.g., `kaggle/titanic`).
    *   `download_path` (Optional): Specifies where to download the dataset. If omitted, it defaults to `./datasets/<dataset_slug>/` relative to the server script's location.

### Prompts

*   **`generate_eda_notebook(dataset_ref: str)`**:
    *   Generates a prompt message suitable for an AI model (like Gemini) to create a basic Exploratory Data Analysis (EDA) notebook for the specified Kaggle dataset reference.
    *   The prompt asks for Python code covering data loading, missing value checks, visualizations, and basic statistics.

## Connecting to Claude Desktop 
Go to Claude > Settings > Developer > Edit Config > claude_desktop_config.json to include the following:

```
{
  "mcpServers": {
    "kaggle-mcp": {
      "command": "kaggle-mcp",
      "cwd": "<path-to-their-cloned-repo>/kaggle-mcp"
    }
  }
}
```

## Usage Example

An AI agent or MCP client could interact with this server like this:

1.  **Agent:** "Search Kaggle for datasets about 'heart disease'"
    *   *Server executes `search_kaggle_datasets(query='heart disease')`*
2.  **Agent:** "Download the dataset 'user/heart-disease-dataset'"
    *   *Server executes `download_kaggle_dataset(dataset_ref='user/heart-disease-dataset')`*
3.  **Agent:** "Generate an EDA notebook prompt for 'user/heart-disease-dataset'"
    *   *Server executes `generate_eda_notebook(dataset_ref='user/heart-disease-dataset')`*
    *   *Server returns a structured prompt message.*
4.  **Agent:** (Sends the prompt to a code-generating model) -> Receives EDA Python code.
