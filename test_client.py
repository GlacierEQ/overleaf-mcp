#!/usr/bin/env python3
"""
Unified test client for Overleaf MCP Server.

This script combines the functionality of both direct tool testing and
client-server connection testing to verify the MCP server is functioning correctly.
It includes comprehensive error handling and debug information.
"""

import asyncio
import argparse
import sys
import os
from pathlib import Path
import traceback

# Add the parent directory to the Python path to import the package if needed
sys.path.insert(0, str(Path(__file__).parent))

# Import the client and server components
from fastmcp.client import Client
from fastmcp.client.transports import create_connected_server_and_client_session, WSTransport

# Import the server
from overleaf_mcp.server import mcp as server_instance
from overleaf_mcp.tools import document_tools, element_tools, format_tools, overleaf_tools

# Create a test directory
TEST_DIR = Path(__file__).parent / "test_output"
TEST_DIR.mkdir(exist_ok=True)

class OverleafMCPTester:
    """Class to test the Overleaf MCP server and its tools."""
    
    def __init__(self, mode="direct"):
        """Initialize the tester with the specified mode.
        
        Args:
            mode: The connection mode ("direct", "websocket", or "tools")
        """
        self.mode = mode
        self.client = None
        self.test_failures = []
        self.test_successes = []
        
    async def setup_client(self):
        """Set up the client based on the selected mode."""
        try:
            if self.mode == "direct":
                print("Setting up direct connection to server...")
                # Create the client directly - this isn't working but keeping as placeholder
                self._session_context = create_connected_server_and_client_session(server_instance)
                self._session = await self._session_context.__aenter__()
                self.client = Client.from_session(self._session)
                print("Direct connection established!")
                
            elif self.mode == "websocket":
                print("Setting up WebSocket connection to server...")
                # Use PORT environment variable or default to 8765
                port = int(os.environ.get("PORT", 8765))
                transport = WSTransport(f"ws://localhost:{port}/ws")
                self.client = Client(transport)
                # Enter the client context manager
                self._client_context = self.client.__aenter__()
                await self._client_context
                print(f"WebSocket connection established to ws://localhost:{port}/ws!")
                
            elif self.mode == "tools":
                print("Using direct tool access (no client-server communication)")
                self.client = None
            
            else:
                raise ValueError(f"Invalid mode: {self.mode}")
                
        except Exception as e:
            print(f"Error setting up client: {str(e)}")
            traceback.print_exc()
            raise
    
    async def cleanup(self):
        """Clean up resources."""
        try:
            if self.mode == "direct" and hasattr(self, '_session_context') and hasattr(self, '_session'):
                await self._session_context.__aexit__(None, None, None)
            elif self.mode == "websocket" and hasattr(self, 'client') and self.client:
                await self.client.__aexit__(None, None, None)
        except Exception as e:
            print(f"Error during cleanup: {str(e)}")
            traceback.print_exc()
    
    async def test_connection(self):
        """Test the client-server connection."""
        if self.mode == "tools":
            print("Skipping connection test in tools mode")
            return True
            
        try:
            print("\n=== Testing Connection ===")
            tools = await self.client.list_tools()
            print(f"Found {len(tools)} tools:")
            for tool in tools[:5]:
                print(f"- {tool.name}: {tool.description}")
            if len(tools) > 5:
                print(f"... and {len(tools) - 5} more")
                
            resources = await self.client.list_resources()
            print(f"Found {len(resources)} resources")
            
            # Test hello_latex tool
            print("\nTesting hello_latex tool:")
            result = await self.client.call_tool("hello_latex")
            print(result)
            
            self.test_successes.append("Connection test")
            return True
            
        except Exception as e:
            print(f"Connection test failed: {e}")
            traceback.print_exc()
            self.test_failures.append("Connection test")
            return False
    
    async def test_document_tools(self):
        """Test the document tools."""
        print("\n=== Document Tools Tests ===")
        try:
            # Test create_document
            test_doc_path = TEST_DIR / "test_document.tex"
            print("\nTesting create_document:")
            
            result = await self.client.call_tool(
                "create_document",
                {
                    "title": "Test Document",
                    "author": "MCP Tester",
                    "document_class": "article",
                    "output_path": str(test_doc_path)
                }
            )
                
            print(result)
            
            # Test open_document
            if test_doc_path.exists():
                print("\nTesting open_document:")
                
                result = await self.client.call_tool(
                    "open_document", 
                    {"file_path": str(test_doc_path)}
                )
                    
                print(result[:200] + "..." if len(result) > 200 else result)
            
            # Test get_project_structure
            print("\nTesting get_project_structure:")
            
            result = await self.client.call_tool(
                "get_project_structure",
                {"directory": str(TEST_DIR)}
            )
                
            print(result)
            
            self.test_successes.append("Document tools test")
            return True
            
        except Exception as e:
            print(f"Document tools test failed: {str(e)}")
            traceback.print_exc()
            self.test_failures.append("Document tools test")
            return False
    
    async def test_element_tools(self):
        """Test the element tools."""
        print("\n=== Element Tools Tests ===")
        try:
            # Test create_equation
            print("\nTesting create_equation:")
            
            result = await self.client.call_tool(
                "create_equation",
                {"equation": "E = mc^2"}
            )
                
            print(result)
            
            # Test create_table
            print("\nTesting create_table:")
            
            result = await self.client.call_tool(
                "create_table",
                {
                    "rows": 3, 
                    "cols": 2,
                    "headers": ["Name", "Age"],
                    "data": [["Alice", "30"], ["Bob", "25"], ["Charlie", "35"]],
                    "caption": "Sample Table"
                }
            )
                
            print(result)
            
            self.test_successes.append("Element tools test")
            return True
            
        except Exception as e:
            print(f"Element tools test failed: {str(e)}")
            traceback.print_exc()
            self.test_failures.append("Element tools test")
            return False
    
    async def test_format_tools(self):
        """Test the format tools."""
        print("\n=== Format Tools Tests ===")
        try:
            # Test format_latex
            print("\nTesting format_latex:")
            unformatted = r"\begin{document}   \section{Test}  This is a test.\end{document}"
            
            result = await self.client.call_tool(
                "format_latex",
                {"latex": unformatted}
            )
                
            print(result)
            
            # Test convert_to_latex
            print("\nTesting convert_to_latex:")
            plain_text = "This is **bold** and *italic* text with a [link](https://example.com)."
            
            result = await self.client.call_tool(
                "convert_to_latex",
                {"text": plain_text}
            )
                
            print(result)
            
            self.test_successes.append("Format tools test")
            return True
            
        except Exception as e:
            print(f"Format tools test failed: {str(e)}")
            traceback.print_exc()
            self.test_failures.append("Format tools test")
            return False
    
    async def test_overleaf_tools(self):
        """Test the overleaf tools."""
        print("\n=== Overleaf Tools Tests ===")
        try:
            # Test get_overleaf_help
            print("\nTesting get_overleaf_help:")
            
            result = await self.client.call_tool("get_overleaf_help")
                
            print(result[:200] + "..." if len(result) > 200 else result)
            
            self.test_successes.append("Overleaf tools test")
            return True
            
        except Exception as e:
            print(f"Overleaf tools test failed: {str(e)}")
            traceback.print_exc()
            self.test_failures.append("Overleaf tools test")
            return False
    
    async def run_tests(self):
        """Run all tests."""
        if self.mode == "tools":
            print("Using direct connection instead of tools mode")
            self.mode = "direct"
            
        try:
            await self.setup_client()
            
            success = await self.test_connection()
            if not success and self.mode == "websocket":
                print("\nWebSocket connection failed. Is the server running?")
                print("Try running: python -m overleaf_mcp.cli run")
                print("Switching to direct connection mode...")
                self.mode = "direct"
                await self.cleanup()  # Clean up previous connection
                await self.setup_client()
                success = await self.test_connection()
            
            await self.test_document_tools()
            await self.test_element_tools()
            await self.test_format_tools()
            await self.test_overleaf_tools()
            
            # Print summary
            print("\n=== Test Summary ===")
            print(f"Successful tests: {len(self.test_successes)} - {', '.join(self.test_successes)}")
            print(f"Failed tests: {len(self.test_failures)} - {', '.join(self.test_failures)}")
            
            return len(self.test_failures) == 0
        finally:
            await self.cleanup()

async def main():
    """Main function to run the tests."""
    parser = argparse.ArgumentParser(description="Test the Overleaf MCP server")
    parser.add_argument(
        "--mode", 
        choices=["direct", "websocket", "tools"], 
        default="direct",
        help="Connection mode: direct (in-process), websocket (external server), or tools (direct function calls)"
    )
    args = parser.parse_args()
    
    tester = OverleafMCPTester(mode=args.mode)
    success = await tester.run_tests()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    asyncio.run(main()) 