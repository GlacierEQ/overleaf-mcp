# Overleaf MCP Client Examples

This directory contains example scripts demonstrating how to use the MCP client to interact with the Overleaf MCP server.

## Prerequisites

Before running these examples, make sure you have:

1. Installed the Overleaf-MCP package and its dependencies
2. Activated the Python virtual environment (if used)
3. For some examples, a running MCP server is required

## Example Scripts

### Basic Client Usage: `client_usage_example.py`

This example demonstrates basic usage of the MCP client to connect to a local MCP server and interact with various LaTeX tools.

**Features demonstrated:**
- Connecting to an MCP server
- Listing available tools
- Calling LaTeX-related tools
- Processing tool results

**How to run:**

```bash
# First, start the MCP server in another terminal
cd overleaf-mcp
python -m overleaf_mcp.cli run

# Then run the client example
python examples/client_usage_example.py
```

### Advanced Client Usage: `advanced_client_example.py`

This example demonstrates more advanced features of the MCP client including different transport options, custom handlers, and error handling.

**Features demonstrated:**
- Using different transport methods (HTTP, WebSocket, Direct)
- Setting up custom message handlers
- Handling server notifications
- Custom roots and sampling functionality

**How to run:**

```bash
# For HTTP and WebSocket examples, start the server first
cd overleaf-mcp
python -m overleaf_mcp.cli run

# Then run the advanced example
python examples/advanced_client_example.py
```

### LaTeX Template Demo: `template_and_converter_demo.py`

This example demonstrates how to use the LaTeX template manager and converter utilities.

**Features demonstrated:**
- Creating and using LaTeX templates
- Rendering templates with variable substitution
- Converting LaTeX to PDF and HTML formats

**How to run:**

```bash
python examples/template_and_converter_demo.py
```

## Expected Results

When running these examples, you should see:

1. **Basic client example**: Connection to the server, listing of tools, and calling basic LaTeX tools with results displayed.

2. **Advanced client example**: Demonstrations of different transport methods, handling of notifications, and more complex tool interactions.

3. **Template demo**: Generation of LaTeX documents from templates and conversion to other formats if the required dependencies are installed.

## Troubleshooting

- If you see connection errors, make sure the MCP server is running
- Check that you've activated the correct Python environment
- For WebSocket connections, ensure your server supports WebSocket transport
- For PDF/HTML conversion in the template demo, make sure LaTeX and other required dependencies are installed

## Creating Your Own Client Applications

You can use these examples as starting points for creating your own applications that interact with the Overleaf MCP server. The key components you'll need are:

1. A `Client` instance configured with the appropriate transport
2. Custom handlers for specific functionality (optional)
3. Asynchronous code to interact with the server

See the FastMCP client documentation for more details on available methods and configuration options. 