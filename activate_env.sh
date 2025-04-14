#!/bin/bash

# Activate the Overleaf MCP environment
# This script activates the virtual environment and updates the PATH
# to find all necessary external dependencies.

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Activate the virtual environment
source "$SCRIPT_DIR/overleaf-mcp-env/bin/activate"

# Update the PATH to find external dependencies (texlive, pandoc)
eval "$(/usr/libexec/path_helper)"

echo "Overleaf MCP environment activated!"
echo "Python: $(which python)"
echo "pdflatex: $(which pdflatex 2>/dev/null || echo 'Not found')"
echo "pandoc: $(which pandoc 2>/dev/null || echo 'Not found')"
echo ""
echo "To run the demo, use: ./run_latex_demo.sh"
echo "To run tests, use: python -m pytest"
echo "To start the MCP server, use: overleaf-mcp run" 