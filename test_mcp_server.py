#!/usr/bin/env python3
"""
Test script for Overleaf MCP Server.

This script starts the MCP server, then connects to it using the client,
and runs tests to verify the functionality.
"""

import asyncio
import subprocess
import sys
import time
import signal
import os
from pathlib import Path
import argparse
import threading

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

async def main():
    """Start server, run tests, then stop server."""
    parser = argparse.ArgumentParser(description="Test the Overleaf MCP server")
    parser.add_argument("--no-server", action="store_true", help="Don't start a server, just run tests")
    parser.add_argument("--port", type=int, default=8765, help="Port to run the server on (default: 8765)")
    args = parser.parse_args()
    
    server_process = None
    
    try:
        # Start the server if needed
        if not args.no_server:
            print("Starting MCP server...")
            # Set port in environment variable
            os.environ["PORT"] = str(args.port)
            
            server_process = subprocess.Popen(
                [sys.executable, "-m", "overleaf_mcp.cli", "run"], 
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )
            
            # Read output and error streams in separate threads
            def print_output(stream, prefix):
                for line in iter(stream.readline, ''):
                    print(f"{prefix}: {line.rstrip()}")
            
            stdout_thread = threading.Thread(
                target=print_output, 
                args=(server_process.stdout, "SERVER"),
                daemon=True
            )
            stderr_thread = threading.Thread(
                target=print_output, 
                args=(server_process.stderr, "SERVER ERROR"),
                daemon=True
            )
            stdout_thread.start()
            stderr_thread.start()
            
            # Give the server some time to start
            time.sleep(5)
            
            # Check if the server started correctly
            if server_process.poll() is not None:
                stdout, stderr = server_process.communicate()
                print("Failed to start server:")
                print(f"STDOUT: {stdout}")
                print(f"STDERR: {stderr}")
                return 1
                
            print("Server started successfully!")
            print(f"WebSocket URL: ws://localhost:{args.port}/ws")
        
        # Run the client tests
        print("Running client tests...")
        result = subprocess.run(
            [sys.executable, "test_client.py", "--mode=websocket"],
            capture_output=True,
            text=True,
            env={**os.environ, "PORT": str(args.port)}
        )
        
        # Print the test output
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
            
        return result.returncode
            
    finally:
        # Clean up the server process
        if server_process and server_process.poll() is None:
            print("Stopping server...")
            # Try graceful shutdown first
            server_process.send_signal(signal.SIGINT)
            try:
                server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                print("Server didn't shut down gracefully, force killing...")
                server_process.kill()
                
            stdout, stderr = server_process.communicate()
            if stdout:
                print(f"Server STDOUT: {stdout}")
            if stderr:
                print(f"Server STDERR: {stderr}")

if __name__ == "__main__":
    sys.exit(asyncio.run(main())) 