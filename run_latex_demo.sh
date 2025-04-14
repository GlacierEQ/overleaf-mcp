#!/bin/bash

# Run the LaTeX Template and Converter Demo
# This script ensures the demo runs from the correct directory

# Change to the project root directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Run the demo script
python examples/template_and_converter_demo.py

echo ""
echo "Demo completed! Check the output directory: ${SCRIPT_DIR}/examples/demo_output" 