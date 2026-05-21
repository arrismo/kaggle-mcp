[![Trust Score](https://archestra.ai/mcp-catalog/api/badge/quality/arrismo/kaggle-mcp)](https://archestra.ai/mcp-catalog/arrismo__kaggle-mcp)
<a href="https://glama.ai/mcp/servers/arwswog1el"><img width="380" height="200" src="https://glama.ai/mcp/servers/arwswog1el/badge" alt="Kaggle MCP Server" /></a>

# Kaggle MCP Server

A Model Context Protocol (MCP) server that exposes Kaggle dataset search, download, and EDA prompt generation to MCP clients such as Claude Desktop.

## Features

- Search Kaggle datasets by keyword.
- Download and unzip Kaggle datasets locally.
- Generate a starter Exploratory Data Analysis (EDA) prompt for a Kaggle dataset.
- Supports Kaggle credentials via environment variables or the standard `kaggle.json` file.
- Runs locally, in Docker, or through Smithery.

## Available MCP Capabilities

### Tools

#### `search_kaggle_datasets(query: str)`

Searches Kaggle for datasets matching `query` and returns up to 10 results as JSON.

Returned fields include:

- `ref`
- `title`
- `subtitle`
- `download_count`
- `last_updated`
- `usability_rating`

#### `download_kaggle_dataset(dataset_ref: str, download_path: str | None = None)`

Downloads and unzips a Kaggle dataset.

- `dataset_ref`: Kaggle dataset reference in `owner/dataset-slug` format, for example `kaggle/titanic`.
- `download_path`: Optional local output path. If omitted, files are saved to `./datasets/<dataset_slug>/`.

### Prompts

#### `generate_eda_notebook(dataset_ref: str)`

Creates a prompt for generating basic Python EDA code for the provided Kaggle dataset reference. The prompt asks for data loading, missing-value checks, visualizations, and summary statistics.

## Requirements

- Python 3.10+
- Kaggle account and API token
- An MCP-compatible client

## Kaggle Credentials

Create a Kaggle API token from your Kaggle account settings:

1. Go to <https://www.kaggle.com/settings>.
2. Select **Create New API Token**.
3. Download `kaggle.json`.

Use either environment variables or the standard Kaggle config file.

### Option 1: Environment variables

Create a `.env` file in the project root:

```dotenv
KAGGLE_USERNAME=your_kaggle_username
KAGGLE_KEY=your_kaggle_api_key
```

### Option 2: `kaggle.json`

Place `kaggle.json` in the standard Kaggle location:

- macOS/Linux: `~/.kaggle/kaggle.json`
- Windows: `C:\Users\<Your User Name>\.kaggle\kaggle.json`

On macOS/Linux, make sure the file is not world-readable:

```bash
chmod 600 ~/.kaggle/kaggle.json
```

## Installation

```bash
git clone <repository-url>
cd kaggle-mcp
```

Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
```

Install dependencies with one of the following methods.

### Using uv

```bash
uv sync
```

### Using pip

```bash
pip install -r requirements.txt
```

## Running Locally

With `uv`:

```bash
uv run kaggle-mcp
```

Or run the server module directly:

```bash
python src/server.py
```

The server communicates over MCP stdio and is intended to be launched by an MCP client.

## Claude Desktop Configuration

Open Claude Desktop settings, then go to **Developer** > **Edit Config** and add this server to `claude_desktop_config.json`.

If installed in the project environment:

```json
{
  "mcpServers": {
    "kaggle-mcp": {
      "command": "uv",
      "args": ["run", "kaggle-mcp"],
      "cwd": "/absolute/path/to/kaggle-mcp",
      "env": {
        "KAGGLE_USERNAME": "your_kaggle_username",
        "KAGGLE_KEY": "your_kaggle_api_key"
      }
    }
  }
}
```

If using `kaggle.json`, you can omit the `env` block.

## Docker

Build the image:

```bash
docker build -t kaggle-mcp .
```

Run with credentials from `.env`:

```bash
docker run --rm -i --env-file .env kaggle-mcp
```

## Smithery

This repository includes `smithery.yaml`. Smithery starts the server over stdio and passes these configuration values as environment variables:

- `kaggleUsername` -> `KAGGLE_USERNAME`
- `kaggleKey` -> `KAGGLE_KEY`

## Example Workflow

1. Ask your MCP client: "Search Kaggle for heart disease datasets."
2. The client calls `search_kaggle_datasets`.
3. Choose a dataset reference from the results, for example `user/heart-disease-dataset`.
4. Ask: "Download `user/heart-disease-dataset`."
5. Ask: "Generate an EDA notebook prompt for `user/heart-disease-dataset`."

## Project Structure

```text
.
├── Dockerfile
├── README.md
├── pyproject.toml
├── requirements.txt
├── smithery.yaml
├── src/
│   ├── __init__.py
│   └── server.py
└── uv.lock
```

Downloaded datasets are saved under `datasets/` by default. This directory is created at runtime when downloads are requested.
