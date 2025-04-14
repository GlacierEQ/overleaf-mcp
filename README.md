# Overleaf MCP Server

An MCP (Model Context Protocol) server that enables LaTeX editing with AI assistance and Overleaf integration. This server allows AI assistants like Claude to help with creating and editing LaTeX documents.

## Features

- LaTeX document editing and creation
- Mathematical equation formatting
- Table and figure generation
- Document compilation
- Overleaf project integration (download/upload)
- All features available on free tier (no paid API dependencies)

## Requirements

- Python 3.10 or higher
- A LaTeX compiler (MiKTeX, TeX Live, etc.)
- Pandoc (for HTML conversion)
- Claude Desktop app or other MCP-compatible client

## Installation

### 1. Install a LaTeX compiler (if not already installed)

#### macOS:
```bash
brew install --cask basictex
```
or for a full installation:
```bash
brew install --cask mactex-no-gui
```

#### Windows:
Download and install MiKTeX from [miktex.org](https://miktex.org/download)

#### Linux (Ubuntu/Debian):
```bash
sudo apt-get install texlive-latex-base texlive-latex-extra
```

### 2. Install Pandoc (for HTML conversion)

#### macOS:
```bash
brew install pandoc
```

#### Windows:
Download and install from [pandoc.org/installing.html](https://pandoc.org/installing.html)

#### Linux (Ubuntu/Debian):
```bash
sudo apt-get install pandoc
```

### 3. Install Overleaf MCP

#### Using pip:
```bash
pip install overleaf-mcp
```

#### Or install from source with a virtual environment:
```bash
git clone https://github.com/username/overleaf-mcp.git
cd overleaf-mcp
python -m venv overleaf-mcp-env
source overleaf-mcp-env/bin/activate  # On Windows: .\overleaf-mcp-env\Scripts\activate
pip install -r requirements.txt
pip install -e .
```

#### Activate the environment with all dependencies (on macOS/Linux):
We provide a convenient script to activate the environment and set up the PATH:
```bash
source ./activate_env.sh
```

## Usage

### 1. Start the MCP server

```bash
overleaf-mcp run
```

### 2. Connect to Claude Desktop

Follow the instructions in Claude Desktop to connect to a local MCP server.

### 3. Overleaf Workflow

1. Download your Overleaf project as a ZIP file
2. Use Claude to help edit the LaTeX files
3. Package the edited project for upload back to Overleaf

### 4. Try the demo

To see the LaTeX template manager and converter in action:
```bash
./run_latex_demo.sh
```

## Available Tools

### Document Operations
- `create_document`: Create a new LaTeX document
- `compile_document`: Compile the current document
- `fix_errors`: Identify and fix compilation errors

### Element Creation
- `create_equation`: Create a LaTeX equation
- `create_table`: Generate a LaTeX table
- `create_figure`: Insert a figure with caption
- `create_section`: Add a new document section

### Overleaf Integration
- `download_from_overleaf`: Instructions for downloading from Overleaf
- `prepare_for_upload`: Package a project for Overleaf upload

## Development

To set up for development:

```bash
git clone https://github.com/username/overleaf-mcp.git
cd overleaf-mcp
python -m venv overleaf-mcp-env
source overleaf-mcp-env/bin/activate  # On Windows: .\overleaf-mcp-env\Scripts\activate
pip install -r requirements.txt
pip install -e ".[dev]"
```

Run tests:

```bash
pytest tests/
```

## License

MIT License 