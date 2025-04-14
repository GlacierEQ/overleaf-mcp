"""
Main MCP server implementation for Overleaf-MCP.
"""

from fastmcp import FastMCP
import sys
import uvicorn
from starlette.applications import Starlette
from starlette.middleware.cors import CORSMiddleware
from starlette.routing import WebSocketRoute, Route, Mount
from starlette.responses import JSONResponse
from starlette.websockets import WebSocket
from mcp.server.websocket import websocket_server
import anyio
from mcp.server.session import ServerSession
import os
from pathlib import Path

# Create the MCP server
mcp = FastMCP(
    "Overleaf LaTeX Editor",
    description="LaTeX editing with Overleaf integration",
    dependencies=["TexSoup>=0.3.1", "pylatexenc>=2.10"],
)

# Import and register tools
from .tools import document_tools, element_tools, format_tools, overleaf_tools
document_tools.register(mcp)
element_tools.register(mcp)
format_tools.register(mcp)
overleaf_tools.register(mcp)

# For testing purposes, we'll keep a simple tool
@mcp.tool()
def hello_latex() -> str:
    """Test tool to verify the server is working"""
    return "Hello from Overleaf MCP Server! The server is running correctly."

async def handle_websocket(websocket: WebSocket):
    """Handle WebSocket connections for MCP protocol."""
    await websocket.accept(subprotocol="mcp")
    
    # Create memory object streams for communication
    read_stream_writer, read_stream = anyio.create_memory_object_stream(0)
    write_stream, write_stream_reader = anyio.create_memory_object_stream(0)
    
    async def ws_reader():
        try:
            async with read_stream_writer:
                async for msg in websocket.iter_text():
                    try:
                        from mcp.types import JSONRPCMessage
                        client_message = JSONRPCMessage.model_validate_json(msg)
                        await read_stream_writer.send(client_message)
                    except Exception as e:
                        await read_stream_writer.send(e)
        except Exception:
            await websocket.close()
    
    async def ws_writer():
        try:
            async with write_stream_reader:
                async for message in write_stream_reader:
                    obj = message.model_dump_json(by_alias=True, exclude_none=True)
                    await websocket.send_text(obj)
        except Exception:
            await websocket.close()
    
    async with anyio.create_task_group() as tg:
        tg.start_soon(ws_reader)
        tg.start_soon(ws_writer)
        
        await mcp._mcp_server.run(
            read_stream,
            write_stream,
            mcp._mcp_server.create_initialization_options(),
        )

async def health_check(scope, receive, send):
    """Simple health check endpoint."""
    response = JSONResponse({"status": "ok", "message": "Overleaf MCP Server is running"})
    await response(scope, receive, send)

def create_app():
    """Create a Starlette application with WebSocket support and CORS."""
    routes = [
        WebSocketRoute("/ws", endpoint=handle_websocket),
        Route("/health", endpoint=health_check, methods=["GET"]),
    ]
    
    app = Starlette(debug=True, routes=routes)
    
    # Add CORS middleware with permissive settings
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Allow all origins
        allow_credentials=True,
        allow_methods=["*"],  # Allow all methods
        allow_headers=["*"],  # Allow all headers
    )
    
    return app

def main():
    """Run the MCP server directly"""
    app = create_app()
    port = int(os.environ.get("PORT", 8765))
    print(f"Starting Overleaf MCP Server on port {port}")
    print(f"WebSocket endpoint: ws://localhost:{port}/ws")
    print(f"Health check: http://localhost:{port}/health")
    uvicorn.run(app, host="0.0.0.0", port=port)

if __name__ == "__main__":
    main() 