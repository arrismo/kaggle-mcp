# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Install uv first for dependency management
RUN pip install uv

# Copy the project definition files and readme
COPY pyproject.toml uv.lock README.md ./

# Copy the source code into the container
COPY src/ ./src/

# Install dependencies using uv sync
# This now happens *after* source code is copied
# --no-cache avoids caching downloads within the layer
RUN uv sync --no-cache

# Command to run the server (Smithery will likely use the command from smithery.yaml)
# Ensure the server listens on STDIO as expected by MCP
CMD ["python", "src/server.py"] 