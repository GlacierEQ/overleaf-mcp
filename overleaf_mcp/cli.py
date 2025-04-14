"""
Command-line interface for Overleaf MCP server.
"""

import argparse
import sys
from . import __version__
from .server import mcp, create_app, main as server_main

def main():
    """Main entry point for the CLI"""
    parser = argparse.ArgumentParser(
        description="Overleaf MCP Server - LaTeX editing with Overleaf integration"
    )
    
    # Add subparsers for different commands
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Run command
    run_parser = subparsers.add_parser("run", help="Run the MCP server")
    run_parser.add_argument("--port", type=int, default=8765, help="Port to run the server on (default: 8765)")
    
    # Version command
    version_parser = subparsers.add_parser("version", help="Show version information")
    
    # Parse arguments
    args = parser.parse_args()
    
    if args.command == "run":
        print(f"Starting Overleaf MCP Server v{__version__}...")
        # Set the port in environment variable
        import os
        if hasattr(args, "port"):
            os.environ["PORT"] = str(args.port)
        server_main()
    elif args.command == "version":
        print(f"Overleaf MCP Server v{__version__}")
    else:
        parser.print_help()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 