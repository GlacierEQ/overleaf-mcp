#!/usr/bin/env python3
"""
Example usage of the MCP client to connect to the Overleaf MCP server.

This example demonstrates how to:
1. Connect to a running Overleaf MCP server
2. List available tools
3. Execute various LaTeX-related tools
4. Handle server responses
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the parent directory to the Python path to import the package if needed
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import the client
from fastmcp.client import Client

# Example project directory - change this to a real LaTeX project path if needed
EXAMPLE_PROJECT_DIR = Path(__file__).parent / "demo_output"
EXAMPLE_PROJECT_DIR.mkdir(exist_ok=True)

# Create a sample LaTeX file for testing
EXAMPLE_TEX_FILE = EXAMPLE_PROJECT_DIR / "example.tex"
EXAMPLE_TEX_CONTENT = r"""
\documentclass{article}
\usepackage[utf8]{inputenc}
\usepackage{hyperref}

\title{MCP Client Example}
\author{MCP Client}
\date{\today}

\begin{document}

\maketitle

\section{Introduction}
This is a sample LaTeX document created for testing the MCP client.

\section{Content}
The MCP client allows you to interact with the Overleaf MCP server programmatically.

\end{document}
"""

# Write the example file
with open(EXAMPLE_TEX_FILE, "w") as f:
    f.write(EXAMPLE_TEX_CONTENT)


async def main():
    """Run the client example."""
    print("Overleaf MCP Client Example")
    print("=========================\n")

    # Create a client connected to a local MCP server
    # Note: This assumes the server is running locally on the default port
    client = Client("http://localhost:5000")

    # Use a context manager to manage the client connection lifecycle
    async with client:
        print("Connected to Overleaf MCP server")
        
        # Test the connection with a ping
        await client.ping()
        print("Ping successful!")

        # List available tools
        print("\nListing available tools:")
        tools = await client.list_tools()
        
        # Filter for Overleaf-specific tools
        overleaf_tools = [tool for tool in tools if "overleaf" in tool.name.lower()]
        for tool in overleaf_tools:
            print(f"- {tool.name}: {tool.description}")

        # Get Overleaf help
        print("\nGetting Overleaf help:")
        try:
            help_content = await client.call_tool("get_overleaf_help")
            # Print just the first few lines
            first_lines = help_content[0].text.split("\n")[:5]
            print("\n".join(first_lines))
            print("...")
        except Exception as e:
            print(f"Error getting help: {e}")

        # Analyze our example project
        print("\nAnalyzing example project:")
        try:
            analysis = await client.call_tool(
                "analyze_overleaf_project", 
                {"project_dir": str(EXAMPLE_PROJECT_DIR)}
            )
            # Print just the first few lines
            first_lines = analysis[0].text.split("\n")[:5]
            print("\n".join(first_lines))
            print("...")
        except Exception as e:
            print(f"Error analyzing project: {e}")

        # Try a general LaTeX tool
        print("\nChecking for document tools:")
        document_tools = [tool for tool in tools if "document" in tool.name.lower()]
        
        if document_tools:
            print(f"Found {len(document_tools)} document tools")
            tool = document_tools[0]
            print(f"Trying tool: {tool.name}")
            
            try:
                result = await client.call_tool(
                    tool.name, 
                    {"file_path": str(EXAMPLE_TEX_FILE)}
                )
                print(f"Tool returned: {result[0].text[:100]}...")
            except Exception as e:
                print(f"Error calling tool: {e}")
        else:
            print("No document tools found")

        # List resources
        print("\nListing resources:")
        try:
            resources = await client.list_resources()
            for res in resources[:3]:  # Show first 3 resources
                print(f"- {res.uri}: {res.name}")
            if len(resources) > 3:
                print(f"... and {len(resources) - 3} more")
        except Exception as e:
            print(f"Error listing resources: {e}")

        print("\nClient example completed!")


if __name__ == "__main__":
    asyncio.run(main()) 