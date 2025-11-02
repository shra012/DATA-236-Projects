#!/bin/bash

# Setup script for Kafka agents using uv

echo "Setting up Kafka agents environment with uv..."
echo "=============================================="

# Check if pyproject.toml exists
if [ ! -f "pyproject.toml" ]; then
    echo "Error: pyproject.toml not found in current directory"
    exit 1
fi

echo "Found pyproject.toml"

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "Error: uv is not installed. Install it with: curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

echo "uv is installed"

# Check if virtual environment exists
if [ -d ".venv" ]; then
    echo ""
    echo "Virtual environment already exists at .venv"
    echo "Using existing virtual environment..."
else
    echo ""
    echo "Creating virtual environment..."
    uv venv .venv
    echo "Virtual environment created at .venv"
fi

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source ./.venv/bin/activate

# Generate requirements.txt from pyproject.toml
echo ""
echo "Compiling requirements.txt from pyproject.toml..."
uv pip compile pyproject.toml --output-file requirements.txt --no-deps

echo "requirements.txt compiled"

# Sync dependencies from pyproject.toml
echo ""
echo "Syncing dependencies from pyproject.toml..."
uv pip sync requirements.txt

echo "Dependencies synced successfully"
