#!/usr/bin/env python3
"""
Advanced usage of the MCP client with custom transports and handlers.

This example demonstrates more advanced features:
1. Using different transport options (HTTP, WebSocket, direct)
2. Setting up custom roots and sampling handlers
3. Handling notifications from the server
4. Handling errors gracefully
"""

import asyncio
import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

# Add the parent directory to the Python path to import the package if needed
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import the client components
from fastmcp.client import Client
from fastmcp.client.roots import RootsList
from fastmcp.client.transports import (
    HTTPTransport,
    WebSocketTransport,
    DirectProcessTransport,
)
import mcp.types as types

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("mcp-client-advanced")

# Example roots directory - where LaTeX projects are stored
ROOTS_DIR = Path(__file__).parent / "demo_output" / "projects"
ROOTS_DIR.mkdir(exist_ok=True, parents=True)

# Create a demo project for our roots
DEMO_PROJECT = ROOTS_DIR / "demo_project"
DEMO_PROJECT.mkdir(exist_ok=True)

# Create a sample LaTeX file for the project
DEMO_TEX_FILE = DEMO_PROJECT / "main.tex"
DEMO_TEX_CONTENT = r"""
\documentclass{article}
\usepackage[utf8]{inputenc}

\title{Advanced MCP Client Demo}
\author{MCP Client}
\date{\today}

\begin{document}

\maketitle

\section{Introduction}
This project demonstrates advanced MCP client features.

\end{document}
"""

# Write the example file
with open(DEMO_TEX_FILE, "w") as f:
    f.write(DEMO_TEX_CONTENT)


# Define a custom message handler to process server notifications
async def message_handler(message: Union[types.ServerNotification, Any]):
    """Handle messages and notifications from the server."""
    if isinstance(message, types.ServerNotification):
        notification = message.unpack()
        
        if hasattr(notification, "method"):
            logger.info(f"Received notification: {notification.method}")
            
            # Handle specific notifications
            if notification.method == "logging/message":
                log_params = notification.params
                logger.info(f"Log message: [{log_params.level}] {log_params.message}")
    elif isinstance(message, Exception):
        logger.error(f"Error in message handling: {message}")


# Define a custom sampling handler
async def sampling_handler(context: Any, params: types.CreateMessageRequestParams) -> types.CreateMessageResult:
    """Handle sampling requests from the server."""
    logger.info(f"Received sampling request for: {params.prompt}")
    
    # In a real implementation, you might call an LLM here
    # For this demo, we'll just return a simple message
    return types.CreateMessageResult(
        message=types.TextContent(
            text=f"Sample response for prompt: {params.prompt}"
        )
    )


async def demonstrate_http_transport():
    """Demonstrate using HTTP transport."""
    print("\n=== HTTP Transport Demo ===")
    
    # Create a client with HTTP transport
    # Note: This requires a running server at the specified URL
    http_transport = HTTPTransport("http://localhost:5000")
    
    client = Client(
        transport=http_transport,
        roots=RootsList([str(ROOTS_DIR)]),
        message_handler=message_handler,
        sampling_handler=sampling_handler,
    )
    
    try:
        async with client:
            print("Connected via HTTP")
            
            # Basic ping test
            await client.ping()
            print("Ping successful")
            
            # List tools
            tools = await client.list_tools()
            print(f"Found {len(tools)} tools")
            
            # Use a simple tool
            try:
                result = await client.call_tool("hello_latex")
                print(f"Tool result: {result[0].text}")
            except Exception as e:
                print(f"Tool error: {e}")
    except Exception as e:
        print(f"HTTP connection failed: {e}")


async def demonstrate_websocket_transport():
    """Demonstrate using WebSocket transport."""
    print("\n=== WebSocket Transport Demo ===")
    
    # Create a client with WebSocket transport
    # Note: This requires a running server with WebSocket support
    ws_transport = WebSocketTransport("ws://localhost:5000/ws")
    
    client = Client(
        transport=ws_transport,
        roots=RootsList([str(ROOTS_DIR)]),
        message_handler=message_handler,
    )
    
    try:
        async with client:
            print("Connected via WebSocket")
            
            # Basic ping test
            await client.ping()
            print("Ping successful")
            
            # Trigger a notification by changing the roots list
            new_roots = list(ROOTS_DIR.glob("*"))
            client.set_roots(RootsList([str(r) for r in new_roots]))
            await client.send_roots_list_changed()
            print("Sent roots_list_changed notification")
            
            # Wait briefly to see if we get any notifications back
            await asyncio.sleep(1)
    except Exception as e:
        print(f"WebSocket connection failed: {e}")


async def demonstrate_direct_transport():
    """Demonstrate using direct process transport."""
    print("\n=== Direct Process Transport Demo ===")
    
    try:
        # Import the MCP server - assuming it's available in the path
        from overleaf_mcp.server import mcp as server_instance
        
        # Create a client with direct process transport
        direct_transport = DirectProcessTransport(server_instance)
        
        client = Client(
            transport=direct_transport,
            roots=RootsList([str(ROOTS_DIR)]),
            message_handler=message_handler,
        )
        
        async with client:
            print("Connected directly to server process")
            
            # Demonstrate logging level control
            await client.set_logging_level(types.LoggingLevel.DEBUG)
            print("Set logging level to DEBUG")
            
            # Read a resource if available
            try:
                resources = await client.list_resources()
                if resources:
                    resource = resources[0]
                    contents = await client.read_resource(resource.uri)
                    print(f"Read resource {resource.name}: {len(contents)} content blocks")
            except Exception as e:
                print(f"Error reading resources: {e}")
                
            # Call a tool with error handling
            try:
                result = await client.call_tool(
                    "analyze_overleaf_project",
                    {"project_dir": str(DEMO_PROJECT)}
                )
                # Just print the first few lines
                content = result[0].text.split("\n")[:3]
                print("\n".join(content) + "...")
            except Exception as e:
                print(f"Tool error: {e}")
                
    except ImportError:
        print("Could not import server module - skipping direct transport demo")


async def main():
    """Run the advanced client examples."""
    print("Advanced Overleaf MCP Client Examples")
    print("===================================\n")
    
    print("These examples demonstrate different transport mechanisms and advanced features.")
    print("Note: Some examples require a running MCP server to connect to.")
    
    # Try HTTP transport (requires running server)
    try:
        await demonstrate_http_transport()
    except Exception as e:
        print(f"HTTP demo failed: {e}")
    
    # Try WebSocket transport (requires running server with WebSocket support)
    try:
        await demonstrate_websocket_transport()
    except Exception as e:
        print(f"WebSocket demo failed: {e}")
    
    # Try direct process transport (does not require external server)
    try:
        await demonstrate_direct_transport()
    except Exception as e:
        print(f"Direct transport demo failed: {e}")
    
    print("\nAdvanced client examples completed!")


if __name__ == "__main__":
    asyncio.run(main()) 